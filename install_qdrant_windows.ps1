# PowerShell script to install Qdrant on Windows
# Run: .\install_qdrant_windows.ps1

Write-Host "========================================"
Write-Host "Qdrant Windows Installation Script"
Write-Host "========================================"
Write-Host ""

# Check if running as administrator (not required but recommended)
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

# Detect architecture
$arch = [System.Environment]::Is64BitOperatingSystem
if (-not $arch) {
    Write-Host "ERROR: 32-bit Windows is not supported" -ForegroundColor Red
    exit 1
}

Write-Host "Detected: Windows x86_64"
Write-Host ""

# Get latest version from GitHub API
Write-Host "Fetching latest Qdrant version..."
try {
    $release = Invoke-RestMethod -Uri "https://api.github.com/repos/qdrant/qdrant/releases/latest"
    $version = $release.tag_name -replace "^v", ""
    Write-Host "Latest version: v$version" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Failed to fetch latest version" -ForegroundColor Red
    Write-Host "Error: $_"
    exit 1
}

# Setup directories
$qdrantDir = Join-Path $env:USERPROFILE ".qdrant"
$qdrantBin = Join-Path $qdrantDir "qdrant.exe"

if (-not (Test-Path $qdrantDir)) {
    New-Item -ItemType Directory -Path $qdrantDir -Force | Out-Null
}

Write-Host ""
Write-Host "Installation directory: $qdrantDir"

# Download URL for Windows
$downloadUrl = "https://github.com/qdrant/qdrant/releases/download/v$version/qdrant-x86_64-pc-windows-msvc.zip"

Write-Host ""
Write-Host "Downloading Qdrant from:"
Write-Host $downloadUrl
Write-Host ""

# Download
$tempFile = Join-Path $env:TEMP "qdrant.zip"
try {
    Write-Host "Downloading... (this may take a minute)"
    Invoke-WebRequest -Uri $downloadUrl -OutFile $tempFile -UseBasicParsing
    Write-Host "Download complete!" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Download failed" -ForegroundColor Red
    Write-Host "Error: $_"
    Write-Host ""
    Write-Host "You can manually download from: https://github.com/qdrant/qdrant/releases"
    exit 1
}

# Extract
Write-Host "Extracting..."
try {
    Expand-Archive -Path $tempFile -DestinationPath $qdrantDir -Force
    Remove-Item $tempFile -Force
    Write-Host "Extraction complete!" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Extraction failed" -ForegroundColor Red
    Write-Host "Error: $_"
    exit 1
}

# Verify installation
if (Test-Path $qdrantBin) {
    Write-Host ""
    Write-Host "Qdrant installed successfully!" -ForegroundColor Green
    Write-Host "Binary location: $qdrantBin"
    
    # Test version
    try {
        $versionOutput = & $qdrantBin --version 2>&1
        Write-Host "Version: $versionOutput"
    } catch {
        Write-Host "Note: Could not verify version"
    }
} else {
    Write-Host "ERROR: Installation failed - binary not found" -ForegroundColor Red
    Write-Host "Expected at: $qdrantBin"
    exit 1
}

# Create storage directory
$storageDir = Join-Path (Get-Location) "qdrant_storage"
if (-not (Test-Path $storageDir)) {
    New-Item -ItemType Directory -Path $storageDir -Force | Out-Null
}

Write-Host ""
Write-Host "========================================"
Write-Host "Installation Complete!"
Write-Host "========================================"
Write-Host ""
Write-Host "Qdrant binary: $qdrantBin"
Write-Host "Storage directory: $storageDir"
Write-Host ""
Write-Host "To start Qdrant manually:"
Write-Host "  & '$qdrantBin' --config-path .\qdrant_config.yaml"
Write-Host ""
Write-Host "Or simply run the Streamlit app - it will start Qdrant automatically:"
Write-Host "  streamlit run streamlit_app.py"
Write-Host ""

# Create a marker file to indicate Qdrant is installed
$markerFile = Join-Path $qdrantDir ".installed"
$version | Out-File -FilePath $markerFile -Encoding UTF8

Write-Host "Done!" -ForegroundColor Green
