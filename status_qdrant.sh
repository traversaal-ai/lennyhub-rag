#!/bin/bash
#
# Check Qdrant status
#

QDRANT_PID_FILE="./qdrant.pid"
QDRANT_LOG_FILE="./qdrant.log"

echo "========================================"
echo "Qdrant Status Check"
echo "========================================"
echo ""

# Check PID file
if [ -f "$QDRANT_PID_FILE" ]; then
    PID=$(cat "$QDRANT_PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "Process Status: ✓ Running"
        echo "PID: $PID"

        # Get memory/CPU usage on macOS or Linux
        if [[ "$OSTYPE" == "darwin"* ]]; then
            ps -p "$PID" -o %cpu,%mem,rss,vsz,etime,comm | tail -1
        else
            ps -p "$PID" -o %cpu,%mem,rss,vsz,etime,cmd | tail -1
        fi
    else
        echo "Process Status: ✗ Not running (stale PID file)"
    fi
else
    echo "Process Status: ✗ Not running (no PID file)"
fi

echo ""

# Check HTTP endpoint
if curl -s http://localhost:6333/health > /dev/null 2>&1; then
    echo "HTTP API (6333): ✓ Accessible"

    # Get version info
    VERSION_INFO=$(curl -s http://localhost:6333/health 2>/dev/null)
    if [ -n "$VERSION_INFO" ]; then
        echo "Version: $(echo $VERSION_INFO | grep -o '"version":"[^"]*"' | cut -d'"' -f4)"
    fi
else
    echo "HTTP API (6333): ✗ Not accessible"
fi

echo ""

# Check collections if accessible
if curl -s http://localhost:6333/collections > /dev/null 2>&1; then
    COLLECTIONS=$(curl -s http://localhost:6333/collections 2>/dev/null)
    COLLECTION_COUNT=$(echo "$COLLECTIONS" | grep -o '"collections":\[' | wc -l | tr -d ' ')

    if [ "$COLLECTION_COUNT" -gt 0 ]; then
        echo "Collections: $(echo "$COLLECTIONS" | grep -o '"name":"[^"]*"' | cut -d'"' -f4 | tr '\n' ', ' | sed 's/,$//')"
    else
        echo "Collections: None"
    fi
fi

echo ""
echo "========================================"
echo ""
echo "Log file: $QDRANT_LOG_FILE"
echo "  Last 5 lines:"
if [ -f "$QDRANT_LOG_FILE" ]; then
    tail -5 "$QDRANT_LOG_FILE" | sed 's/^/  /'
else
    echo "  (No log file found)"
fi

echo ""
echo "To view full logs:"
echo "  tail -f $QDRANT_LOG_FILE"
echo ""
