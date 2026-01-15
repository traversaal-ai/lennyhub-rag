#!/bin/bash
#
# Run Streamlit App for LennyHub RAG
#

set -e

echo "========================================"
echo "LennyHub RAG Streamlit App"
echo "========================================"
echo ""

# Check if Qdrant is running
if curl -s http://localhost:6333/ > /dev/null 2>&1; then
    echo "✓ Qdrant is running"
else
    echo "⚠️  Qdrant is not running"
    echo ""
    echo "Would you like to start Qdrant? (y/n)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        ./start_qdrant.sh
        echo ""
    else
        echo "You can start Qdrant later with: ./start_qdrant.sh"
        echo ""
    fi
fi

# Check if streamlit is installed
if ! command -v streamlit &> /dev/null; then
    echo "⚠️  Streamlit not found"
    echo "Installing dependencies..."
    pip install -r requirements.txt
    echo ""
fi

echo "Starting Streamlit app..."
echo "The app will open in your browser automatically"
echo ""
echo "Press Ctrl+C to stop the app"
echo ""

# Run streamlit
streamlit run streamlit_app.py
