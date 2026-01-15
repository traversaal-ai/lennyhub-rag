"""
Query RAG with detailed source attribution - shows chunks AND their source documents

This script provides maximum transparency by showing:
1. The specific chunks retrieved from the vector database
2. The source document/transcript for each chunk
3. The final generated answer

Usage:
    export OPENAI_API_KEY='your-api-key'
    python query_with_sources.py "Your question here"
"""

import os
import asyncio
import json
import numpy as np
from pathlib import Path
from raganything import RAGAnything, RAGAnythingConfig
from lightrag.llm.openai import openai_complete_if_cache, openai_embed
from lightrag.utils import EmbeddingFunc
from lightrag import QueryParam
from qdrant_config import get_lightrag_kwargs


def load_chunk_metadata(working_dir="./rag_storage"):
    """Load chunk metadata to map chunks to source documents"""
    metadata = {}

    # Load text chunks with metadata
    chunks_file = Path(working_dir) / "kv_store_text_chunks.json"
    if chunks_file.exists():
        with open(chunks_file, 'r') as f:
            chunks_data = json.load(f)
            metadata['chunks'] = chunks_data

    # Load document status to get file paths
    doc_status_file = Path(working_dir) / "kv_store_doc_status.json"
    if doc_status_file.exists():
        with open(doc_status_file, 'r') as f:
            doc_status = json.load(f)
            metadata['doc_status'] = doc_status

    # Load full docs
    full_docs_file = Path(working_dir) / "kv_store_full_docs.json"
    if full_docs_file.exists():
        with open(full_docs_file, 'r') as f:
            full_docs = json.load(f)
            metadata['full_docs'] = full_docs

    return metadata


def extract_chunk_sources(context: str, metadata: dict):
    """Extract chunk information and map to source documents"""
    chunks_info = []

    # Parse context - LightRAG formats it with separators
    sections = context.split("-----")

    for section in sections:
        section = section.strip()
        if not section or len(section) < 20:
            continue

        chunk_info = {
            'content': section,
            'source': 'Unknown',
            'chunk_id': None
        }

        # Try to find matching chunk in metadata
        if 'chunks' in metadata:
            for chunk_id, chunk_data in metadata['chunks'].items():
                if isinstance(chunk_data, dict) and 'content' in chunk_data:
                    chunk_content = chunk_data['content']
                    # Check if this context section matches a chunk
                    if chunk_content in section or section in chunk_content:
                        chunk_info['chunk_id'] = chunk_id

                        # Find source document
                        if 'full_docs' in metadata:
                            for doc_id, doc_data in metadata['full_docs'].items():
                                if isinstance(doc_data, dict):
                                    if 'chunks' in doc_data and chunk_id in doc_data['chunks']:
                                        chunk_info['source'] = doc_data.get('file_name', doc_id)
                                        break

                        # Also check doc_status for file_path
                        if chunk_info['source'] == 'Unknown' and 'doc_status' in metadata:
                            for doc_id, doc_data in metadata['doc_status'].items():
                                if isinstance(doc_data, dict) and 'chunks_list' in doc_data:
                                    if chunk_id in doc_data['chunks_list']:
                                        file_path = doc_data.get('file_path', '')
                                        chunk_info['source'] = Path(file_path).stem if file_path else doc_id
                                        break
                        break

        chunks_info.append(chunk_info)

    return chunks_info


async def query_with_detailed_sources(question: str, mode: str = "hybrid"):
    """Query RAG and show detailed source attribution"""

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

    # Load chunk metadata
    print("Loading chunk metadata...")
    metadata = load_chunk_metadata()

    print("\n" + "=" * 100)
    print(f"QUESTION: {question}")
    print("=" * 100)

    # Step 1: Retrieve context chunks
    print("\n📚 RETRIEVED SOURCES:")
    print("=" * 100)

    try:
        # Get context without generating answer
        query_param = QueryParam(mode=mode, only_need_context=True)
        context = await rag.lightrag.aquery(question, param=query_param)

        if context:
            # Extract and show chunks with sources
            chunks_info = extract_chunk_sources(context, metadata)

            # Group by source document
            sources_map = {}
            for chunk in chunks_info:
                source = chunk['source']
                if source not in sources_map:
                    sources_map[source] = []
                sources_map[source].append(chunk)

            print(f"\nRetrieved from {len(sources_map)} source document(s):\n")

            for source, chunks in sources_map.items():
                print(f"\n{'═' * 100}")
                print(f"📄 SOURCE: {source}")
                print(f"   Chunks used: {len(chunks)}")
                print(f"{'═' * 100}")

                for i, chunk in enumerate(chunks, 1):
                    print(f"\n┌─ Chunk {i} " + "─" * 87)
                    if chunk['chunk_id']:
                        print(f"│ Chunk ID: {chunk['chunk_id']}")

                    # Show content (truncated if too long)
                    content = chunk['content']
                    if len(content) > 600:
                        print(f"│\n│ {content[:600]}...")
                        print(f"│\n│ [Truncated - Full chunk is {len(content)} characters]")
                    else:
                        print(f"│\n│ {content}")

                    print(f"└─" + "─" * 98)

        else:
            print("No context retrieved.")

    except Exception as e:
        print(f"Error retrieving sources: {e}")
        import traceback
        traceback.print_exc()

    # Step 2: Generate answer
    print("\n\n💡 GENERATED ANSWER:")
    print("=" * 100)

    try:
        response = await rag.aquery(question, mode=mode)
        print(f"\n{response}\n")
    except Exception as e:
        print(f"Error generating answer: {e}")

    print("=" * 100)

    # Summary
    if context:
        print(f"\n✓ Answer generated using {len(chunks_info)} chunk(s) from {len(sources_map)} source(s)")

    rag.close()


async def main():
    """Main function"""

    import sys

    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
        await query_with_detailed_sources(question)
        return

    # Default example
    print("\n" + "=" * 100)
    print("Example Query with Detailed Source Attribution")
    print("=" * 100)

    example_question = "What is a curiosity loop?"
    await query_with_detailed_sources(example_question)

    print("\n" + "=" * 100)
    print("Usage: python query_with_sources.py 'your question here'")
    print("=" * 100)


if __name__ == "__main__":
    asyncio.run(main())
