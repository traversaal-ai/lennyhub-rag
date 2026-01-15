#!/bin/bash
#
# Install Qdrant locally (without Docker)
# This script downloads and sets up Qdrant binary for your platform
#

set -e  # Exit on error

echo "========================================"
echo "Qdrant Local Installation Script"
echo "========================================"
echo ""

# Detect OS and architecture
OS=$(uname -s | tr '[:upper:]' '[:lower:]')
ARCH=$(uname -m)

# Map architecture names
case "$ARCH" in
    x86_64)
        ARCH="x86_64"
        ;;
    arm64|aarch64)
        ARCH="aarch64"
        ;;
    *)
        echo "❌ Unsupported architecture: $ARCH"
        echo "Supported: x86_64, arm64/aarch64"
        exit 1
        ;;
esac

# Map OS names
case "$OS" in
    darwin)
        PLATFORM="${ARCH}-apple-darwin"
        ;;
    linux)
        PLATFORM="${ARCH}-unknown-linux-musl"
        ;;
    *)
        echo "❌ Unsupported OS: $OS"
        echo "Supported: macOS (darwin), Linux"
        exit 1
        ;;
esac

echo "Detected platform: $OS on $ARCH"
echo "Qdrant platform: $PLATFORM"
echo ""

# Get latest version
echo "Fetching latest Qdrant version..."
LATEST_VERSION=$(curl -s https://api.github.com/repos/qdrant/qdrant/releases/latest | grep '"tag_name"' | sed -E 's/.*"v([^"]+)".*/\1/')

if [ -z "$LATEST_VERSION" ]; then
    echo "❌ Failed to fetch latest version"
    exit 1
fi

echo "Latest version: v$LATEST_VERSION"
echo ""

# Create directory for Qdrant
QDRANT_DIR="$HOME/.qdrant"
QDRANT_BIN="$QDRANT_DIR/qdrant"
QDRANT_STORAGE="./qdrant_storage"

mkdir -p "$QDRANT_DIR"

# Download URL
DOWNLOAD_URL="https://github.com/qdrant/qdrant/releases/download/v${LATEST_VERSION}/qdrant-${PLATFORM}.tar.gz"

echo "Downloading Qdrant from:"
echo "$DOWNLOAD_URL"
echo ""

# Download Qdrant
TEMP_FILE="/tmp/qdrant.tar.gz"
if curl -L -o "$TEMP_FILE" "$DOWNLOAD_URL"; then
    echo "✓ Download complete"
else
    echo "❌ Download failed"
    echo ""
    echo "Available releases at: https://github.com/qdrant/qdrant/releases"
    exit 1
fi

# Extract
echo "Extracting..."
tar -xzf "$TEMP_FILE" -C "$QDRANT_DIR" --strip-components=0
rm "$TEMP_FILE"

# Make executable
chmod +x "$QDRANT_BIN"

# Verify installation
if [ -f "$QDRANT_BIN" ]; then
    VERSION_OUTPUT=$("$QDRANT_BIN" --version 2>&1 || true)
    echo "✓ Qdrant installed successfully at: $QDRANT_BIN"
    echo "  Version: $VERSION_OUTPUT"
else
    echo "❌ Installation failed - binary not found"
    exit 1
fi

echo ""
echo "========================================"
echo "Installation Complete!"
echo "========================================"
echo ""
echo "Qdrant binary: $QDRANT_BIN"
echo "Storage will be in: $QDRANT_STORAGE"
echo ""
echo "To start Qdrant:"
echo "  ./start_qdrant.sh"
echo ""
echo "Or manually:"
echo "  $QDRANT_BIN --storage-path $QDRANT_STORAGE"
echo ""
echo "To add to PATH (optional):"
echo "  echo 'export PATH=\"\$PATH:$QDRANT_DIR\"' >> ~/.bashrc"
echo "  source ~/.bashrc"
echo ""
