# Qdrant Setup Guide for LennyHub RAG

This guide explains how to set up and use Qdrant as the vector database for the LennyHub RAG system.

## Overview

Qdrant is a production-grade vector database that replaces the default NanoVectorDB (JSON-based storage). Benefits include:
- Better performance for large datasets
- Persistent storage in a dedicated database
- Advanced filtering and search capabilities
- Production-ready reliability

## Prerequisites

- **Windows**, macOS, or Linux operating system
- Python 3.8+ with pip
- `curl` command (macOS/Linux) or PowerShell (Windows)

## Installation

### Windows Installation

```powershell
# Run the Windows installation script
.\install_qdrant_windows.ps1
```

This script will:
- Download the latest Qdrant binary for Windows (x86_64)
- Install it to `~/.qdrant/qdrant.exe`
- Create the storage directory
- Verify the installation

**Note:** The Streamlit app will **automatically start Qdrant** when you launch it, so manual startup is optional.

### macOS/Linux Installation

```bash
cd lennyhub-rag
./install_qdrant_local.sh
```

This script will:
- Detect your platform (macOS/Linux, x86_64/ARM)
- Download the latest Qdrant binary
- Install it to `~/.qdrant/qdrant`
- Verify the installation

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

This installs `qdrant-client` and other required packages.

### 3. Configure Environment

The `.env` file should already have Qdrant configured:

```bash
# Qdrant Configuration
USE_QDRANT=true
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION_NAME=lennyhub
```

## Usage

### Starting Qdrant

```bash
./start_qdrant.sh
```

You should see:
```
✓ Qdrant started successfully!

PID: 12345
HTTP API: http://localhost:6333
gRPC API: http://localhost:6334
Dashboard: http://localhost:6333/dashboard
```

### Verify It's Running

```bash
# Check status
./status_qdrant.sh

# Or check health endpoint
curl http://localhost:6333/health
```

### Test Configuration

```bash
python qdrant_config.py
```

Expected output:
```
✓ Using Qdrant vector database
  URL: http://localhost:6333
  Collection: lennyhub
✓ Connected! Found 0 collection(s)
```

### Build RAG Index

```bash
# Build with all transcripts
python build_transcript_rag.py

# Or build with first 10 transcripts (for testing)
python build_transcript_rag.py  # Edit MAX_TRANSCRIPTS in script
```

### Query the System

```bash
# Simple query
python query_rag.py "What is a curiosity loop?"

# Interactive mode
python query_rag.py --interactive

# With source attribution
python query_with_sources.py "What is a curiosity loop?"
```

### Stopping Qdrant

```bash
./stop_qdrant.sh
```

## Management Commands

### Check Status

```bash
./status_qdrant.sh
```

Shows:
- Process status (running/stopped)
- PID and resource usage
- HTTP API accessibility
- Collections and their status
- Recent log entries

### View Logs

```bash
# Follow logs in real-time
tail -f qdrant.log

# View last 50 lines
tail -50 qdrant.log
```

### Qdrant Dashboard

Access the web UI at: http://localhost:6333/dashboard

Features:
- View collections
- Inspect vectors
- Run test queries
- Monitor performance

## File Locations

```
lennyhub-rag/
├── install_qdrant_local.sh     # Installation script
├── start_qdrant.sh             # Start Qdrant
├── stop_qdrant.sh              # Stop Qdrant
├── status_qdrant.sh            # Check status
├── qdrant_config.yaml          # Qdrant configuration
├── qdrant.pid                  # Process ID (when running)
├── qdrant.log                  # Qdrant logs
├── qdrant_storage/             # Vector data (gitignored)
└── rag_storage/                # Knowledge graph & metadata
```

**Binary location:** `~/.qdrant/qdrant`

## Switching Between NanoVectorDB and Qdrant

### Switch to Qdrant

1. Edit `.env`: Set `USE_QDRANT=true`
2. Start Qdrant: `./start_qdrant.sh`
3. Rebuild index: `python build_transcript_rag.py`

### Switch to NanoVectorDB

1. Edit `.env`: Set `USE_QDRANT=false`
2. Rebuild index: `python build_transcript_rag.py`
3. (Optional) Stop Qdrant: `./stop_qdrant.sh`

The system automatically detects the configuration.

## Troubleshooting

### Installation Issues

**Problem:** Installation script fails

**Solutions:**
```bash
# Check platform support
uname -s  # Should be Darwin (macOS) or Linux
uname -m  # Should be x86_64 or arm64/aarch64

# Check internet connection
curl -I https://github.com

# Manual download from:
# https://github.com/qdrant/qdrant/releases
```

### Qdrant Won't Start

**Problem:** `start_qdrant.sh` fails

**Solutions:**
```bash
# Check if port 6333 is already in use
lsof -i :6333

# Kill any existing Qdrant process
pkill -f qdrant

# Remove stale PID file
rm qdrant.pid

# Try starting again
./start_qdrant.sh

# View logs for errors
tail -f qdrant.log
```

### Permission Denied

**Problem:** Permission errors when running scripts

**Solution:**
```bash
# Make scripts executable
chmod +x *.sh

# Make Qdrant binary executable
chmod +x ~/.qdrant/qdrant
```

### Connection Refused

**Problem:** `Cannot connect to Qdrant at http://localhost:6333`

**Solutions:**
1. Verify Qdrant is running: `./status_qdrant.sh`
2. Check logs: `tail -f qdrant.log`
3. Restart: `./stop_qdrant.sh && ./start_qdrant.sh`

### Collections Not Found

**Problem:** "Collection not found" errors

**Solution:**
Rebuild the index:
```bash
python build_transcript_rag.py
```

### Port Already in Use

**Problem:** Port 6333 is busy

**Solutions:**
```bash
# Find what's using the port
lsof -i :6333

# Kill the process
kill <PID>

# Or edit qdrant_config.yaml to use different ports
```

## Advanced Configuration

### Custom Ports

Edit `qdrant_config.yaml`:

```yaml
service:
  http_port: 6333  # Change to your preferred port
  grpc_port: 6334  # Change to your preferred port
```

Then update `.env`:
```bash
QDRANT_URL=http://localhost:YOUR_PORT
```

### Performance Tuning

Edit `qdrant_config.yaml`:

```yaml
storage:
  storage_path: ./qdrant_storage
  performance:
    max_search_threads: 4

service:
  http_port: 6333
  grpc_port: 6334
  max_request_size_mb: 32

log_level: INFO  # Options: TRACE, DEBUG, INFO, WARN, ERROR
```

### Multiple Collections

To use different collections for different projects:

```bash
# In .env
QDRANT_COLLECTION_NAME=project_a

# Or override in code
lightrag_kwargs = get_lightrag_kwargs(collection_name="project_b")
```

## Resources

- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [Qdrant Python Client](https://github.com/qdrant/qdrant-client)
- [LightRAG](https://github.com/HKUDS/LightRAG)
- [Qdrant GitHub Releases](https://github.com/qdrant/qdrant/releases)

## Support

If you encounter issues:

1. Check this troubleshooting guide
2. Review logs: `tail -f qdrant.log`
3. Test configuration: `python qdrant_config.py`
4. Check health: `curl http://localhost:6333/health`
5. Verify status: `./status_qdrant.sh`

For Qdrant-specific issues: https://qdrant.tech/documentation/
