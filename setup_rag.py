#!/usr/bin/env python3
"""
Automated RAG Setup Script

This script handles the complete setup process:
1. Checks if Qdrant is installed
2. Starts Qdrant server
3. Builds embeddings from transcripts
4. Tests the RAG system

Usage:
    python setup_rag.py                    # Process all transcripts
    python setup_rag.py --quick            # Process first 10 transcripts only
    python setup_rag.py --max 5            # Process first 5 transcripts
"""

import os
import sys
import time
import asyncio
import argparse
import subprocess
from pathlib import Path
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()


def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 70)
    print(text)
    print("=" * 70 + "\n")


def print_step(step_num, text):
    """Print a formatted step"""
    print(f"\n[Step {step_num}] {text}")
    print("-" * 70)


def check_qdrant_installed():
    """Check if Qdrant binary is installed"""
    qdrant_bin = Path.home() / ".qdrant" / "qdrant"
    return qdrant_bin.exists()


def install_qdrant():
    """Install Qdrant binary"""
    print("Installing Qdrant locally...")
    install_script = Path("./install_qdrant_local.sh")

    if not install_script.exists():
        print("ERROR: install_qdrant_local.sh not found!")
        print("Please ensure you're running this script from the lennyhub-rag directory.")
        return False

    # Make script executable
    os.chmod(install_script, 0o755)

    # Run installation script
    result = subprocess.run(
        ["bash", str(install_script)],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        print("✓ Qdrant installed successfully!")
        return True
    else:
        print("ERROR: Qdrant installation failed!")
        print(result.stderr)
        return False


def is_qdrant_running():
    """Check if Qdrant server is running"""
    try:
        # Qdrant's root endpoint returns version info
        response = requests.get("http://localhost:6333/", timeout=2)
        return response.status_code == 200
    except:
        return False


def start_qdrant():
    """Start Qdrant server"""
    print("Starting Qdrant server...")
    start_script = Path("./start_qdrant.sh")

    if not start_script.exists():
        print("ERROR: start_qdrant.sh not found!")
        return False

    # Make script executable
    os.chmod(start_script, 0o755)

    # Run start script
    result = subprocess.run(
        ["bash", str(start_script)],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        print("✓ Qdrant started successfully!")
        return True
    else:
        # Check if it's already running
        if "already running" in result.stdout.lower():
            print("✓ Qdrant is already running!")
            return True
        print("ERROR: Failed to start Qdrant!")
        print(result.stderr)
        return False


def wait_for_qdrant(timeout=30):
    """Wait for Qdrant to be ready"""
    print("Waiting for Qdrant to be ready...")
    start_time = time.time()

    while time.time() - start_time < timeout:
        if is_qdrant_running():
            print("✓ Qdrant is ready!")
            return True
        time.sleep(1)
        sys.stdout.write(".")
        sys.stdout.flush()

    print("\nERROR: Qdrant failed to start within timeout!")
    return False


def check_api_key():
    """Check if OpenAI API key is set"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY environment variable not set!")
        print("\nPlease set your OpenAI API key:")
        print("  export OPENAI_API_KEY='your-api-key-here'")
        print("\nOr add it to the .env file.")
        return False
    print("✓ OpenAI API key found!")
    return True


async def build_rag(max_transcripts=None):
    """Build RAG system with embeddings"""
    from raganything import RAGAnything, RAGAnythingConfig
    from lightrag.llm.openai import openai_complete_if_cache, openai_embed
    from lightrag.utils import EmbeddingFunc
    from qdrant_config import get_lightrag_kwargs
    import numpy as np

    # Configure RAG system
    config = RAGAnythingConfig(
        working_dir="./rag_storage",
        parser="mineru",
        enable_image_processing=False,
        enable_table_processing=False,
        enable_equation_processing=False,
    )

    # Set up LLM and embedding functions
    print("Setting up LLM and embedding functions...")

    async def llm_model_func(prompt, system_prompt=None, history_messages=[], **kwargs):
        return await openai_complete_if_cache(
            "gpt-4o-mini",
            prompt,
            system_prompt=system_prompt,
            history_messages=history_messages,
            **kwargs
        )

    async def embedding_func(texts: list[str]) -> np.ndarray:
        return await openai_embed(texts, model="text-embedding-3-small")

    # Get Qdrant configuration
    lightrag_kwargs = get_lightrag_kwargs()

    # Initialize RAG system
    print("Initializing RAG system...")
    rag = RAGAnything(
        config=config,
        llm_model_func=llm_model_func,
        embedding_func=EmbeddingFunc(
            embedding_dim=1536,
            max_token_size=8192,
            func=embedding_func
        ),
        lightrag_kwargs=lightrag_kwargs
    )

    # Get transcript files
    transcript_dir = Path("./data")
    all_files = sorted(list(transcript_dir.glob("*.txt")))

    if max_transcripts:
        all_files = all_files[:max_transcripts]

    print(f"\nFound {len(all_files)} transcript(s) to process")

    # Ensure LightRAG is initialized
    await rag._ensure_lightrag_initialized()

    # Process each transcript
    print("\nProcessing transcripts and building embeddings...")
    for i, transcript_file in enumerate(all_files, 1):
        print(f"\n[{i}/{len(all_files)}] Processing: {transcript_file.name}")

        # Read transcript content
        with open(transcript_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Insert into RAG system
        content_list = [{
            "type": "text",
            "text": content,
            "page_idx": 0
        }]

        await rag.insert_content_list(
            content_list=content_list,
            file_path=str(transcript_file),
            doc_id=f"transcript-{transcript_file.stem}"
        )
        print(f"✓ Successfully indexed!")

    print_header("RAG System Built Successfully!")

    # Test with a sample question
    print("Testing RAG system with sample question...\n")
    print("Question: What is a curiosity loop and how does it work?")
    print("-" * 70 + "\n")

    try:
        response = await rag.aquery(
            "What is a curiosity loop and how does it work?",
            mode="hybrid"
        )
        print("Answer:")
        print(response)
    except Exception as e:
        print(f"Warning: Test query failed: {e}")

    # Close RAG system
    rag.close()

    return True


async def main():
    """Main setup function"""
    parser = argparse.ArgumentParser(description="Setup RAG system with Qdrant")
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Process only first 10 transcripts (for quick testing)"
    )
    parser.add_argument(
        "--max",
        type=int,
        help="Maximum number of transcripts to process"
    )
    args = parser.parse_args()

    # Determine max transcripts
    max_transcripts = None
    if args.quick:
        max_transcripts = 10
    elif args.max:
        max_transcripts = args.max

    print_header("RAG-Anything Setup with Local Qdrant")

    # Step 1: Check if Qdrant is installed
    print_step(1, "Checking Qdrant Installation")
    if not check_qdrant_installed():
        print("Qdrant not found. Installing...")
        if not install_qdrant():
            print("\nSetup failed! Please install Qdrant manually:")
            print("  ./install_qdrant_local.sh")
            return 1
    else:
        print("✓ Qdrant is already installed!")

    # Step 2: Check API key
    print_step(2, "Checking OpenAI API Key")
    if not check_api_key():
        return 1

    # Step 3: Start Qdrant
    print_step(3, "Starting Qdrant Server")
    if is_qdrant_running():
        print("✓ Qdrant is already running!")
    else:
        if not start_qdrant():
            return 1
        if not wait_for_qdrant():
            return 1

    # Step 4: Build RAG with embeddings
    print_step(4, "Building RAG System and Creating Embeddings")

    mode_text = "all transcripts"
    if max_transcripts:
        mode_text = f"first {max_transcripts} transcripts"
    print(f"Processing {mode_text}...\n")

    try:
        success = await build_rag(max_transcripts=max_transcripts)
        if not success:
            return 1
    except Exception as e:
        print(f"\nERROR: Failed to build RAG system: {e}")
        import traceback
        traceback.print_exc()
        return 1

    # Final summary
    print_header("Setup Complete!")
    print("Your RAG system is ready to use!\n")
    print("Next steps:")
    print("  1. Query the system:")
    print('     python query_rag.py "Your question here"')
    print("     python query_rag.py --interactive\n")
    print("  2. Query with sources:")
    print('     python query_with_sources.py "Your question"\n')
    print("  3. Check Qdrant status:")
    print("     ./status_qdrant.sh")
    print("     curl http://localhost:6333/health\n")
    print("  4. View dashboard:")
    print("     http://localhost:6333/dashboard\n")

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
