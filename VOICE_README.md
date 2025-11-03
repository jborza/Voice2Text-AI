# Voice 2 Text

A Python GUI app for voice recognition that integrates with Ollama AI and provides text-to-speech.

## Features

- 🎤 **Real-time Speech-to-Text**: GPU-accelerated Whisper with selectable model sizes for fast, accurate transcription
- 🤖 **AI Integration**: Send transcribed text to Ollama models for AI responses
- 🗣️ **Text-to-Speech**: Automatic speech synthesis of AI responses
- 📋 **Copy and Send**: Copy text or send directly to AI
- 🎙️ **Microphone Selection**: Choose from available audio input devices
- 🔧 **Model Selection**: Dropdown menus for Whisper model and AI model preferences
- 💾 **Persistent Settings**: Remembers microphone, Whisper model, and AI model preferences

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Install Ollama:
   - Download from https://ollama.ai
   - Follow installation instructions for your OS

3. Start Ollama server:
```bash
ollama serve
```

4. Pull an AI model (e.g., llama3.2):
```bash
ollama pull llama3.2
```

## GPU Requirements

For optimal performance with GPU acceleration:
- NVIDIA GPU with CUDA support (compute capability 3.5+)
- CUDA toolkit 11.8 or later
- PyTorch with CUDA support (automatically installed via requirements.txt)

The app will fall back to CPU if no GPU is available, but performance will be slower.

## Usage

1. Run the app:
```bash
python voice_app.py
```

2. Select your microphone, Whisper model, and preferred AI model from the dropdowns

3. Click "🎙️ Start Dictation" to begin voice recognition

4. Speak clearly into your microphone - text will appear in real-time

5. Click "⏹️ Stop Dictation" to finish and automatically copy text to clipboard

6. Click "🤖 Send to AI" to send the transcribed text to the selected AI model

7. The AI response will appear in the bottom text area and be spoken automatically

8. Use "📋 Copy" to copy text, "🗑️ Clear" to reset, or "⏹️ Stop TTS" to stop speech (note: TTS cannot be interrupted with pyttsx3)

## Requirements

- Python 3.8+
- Working microphone
- Ollama running locally (see Installation)
- For GPU acceleration: NVIDIA GPU with CUDA support
- PyAudio (may require system audio libraries on Linux)

### System Audio Libraries (Linux)

For PyAudio on Linux, you may need to install:
```bash
sudo apt-get install portaudio19-dev python3-pyaudio
```

## Configuration

Settings are saved in `voice_config.json`:
```json
{
  "microphone_index": 0,
  "selected_model": "llama3.2",
  "whisper_model": "base"
}
```

## Troubleshooting

### No microphones detected
- Check microphone permissions
- Ensure microphone is properly connected
- Try running as administrator/sudo

### Poor recognition accuracy
- Speak clearly and closer to microphone
- Reduce background noise
- Adjust microphone sensitivity in system settings
- Try a larger Whisper model (small/medium/large) for better accuracy, or smaller (tiny/base) for faster processing

### Ollama connection issues
- Ensure Ollama is running: `ollama serve`
- Check if the selected model is pulled: `ollama list`
- Verify Ollama is accessible at http://localhost:11434

### GPU not detected
- Ensure CUDA is installed and in PATH
- Check PyTorch CUDA support: `python -c "import torch; print(torch.cuda.is_available())"`
- Fall back to CPU if GPU issues persist

### TTS issues
- pyttsx3 uses system TTS engines
- On Linux, ensure speech-dispatcher is installed
- TTS cannot be stopped mid-speech with pyttsx3

### Import errors
- Install missing dependencies: `pip install -r requirements.txt`
- For PyAudio issues on Linux, install system packages
- Ensure CUDA-compatible PyTorch for GPU support

## Integration with AI

The app integrates with Ollama for AI conversations:

1. Transcribe your speech
2. Send to AI for intelligent responses
3. Get spoken replies automatically
4. Continue the conversation naturally

The app provides a complete voice-AI interaction experience with real-time transcription and responsive AI integration.

## License

MIT License - Feel free to modify and distribute.