"""
Chatbot module for the Whisper Transcription Tool.
Handles transcript analysis and interactive conversation.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Union

from ..core.config import load_config
from ..core.events import EventType, publish
from ..core.exceptions import ChatbotError
from ..core.logging_setup import get_logger
from ..core.models import ChatbotResult
from ..core.utils import ensure_directory_exists, get_output_path

logger = get_logger(__name__)

# Default system prompt for the chatbot
DEFAULT_SYSTEM_PROMPT = """
Du bist ein hilfreicher Assistent, der Transkripte analysiert. 
Deine Aufgabe ist es, wichtige Informationen aus dem Transkript zu extrahieren, 
Zusammenfassungen zu erstellen und Fragen zum Inhalt zu beantworten.
Sei präzise, höflich und hilfreich.
"""


def analyze_transcript(
    transcript_path: Union[str, Path],
    output_path: Optional[Union[str, Path]] = None,
    analysis_type: str = "summary",
    config: Optional[Dict] = None
) -> ChatbotResult:
    """
    Analyze a transcript using the chatbot.
    
    Args:
        transcript_path: Path to transcript file
        output_path: Path to save analysis results
        analysis_type: Type of analysis to perform (summary, key_points, qa)
        config: Configuration dictionary
        
    Returns:
        ChatbotResult object
    """
    # Load config if not provided
    if config is None:
        config = load_config()
    
    # Validate transcript file
    transcript_path = str(transcript_path)
    if not os.path.exists(transcript_path):
        error_msg = f"Transcript file not found: {transcript_path}"
        logger.error(error_msg)
        return ChatbotResult(success=False, error=error_msg)
    
    # Generate output path if not provided
    if output_path is None:
        output_dir = config["output"]["default_directory"] if "output" in config and "default_directory" in config["output"] else None
        output_path = get_output_path(transcript_path, output_dir, "md", suffix="_analysis")
    else:
        output_path = str(output_path)
    
    # Ensure output directory exists
    ensure_directory_exists(os.path.dirname(output_path))
    
    # Publish event
    publish(EventType.CHATBOT_ANALYSIS_STARTED, {
        "transcript_path": transcript_path,
        "analysis_type": analysis_type,
        "output_path": output_path
    })
    
    try:
        # Read transcript
        with open(transcript_path, "r", encoding="utf-8") as f:
            transcript_text = f.read()
        
        # Get chatbot model from config
        model = config.get("chatbot", {}).get("model", "mistral-7b")
        
        # Determine if we're using a local model or API
        use_local = config.get("chatbot", {}).get("mode", "local") == "local"
        
        # Generate analysis based on analysis type
        if use_local:
            analysis = generate_analysis_local(transcript_text, analysis_type, model)
        else:
            api_key = config.get("chatbot", {}).get("api_key", "")
            if not api_key:
                error_msg = "API key not provided for chatbot"
                logger.error(error_msg)
                return ChatbotResult(success=False, error=error_msg)
            
            analysis = generate_analysis_api(transcript_text, analysis_type, api_key, model)
        
        # Write analysis to output file
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(analysis)
        
        # Publish success event
        publish(EventType.CHATBOT_ANALYSIS_COMPLETED, {
            "transcript_path": transcript_path,
            "output_path": output_path,
            "analysis_type": analysis_type
        })
        
        # Return result
        return ChatbotResult(
            success=True,
            output_file=output_path,
            transcript_path=transcript_path,
            analysis_type=analysis_type,
            analysis_text=analysis
        )
    
    except Exception as e:
        error_msg = f"Error analyzing transcript: {str(e)}"
        logger.error(error_msg)
        publish(EventType.CHATBOT_ANALYSIS_FAILED, {
            "transcript_path": transcript_path,
            "error": error_msg
        })
        return ChatbotResult(success=False, error=error_msg)


def generate_analysis_local(
    transcript_text: str,
    analysis_type: str,
    model: str = "mistral-7b"
) -> str:
    """
    Generate analysis using a local LLM.
    
    Args:
        transcript_text: Transcript text
        analysis_type: Type of analysis to perform
        model: Model to use
        
    Returns:
        Analysis text
    """
    try:
        # Import optional dependencies
        try:
            from llama_cpp import Llama
        except ImportError:
            logger.error("llama-cpp-python not installed. Please install it to use local models.")
            raise ChatbotError("llama-cpp-python not installed")
        
        # Get model path from config
        config = load_config()
        models_dir = config.get("chatbot", {}).get("models_dir", str(Path.home() / "llm_models"))
        
        # Ensure models directory exists
        ensure_directory_exists(models_dir)
        
        # Look for model file
        model_files = [
            os.path.join(models_dir, f"{model}.gguf"),
            os.path.join(models_dir, f"{model}.bin"),
            os.path.join(models_dir, model)
        ]
        
        model_path = None
        for file_path in model_files:
            if os.path.exists(file_path):
                model_path = file_path
                break
        
        if not model_path:
            logger.error(f"Model file not found for {model}")
            raise ChatbotError(f"Model file not found for {model}")
        
        # Load model
        logger.info(f"Loading model: {model_path}")
        llm = Llama(
            model_path=model_path,
            n_ctx=4096,  # Context window
            n_threads=4   # Number of threads
        )
        
        # Generate prompt based on analysis type
        prompt = generate_prompt(transcript_text, analysis_type)
        
        # Generate response
        logger.info("Generating analysis...")
        response = llm(
            prompt,
            max_tokens=2048,
            temperature=0.7,
            top_p=0.9,
            echo=False
        )
        
        # Extract text from response
        if isinstance(response, dict) and "choices" in response:
            analysis = response["choices"][0]["text"]
        elif isinstance(response, dict) and "text" in response:
            analysis = response["text"]
        else:
            analysis = str(response)
        
        return analysis
    
    except Exception as e:
        logger.error(f"Error generating local analysis: {e}")
        # Fallback to a simple analysis
        return generate_fallback_analysis(transcript_text, analysis_type)


def generate_analysis_api(
    transcript_text: str,
    analysis_type: str,
    api_key: str,
    model: str = "gpt-3.5-turbo"
) -> str:
    """
    Generate analysis using an API-based LLM.
    
    Args:
        transcript_text: Transcript text
        analysis_type: Type of analysis to perform
        api_key: API key
        model: Model to use
        
    Returns:
        Analysis text
    """
    try:
        # Import optional dependencies
        try:
            import openai
        except ImportError:
            logger.error("openai not installed. Please install it to use API models.")
            raise ChatbotError("openai not installed")
        
        # Set up OpenAI client
        client = openai.OpenAI(api_key=api_key)
        
        # Generate prompt based on analysis type
        prompt = generate_prompt(transcript_text, analysis_type)
        
        # Generate response
        logger.info(f"Generating analysis using API model: {model}")
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": DEFAULT_SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2048,
            temperature=0.7,
            top_p=0.9
        )
        
        # Extract text from response
        analysis = response.choices[0].message.content
        
        return analysis
    
    except Exception as e:
        logger.error(f"Error generating API analysis: {e}")
        # Fallback to a simple analysis
        return generate_fallback_analysis(transcript_text, analysis_type)


def generate_prompt(transcript_text: str, analysis_type: str) -> str:
    """
    Generate a prompt for the chatbot based on analysis type.
    
    Args:
        transcript_text: Transcript text
        analysis_type: Type of analysis to perform
        
    Returns:
        Prompt text
    """
    if analysis_type == "summary":
        return f"""
        Bitte erstelle eine Zusammenfassung des folgenden Transkripts.
        Fasse die wichtigsten Punkte zusammen und strukturiere die Zusammenfassung klar.
        
        Transkript:
        {transcript_text}
        """
    
    elif analysis_type == "key_points":
        return f"""
        Bitte extrahiere die wichtigsten Punkte aus dem folgenden Transkript.
        Liste die Schlüsselinformationen, wichtige Fakten und Entscheidungen auf.
        
        Transkript:
        {transcript_text}
        """
    
    elif analysis_type == "qa":
        return f"""
        Bitte analysiere das folgende Transkript und erstelle eine Liste von 5 wichtigen Fragen und Antworten,
        die den Inhalt des Transkripts abdecken. Die Fragen sollten die wichtigsten Informationen im Transkript ansprechen.
        
        Transkript:
        {transcript_text}
        """
    
    else:
        return f"""
        Bitte analysiere das folgende Transkript und gib deine Erkenntnisse wieder.
        
        Transkript:
        {transcript_text}
        """


def generate_fallback_analysis(transcript_text: str, analysis_type: str) -> str:
    """
    Generate a simple fallback analysis when LLM processing fails.
    
    Args:
        transcript_text: Transcript text
        analysis_type: Type of analysis to perform
        
    Returns:
        Analysis text
    """
    # Simple word count and statistics
    word_count = len(transcript_text.split())
    line_count = len(transcript_text.splitlines())
    
    analysis = f"""
    # Einfache Transkriptanalyse
    
    ## Statistiken
    - Wortanzahl: {word_count}
    - Zeilenanzahl: {line_count}
    
    ## Hinweis
    Die vollständige Analyse konnte nicht generiert werden. 
    Dies ist eine einfache statistische Analyse des Transkripts.
    
    ## Erste 100 Wörter des Transkripts
    {' '.join(transcript_text.split()[:100])}...
    """
    
    return analysis


def chat_with_transcript(
    transcript_path: Union[str, Path],
    question: str,
    config: Optional[Dict] = None
) -> str:
    """
    Ask a question about a transcript.
    
    Args:
        transcript_path: Path to transcript file
        question: Question to ask
        config: Configuration dictionary
        
    Returns:
        Answer text
    """
    # Load config if not provided
    if config is None:
        config = load_config()
    
    # Validate transcript file
    transcript_path = str(transcript_path)
    if not os.path.exists(transcript_path):
        error_msg = f"Transcript file not found: {transcript_path}"
        logger.error(error_msg)
        return f"Fehler: {error_msg}"
    
    try:
        # Read transcript
        with open(transcript_path, "r", encoding="utf-8") as f:
            transcript_text = f.read()
        
        # Get chatbot model from config
        model = config.get("chatbot", {}).get("model", "mistral-7b")
        
        # Determine if we're using a local model or API
        use_local = config.get("chatbot", {}).get("mode", "local") == "local"
        
        # Generate prompt
        prompt = f"""
        Basierend auf dem folgenden Transkript, beantworte bitte diese Frage:
        
        Frage: {question}
        
        Transkript:
        {transcript_text}
        """
        
        # Generate answer
        if use_local:
            answer = generate_answer_local(prompt, model)
        else:
            api_key = config.get("chatbot", {}).get("api_key", "")
            if not api_key:
                return "Fehler: API-Schlüssel nicht konfiguriert"
            
            answer = generate_answer_api(prompt, api_key, model)
        
        return answer
    
    except Exception as e:
        error_msg = f"Error chatting with transcript: {str(e)}"
        logger.error(error_msg)
        return f"Fehler: {error_msg}"


def generate_answer_local(prompt: str, model: str) -> str:
    """
    Generate an answer using a local LLM.
    
    Args:
        prompt: Prompt text
        model: Model to use
        
    Returns:
        Answer text
    """
    # This is similar to generate_analysis_local but simplified for Q&A
    try:
        # Import optional dependencies
        from llama_cpp import Llama
        
        # Get model path from config
        config = load_config()
        models_dir = config.get("chatbot", {}).get("models_dir", str(Path.home() / "llm_models"))
        
        # Look for model file
        model_files = [
            os.path.join(models_dir, f"{model}.gguf"),
            os.path.join(models_dir, f"{model}.bin"),
            os.path.join(models_dir, model)
        ]
        
        model_path = None
        for file_path in model_files:
            if os.path.exists(file_path):
                model_path = file_path
                break
        
        if not model_path:
            return f"Fehler: Modelldatei für {model} nicht gefunden"
        
        # Load model
        llm = Llama(
            model_path=model_path,
            n_ctx=4096,
            n_threads=4
        )
        
        # Generate response
        response = llm(
            prompt,
            max_tokens=1024,
            temperature=0.7,
            top_p=0.9,
            echo=False
        )
        
        # Extract text from response
        if isinstance(response, dict) and "choices" in response:
            answer = response["choices"][0]["text"]
        elif isinstance(response, dict) and "text" in response:
            answer = response["text"]
        else:
            answer = str(response)
        
        return answer
    
    except Exception as e:
        logger.error(f"Error generating local answer: {e}")
        return f"Fehler bei der Antwortgenerierung: {str(e)}"


def generate_answer_api(prompt: str, api_key: str, model: str) -> str:
    """
    Generate an answer using an API-based LLM.
    
    Args:
        prompt: Prompt text
        api_key: API key
        model: Model to use
        
    Returns:
        Answer text
    """
    try:
        # Import optional dependencies
        import openai
        
        # Set up OpenAI client
        client = openai.OpenAI(api_key=api_key)
        
        # Generate response
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": DEFAULT_SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1024,
            temperature=0.7,
            top_p=0.9
        )
        
        # Extract text from response
        answer = response.choices[0].message.content
        
        return answer
    
    except Exception as e:
        logger.error(f"Error generating API answer: {e}")
        return f"Fehler bei der Antwortgenerierung: {str(e)}"
