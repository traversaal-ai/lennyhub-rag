"""
Worker script for RAG queries - runs in a separate process to avoid event loop conflicts.
Called by streamlit_app.py via subprocess.
"""

import sys
import os
import json
import asyncio

# Ensure environment variables are set
os.environ.setdefault("QDRANT_URL", "http://localhost:6333")
os.environ.setdefault("QDRANT_COLLECTION_NAME", "lennyhub")

from dotenv import load_dotenv
load_dotenv()


async def run_query(question: str, mode: str = "hybrid") -> dict:
    """Run a RAG query and return the result"""
    try:
        from raganything import RAGAnything, RAGAnythingConfig
        from lightrag.llm.openai import openai_complete_if_cache, openai_embed
        from lightrag.utils import EmbeddingFunc
        from qdrant_config import get_lightrag_kwargs
        import numpy as np

        config = RAGAnythingConfig(
            working_dir="./rag_storage",
            parser="mineru",
            enable_image_processing=False,
            enable_table_processing=False,
            enable_equation_processing=False,
        )

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

        lightrag_kwargs = get_lightrag_kwargs(verbose=False)

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

        # Initialize and query
        await rag._ensure_lightrag_initialized()
        response = await rag.aquery(question, mode=mode)
        
        # Cleanup
        try:
            await rag.finalize_storages()
        except:
            pass
        try:
            rag.close()
        except:
            pass

        return {"success": True, "response": response, "error": None}

    except Exception as e:
        return {"success": False, "response": None, "error": str(e)}


def main():
    """Main entry point - reads question from command line args"""
    if len(sys.argv) < 2:
        print(json.dumps({"success": False, "response": None, "error": "No question provided"}))
        sys.exit(1)
    
    question = sys.argv[1]
    mode = sys.argv[2] if len(sys.argv) > 2 else "hybrid"
    
    # Run the query
    result = asyncio.run(run_query(question, mode))
    
    # Output as JSON
    print(json.dumps(result))


if __name__ == "__main__":
    main()
