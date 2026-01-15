#!/bin/bash
#
# Start Qdrant locally (without Docker)
#

set -e

QDRANT_BIN="$HOME/.qdrant/qdrant"
QDRANT_STORAGE="./qdrant_storage"
QDRANT_PID_FILE="./qdrant.pid"
QDRANT_LOG_FILE="./qdrant.log"

# Check if Qdrant is installed
if [ ! -f "$QDRANT_BIN" ]; then
    echo "❌ Qdrant not found at: $QDRANT_BIN"
    echo ""
    echo "Please install Qdrant first:"
    echo "  ./install_qdrant_local.sh"
    exit 1
fi

# Check if already running
if [ -f "$QDRANT_PID_FILE" ]; then
    PID=$(cat "$QDRANT_PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "✓ Qdrant is already running (PID: $PID)"
        echo ""
        echo "To check status:"
        echo "  curl http://localhost:6333/health"
        exit 0
    else
        # Stale PID file
        rm "$QDRANT_PID_FILE"
    fi
fi

# Create storage directory
mkdir -p "$QDRANT_STORAGE"

echo "Starting Qdrant..."
echo "Binary: $QDRANT_BIN"
echo "Storage: $QDRANT_STORAGE"
echo "Log file: $QDRANT_LOG_FILE"
echo ""

# Start Qdrant in background
nohup "$QDRANT_BIN" \
    --config-path "./qdrant_config.yaml" \
    > "$QDRANT_LOG_FILE" 2>&1 &

QDRANT_PID=$!

# Save PID
echo "$QDRANT_PID" > "$QDRANT_PID_FILE"

# Wait a bit for startup
echo "Waiting for Qdrant to start..."
sleep 3

# Check if it's running
if ps -p "$QDRANT_PID" > /dev/null 2>&1; then
    # Test connection
    if curl -s http://localhost:6333/health > /dev/null 2>&1; then
        echo "✓ Qdrant started successfully!"
        echo ""
        echo "PID: $QDRANT_PID"
        echo "HTTP API: http://localhost:6333"
        echo "gRPC API: http://localhost:6334"
        echo "Dashboard: http://localhost:6333/dashboard"
        echo ""
        echo "To check status:"
        echo "  curl http://localhost:6333/health"
        echo ""
        echo "To view logs:"
        echo "  tail -f $QDRANT_LOG_FILE"
        echo ""
        echo "To stop:"
        echo "  ./stop_qdrant.sh"
    else
        echo "⚠️  Qdrant started but health check failed"
        echo "Check logs: tail -f $QDRANT_LOG_FILE"
    fi
else
    echo "❌ Failed to start Qdrant"
    echo "Check logs: tail -f $QDRANT_LOG_FILE"
    rm -f "$QDRANT_PID_FILE"
    exit 1
fi
