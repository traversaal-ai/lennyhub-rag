# 🎙️ LennyHub RAG

A production-ready RAG (Retrieval-Augmented Generation) system built on transcripts from [Lenny's Podcast](https://www.lennysnewsletter.com/podcast), featuring conversations with top product leaders and growth experts.

## 🌟 Key Features

- **🚀 One-Command Setup**: Automated installation and indexing with `setup_rag.py`
- **🎨 Visual Web Interface**: Beautiful Streamlit app for querying and exploration
- **🗄️ Qdrant Vector Database**: Production-grade local vector storage (no Docker needed)
- **📊 Knowledge Graph RAG**: Advanced retrieval with LightRAG entity and relationship extraction
- **🔍 Multiple Search Modes**: Hybrid, local, global, and naive search strategies
- **📚 297 Podcast Transcripts**: Comprehensive knowledge base from industry leaders
- **💡 Interactive Queries**: Both CLI and web-based query interfaces
- **⚡ Fast & Efficient**: Caching, parallel processing, and optimized embeddings

## 📊 Dataset

### 297 Podcast Transcripts Available

Featuring conversations with:
- **Product Leaders**: Julie Zhuo, Shreyas Doshi, Adam Fishman
- **Growth Experts**: Brian Balfour, Elena Verna, Kevin Kwok
- **Founders**: Patrick Collison, Amjad Masad, Andrew Wilkinson
- **Executives**: Ada Chen Rekhi, Claire Hughes Johnson, Gokul Rajaram
- And many more!

**Topics covered**: Product management, growth strategy, career development, startup advice, leadership, decision-making frameworks, and more.

## 🚀 Quick Start (4 Steps)

### 1. Clone the Repository

```bash
git clone https://github.com/traversaal-ai/lennyhub-rag.git
cd lennyhub-rag
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure API Key

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=your-key-here
```

### 4. Run Automated Setup

**Sequential Mode (Reliable)**
```bash
# Process first 10 transcripts (quick test - 5 min)
python setup_rag.py --quick

# Process first 50 transcripts (30-40 min)
python setup_rag.py --max 50

# Process all 297 transcripts (2-3 hours)
python setup_rag.py
```

**Parallel Mode (5-10x Faster!)** ⚡
```bash
# Process 50 transcripts in parallel (6-8 min)
python setup_rag.py --max 50 --parallel

# All 297 transcripts in parallel (25-35 min)
python setup_rag.py --parallel

# Custom workers (default: 5, max: 10)
python setup_rag.py --parallel --workers 8
```

**What this does:**
- ✅ Installs Qdrant locally (if needed)
- ✅ Starts Qdrant server
- ✅ Builds embeddings and knowledge graph (sequential or parallel)
- ✅ Automatically resumes from where you left off
- ✅ Tests the system automatically

## 🎨 Visual Interface (Streamlit App)

Launch the beautiful web UI:

```bash
./run_streamlit.sh
```

**Features:**
- 🔍 **Query Tab**: Ask questions with AI-powered search
- 📊 **Statistics Tab**: View system health and metrics
- 📖 **Transcripts Tab**: Browse and preview all transcripts
- ⚙️ **Sidebar**: Real-time status, settings, and quick links
- 💡 **Sample Questions**: Pre-built queries to get started

**Screenshot Features:**
- Clean, modern interface
- Multiple query modes (hybrid, local, global, naive)
- Real-time Qdrant status monitoring
- Query timing and metadata
- Transcript filtering and preview

## 💻 Command Line Interface

### Interactive Query Mode

```bash
python query_rag.py --interactive
```

### Single Queries

```bash
python query_rag.py "What is a curiosity loop?"
python query_rag.py "What is the growth competency model?"
```

### Query with Sources

```bash
python query_with_sources.py "What are best practices for onboarding?"
python query_rag_with_chunks.py "How do you build a great product team?"
```

## 💡 Example Queries

### Career Strategy
```
"What is the explore and exploit framework for career development?"
"How do you avoid being the boiled frog in your career?"
"What advice does Ada give about early career strategy?"
"How should you use values to make career decisions?"
```

### Growth & Product Management
```
"What are the four components of the growth competency model?"
"Why is onboarding important for growth?"
"How can onboarding improve retention?"
"What are opinionated defaults?"
```

### Decision Making & Frameworks
```
"What is a curiosity loop and how does it work?"
"What is the PMF framework for choosing a company?"
"What is the inner vs outer scorecard concept?"
"What is the eating your vegetables concept?"
```

### Leadership & Management
```
"Should you start a company with your partner?"
"How do you build trust with your team?"
"What makes a great product leader?"
```

## 📖 Documentation

### Quick Start Guides
- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Complete setup instructions
- **[STREAMLIT_QUICKSTART.md](STREAMLIT_QUICKSTART.md)** - Launch web UI in 3 steps
- **[VISUAL_APP_SUMMARY.md](VISUAL_APP_SUMMARY.md)** - Streamlit app features overview

### Technical Documentation
- **[QDRANT_SETUP.md](QDRANT_SETUP.md)** - Qdrant installation and configuration
- **[STREAMLIT_README.md](STREAMLIT_README.md)** - Full Streamlit app documentation
- **[OVERVIEW.md](OVERVIEW.md)** - Technical architecture deep dive
- **[ADDING_TRANSCRIPTS.md](ADDING_TRANSCRIPTS.md)** - Guide for adding more transcripts

### Reference
- **[sample_questions.txt](sample_questions.txt)** - 70+ curated questions
- **[MULTI_TURN_QUESTIONS.md](MULTI_TURN_QUESTIONS.md)** - 85+ complex queries

## 🗂️ Project Structure

```
lennyhub-rag/
├── 📊 Data & Storage
│   ├── data/                         # 297 podcast transcripts
│   ├── rag_storage/                  # Knowledge graph & metadata
│   └── qdrant_storage/               # Vector embeddings (local DB)
│
├── 🚀 Setup & Configuration
│   ├── setup_rag.py                  # One-command automated setup
│   ├── install_qdrant_local.sh       # Install Qdrant binary
│   ├── start_qdrant.sh               # Start Qdrant server
│   ├── stop_qdrant.sh                # Stop Qdrant server
│   ├── status_qdrant.sh              # Check Qdrant status
│   ├── qdrant_config.yaml            # Qdrant configuration
│   ├── qdrant_config.py              # Python Qdrant config
│   ├── requirements.txt              # Python dependencies
│   └── .env                          # API keys & settings
│
├── 🎨 User Interfaces
│   ├── streamlit_app.py              # Visual web interface
│   ├── run_streamlit.sh              # Launch Streamlit app
│   ├── query_rag.py                  # CLI query interface
│   ├── query_with_sources.py         # Query with source attribution
│   └── query_rag_with_chunks.py      # Query with chunk details
│
├── 🔧 Building & Processing
│   ├── build_transcript_rag.py       # Build RAG (all transcripts)
│   ├── build_rag_quick.py            # Quick build (10 transcripts)
│   └── build_transcript_rag_parallel.py  # Parallel processing
│
└── 📚 Documentation
    ├── README.md                     # This file
    ├── SETUP_GUIDE.md                # Setup instructions
    ├── STREAMLIT_QUICKSTART.md       # Streamlit quick start
    ├── STREAMLIT_README.md           # Streamlit full docs
    ├── VISUAL_APP_SUMMARY.md         # Streamlit features
    ├── QDRANT_SETUP.md               # Qdrant documentation
    ├── OVERVIEW.md                   # Technical architecture
    └── ADDING_TRANSCRIPTS.md         # Adding transcripts
```

## 🎯 Use Cases

### For Product Managers
- Research frameworks and best practices
- Learn from top PMs at Airbnb, Stripe, Meta
- Study product strategy and execution
- Interview preparation

### For Growth Professionals
- Understand growth competency models
- Learn retention and onboarding strategies
- Study successful growth strategies
- Framework deep-dives

### For Career Development
- Career strategy frameworks
- Decision-making guidance
- Leadership insights
- Personal values exploration

### For Founders & Leaders
- Startup advice from successful founders
- Leadership frameworks
- Team building strategies
- Strategic decision-making

## 🧠 How It Works

### Architecture

```
User Query
    ↓
Streamlit UI / CLI
    ↓
RAG System (RAG-Anything)
    ↓
LightRAG (Knowledge Graph)
    ↓
├─→ Entity Extraction (GPT-4o-mini)
├─→ Relationship Mapping
├─→ Embeddings (text-embedding-3-small)
└─→ Qdrant Vector Storage
    ↓
Hybrid Search (local + global + vector)
    ↓
Answer Synthesis (GPT-4o-mini)
    ↓
Results with Sources
```

### Parallel Processing

The system supports parallel transcript processing for significantly faster indexing:

**Sequential Processing**:
- Processes one transcript at a time
- Safer, more predictable
- ~2-3 minutes per transcript

**Parallel Processing** (⚡ 5-10x faster):
- Processes 5-10 transcripts simultaneously
- Uses asyncio semaphore for concurrency control
- Rate-limit safe (max 10 workers)
- Smart resume: skips already-processed transcripts
- ~20-30 seconds per transcript (with 5 workers)

```bash
# Enable parallel mode
python setup_rag.py --max 50 --parallel

# Custom concurrency
python setup_rag.py --parallel --workers 8
```

### Search Modes

**Hybrid** (Recommended)
- Combines local + global + vector search
- Best overall results
- Balanced speed and accuracy

**Local**
- Entity-focused search
- Fast and precise
- Great for specific concepts

**Global**
- Relationship-focused
- Broader context
- Best for understanding connections

**Naive**
- Pure vector similarity
- Fastest mode
- Simple semantic search

---

## 🎓 Want to Build Your Own AI Agents?
<img width="1177" height="327" alt="Screenshot 2026-01-16 at 20 13 13" src="https://github.com/user-attachments/assets/96b446d7-7db4-4fb5-a191-23fbab77ba8f" />

This RAG system demonstrates advanced agent engineering with knowledge graphs, vector databases, and LLM orchestration. Want to learn how to build systems like this from scratch?

**Join the Agent Engineering Bootcamp: Developers Edition**
- Learn to build production-ready AI agents
- Master RAG, LLMs, and agentic workflows
- Taught by [Hamza Farooq](https://www.linkedin.com/in/hamzafarooq/) (Ex-Google, Prof UCLA & UMN)
- 4.8★ rating from 95+ students

**[Get $200 OFF with code 200OFF →](https://maven.com/boring-bot/advanced-llm?promoCode=200OFF)**

---

## 🏗️ Technical Stack

- **RAG Framework**: [RAG-Anything](https://github.com/HKUDS/RAG-Anything) v1.2.9+
- **Knowledge Graph**: [LightRAG](https://github.com/HKUDS/LightRAG) v1.4.9+
- **Vector Database**: [Qdrant](https://qdrant.tech/) v1.16+
- **LLM**: OpenAI GPT-4o-mini
- **Embeddings**: OpenAI text-embedding-3-small (1536 dims)
- **Web UI**: Streamlit 1.28+
- **Language**: Python 3.8+

## 💰 Cost & Performance

### Initial Build Costs

| Transcripts | Embeddings | Entity Extraction | Total | Sequential | Parallel (5x) |
|------------|------------|-------------------|-------|------------|---------------|
| 10 (quick) | $0.04 | $0.20 | ~$0.24 | 5 min | 5 min* |
| 50 | $0.20 | $1.00 | ~$1.20 | 30-40 min | **6-8 min** |
| 297 (all) | $1.20 | $6.00 | ~$7.20 | 2-3 hrs | **25-35 min** |

*Small batches don't benefit much from parallelization

### Query Costs
- **Per Query**: $0.001-0.01
- **Cached Queries**: Free (stored responses)
- **Typical Session**: ~$0.05-0.10

### Cost Optimization
- LLM response caching (saves ~80% on repeated queries)
- Efficient chunking and embedding strategies
- Smart query routing

## ⚙️ System Requirements

- **OS**: macOS or Linux
- **Python**: 3.8 or higher
- **RAM**: 2GB+ recommended (4GB+ for all transcripts)
- **Disk Space**:
  - Base: ~500MB
  - 10 transcripts: ~1GB
  - 50 transcripts: ~2GB
  - 297 transcripts: ~5GB
- **Internet**: Required for OpenAI API calls

## 🔧 Advanced Usage

### Custom Configuration

Edit `.env` file:
```bash
# Vector Database
USE_QDRANT=true
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION_NAME=lennyhub

# Working Directory
WORKING_DIR=./rag_storage
```

### Qdrant Management

```bash
# Start Qdrant
./start_qdrant.sh

# Check status
./status_qdrant.sh

# View logs
tail -f qdrant.log

# Stop Qdrant
./stop_qdrant.sh

# Dashboard
open http://localhost:6333/dashboard
```

### Manual Build (Advanced)

**Sequential Processing**:
```bash
# Build all transcripts
python build_transcript_rag.py

# Quick build (10 transcripts)
python build_rag_quick.py
```

**Parallel Processing** (5-10x faster):
```bash
# Using setup_rag.py (recommended)
python setup_rag.py --max 50 --parallel --workers 5

# Using standalone parallel script
python build_transcript_rag_parallel.py
```

**Performance Comparison**:
- Sequential: ~2-3 min/transcript
- Parallel (5 workers): ~20-30 sec/transcript
- Parallel (10 workers): ~15-20 sec/transcript

### Programmatic Access

```python
from raganything import RAGAnything, RAGAnythingConfig
from qdrant_config import get_lightrag_kwargs
import asyncio

# Initialize
config = RAGAnythingConfig(working_dir="./rag_storage")
lightrag_kwargs = get_lightrag_kwargs()
rag = RAGAnything(config=config, lightrag_kwargs=lightrag_kwargs)

# Query
response = await rag.aquery("Your question here", mode="hybrid")
print(response)
```

## 🐛 Troubleshooting

### Qdrant Issues

```bash
# Check if running
curl http://localhost:6333/

# Restart Qdrant
./stop_qdrant.sh && ./start_qdrant.sh

# View logs
tail -f qdrant.log
```

### Setup Issues

```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade

# Check API key
echo $OPENAI_API_KEY

# Clear cache and rebuild
rm -rf rag_storage/ qdrant_storage/
python setup_rag.py --quick
```

### Streamlit Issues

```bash
# Clear cache
streamlit cache clear

# Run on different port
streamlit run streamlit_app.py --server.port 8502

# Check logs
streamlit run streamlit_app.py --logger.level debug
```

## 📈 Performance Tips

### Indexing Performance
1. **Use Parallel Mode**: 5-10x faster with `--parallel` flag
2. **Adjust Workers**: More workers = faster (up to 10 for rate limits)
3. **Smart Resume**: System automatically skips processed transcripts
4. **Start Small**: Test with `--quick` before full indexing
5. **Monitor Resources**: Check RAM usage with large datasets

### Query Performance
1. **Use Hybrid Mode**: Best balance of speed and accuracy
2. **Enable Caching**: Responses are cached automatically (saves ~80%)
3. **Batch Queries**: Process multiple questions in one session
4. **Choose Right Mode**: Naive is fastest, hybrid is most accurate
5. **Reuse Sessions**: Keep Streamlit app running for instant queries

## 🤝 Contributing

Contributions welcome! Areas for improvement:

- Add more transcripts
- Improve query templates
- Enhance UI features
- Add new search modes
- Optimize performance
- Expand documentation

## 📝 License

See [LICENSE](LICENSE) file for details.

## 🙏 Credits

- **Transcripts**: [Lenny's Podcast](https://www.lennysnewsletter.com/podcast)
- **RAG Framework**: [RAG-Anything](https://github.com/HKUDS/RAG-Anything) by HKUDS
- **Knowledge Graph**: [LightRAG](https://github.com/HKUDS/LightRAG) by HKUDS
- **Vector Database**: [Qdrant](https://qdrant.tech/)
- **LLM & Embeddings**: [OpenAI](https://openai.com/)

## 🌟 Featured Guests

Ada Chen Rekhi, Adam Fishman, Adam Grenier, Andrew Wilkinson, Annie Duke, Brian Balfour, Casey Winters, Claire Hughes Johnson, Elena Verna, Gokul Rajaram, Jeff Weinstein, Julie Zhuo, Kevin Kwok, Lenny Rachitsky, Maggie Crowley, Marily Nika, Patrick Collison, Shreyas Doshi, and 279 more amazing guests!

## 📧 Support

- Check [SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed instructions
- See [TROUBLESHOOTING](QDRANT_SETUP.md#troubleshooting) section
- Review [sample_questions.txt](sample_questions.txt) for query examples

## 🎉 What's New

### Latest Updates

⚡ **Parallel Processing**: 5-10x faster indexing with `--parallel` flag 
✨ **One-Command Setup**: Automated `setup_rag.py` script 
🎨 **Streamlit Web UI**: Beautiful visual interface 
🗄️ **Local Qdrant**: Production vector DB (no Docker) 
📚 **297 Transcripts**: Complete podcast library 
🚀 **Smart Resume**: Automatically skips processed transcripts 
📊 **Statistics Dashboard**: Real-time system monitoring 
💡 **Sample Questions**: Built-in query examples 

---

**Ready to explore?**

```bash
git clone https://github.com/traversaal-ai/lennyhub-rag.git
cd lennyhub-rag
python setup_rag.py --quick
```

---

## 🚀 Level Up Your AI Agent Skills

Enjoyed building with this RAG system? Take your skills to the next level!

**Agent Engineering Bootcamp: Developers Edition** teaches you to build production-ready AI agents like this one (and more advanced systems). Learn RAG pipelines, knowledge graphs, LLM orchestration, and agentic workflows from industry experts.

**Taught by [Hamza Farooq](https://www.linkedin.com/in/hamzafarooq/)**
- Founder & Ex-Google Engineer 
- Professor at Stanford Continuing Studies, UCLA & UMN
- 4.8★ rating (95+ students)

**[Enroll now with $200 OFF →](https://maven.com/boring-bot/advanced-llm?promoCode=200OFF)**

---

Built with ❤️ using RAG-Anything, LightRAG, Qdrant, and Streamlit
