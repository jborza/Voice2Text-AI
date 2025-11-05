#!/bin/bash
# Voice2Text AI Launcher Script

echo "🎤 Starting Voice2Text AI Application..."
echo "================================================"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo ""
    echo "Please run the following commands to set up the environment:"
    echo "  python3 -m venv venv"
    echo "  source venv/bin/activate"
    echo "  pip install -r requirements.txt"
    echo ""
    echo "Also ensure Ollama is running: ollama serve"
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Check if required packages are installed
echo "🔍 Checking dependencies..."
python -c "import pyaudio, faster_whisper, torch, numpy, requests, gtts, pygame" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Some dependencies are missing!"
    echo ""
    echo "Please install dependencies:"
    echo "  source venv/bin/activate"
    echo "  pip install -r requirements.txt"
    echo ""
    echo "If you get audio-related errors, you may need:"
    echo "  sudo apt-get install portaudio19-dev python3-pyaudio (Ubuntu/Debian)"
    echo "  # or equivalent for your system"
    exit 1
fi

# Set CUDA library path for GPU acceleration (optional)
if [ -d "venv/lib/python*/site-packages/nvidia" ]; then
    export LD_LIBRARY_PATH="$PWD/venv/lib/python*/site-packages/nvidia/cudnn/lib:$LD_LIBRARY_PATH"
    echo "🎮 CUDA support detected"
fi

echo "🚀 Starting Voice2Text AI..."
# Run the main application
python voice_app.py

echo "👋 Voice2Text AI closed."