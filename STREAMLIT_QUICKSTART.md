# 🚀 Streamlit App - Quick Start

Visual web interface for your LennyHub RAG system in 3 simple steps!

## Step 1: Start Qdrant (if not running)

```bash
./start_qdrant.sh
```

## Step 2: Launch Streamlit App

```bash
./run_streamlit.sh
```

Or manually:
```bash
streamlit run streamlit_app.py
```

## Step 3: Use the App!

The app will open automatically in your browser at: http://localhost:8501

### What You Can Do:

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
- ⚡ Fast query responses
- 📈 Real-time system status
- 💡 Sample questions included
- 🔧 Multiple query modes

## Example Questions to Try

1. "What is a curiosity loop and how does it work?"
2. "What are Ada's personal values?"
3. "What is the growth competency model?"
4. "Why is onboarding important for growth?"
5. "What advice is given about building an early career?"

## Tips

- **First query may be slower** - subsequent queries use cache
- **Use hybrid mode** for best results (default)
- **Check sidebar** for system status
- **Clear cache** if results seem stale (press 'C')

## Stopping the App

Press `Ctrl+C` in the terminal where the app is running.

## Need Help?

- Check system status: `./status_qdrant.sh`
- View full docs: See `STREAMLIT_README.md`
- Restart Qdrant: `./stop_qdrant.sh && ./start_qdrant.sh`

That's it! Enjoy exploring your RAG system visually! 🎉
