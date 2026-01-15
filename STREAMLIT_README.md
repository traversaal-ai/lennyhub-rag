# Streamlit App for LennyHub RAG

Visual web interface for querying and exploring the LennyHub RAG system.

![Streamlit App](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)

## Features

- 🔍 **Interactive Query Interface** - Ask questions with a user-friendly web UI
- 📊 **System Statistics** - View Qdrant status, collections, and data metrics
- 📖 **Transcript Browser** - Browse and preview all available transcripts
- ⚙️ **Query Modes** - Choose between hybrid, local, global, or naive search
- 💡 **Sample Questions** - Pre-built questions to get you started
- 📈 **Real-time Status** - Monitor Qdrant and API connection status

## Quick Start

### Option 1: Easy Start (Recommended)

```bash
./run_streamlit.sh
```

This script will:
- Check if Qdrant is running (offer to start it if not)
- Install dependencies if needed
- Launch the Streamlit app

### Option 2: Manual Start

```bash
# 1. Ensure Qdrant is running
./start_qdrant.sh

# 2. Install dependencies (first time only)
pip install streamlit requests

# 3. Run the app
streamlit run streamlit_app.py
```

### Option 3: With Custom Port

```bash
streamlit run streamlit_app.py --server.port 8501
```

## Prerequisites

Before running the app, make sure you have:

1. ✅ Python 3.8 or higher
2. ✅ Qdrant installed and running (`./start_qdrant.sh`)
3. ✅ OpenAI API key configured in `.env`
4. ✅ RAG system built with embeddings (`python setup_rag.py`)

## Using the App

### 1. Query Tab

The main interface for asking questions:

- **Enter a question** in the text input
- **Select query mode** from the sidebar (hybrid recommended)
- **Click Search** to get AI-powered answers
- View **sample questions** for inspiration
- See **query metadata** including response time

**Query Modes:**
- `hybrid` - Best overall results (combines local + global + vector search)
- `local` - Entity-focused search
- `global` - Relationship-focused search
- `naive` - Simple vector similarity search

### 2. Statistics Tab

View system information:

- Qdrant connection status
- Number of collections and transcripts
- Data size and API status
- Detailed collection information

### 3. Transcripts Tab

Browse available transcripts:

- **Filter** transcripts by name
- **View** transcript previews
- See transcript **size** information
- Grid layout for easy browsing

## Interface Sections

### Sidebar

- **System Status** - Qdrant and API connection
- **Collections** - List of vector collections
- **Data Statistics** - Transcript count and size
- **Query Settings** - Select search mode
- **Quick Links** - Qdrant dashboard and more

### Main Area

- **Query Interface** - Search and get answers
- **Results Display** - Formatted answers with metadata
- **Statistics** - System metrics and health
- **Transcript Browser** - View available data

## Configuration

The app uses the same configuration as the CLI tools:

- **Working directory**: `./rag_storage`
- **Qdrant URL**: `http://localhost:6333`
- **Collection**: `lennyhub` (from `.env`)
- **OpenAI API Key**: From `.env` file

## Keyboard Shortcuts

When the app is running:

- `Ctrl+C` - Stop the app
- `R` - Rerun the app
- `C` - Clear cache

## Troubleshooting

### App won't start

```bash
# Install dependencies
pip install -r requirements.txt

# Try running again
streamlit run streamlit_app.py
```

### "Qdrant not running" error

```bash
# Check Qdrant status
./status_qdrant.sh

# Start Qdrant if needed
./start_qdrant.sh
```

### "OpenAI API key missing" error

```bash
# Add to .env file
echo "OPENAI_API_KEY=your-key-here" >> .env
```

### Port already in use

```bash
# Use a different port
streamlit run streamlit_app.py --server.port 8502
```

### App is slow or unresponsive

- Check if Qdrant is running: `curl http://localhost:6333/`
- Clear Streamlit cache: Press `C` in the app
- Restart the app: `Ctrl+C` then run again

## Advanced Usage

### Custom Configuration

Edit `streamlit_app.py` to customize:

- Page layout and styling
- Query timeout settings
- Display formatting
- Cache behavior

### Running on a Server

```bash
# Run on all network interfaces
streamlit run streamlit_app.py --server.address 0.0.0.0

# Disable CORS checks
streamlit run streamlit_app.py --server.enableCORS false
```

### Performance Optimization

The app uses Streamlit's caching:

- `@st.cache_resource` - Cache RAG initialization
- `@st.cache_data` - Cache Qdrant status checks

To clear cache:
- Press `C` in the app
- Or use the sidebar menu: `Clear cache`

## Architecture

```
streamlit_app.py
├── UI Components
│   ├── Header and navigation
│   ├── Sidebar (status, settings)
│   └── Main tabs (Query, Stats, Transcripts)
├── Backend Functions
│   ├── check_qdrant_status()
│   ├── initialize_rag()
│   └── query_rag()
└── Integration
    ├── raganything
    ├── qdrant_config
    └── OpenAI API
```

## Tips

1. **First query is slower** - Subsequent queries use cache
2. **Hybrid mode** - Best for most questions
3. **Sample questions** - Use these to explore capabilities
4. **Filter transcripts** - Quickly find relevant sources
5. **Check metadata** - See query timing and parameters

## Screenshots

### Query Interface
- Clean, intuitive search box
- Sample questions for inspiration
- Real-time status indicators

### Results Display
- Formatted markdown answers
- Query metadata and timing
- Source attribution

### Statistics Dashboard
- System health metrics
- Collection details
- Data statistics

## Integration

The Streamlit app integrates with:

- **Qdrant** - Vector database (port 6333)
- **OpenAI API** - LLM and embeddings
- **LightRAG** - Knowledge graph and retrieval
- **RAG-Anything** - Document processing

## Development

To modify the app:

1. Edit `streamlit_app.py`
2. The app will auto-reload on save
3. Test changes immediately

Add new features:
- New tabs in the main area
- Additional sidebar widgets
- Custom query visualizations
- Export functionality

## Resources

- [Streamlit Documentation](https://docs.streamlit.io/)
- [Qdrant Dashboard](http://localhost:6333/dashboard)
- [OpenAI API](https://platform.openai.com/docs)

## Support

If you encounter issues:

1. Check Qdrant status: `./status_qdrant.sh`
2. Verify API key: `echo $OPENAI_API_KEY`
3. View logs: `tail -f qdrant.log`
4. Clear cache: Press `C` in the app

## Next Steps

After using the app:

- Explore different query modes
- Try sample questions
- Browse all transcripts
- Check system statistics
- Build more embeddings with `python setup_rag.py`

Enjoy exploring your RAG system with the visual interface!
