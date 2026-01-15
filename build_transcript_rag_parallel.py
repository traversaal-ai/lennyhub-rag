"""
Build RAG system from podcast transcripts using RAG-Anything (PARALLEL VERSION)

This version processes transcripts in parallel for much faster ingestion.

Requirements:
- OPENAI_API_KEY environment variable must be set
- Or you can modify this script to use a different LLM provider

Usage:
    export OPENAI_API_KEY="your-api-key"
    python build_transcript_rag_parallel.py
"""

import os
import asyncio
import json
from pathlib import Path
from dotenv import load_dotenv
from raganything import RAGAnything, RAGAnythingConfig
from lightrag.llm.openai import openai_complete_if_cache, openai_embed
from lightrag.utils import EmbeddingFunc
from qdrant_config import get_lightrag_kwargs
import numpy as np
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Configuration
MAX_TRANSCRIPTS = 23  # Process up to 23 transcripts to reach 150 total
CONCURRENT_LIMIT = 5   # Process 5 transcripts at a time (adjust based on rate limits)

# Shared counters for progress tracking
processed_count = 0
total_to_process = 0
lock = asyncio.Lock()


def get_already_processed_docs():
    """Get list of already processed document IDs"""
    doc_status_file = Path("./rag_storage/kv_store_doc_status.json")
    if doc_status_file.exists():
        try:
            with open(doc_status_file, 'r') as f:
                doc_status = json.load(f)
                return set(doc_status.keys())
        except Exception as e:
            print(f"Warning: Could not read doc_status file: {e}")
    return set()


async def process_single_transcript(rag, transcript_file, semaphore):
    """Process a single transcript with semaphore control"""
    global processed_count

    async with semaphore:  # Limit concurrent processing
        doc_id = f"transcript-{transcript_file.stem}"

        try:
            # Read transcript content
            with open(transcript_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Insert into RAG system
            content_list = [
                {
                    "type": "text",
                    "text": content,
                    "page_idx": 0
                }
            ]

            await rag.insert_content_list(
                content_list=content_list,
                file_path=str(transcript_file),
                doc_id=doc_id
            )

            # Update progress counter
            async with lock:
                processed_count += 1
                current = processed_count

            print(f"[{current}/{total_to_process}] ✓ {transcript_file.name}")
            return True, transcript_file.name

        except Exception as e:
            print(f"[ERROR] ✗ {transcript_file.name}: {str(e)}")
            return False, transcript_file.name


async def main():
    global total_to_process, processed_count

    start_time = datetime.now()

    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY environment variable not set!")
        print("\nPlease set your OpenAI API key:")
        print("  export OPENAI_API_KEY='your-api-key-here'")
        print("\nOr modify this script to use a different LLM provider.")
        return

    print("="*70)
    print("PARALLEL TRANSCRIPT INGESTION")
    print("="*70)
    print(f"Max transcripts: {MAX_TRANSCRIPTS}")
    print(f"Concurrent limit: {CONCURRENT_LIMIT}")
    print()

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

    async def llm_model_func(
        prompt, system_prompt=None, history_messages=[], **kwargs
    ) -> str:
        return await openai_complete_if_cache(
            "gpt-4o-mini",
            prompt,
            system_prompt=system_prompt,
            history_messages=history_messages,
            **kwargs
        )

    async def embedding_func(texts: list[str]) -> np.ndarray:
        return await openai_embed(
            texts,
            model="text-embedding-3-small"
        )

    # Get Qdrant configuration
    lightrag_kwargs = get_lightrag_kwargs()

    # Initialize RAG system with LLM functions
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

    # Ensure LightRAG is initialized
    await rag._ensure_lightrag_initialized()

    # Get all transcript files
    transcript_dir = Path("./data")
    all_transcript_files = sorted(list(transcript_dir.glob("*.txt")))

    print(f"\nFound {len(all_transcript_files)} transcript files in data/")

    # Get already processed documents
    already_processed = get_already_processed_docs()
    print(f"Already processed: {len(already_processed)} documents")

    # Filter out already processed transcripts
    transcript_files = []
    for file in all_transcript_files:
        doc_id = f"transcript-{file.stem}"
        if doc_id not in already_processed:
            transcript_files.append(file)

    # Limit to MAX_TRANSCRIPTS
    if len(transcript_files) > MAX_TRANSCRIPTS:
        print(f"\nLimiting to first {MAX_TRANSCRIPTS} unprocessed transcripts")
        transcript_files = transcript_files[:MAX_TRANSCRIPTS]

    total_to_process = len(transcript_files)

    if total_to_process == 0:
        print("\n✓ All transcripts already processed!")
        print(f"Total documents in system: {len(already_processed)}")
        rag.close()
        return

    print(f"\nWill process: {total_to_process} new transcripts")
    print(f"Processing {CONCURRENT_LIMIT} transcripts at a time...")
    print("\nStarting parallel processing...")
    print("="*70)

    # Create semaphore for concurrency control
    semaphore = asyncio.Semaphore(CONCURRENT_LIMIT)

    # Process all transcripts in parallel (with semaphore limiting concurrency)
    tasks = [
        process_single_transcript(rag, transcript_file, semaphore)
        for transcript_file in transcript_files
    ]

    # Wait for all tasks to complete
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Calculate statistics
    successful = sum(1 for r in results if isinstance(r, tuple) and r[0])
    failed = total_to_process - successful

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    print("\n" + "="*70)
    print("INGESTION COMPLETE")
    print("="*70)
    print(f"Successfully processed: {successful}/{total_to_process}")
    print(f"Failed: {failed}")
    print(f"Total time: {duration:.1f} seconds ({duration/60:.1f} minutes)")
    print(f"Average: {duration/total_to_process:.1f} seconds per transcript")
    print(f"Total documents in system: {len(already_processed) + successful}")
    print("="*70)

    # Close RAG system
    rag.close()

    print("\n✓ RAG system ready for queries!")
    print("\nTest the system with:")
    print("  python query_rag.py --interactive")


if __name__ == "__main__":
    asyncio.run(main())
