"""
Streamlit App for LennyHub RAG System

Visual interface for querying and exploring the RAG system with Qdrant.

Usage:
    streamlit run streamlit_app.py
"""

import streamlit as st
import asyncio
import os
import sys
import platform
import subprocess
import shutil
import time
from pathlib import Path
from dotenv import load_dotenv
import requests
from datetime import datetime
import json

# Load environment variables
load_dotenv()

# Ensure Qdrant environment variables are set (required by LightRAG)
if not os.getenv("QDRANT_URL"):
    os.environ["QDRANT_URL"] = "http://localhost:6333"
if not os.getenv("QDRANT_COLLECTION_NAME"):
    os.environ["QDRANT_COLLECTION_NAME"] = "lennyhub"

# Page config
st.set_page_config(
    page_title="LennyHub RAG Explorer",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .status-box {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .status-success {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .status-error {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
    }
    .query-result {
        # background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-top: 1rem;
        border-left: 4px solid #007bff;
    }
    .metric-card {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)


def find_qdrant_binary():
    """Find Qdrant binary path"""
    system = platform.system()
    
    if system == "Windows":
        # Windows paths
        possible_paths = [
            os.path.expanduser("~/.qdrant/qdrant.exe"),
            os.path.expanduser("~/.qdrant/qdrant"),
            os.path.join(os.getenv("LOCALAPPDATA", ""), "qdrant", "qdrant.exe"),
        ]
        
        # Check direct paths first
        for path in possible_paths:
            if os.path.isfile(path):
                return path
        
        # Check PATH using shutil.which (more reliable)
        for cmd in ["qdrant.exe", "qdrant"]:
            found = shutil.which(cmd)
            if found and os.path.isfile(found):
                return found
    else:
        # Unix-like paths
        possible_paths = [
            os.path.expanduser("~/.qdrant/qdrant"),
            "/usr/local/bin/qdrant",
            "/usr/bin/qdrant",
        ]
        
        # Check direct paths first
        for path in possible_paths:
            if os.path.isfile(path) and os.access(path, os.X_OK):
                return path
        
        # Check PATH using shutil.which
        found = shutil.which("qdrant")
        if found and os.path.isfile(found):
            return found
    
    return None


def start_qdrant():
    """Start Qdrant server if not already running"""
    # First check if already running
    try:
        response = requests.get("http://localhost:6333/health", timeout=2)
        if response.status_code == 200:
            return True, "Already running"
    except:
        pass
    
    # Find Qdrant binary
    qdrant_bin = find_qdrant_binary()
    if not qdrant_bin:
        return False, "Qdrant binary not found. Please install Qdrant first."
    
    # Check if config file exists
    config_path = Path("./qdrant_config.yaml")
    if not config_path.exists():
        return False, "qdrant_config.yaml not found"
    
    # Start Qdrant
    try:
        system = platform.system()
        storage_dir = Path("./qdrant_storage")
        storage_dir.mkdir(exist_ok=True)
        
        if system == "Windows":
            # Windows: start in background
            # Use CREATE_NO_WINDOW to hide console window
            try:
                process = subprocess.Popen(
                    [qdrant_bin, "--config-path", str(config_path.absolute())],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    creationflags=subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS,
                    cwd=os.getcwd()
                )
            except AttributeError:
                # CREATE_NO_WINDOW not available (Python < 3.7)
                process = subprocess.Popen(
                    [qdrant_bin, "--config-path", str(config_path.absolute())],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    creationflags=subprocess.DETACHED_PROCESS,
                    cwd=os.getcwd()
                )
        else:
            # Unix-like: use nohup equivalent
            process = subprocess.Popen(
                [qdrant_bin, "--config-path", str(config_path.absolute())],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True,
                cwd=os.getcwd()
            )
        
        # Wait a bit for startup
        time.sleep(3)
        
        # Check if process is still running
        if process.poll() is not None:
            # Process exited
            stderr = process.stderr.read().decode() if process.stderr else "Unknown error"
            return False, f"Qdrant process exited: {stderr}"
        
        # Check if Qdrant is responding
        max_retries = 10
        for i in range(max_retries):
            try:
                response = requests.get("http://localhost:6333/health", timeout=2)
                if response.status_code == 200:
                    return True, "Started successfully"
            except:
                time.sleep(1)
        
        return False, "Qdrant started but not responding"
        
    except Exception as e:
        return False, f"Failed to start Qdrant: {str(e)}"


@st.cache_resource
def check_qdrant_status():
    """Check if Qdrant is running and get collections info"""
    try:
        response = requests.get("http://localhost:6333/", timeout=2)
        if response.status_code == 200:
            version_info = response.json()

            # Get collections
            collections_response = requests.get("http://localhost:6333/collections", timeout=2)
            collections = collections_response.json().get("result", {}).get("collections", [])

            return {
                "status": "running",
                "version": version_info.get("version", "unknown"),
                "collections": collections
            }
    except:
        pass

    return {
        "status": "stopped",
        "version": None,
        "collections": []
    }


def create_rag_instance():
    """Create a fresh RAG instance (not cached to avoid event loop issues)"""
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

    return rag


def initialize_rag():
    """Initialize RAG system with fresh instance to avoid event loop conflicts"""
    try:
        rag = create_rag_instance()
        return rag, None
    except Exception as e:
        return None, str(e)


def get_transcript_stats():
    """Get statistics about transcripts"""
    data_dir = Path("./data")
    transcripts = list(data_dir.glob("*.txt"))

    stats = {
        "total_transcripts": len(transcripts),
        "total_size": sum(f.stat().st_size for f in transcripts),
        "transcripts": [f.stem for f in sorted(transcripts)]
    }

    return stats


def query_rag_sync(question, mode="hybrid"):
    """Query the RAG system via subprocess for complete isolation"""
    import subprocess
    import json
    
    try:
        # Get the Python executable from the virtual environment
        python_exe = sys.executable
        
        # Run query_worker.py in a separate process
        result = subprocess.run(
            [python_exe, "query_worker.py", question, mode],
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
            cwd=os.getcwd()
        )
        
        if result.returncode != 0:
            # Check stderr for errors
            error_msg = result.stderr.strip() if result.stderr else "Unknown error"
            return None, f"Worker process failed: {error_msg}"
        
        # Parse JSON output
        output = result.stdout.strip()
        if not output:
            return None, "No output from worker process"
        
        # Find the JSON in the output (skip any log lines)
        json_line = None
        for line in output.split('\n'):
            line = line.strip()
            if line.startswith('{') and line.endswith('}'):
                json_line = line
        
        if not json_line:
            # Try parsing the whole output
            json_line = output.split('\n')[-1]
        
        data = json.loads(json_line)
        
        if data.get("success"):
            return data.get("response"), None
        else:
            return None, data.get("error", "Unknown error")
            
    except subprocess.TimeoutExpired:
        return None, "Query timed out after 5 minutes"
    except json.JSONDecodeError as e:
        return None, f"Failed to parse worker response: {e}"
    except Exception as e:
        return None, f"Query failed: {str(e)}"


def main():
    # Header
    st.markdown('<div class="main-header">🎙️ LennyHub RAG Explorer</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Query and explore podcast transcripts with AI-powered search</div>', unsafe_allow_html=True)

    # Check and start Qdrant if needed (only once per session)
    if "qdrant_started" not in st.session_state:
        qdrant_status = check_qdrant_status()
        if qdrant_status["status"] != "running":
            with st.spinner("Starting Qdrant..."):
                success, message = start_qdrant()
                if success:
                    st.session_state.qdrant_started = True
                    # Clear cache to refresh status
                    check_qdrant_status.clear()
                    st.rerun()
                else:
                    st.session_state.qdrant_started = False
                    st.session_state.qdrant_error = message
        else:
            st.session_state.qdrant_started = True

    # Sidebar
    with st.sidebar:
        st.header("⚙️ System Status")

        # Check Qdrant status
        qdrant_status = check_qdrant_status()

        if qdrant_status["status"] == "running":
            st.markdown(f"""
            <div class="status-box status-success">
                ✓ Qdrant: Running<br>
                Version: {qdrant_status["version"]}<br>
                Collections: {len(qdrant_status["collections"])}
            </div>
            """, unsafe_allow_html=True)

            # Show collections
            if qdrant_status["collections"]:
                st.subheader("📊 Collections")
                for col in qdrant_status["collections"]:
                    st.text(f"• {col['name']}")
        else:
            # Show error if startup failed
            error_msg = ""
            if hasattr(st.session_state, 'qdrant_error'):
                error_msg = f"<br>Error: {st.session_state.qdrant_error}"
                st.markdown(f"""
                <div class="status-box status-error">
                    ✗ Qdrant: Not Running{error_msg}<br>
                    Please ensure Qdrant is installed and qdrant_config.yaml exists.
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="status-box status-error">
                    ✗ Qdrant: Not Running{error_msg}<br>
                    Starting automatically...
                </div>
                """, unsafe_allow_html=True)

        # API Key status
        st.markdown("---")
        if os.getenv("OPENAI_API_KEY"):
            st.success("✓ OpenAI API Key: Configured")
        else:
            st.error("✗ OpenAI API Key: Missing")

        # Transcript stats
        st.markdown("---")
        st.subheader("📚 Data Statistics")
        stats = get_transcript_stats()

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Transcripts", stats["total_transcripts"])
        with col2:
            st.metric("Total Size", f"{stats['total_size'] / 1024 / 1024:.1f} MB")

        # Links
        st.markdown("---")
        st.subheader("🔗 Quick Links")
        st.markdown("[Qdrant Dashboard](http://localhost:6333/dashboard)")
        st.markdown("[GitHub](https://github.com)")

        # Query mode selector
        st.markdown("---")
        st.subheader("🔍 Query Settings")
        query_mode = st.selectbox(
            "Search Mode",
            ["hybrid", "local", "global", "naive"],
            help="Hybrid: Best overall results | Local: Entity-focused | Global: Relationship-focused | Naive: Vector search only"
        )

    # Main content area
    tab1, tab2, tab3 = st.tabs(["🔍 Query", "📊 Statistics", "📖 Transcripts"])

    # Tab 1: Query Interface
    with tab1:
        st.header("Ask a Question")

        # Sample questions
        with st.expander("💡 Sample Questions"):
            sample_questions = [
                "What is a curiosity loop and how does it work?",
                "What are Ada's personal values?",
                "What advice does Ada give about building an early career?",
                "What is the 'eating your vegetables' concept?",
                "Should you start a company with your partner?",
                "What is the explore and exploit framework for career development?",
                "What is Adam Fishman's growth competency model?",
                "Why is onboarding important for growth?",
                "What is the PMF framework for choosing a company to work at?",
            ]

            for i, q in enumerate(sample_questions, 1):
                st.text(f"{i}. {q}")

        # Query input
        question = st.text_input(
            "Enter your question:",
            placeholder="e.g., What is a curiosity loop?",
            key="query_input"
        )

        col1, col2, col3 = st.columns([1, 1, 4])
        with col1:
            search_button = st.button("🔍 Search", type="primary", use_container_width=True)
        with col2:
            clear_button = st.button("🗑️ Clear", use_container_width=True)

        if clear_button:
            st.rerun()

        # Process query
        if search_button and question:
            if qdrant_status["status"] != "running":
                st.error("⚠️ Qdrant is not running. Please start it first: `./start_qdrant.sh`")
            elif not os.getenv("OPENAI_API_KEY"):
                st.error("⚠️ OpenAI API key is not configured. Please set it in the .env file.")
            else:
                with st.spinner("🤔 Thinking..."):
                    # Query with fresh RAG instance
                    start_time = datetime.now()
                    response, error = query_rag_sync(question, mode=query_mode)
                    end_time = datetime.now()
                    duration = (end_time - start_time).total_seconds()

                    if error:
                        st.error(f"Query failed: {error}")
                    else:
                        # Display result
                        st.success(f"✓ Query completed in {duration:.2f} seconds")

                        st.markdown("### 📝 Answer")
                        st.markdown(f'<div class="query-result">{response}</div>', unsafe_allow_html=True)

                        # Metadata
                        with st.expander("ℹ️ Query Metadata"):
                            st.json({
                                "question": question,
                                "mode": query_mode,
                                "duration_seconds": round(duration, 2),
                                    "timestamp": datetime.now().isoformat()
                                })

    # Tab 2: Statistics
    with tab2:
        st.header("System Statistics")

        if qdrant_status["status"] == "running":
            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("Qdrant Status", "Running ✓")
                st.metric("Version", qdrant_status["version"])
                st.markdown('</div>', unsafe_allow_html=True)

            with col2:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("Collections", len(qdrant_status["collections"]))
                st.metric("Transcripts", stats["total_transcripts"])
                st.markdown('</div>', unsafe_allow_html=True)

            with col3:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("Data Size", f"{stats['total_size'] / 1024 / 1024:.1f} MB")
                st.metric("API Status", "Ready ✓")
                st.markdown('</div>', unsafe_allow_html=True)

            # Collection details
            st.subheader("Collection Details")
            for col in qdrant_status["collections"]:
                with st.expander(f"📦 {col['name']}"):
                    st.json(col)
        else:
            st.warning("Qdrant is not running. Start it with: `./start_qdrant.sh`")

    # Tab 3: Transcripts
    with tab3:
        st.header("Available Transcripts")

        # Search transcripts
        search_term = st.text_input("🔍 Filter transcripts:", placeholder="Search by name...")

        filtered_transcripts = [t for t in stats["transcripts"] if search_term.lower() in t.lower()] if search_term else stats["transcripts"]

        st.write(f"Showing {len(filtered_transcripts)} of {stats['total_transcripts']} transcripts")

        # Display transcripts in a grid
        cols = st.columns(3)
        for i, transcript in enumerate(filtered_transcripts):
            with cols[i % 3]:
                transcript_file = Path("./data") / f"{transcript}.txt"
                size = transcript_file.stat().st_size / 1024  # KB

                with st.container():
                    st.markdown(f"**{transcript}**")
                    st.caption(f"Size: {size:.1f} KB")

                    if st.button(f"View", key=f"view_{i}"):
                        with st.expander(f"Content: {transcript}", expanded=True):
                            with open(transcript_file, 'r', encoding='utf-8') as f:
                                content = f.read()
                                # Show first 1000 characters
                                st.text_area(
                                    "Preview",
                                    content[:1000] + "..." if len(content) > 1000 else content,
                                    height=300
                                )
                                st.info(f"Total length: {len(content)} characters")


if __name__ == "__main__":
    main()
