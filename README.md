# Dictation to Ollama App

A Python application for Linux Mint that allows voice dictation, sends text to a local Ollama model, and reads the response aloud.

## Requirements

- Python 3
- Ollama running locally (http://localhost:11434)
- ALSA audio system

## Installation

1. Create a virtual environment:
   ```bash
   python3 -m venv venv
   ```

2. Activate the virtual environment:
   ```bash
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Ensure Ollama is installed and running with models available.

## Usage

1. Activate the virtual environment (if not already):
   ```bash
   source venv/bin/activate
   ```

2. Run the app:
   ```bash
   python main.py
   ```

2. Select your microphone from the input device dropdown.

3. Select your speakers from the output device dropdown (note: TTS currently uses default speakers).

4. Select an Ollama model from the dropdown.

5. Click "Test Input Device" to verify your mic.

6. Click "Start Dictation" to begin voice input, speak, then "Stop Dictation".

7. Edit the transcribed text if needed, then click "Send to Ollama" for response.

The app remembers your selections, sends text to Ollama, displays and speaks the response.

## Notes

- Speech recognition uses Google's service (requires internet).
- Text-to-speech uses pyttsx3 with espeak on Linux.
- Output device selection for TTS is not implemented; uses default speakers.
- Settings (device and model selections) are saved automatically.

## Troubleshooting

- If "Could not understand audio", test your microphone with `python test_mic.py` (ensure venv activated).
- Check microphone permissions and levels with `alsamixer`.
- Ensure selected input device is correct and working.