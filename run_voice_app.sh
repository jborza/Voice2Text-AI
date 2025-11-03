#!/bin/bash
# Voice-to-OpenCode Launcher Script

echo "🎤 Starting Voice To AI Application..."
echo "================================================"

# Check if virtual environment exists
if [ ! -d "voice_env" ]; then
    echo "❌ Virtual environment not found!"
    echo "Run: python3 -m venv voice_env && source voice_env/bin/activate && pip install SpeechRecognition pyperclip pyaudio pocketsphinx"
    exit 1
fi

# Activate virtual environment and run the app
source voice_env/bin/activate

# Set CUDA library path for GPU acceleration
export LD_LIBRARY_PATH="$PWD/voice_env/lib/python3.12/site-packages/nvidia/cudnn/lib:$LD_LIBRARY_PATH"

python voice_app.py

echo "👋 Voice app closed."