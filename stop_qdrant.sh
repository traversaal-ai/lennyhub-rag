#!/bin/bash
#
# Stop Qdrant local instance
#

QDRANT_PID_FILE="./qdrant.pid"

if [ ! -f "$QDRANT_PID_FILE" ]; then
    echo "✓ Qdrant is not running (no PID file found)"
    exit 0
fi

PID=$(cat "$QDRANT_PID_FILE")

if ps -p "$PID" > /dev/null 2>&1; then
    echo "Stopping Qdrant (PID: $PID)..."
    kill "$PID"

    # Wait for process to stop
    for i in {1..10}; do
        if ! ps -p "$PID" > /dev/null 2>&1; then
            echo "✓ Qdrant stopped successfully"
            rm "$QDRANT_PID_FILE"
            exit 0
        fi
        sleep 1
    done

    # Force kill if still running
    echo "Force stopping..."
    kill -9 "$PID" 2>/dev/null || true
    rm "$QDRANT_PID_FILE"
    echo "✓ Qdrant stopped"
else
    echo "✓ Qdrant is not running (stale PID file)"
    rm "$QDRANT_PID_FILE"
fi
