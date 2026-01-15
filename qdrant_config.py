"""
Qdrant Configuration Module for LennyHub RAG

This module provides centralized configuration for Qdrant vector database.
It handles environment variable loading, connection testing, and fallback
to NanoVectorDB if Qdrant is unavailable.

Usage:
    from qdrant_config import get_lightrag_kwargs

    lightrag_kwargs = get_lightrag_kwargs()
    rag = RAGAnything(
        config=config,
        llm_model_func=llm_model_func,
        embedding_func=embedding_func,
        lightrag_kwargs=lightrag_kwargs
    )
"""

import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def test_qdrant_connection(url: str) -> bool:
    """
    Test if Qdrant server is accessible.

    Args:
        url: Qdrant server URL (e.g., http://localhost:6333)

    Returns:
        True if connection successful, False otherwise
    """
    try:
        from qdrant_client import QdrantClient

        client = QdrantClient(url=url, timeout=5)
        # Try to get collections (will fail if server not accessible)
        client.get_collections()
        return True
    except Exception as e:
        print(f"Warning: Cannot connect to Qdrant at {url}: {e}")
        return False


def get_lightrag_kwargs(
    use_qdrant: Optional[bool] = None,
    qdrant_url: Optional[str] = None,
    collection_name: Optional[str] = None,
    verbose: bool = True
) -> Dict[str, Any]:
    """
    Get LightRAG configuration kwargs for vector database.

    Args:
        use_qdrant: Override USE_QDRANT env var (True/False/None for auto)
        qdrant_url: Override QDRANT_URL env var
        collection_name: Override QDRANT_COLLECTION_NAME env var
        verbose: Print configuration info

    Returns:
        Dictionary with lightrag_kwargs for RAGAnything initialization
        Returns empty dict if Qdrant disabled or unavailable (uses NanoVectorDB)
    """
    # Get configuration from environment or parameters
    if use_qdrant is None:
        use_qdrant_str = os.getenv("USE_QDRANT", "true").lower()
        use_qdrant = use_qdrant_str in ["true", "1", "yes"]

    if not use_qdrant:
        if verbose:
            print("✓ Using NanoVectorDB (default JSON storage)")
        return {}

    # Get Qdrant settings
    url = qdrant_url or os.getenv("QDRANT_URL", "http://localhost:6333")
    collection = collection_name or os.getenv("QDRANT_COLLECTION_NAME", "lennyhub")

    # Test connection
    if not test_qdrant_connection(url):
        print(f"\n⚠️  Qdrant not accessible at {url}")
        print("   Falling back to NanoVectorDB (default JSON storage)")
        print("   To use Qdrant, ensure it's running:")
        print("   - Run: ./start_qdrant.sh")
        print("   - Or install first: ./install_qdrant_local.sh")
        print("   - Or set USE_QDRANT=false in .env to disable this warning\n")
        return {}

    # Qdrant is available - use it
    if verbose:
        print(f"✓ Using Qdrant vector database")
        print(f"  URL: {url}")
        print(f"  Collection: {collection}")

    lightrag_kwargs = {
        "vector_storage": "QdrantVectorDBStorage",
        "vector_db_storage_cls_kwargs": {
            "url": url,
            "collection_name": collection
        }
    }

    return lightrag_kwargs


def get_qdrant_client(
    qdrant_url: Optional[str] = None
) -> Optional[Any]:
    """
    Get a Qdrant client instance for direct access.

    Args:
        qdrant_url: Override QDRANT_URL env var

    Returns:
        QdrantClient instance or None if unavailable
    """
    try:
        from qdrant_client import QdrantClient

        url = qdrant_url or os.getenv("QDRANT_URL", "http://localhost:6333")

        if not test_qdrant_connection(url):
            return None

        return QdrantClient(url=url)
    except ImportError:
        print("Error: qdrant-client not installed. Run: pip install qdrant-client")
        return None
    except Exception as e:
        print(f"Error creating Qdrant client: {e}")
        return None


if __name__ == "__main__":
    """Test configuration when run directly"""
    print("=" * 70)
    print("Qdrant Configuration Test")
    print("=" * 70)

    # Test environment variables
    print("\nEnvironment Variables:")
    print(f"  USE_QDRANT: {os.getenv('USE_QDRANT', 'not set (defaults to true)')}")
    print(f"  QDRANT_URL: {os.getenv('QDRANT_URL', 'not set (defaults to http://localhost:6333)')}")
    print(f"  QDRANT_COLLECTION_NAME: {os.getenv('QDRANT_COLLECTION_NAME', 'not set (defaults to lennyhub)')}")

    # Test configuration
    print("\nTesting configuration...")
    lightrag_kwargs = get_lightrag_kwargs(verbose=True)

    if lightrag_kwargs:
        print("\n✓ Qdrant configuration ready:")
        print(f"  {lightrag_kwargs}")
    else:
        print("\n✓ Using NanoVectorDB (default)")

    # Test client
    print("\nTesting Qdrant client...")
    client = get_qdrant_client()
    if client:
        try:
            collections = client.get_collections()
            print(f"✓ Connected! Found {len(collections.collections)} collection(s)")
            if collections.collections:
                for col in collections.collections:
                    print(f"  - {col.name}")
        except Exception as e:
            print(f"✗ Error: {e}")
    else:
        print("✗ Could not create client")

    print("\n" + "=" * 70)
