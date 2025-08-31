#!/usr/bin/env python3
"""
Test script for audio chunking functionality.
Creates a test audio file and tests the chunking feature.
"""

import os
import sys
import tempfile
import subprocess
from pathlib import Path

# Add project directory to path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

from src.whisper_transcription_tool.core.audio_chunker import AudioChunker
from src.whisper_transcription_tool.core.config import load_config
from src.whisper_transcription_tool.module1_transcribe import transcribe_audio


def create_test_audio(duration_minutes=25, output_path=None):
    """
    Create a test audio file using FFmpeg.
    
    Args:
        duration_minutes: Duration in minutes
        output_path: Output file path
        
    Returns:
        Path to created audio file
    """
    if output_path is None:
        output_path = os.path.join(tempfile.gettempdir(), f"test_audio_{duration_minutes}min.wav")
    
    # Create silence audio file with FFmpeg
    duration_seconds = duration_minutes * 60
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", f"sine=frequency=440:duration={duration_seconds}",
        "-ar", "16000",
        "-ac", "1",
        output_path
    ]
    
    print(f"Creating test audio file ({duration_minutes} minutes)...")
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"✓ Created test audio: {output_path}")
        return output_path
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to create test audio: {e}")
        return None


def test_chunk_detection():
    """Test if chunk detection works correctly."""
    print("\n=== Testing Chunk Detection ===")
    
    config = load_config()
    chunker = AudioChunker(config)
    
    # Create test files
    test_files = [
        (15, False),  # 15 minutes - should not chunk
        (19, False),  # 19 minutes - should not chunk  
        (20, False),  # 20 minutes - exactly at threshold
        (21, True),   # 21 minutes - should chunk
        (45, True),   # 45 minutes - should chunk
    ]
    
    for duration, should_chunk in test_files:
        print(f"\nTesting {duration} minute file...")
        audio_path = create_test_audio(duration)
        
        if audio_path:
            result = chunker.should_chunk(audio_path)
            expected = "should chunk" if should_chunk else "should NOT chunk"
            actual = "chunks" if result else "does NOT chunk"
            
            if result == should_chunk:
                print(f"✓ PASS: {duration} min file {expected} and {actual}")
            else:
                print(f"✗ FAIL: {duration} min file {expected} but {actual}")
            
            # Clean up
            os.remove(audio_path)


def test_chunk_splitting():
    """Test actual audio splitting."""
    print("\n=== Testing Audio Splitting ===")
    
    config = load_config()
    chunker = AudioChunker(config)
    
    # Create a 45-minute test file
    duration = 45
    print(f"\nCreating {duration} minute test file...")
    audio_path = create_test_audio(duration)
    
    if not audio_path:
        print("✗ Failed to create test audio")
        return
    
    try:
        # Split the audio
        print("Splitting audio into chunks...")
        chunks = chunker.split_audio(audio_path)
        
        print(f"✓ Created {len(chunks)} chunks:")
        for chunk in chunks:
            print(f"  - {chunk['filename']}: {chunk['duration']:.1f}s @ {chunk['start_time']:.1f}s")
        
        # Expected: 3 chunks (0-20min, 20-40min, 40-45min)
        expected_chunks = 3
        if len(chunks) == expected_chunks:
            print(f"✓ PASS: Got expected {expected_chunks} chunks")
        else:
            print(f"✗ FAIL: Expected {expected_chunks} chunks, got {len(chunks)}")
        
        # Clean up chunks
        if chunks:
            chunk_dir = os.path.dirname(chunks[0]['path'])
            chunker.cleanup_chunks(chunk_dir)
            print("✓ Cleaned up chunk files")
        
    finally:
        # Clean up test file
        if os.path.exists(audio_path):
            os.remove(audio_path)


def test_transcription_with_chunks():
    """Test end-to-end transcription with chunking."""
    print("\n=== Testing Chunked Transcription ===")
    
    # Create a 25-minute test file
    duration = 25
    print(f"\nCreating {duration} minute test file...")
    audio_path = create_test_audio(duration)
    
    if not audio_path:
        print("✗ Failed to create test audio")
        return
    
    try:
        print("Starting chunked transcription...")
        
        # Note: This will only work if you have a Whisper model installed
        # For testing without a model, you can comment this out
        """
        result = transcribe_audio(
            audio_path=audio_path,
            output_format="txt",
            model="tiny"  # Use tiny model for faster testing
        )
        
        if result.success:
            print(f"✓ Transcription completed successfully")
            if result.metadata and 'chunks' in result.metadata:
                print(f"  - Processed {result.metadata['chunks']} chunks")
        else:
            print(f"✗ Transcription failed: {result.error}")
        """
        
        print("✓ Test audio created successfully")
        print("  (Skipping actual transcription - requires Whisper model)")
        
    finally:
        # Clean up test file
        if os.path.exists(audio_path):
            os.remove(audio_path)


def main():
    """Run all tests."""
    print("=" * 50)
    print("AUDIO CHUNKING TEST SUITE")
    print("=" * 50)
    
    # Check FFmpeg availability
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        print("✓ FFmpeg is available")
    except:
        print("✗ FFmpeg not found - please install FFmpeg first")
        return
    
    # Run tests
    test_chunk_detection()
    test_chunk_splitting()
    test_transcription_with_chunks()
    
    print("\n" + "=" * 50)
    print("TEST SUITE COMPLETED")
    print("=" * 50)


if __name__ == "__main__":
    main()