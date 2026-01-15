# Quick Setup Guide

This guide shows you how to set up the RAG system with local Qdrant in one command.

## Prerequisites

- Python 3.8+
- OpenAI API key

## One-Command Setup

The `setup_rag.py` script automates the entire setup process:

```bash
cd lennyhub-rag
python setup_rag.py
```

This script will automatically:
1. ✓ Check if Qdrant is installed (installs if needed)
2. ✓ Verify your OpenAI API key
3. ✓ Start Qdrant server
4. ✓ Build embeddings from all transcripts
5. ✓ Test the RAG system

## Setup Options

### Process All Transcripts (Full Setup)
```bash
python setup_rag.py
```

### Quick Setup (First 10 Transcripts Only)
```bash
python setup_rag.py --quick
```

### Custom Number of Transcripts
```bash
python setup_rag.py --max 5
```

## After Setup

Once setup is complete, you can:

### 1. Query the System
```bash
# Single query
python query_rag.py "What is a curiosity loop?"

# Interactive mode
python query_rag.py --interactive
```

### 2. Query with Sources
```bash
python query_with_sources.py "What are the best practices for product management?"
```

### 3. Check Qdrant Status
```bash
./status_qdrant.sh
```

### 4. View Dashboard
Open in browser: http://localhost:6333/dashboard

### 5. Stop Qdrant (When Done)
```bash
./stop_qdrant.sh
```

## Troubleshooting

### Setup fails with "OPENAI_API_KEY not set"
```bash
# Add to .env file
echo "OPENAI_API_KEY=your-key-here" >> .env

# Or export temporarily
export OPENAI_API_KEY='your-key-here'
```

### Qdrant won't start
```bash
# Check if port is in use
lsof -i :6333

# Kill existing Qdrant
pkill -f qdrant

# Try setup again
python setup_rag.py
```

### Want to rebuild from scratch
```bash
# Stop Qdrant
./stop_qdrant.sh

# Remove old data
rm -rf qdrant_storage/ rag_storage/

# Run setup again
python setup_rag.py
```

## Manual Setup (Alternative)

If you prefer manual control:

```bash
# 1. Install Qdrant
./install_qdrant_local.sh

# 2. Start Qdrant
./start_qdrant.sh

# 3. Build RAG (all transcripts)
python build_transcript_rag.py

# Or quick build (10 transcripts)
python build_rag_quick.py
```

## Summary

**Automated (Recommended):**
```bash
python setup_rag.py              # Full setup
python setup_rag.py --quick      # Quick setup
```

**Manual:**
```bash
./install_qdrant_local.sh       # One-time
./start_qdrant.sh               # Each session
python build_transcript_rag.py   # Build embeddings
```

Both approaches work - use what fits your workflow!
