# 🚀 Streamlit App - Quick Start

Visual web interface for your LennyHub RAG system - works on **Windows, macOS, and Linux**!

## Quick Start (2 Steps!)

### Step 1: Install Qdrant (One-time setup)

**Windows (PowerShell):**
```powershell
.\install_qdrant_windows.ps1
```

**macOS/Linux:**
```bash
./install_qdrant_local.sh
```

### Step 2: Launch Streamlit App

**Windows:**
```powershell
.venv\Scripts\Activate.ps1
streamlit run streamlit_app.py
```

**macOS/Linux:**
```bash
source .venv/bin/activate
streamlit run streamlit_app.py
```

Or use the helper script:
```bash
./run_streamlit.sh
```

**That's it!** 🎉 The app will:
- ✅ **Automatically start Qdrant** if it's not running
- ✅ Open in your browser at http://localhost:8501
- ✅ Handle multiple queries without issues

## What You Can Do

🔍 **Query Tab**
- Ask questions about the podcasts
- Get AI-powered answers
- Try sample questions
- Switch between search modes (hybrid, local, global, naive)

📊 **Statistics Tab**
- View Qdrant status
- Check collection info
- See data metrics

📖 **Transcripts Tab**
- Browse all transcripts
- Filter by name
- Preview content

## Features

- ✨ Clean, modern interface
- 🎨 Syntax highlighting for answers
- ⚡ Fast query responses (subprocess isolation for stability)
- 📈 Real-time system status
- 💡 Sample questions included
- 🔧 Multiple query modes
- 🔄 **Unlimited queries** - no event loop conflicts!
- 🚀 **Auto-start Qdrant** - no manual steps needed

## Example Questions to Try

1. "What is a curiosity loop and how does it work?"
2. "What are Ada's personal values?"
3. "What is the growth competency model?"
4. "Why is onboarding important for growth?"
5. "What advice is given about building an early career?"
6. "What is Adam Fishman's growth competency model?"
7. "Should you start a company with your partner?"

## Tips

- **First query may be slower** - subsequent queries use cache
- **Use hybrid mode** for best results (default)
- **Check sidebar** for system status
- **Run unlimited queries** - each query runs in isolation
- **5 minute timeout** - complex queries have plenty of time

## Architecture

The app uses a **subprocess-based query system** for maximum stability:

```
Streamlit App
    ↓
query_worker.py (separate process)
    ↓
RAG System → Qdrant → OpenAI
    ↓
JSON Response → Streamlit Display
```

This ensures:
- No event loop conflicts between queries
- Clean state for each query
- Reliable multi-query sessions

## Stopping the App

Press `Ctrl+C` in the terminal where the app is running.

## Troubleshooting

### Windows: Qdrant not found
```powershell
# Run the installation script
.\install_qdrant_windows.ps1
```

### Query fails with timeout
- Check your internet connection
- Verify OpenAI API key is set in `.env`
- Try a simpler query first

### Qdrant won't start
```powershell
# Windows - Check if already running
Invoke-RestMethod -Uri "http://localhost:6333/"

# macOS/Linux
curl http://localhost:6333/
```

## Need Help?

- **Windows users**: See `install_qdrant_windows.ps1`
- **Check system status**: `./status_qdrant.sh` (macOS/Linux)
- **View full docs**: See `STREAMLIT_README.md`
- **Qdrant setup**: See `QDRANT_SETUP.md`

Enjoy exploring your RAG system visually! 🎉
