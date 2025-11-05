#!/bin/bash
# Voice2Text AI Launcher Script

echo "🎤 Starting Voice2Text AI Application..."
echo "================================================"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    echo "Also ensure Ollama is running: ollama serve"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Set CUDA library path for GPU acceleration (optional)
if [ -d "venv/lib/python*/site-packages/nvidia" ]; then
    export LD_LIBRARY_PATH="$PWD/venv/lib/python*/site-packages/nvidia/cudnn/lib:$LD_LIBRARY_PATH"
fi

# Run the main application
python voice_app.py

echo "👋 Voice2Text AI closed."