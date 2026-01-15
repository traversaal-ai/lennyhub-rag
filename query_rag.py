"""
Simple script to query the Transcript RAG system

Usage:
    export OPENAI_API_KEY='your-api-key'
    python query_rag.py
"""

import os
import asyncio
import numpy as np
from pathlib import Path
from raganything import RAGAnything, RAGAnythingConfig
from lightrag.llm.openai import openai_complete_if_cache, openai_embed
from lightrag.utils import EmbeddingFunc
from qdrant_config import get_lightrag_kwargs


async def query_rag(question: str, mode: str = "hybrid"):
    """Query the RAG system with a question"""

    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY environment variable not set!")
        print("\nPlease set your OpenAI API key:")
        print("  export OPENAI_API_KEY='your-api-key-here'")
        return

    # Configure RAG
    config = RAGAnythingConfig(working_dir="./rag_storage")

    # Set up LLM functions
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

    # Initialize RAG
    print("Initializing RAG system...")
    rag = RAGAnything(
        config=config,
        llm_model_func=llm_model_func,
        embedding_func=EmbeddingFunc(
            embedding_dim=1536, max_token_size=8192, func=embedding_func
        ),
        lightrag_kwargs=lightrag_kwargs
    )

    # Ensure LightRAG is initialized
    await rag._ensure_lightrag_initialized()

    # Query the RAG
    print(f"\nQuestion: {question}")
    print(f"Mode: {mode}")
    print("-" * 60)

    response = await rag.aquery(question, mode=mode)

    print(f"\nAnswer:\n{response}\n")

    rag.close()


async def interactive_mode():
    """Interactive mode for querying the RAG"""

    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY environment variable not set!")
        print("\nPlease set your OpenAI API key:")
        print("  export OPENAI_API_KEY='your-api-key-here'")
        return

    # Configure RAG
    config = RAGAnythingConfig(working_dir="./rag_storage")

    # Set up LLM functions
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

    # Initialize RAG
    print("Initializing RAG system...")
    rag = RAGAnything(
        config=config,
        llm_model_func=llm_model_func,
        embedding_func=EmbeddingFunc(
            embedding_dim=1536, max_token_size=8192, func=embedding_func
        ),
        lightrag_kwargs=lightrag_kwargs
    )

    # Ensure LightRAG is initialized
    await rag._ensure_lightrag_initialized()

    print("\n" + "=" * 60)
    print("Transcript RAG System - Interactive Mode")
    print("=" * 60)
    print("\nAsk questions about the podcast transcripts!")
    print("Type 'quit' or 'exit' to stop\n")

    while True:
        question = input("\nYour question: ").strip()

        if question.lower() in ["quit", "exit", "q"]:
            print("\nGoodbye!")
            break

        if not question:
            continue

        print("-" * 60)
        try:
            response = await rag.aquery(question, mode="hybrid")
            print(f"\nAnswer:\n{response}\n")
        except Exception as e:
            print(f"\nError: {e}\n")

    rag.close()


async def main():
    """Main function with example queries"""

    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == "--interactive" or sys.argv[1] == "-i":
            await interactive_mode()
            return

        # Query from command line
        question = " ".join(sys.argv[1:])
        await query_rag(question)
        return

    # Default: run example queries
    example_questions = [
        "What is a curiosity loop and how does it work?",
        "What are the four components of the growth competency model?",
        "What advice does Ada give about career decisions?",
    ]

    print("\n" + "=" * 60)
    print("Running Example Queries")
    print("=" * 60)

    for i, question in enumerate(example_questions, 1):
        print(f"\n\n{'='*60}")
        print(f"Example {i}:")
        print("=" * 60)
        await query_rag(question)

    print("\n" + "=" * 60)
    print("For interactive mode, run: python query_rag.py --interactive")
    print("For custom query, run: python query_rag.py 'your question here'")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
