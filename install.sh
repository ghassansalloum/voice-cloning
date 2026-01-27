#!/bin/bash
# Voice Cloning Setup Script
# Automates the full setup process for the voice cloning app

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print functions
print_error() {
    echo -e "${RED}ERROR: $1${NC}"
}

print_success() {
    echo -e "${GREEN}$1${NC}"
}

print_warning() {
    echo -e "${YELLOW}WARNING: $1${NC}"
}

print_info() {
    echo -e "${BLUE}$1${NC}"
}

print_step() {
    echo -e "\n${BLUE}==>${NC} $1"
}

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo ""
echo "=========================================="
echo "  Voice Cloning Setup Script"
echo "=========================================="
echo ""

# Step 1: Check macOS
print_step "Checking system requirements..."

if [[ "$(uname)" != "Darwin" ]]; then
    print_error "This application requires macOS."
    exit 1
fi
print_success "  macOS detected"

# Step 2: Check Apple Silicon
ARCH=$(uname -m)
if [[ "$ARCH" != "arm64" ]]; then
    print_error "This application requires Apple Silicon (M1/M2/M3)."
    print_info "  Detected architecture: $ARCH"
    exit 1
fi
print_success "  Apple Silicon detected"

# Step 3: Check Python version
print_step "Checking Python installation..."

if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed."
    print_info "  Please install Python 3.10 or later from https://python.org"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)

if [[ "$PYTHON_MAJOR" -lt 3 ]] || [[ "$PYTHON_MAJOR" -eq 3 && "$PYTHON_MINOR" -lt 10 ]]; then
    print_error "Python 3.10 or later is required."
    print_info "  Detected version: $PYTHON_VERSION"
    exit 1
fi
print_success "  Python $PYTHON_VERSION detected"

# Step 4: Check RAM
print_step "Checking system memory..."

# Get total RAM in GB (macOS)
TOTAL_RAM_BYTES=$(sysctl -n hw.memsize)
TOTAL_RAM_GB=$((TOTAL_RAM_BYTES / 1073741824))

if [[ "$TOTAL_RAM_GB" -lt 16 ]]; then
    print_warning "16GB RAM recommended for optimal performance."
    print_info "  Detected: ${TOTAL_RAM_GB}GB RAM"
    print_info "  The app may run slowly or encounter memory issues."
else
    print_success "  ${TOTAL_RAM_GB}GB RAM detected"
fi

# Step 5: Create virtual environment
print_step "Setting up virtual environment..."

if [[ -d "venv" ]]; then
    print_info "  Virtual environment already exists"
else
    print_info "  Creating virtual environment..."
    python3 -m venv venv
    print_success "  Virtual environment created"
fi

# Step 6: Activate virtual environment and install dependencies
print_step "Installing dependencies..."

# Activate venv
source venv/bin/activate

# Upgrade pip
print_info "  Upgrading pip..."
pip install --upgrade pip --quiet

# Install requirements
print_info "  Installing packages from requirements.txt..."
pip install -r requirements.txt

print_success "  Dependencies installed"

# Step 7: Verify installation
print_step "Verifying installation..."

VERIFICATION_FAILED=0

# Check gradio
if python3 -c "import gradio" 2>/dev/null; then
    print_success "  gradio - OK"
else
    print_error "  gradio - FAILED"
    VERIFICATION_FAILED=1
fi

# Check torch
if python3 -c "import torch" 2>/dev/null; then
    print_success "  torch - OK"
else
    print_error "  torch - FAILED"
    VERIFICATION_FAILED=1
fi

# Check soundfile
if python3 -c "import soundfile" 2>/dev/null; then
    print_success "  soundfile - OK"
else
    print_error "  soundfile - FAILED"
    VERIFICATION_FAILED=1
fi

# Check mlx_audio
if python3 -c "import mlx_audio" 2>/dev/null; then
    print_success "  mlx_audio - OK"
else
    print_error "  mlx_audio - FAILED"
    VERIFICATION_FAILED=1
fi

if [[ "$VERIFICATION_FAILED" -eq 1 ]]; then
    echo ""
    print_error "Some packages failed to install. Please check the errors above."
    exit 1
fi

# Step 8: Print success message and next steps
echo ""
echo "=========================================="
print_success "  Installation Complete!"
echo "=========================================="
echo ""
echo "To start the application:"
echo ""
echo "  1. Activate the virtual environment:"
echo "     ${BLUE}source venv/bin/activate${NC}"
echo ""
echo "  2. Run the app:"
echo "     ${BLUE}python app.py${NC}"
echo ""
echo "  3. Open your browser to:"
echo "     ${BLUE}http://127.0.0.1:7860${NC}"
echo ""
print_info "Note: The first run will download the model (~1.2GB)"
echo ""
