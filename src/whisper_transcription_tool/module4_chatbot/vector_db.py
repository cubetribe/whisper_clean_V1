"""
Vector database integration for the Whisper Transcription Tool.
Handles storing and retrieving transcript embeddings for semantic search.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Union

from ..core.config import load_config
from ..core.events import EventType, publish
from ..core.exceptions import VectorDBError
from ..core.logging_setup import get_logger
from ..core.utils import ensure_directory_exists

logger = get_logger(__name__)


def initialize_vector_db(config: Optional[Dict] = None) -> bool:
    """
    Initialize the vector database.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        True if successful, False otherwise
    """
    # Load config if not provided
    if config is None:
        config = load_config()
    
    try:
        # Import optional dependencies
        try:
            import chromadb
        except ImportError:
            logger.error("chromadb not installed. Please install it to use vector database functionality.")
            raise VectorDBError("chromadb not installed")
        
        # Get vector database path from config
        db_path = config.get("chatbot", {}).get("vector_db_path", str(Path.home() / "whisper_vectordb"))
        
        # Ensure directory exists
        ensure_directory_exists(db_path)
        
        # Initialize client
        client = chromadb.PersistentClient(path=db_path)
        
        # Create collection if it doesn't exist
        try:
            collection = client.get_collection("transcripts")
            logger.info(f"Vector database collection 'transcripts' already exists with {collection.count()} documents")
        except:
            collection = client.create_collection("transcripts")
            logger.info("Created new vector database collection 'transcripts'")
        
        return True
    
    except Exception as e:
        logger.error(f"Error initializing vector database: {e}")
        return False


def add_transcript_to_vector_db(
    transcript_path: Union[str, Path],
    metadata: Optional[Dict] = None,
    config: Optional[Dict] = None
) -> bool:
    """
    Add a transcript to the vector database.
    
    Args:
        transcript_path: Path to transcript file
        metadata: Additional metadata
        config: Configuration dictionary
        
    Returns:
        True if successful, False otherwise
    """
    # Load config if not provided
    if config is None:
        config = load_config()
    
    try:
        # Import optional dependencies
        try:
            import chromadb
            from sentence_transformers import SentenceTransformer
        except ImportError:
            logger.error("Required packages not installed. Please install chromadb and sentence-transformers.")
            raise VectorDBError("Required packages not installed")
        
        # Validate transcript file
        transcript_path = str(transcript_path)
        if not os.path.exists(transcript_path):
            error_msg = f"Transcript file not found: {transcript_path}"
            logger.error(error_msg)
            return False
        
        # Read transcript
        with open(transcript_path, "r", encoding="utf-8") as f:
            transcript_text = f.read()
        
        # Get vector database path from config
        db_path = config.get("chatbot", {}).get("vector_db_path", str(Path.home() / "whisper_vectordb"))
        
        # Initialize client
        client = chromadb.PersistentClient(path=db_path)
        
        # Get or create collection
        try:
            collection = client.get_collection("transcripts")
        except:
            collection = client.create_collection("transcripts")
        
        # Prepare metadata
        if metadata is None:
            metadata = {}
        
        metadata["file_path"] = transcript_path
        metadata["file_name"] = os.path.basename(transcript_path)
        
        # Generate document ID
        doc_id = f"doc_{os.path.basename(transcript_path)}_{hash(transcript_text) % 10000}"
        
        # Split transcript into chunks
        chunks = split_text_into_chunks(transcript_text, chunk_size=512, overlap=50)
        
        # Initialize embedding model
        model_name = config.get("chatbot", {}).get("embedding_model", "all-MiniLM-L6-v2")
        model = SentenceTransformer(model_name)
        
        # Add chunks to collection
        for i, chunk in enumerate(chunks):
            chunk_id = f"{doc_id}_chunk_{i}"
            chunk_metadata = metadata.copy()
            chunk_metadata["chunk_index"] = i
            chunk_metadata["total_chunks"] = len(chunks)
            
            # Generate embedding
            embedding = model.encode(chunk).tolist()
            
            # Add to collection
            collection.add(
                ids=[chunk_id],
                embeddings=[embedding],
                metadatas=[chunk_metadata],
                documents=[chunk]
            )
        
        logger.info(f"Added transcript {transcript_path} to vector database with {len(chunks)} chunks")
        
        # Publish event
        publish(EventType.VECTOR_DB_DOCUMENT_ADDED, {
            "transcript_path": transcript_path,
            "chunks": len(chunks),
            "doc_id": doc_id
        })
        
        return True
    
    except Exception as e:
        logger.error(f"Error adding transcript to vector database: {e}")
        return False


def search_vector_db(
    query: str,
    n_results: int = 5,
    config: Optional[Dict] = None
) -> List[Dict]:
    """
    Search the vector database for similar content.
    
    Args:
        query: Search query
        n_results: Number of results to return
        config: Configuration dictionary
        
    Returns:
        List of search results
    """
    # Load config if not provided
    if config is None:
        config = load_config()
    
    try:
        # Import optional dependencies
        try:
            import chromadb
            from sentence_transformers import SentenceTransformer
        except ImportError:
            logger.error("Required packages not installed. Please install chromadb and sentence-transformers.")
            raise VectorDBError("Required packages not installed")
        
        # Get vector database path from config
        db_path = config.get("chatbot", {}).get("vector_db_path", str(Path.home() / "whisper_vectordb"))
        
        # Initialize client
        client = chromadb.PersistentClient(path=db_path)
        
        # Get collection
        try:
            collection = client.get_collection("transcripts")
        except:
            logger.error("Vector database collection 'transcripts' not found")
            return []
        
        # Initialize embedding model
        model_name = config.get("chatbot", {}).get("embedding_model", "all-MiniLM-L6-v2")
        model = SentenceTransformer(model_name)
        
        # Generate query embedding
        query_embedding = model.encode(query).tolist()
        
        # Search collection
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            include=["documents", "metadatas", "distances"]
        )
        
        # Format results
        formatted_results = []
        if results and "documents" in results and results["documents"]:
            for i, doc in enumerate(results["documents"][0]):
                result = {
                    "text": doc,
                    "metadata": results["metadatas"][0][i] if "metadatas" in results else {},
                    "distance": results["distances"][0][i] if "distances" in results else None
                }
                formatted_results.append(result)
        
        return formatted_results
    
    except Exception as e:
        logger.error(f"Error searching vector database: {e}")
        return []


def split_text_into_chunks(text: str, chunk_size: int = 512, overlap: int = 50) -> List[str]:
    """
    Split text into overlapping chunks.
    
    Args:
        text: Text to split
        chunk_size: Maximum chunk size in characters
        overlap: Overlap between chunks in characters
        
    Returns:
        List of text chunks
    """
    # Split text into paragraphs
    paragraphs = text.split("\n\n")
    
    chunks = []
    current_chunk = ""
    
    for paragraph in paragraphs:
        # If adding this paragraph would exceed chunk size, save current chunk and start a new one
        if len(current_chunk) + len(paragraph) > chunk_size:
            chunks.append(current_chunk.strip())
            
            # Start new chunk with overlap from previous chunk
            words = current_chunk.split()
            overlap_text = " ".join(words[-overlap:]) if len(words) > overlap else current_chunk
            current_chunk = overlap_text + "\n\n" + paragraph
        else:
            # Add paragraph to current chunk
            if current_chunk:
                current_chunk += "\n\n" + paragraph
            else:
                current_chunk = paragraph
    
    # Add the last chunk if it's not empty
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    return chunks


def clear_vector_db(config: Optional[Dict] = None) -> bool:
    """
    Clear the vector database.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        True if successful, False otherwise
    """
    # Load config if not provided
    if config is None:
        config = load_config()
    
    try:
        # Import optional dependencies
        import chromadb
        
        # Get vector database path from config
        db_path = config.get("chatbot", {}).get("vector_db_path", str(Path.home() / "whisper_vectordb"))
        
        # Initialize client
        client = chromadb.PersistentClient(path=db_path)
        
        # Delete collection if it exists
        try:
            client.delete_collection("transcripts")
            logger.info("Deleted vector database collection 'transcripts'")
        except:
            logger.warning("Vector database collection 'transcripts' not found")
        
        # Create new collection
        client.create_collection("transcripts")
        logger.info("Created new vector database collection 'transcripts'")
        
        # Publish event
        publish(EventType.VECTOR_DB_CLEARED, {})
        
        return True
    
    except Exception as e:
        logger.error(f"Error clearing vector database: {e}")
        return False
