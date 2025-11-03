#!/usr/bin/env python3
"""
Voice-to-Text Tool for OpenCode Integration

This script provides offline speech recognition that copies transcribed text
to the clipboard for easy integration with OpenCode editor.

Features:
- Offline speech recognition using PocketSphinx
- Clipboard integration
- Hotkey support (Ctrl+Shift+V to start/stop)
- Real-time transcription display
- Configurable microphone selection

Requirements:
- pip install SpeechRecognition pyperclip pyaudio pocketsphinx keyboard

Usage:
python voice_to_opencode.py
"""

import speech_recognition as sr
import pyperclip
import threading
import time
import sys
import os
import json
import keyboard
import pyaudio
import re

class VoiceToOpenCode:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.is_listening = False
        self.current_text = ""
        self.config_file = 'voice_config.json'
        self.config = self.load_config()

        # Audio setup
        self.audio = pyaudio.PyAudio()
        self.microphones = self.get_microphones()
        self.selected_mic_index = self.config.get('microphone_index', 0)

        print("🎤 Voice-to-OpenCode Tool")
        print("=========================")
        print(f"Available microphones: {len(self.microphones)}")
        for i, mic in enumerate(self.microphones):
            print(f"  {i}: {mic}")
        print(f"Selected microphone: {self.selected_mic_index}")
        print("\nControls:")
        print("  Ctrl+Shift+V: Start/Stop listening")
        print("  Ctrl+C: Exit")
        print("  Transcribed text is automatically copied to clipboard")
        print("=========================\n")

    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def save_config(self):
        config = {
            'microphone_index': self.selected_mic_index
        }
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f)
        except:
            pass

    def get_microphones(self):
        microphones = []
        for i in range(self.audio.get_device_count()):
            info = self.audio.get_device_info_by_index(i)
            max_input = info.get('maxInputChannels', 0)
            if isinstance(max_input, (int, float)) and max_input > 0:
                microphones.append(f"{info.get('name')} (Index: {i})")
        return microphones

    def get_mic_device_index(self, mic_string):
        match = re.search(r'Index: (\d+)', mic_string)
        return int(match.group(1)) if match else 0

    def start_listening(self):
        if self.is_listening:
            self.stop_listening()
            return

        self.is_listening = True
        self.current_text = ""
        print("🎙️  Started listening... Speak now!")

        # Start listening in a separate thread
        threading.Thread(target=self.listen_loop, daemon=True).start()

    def stop_listening(self):
        self.is_listening = False
        if self.current_text:
            pyperclip.copy(self.current_text)
            print(f"📋 Copied to clipboard: {self.current_text}")
        print("⏹️  Stopped listening\n")

    def listen_loop(self):
        try:
            device_index = self.get_mic_device_index(self.microphones[self.selected_mic_index])
            with sr.Microphone(device_index=device_index) as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                print("🔄 Adjusted for ambient noise")

                while self.is_listening:
                    try:
                        print("👂 Listening...")
                        audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)

                        print("🔍 Recognizing...")
                        # Use offline PocketSphinx for recognition
                        text = self.recognizer.recognize_sphinx(audio)

                        if text:
                            self.current_text += text + " "
                            print(f"✨ Recognized: {text}")
                            # Copy to clipboard immediately
                            pyperclip.copy(self.current_text.strip())
                        else:
                            print("❓ No speech detected")

                    except sr.WaitTimeoutError:
                        print("⏰ Timeout - no speech detected")
                        continue
                    except sr.UnknownValueError:
                        print("❌ Could not understand audio")
                    except sr.RequestError as e:
                        print(f"❌ Recognition error: {e}")
                    except Exception as e:
                        print(f"❌ Error: {e}")

        except Exception as e:
            print(f"❌ Microphone error: {e}")
            self.is_listening = False

    def select_microphone(self):
        print("\nAvailable microphones:")
        for i, mic in enumerate(self.microphones):
            print(f"  {i}: {mic}")

        try:
            choice = int(input("Select microphone (number): "))
            if 0 <= choice < len(self.microphones):
                self.selected_mic_index = choice
                self.save_config()
                print(f"✅ Selected: {self.microphones[choice]}")
            else:
                print("❌ Invalid choice")
        except ValueError:
            print("❌ Please enter a number")

    def run(self):
        # Try to set up hotkey, but handle permission issues
        try:
            keyboard.add_hotkey('ctrl+shift+v', self.start_listening)
            has_keyboard_support = True
            print("Ready! Press Ctrl+Shift+V to start/stop voice recognition")
        except Exception as e:
            has_keyboard_support = False
            print(f"⚠️  Global hotkeys not available (requires root): {e}")
            print("You can still use the tool by calling functions directly")

        print("Available commands:")
        if has_keyboard_support:
            print("  Ctrl+Shift+V: Start/Stop listening")
            print("  Press 'm' then Enter: Change microphone")
            print("  Press 'q' then Enter: Quit")
        else:
            print("  Type 'start' to begin listening")
            print("  Type 'stop' to stop listening")
            print("  Type 'mic' to change microphone")
            print("  Type 'quit' to exit")
        print()

        try:
            if has_keyboard_support:
                while True:
                    if keyboard.is_pressed('m'):
                        self.select_microphone()
                        time.sleep(0.5)  # Prevent multiple triggers
                    elif keyboard.is_pressed('q'):
                        break
                    time.sleep(0.1)
            else:
                # Fallback to manual input
                while True:
                    try:
                        cmd = input("Command: ").strip().lower()
                        if cmd == 'start':
                            self.start_listening()
                        elif cmd == 'stop':
                            self.stop_listening()
                        elif cmd == 'mic':
                            self.select_microphone()
                        elif cmd == 'quit':
                            break
                        else:
                            print("Commands: start, stop, mic, quit")
                    except KeyboardInterrupt:
                        break

        except KeyboardInterrupt:
            pass
        finally:
            self.audio.terminate()
            self.save_config()
            print("\n👋 Goodbye!")

def main():
    try:
        voice_tool = VoiceToOpenCode()
        voice_tool.run()
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install required packages:")
        print("  pip install SpeechRecognition pyperclip pyaudio pocketsphinx keyboard")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()