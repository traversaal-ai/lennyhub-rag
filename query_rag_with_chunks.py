"""
Query the Transcript RAG system and show the specific chunks used

This script shows:
1. The retrieved chunks that were used to generate the answer
2. The source file for each chunk
3. The final generated answer

Usage:
    export OPENAI_API_KEY='your-api-key'
    python query_rag_with_chunks.py "Your question here"

    # Interactive mode
    python query_rag_with_chunks.py --interactive
"""

import os
import asyncio
import numpy as np
from pathlib import Path
from raganything import RAGAnything, RAGAnythingConfig
from lightrag.llm.openai import openai_complete_if_cache, openai_embed
from lightrag.utils import EmbeddingFunc
from lightrag import QueryParam
from qdrant_config import get_lightrag_kwargs


async def query_with_chunks(question: str, mode: str = "hybrid", show_chunks: bool = True):
    """Query the RAG system and show chunks used"""

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

    print(f"\nQuestion: {question}")
    print(f"Mode: {mode}")
    print("=" * 80)

    # Step 1: Get the retrieved context (chunks) without generating answer
    if show_chunks:
        print("\n📚 RETRIEVED CHUNKS (Used to generate the answer):")
        print("=" * 80)

        try:
            # Query with only_need_context=True to get chunks without answer
            query_param = QueryParam(mode=mode, only_need_context=True)
            context = await rag.lightrag.aquery(question, param=query_param)

            if context:
                # Parse and display chunks
                # LightRAG returns context with separators like "--New Chunk--"
                chunks = context.split("-----")

                print(f"\nFound {len(chunks)} relevant chunks:\n")

                for i, chunk in enumerate(chunks, 1):
                    chunk = chunk.strip()
                    if chunk and len(chunk) > 10:  # Filter out empty/tiny chunks
                        print(f"\n{'─' * 80}")
                        print(f"CHUNK {i}:")
                        print(f"{'─' * 80}")

                        # Try to extract source info if available
                        lines = chunk.split('\n')

                        # Display chunk content
                        # Truncate very long chunks for readability
                        if len(chunk) > 500:
                            print(chunk[:500] + "...")
                            print(f"\n[Truncated - full chunk is {len(chunk)} characters]")
                        else:
                            print(chunk)

                print(f"\n{'=' * 80}")
            else:
                print("No context retrieved.")

        except Exception as e:
            print(f"Error retrieving chunks: {e}")
            print("Falling back to standard query...")

    # Step 2: Generate the final answer
    print("\n\n💡 GENERATED ANSWER:")
    print("=" * 80)

    response = await rag.aquery(question, mode=mode)
    print(f"\n{response}\n")

    print("=" * 80)

    rag.close()


async def interactive_mode():
    """Interactive mode for querying with chunk visibility"""

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

    print("\n" + "=" * 80)
    print("Transcript RAG System - Interactive Mode (WITH CHUNKS)")
    print("=" * 80)
    print("\nThis mode shows the actual chunks used to generate each answer.")
    print("\nCommands:")
    print("  - Type your question to get an answer with sources")
    print("  - Type 'no-chunks' to hide chunk details")
    print("  - Type 'show-chunks' to show chunk details")
    print("  - Type 'quit' or 'exit' to stop\n")

    show_chunks = True

    while True:
        question = input("\nYour question: ").strip()

        if question.lower() in ["quit", "exit", "q"]:
            print("\nGoodbye!")
            break

        if question.lower() == "no-chunks":
            show_chunks = False
            print("✓ Chunk display disabled")
            continue

        if question.lower() == "show-chunks":
            show_chunks = True
            print("✓ Chunk display enabled")
            continue

        if not question:
            continue

        print("=" * 80)

        try:
            # Get chunks if enabled
            if show_chunks:
                print("\n📚 RETRIEVED CHUNKS:")
                print("=" * 80)

                query_param = QueryParam(mode="hybrid", only_need_context=True)
                context = await rag.lightrag.aquery(question, param=query_param)

                if context:
                    chunks = context.split("-----")
                    print(f"\nFound {len(chunks)} relevant chunks:\n")

                    for i, chunk in enumerate(chunks, 1):
                        chunk = chunk.strip()
                        if chunk and len(chunk) > 10:
                            print(f"\n{'─' * 80}")
                            print(f"CHUNK {i}:")
                            print(f"{'─' * 80}")

                            # Truncate for readability
                            if len(chunk) > 400:
                                print(chunk[:400] + "...")
                                print(f"[Truncated - full chunk is {len(chunk)} chars]")
                            else:
                                print(chunk)

            # Generate answer
            print("\n\n💡 GENERATED ANSWER:")
            print("=" * 80)
            response = await rag.aquery(question, mode="hybrid")
            print(f"\n{response}\n")

        except Exception as e:
            print(f"\nError: {e}\n")

    rag.close()


async def main():
    """Main function"""

    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == "--interactive" or sys.argv[1] == "-i":
            await interactive_mode()
            return

        # Query from command line
        question = " ".join(sys.argv[1:])
        await query_with_chunks(question)
        return

    # Default: show example
    print("\n" + "=" * 80)
    print("Example Query with Chunks")
    print("=" * 80)

    example_question = "What is a curiosity loop and how does it work?"
    await query_with_chunks(example_question)

    print("\n" + "=" * 80)
    print("Usage:")
    print("  python query_rag_with_chunks.py 'your question here'")
    print("  python query_rag_with_chunks.py --interactive")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
