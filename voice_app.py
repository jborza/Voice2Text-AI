#!/usr/bin/env python3
"""
Voice 2 Text GUI Application

A standalone GUI app for voice recognition that integrates with AI.
Features a simple interface with start/stop buttons and automatic clipboard copying.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import pyperclip
import threading
import time
import os
import json
import pyaudio
import numpy as np
import tempfile
import wave
from faster_whisper import WhisperModel
from scipy.signal import resample
import torch
import requests
from gtts import gTTS
import pygame
from PIL import Image, ImageTk
import datetime
import queue

class VoiceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Voice 2 Text")
        self.root.geometry("900x800")
        self.root.configure(bg='black')
        self.root.resizable(True, True)

        # Create canvas with gradient background
        self.canvas = tk.Canvas(self.root, width=900, height=800, highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)

        # Bind resize event
        self.canvas.bind('<Configure>', self.on_canvas_resize)

        # Create initial gradient
        self.create_gradient(900, 800)

        # Config
        self.config_file = 'voice_config.json'
        self.config = self.load_config()

        # Audio devices
        self.audio = pyaudio.PyAudio()
        self.microphones = self.get_microphones()
        self.selected_mic_index = self.config.get('microphone_index', 0)

        # Whisper models
        self.whisper_models = ["tiny", "base", "small", "medium", "large-v2", "large-v3"]
        self.selected_whisper_model = self.config.get('whisper_model', 'base')

        # Speech recognition with Faster Whisper
        self.load_whisper_model()

        # Text-to-speech engine
        pygame.mixer.init()
        self.tts_playing = False

        # Queue for thread-safe GUI updates
        self.queue = queue.Queue()
        self.process_queue()

        # Ollama models
        self.ollama_models = self.get_ollama_models()
        self.selected_model = self.config.get('selected_model', "llama3.2" if "llama3.2" in self.ollama_models else (self.ollama_models[0] if self.ollama_models else "llama3.2"))
        self.is_listening = False
        self.current_text = ""
        self.audio_stream = None
        self.audio_frames = []

        # GUI elements
        self.create_gui()

        # Bind close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def update_time(self):
        current_time = datetime.datetime.now().strftime("%I:%M:%S %p")
        self.time_label.config(text=current_time)
        self.root.after(1000, self.update_time)

    def process_queue(self):
        try:
            while True:
                msg = self.queue.get_nowait()
                if msg[0] == "update_status":
                    self.update_status(msg[1], msg[2])
                elif msg[0] == "update_transcript":
                    self.text_area.insert(tk.END, f"{msg[1]}\n")
                    self.text_area.see(tk.END)
                    self.root.update_idletasks()
                elif msg[0] == "show_error":
                    messagebox.showerror("Error", msg[1])
                elif msg[0] == "clear_ai":
                    self.ai_text_area.delete(1.0, tk.END)
                elif msg[0] == "insert_ai":
                    self.ai_text_area.insert(tk.END, msg[1])
                elif msg[0] == "stop_dictation":
                    self.stop_dictation()
        except queue.Empty:
            pass
        self.root.after(100, self.process_queue)

    def get_ollama_models(self):
        try:
            response = requests.get('http://localhost:11434/api/tags', timeout=5)
            if response.status_code == 200:
                models = [model['name'] for model in response.json()['models']]
                return models
            else:
                return []
        except:
            return []

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
            'microphone_index': self.selected_mic_index,
            'selected_model': self.selected_model,
            'whisper_model': self.selected_whisper_model
        }
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f)
        except:
            pass

    def on_close(self):
        self.save_config()
        self.audio.terminate()
        self.root.destroy()

    def create_gradient(self, width, height):
        color1 = (0, 0, 0)
        color2 = (0, 0, 51)
        img = Image.new('RGB', (width, height), color1)
        for y in range(height):
            r = int(color1[0] + (color2[0] - color1[0]) * y / height)
            g = int(color1[1] + (color2[1] - color1[1]) * y / height)
            b = int(color1[2] + (color2[2] - color1[2]) * y / height)
            for x in range(width):
                img.putpixel((x, y), (r, g, b))
        self.bg_photo = ImageTk.PhotoImage(img)
        self.canvas.delete("gradient")
        self.canvas.create_image(0, 0, anchor='nw', image=self.bg_photo, tags="gradient")

    def on_canvas_resize(self, event):
        width = event.width
        height = event.height
        self.create_gradient(width, height)

    def get_microphones(self):
        microphones = []
        for i in range(self.audio.get_device_count()):
            info = self.audio.get_device_info_by_index(i)
            max_input = info.get('maxInputChannels', 0)
            if isinstance(max_input, (int, float)) and max_input > 0:
                microphones.append(f"{info.get('name')} (Index: {i})")
        return microphones

    def get_mic_device_index(self, mic_string):
        import re
        match = re.search(r'Index: (\d+)', mic_string)
        return int(match.group(1)) if match else 0

    def load_whisper_model(self):
        print(f"Loading Whisper model: {self.selected_whisper_model}... (this may take a minute)")
        device = "cuda" if torch.cuda.is_available() else "cpu"
        compute_type = "float16" if device == "cuda" else "int8"
        print(f"Using device: {device}, compute_type: {compute_type}")
        try:
            self.model = WhisperModel(self.selected_whisper_model, device=device, compute_type=compute_type)
            print("Whisper model loaded!")
            try:
                self.queue.put(("update_status", "Whisper model loaded!", "#00aa00"))
            except AttributeError:
                pass  # Queue not initialized yet
        except Exception as e:
            if "out of memory" in str(e).lower() and device == "cuda":
                print("CUDA out of memory, falling back to CPU...")
                device = "cpu"
                compute_type = "int8"
                try:
                    self.model = WhisperModel(self.selected_whisper_model, device=device, compute_type=compute_type)
                    print("Whisper model loaded on CPU!")
                    try:
                        self.queue.put(("update_status", "Whisper model loaded on CPU!", "#00aa00"))
                    except AttributeError:
                        pass
                except Exception as e2:
                    print(f"Failed to load model: {e2}")
                    try:
                        self.queue.put(("show_error", f"Failed to load Whisper model: {e2}"))
                    except AttributeError:
                        pass
            else:
                print(f"Failed to load model: {e}")
                try:
                    self.queue.put(("show_error", f"Failed to load Whisper model: {e}"))
                except AttributeError:
                    pass

    def audio_callback(self, in_data, frame_count, time_info, status):
        """Callback for audio stream"""
        if self.is_listening:
            self.audio_frames.append(in_data)
        return (in_data, pyaudio.paContinue)

    def create_gui(self):
        # Style
        style = ttk.Style()
        style.configure('TFrame', background='#000022')
        style.configure('TButton', font=('Helvetica', 12), padding=10, background='#000022', foreground='white')
        style.configure('TLabel', font=('Helvetica', 10), background='#000000', foreground='white')
        style.configure('TCombobox', font=('Helvetica', 10), fieldbackground='white', foreground='black', selectbackground='#000055', selectforeground='white')
        style.configure('TCombobox.Listbox', background='#000022', foreground='white', selectbackground='#000055', selectforeground='white')

        # Title
        title_label = tk.Label(self.root, text="Voice 2 Text", font=('Arial Black', 26, 'bold'), bg='black', fg='white')
        self.canvas.create_window(450, 50, window=title_label)

        # Version
        version_label = tk.Label(self.root, text="v0.02", font=('Helvetica', 8), bg='#000000', fg='white')
        self.canvas.create_window(850, 20, window=version_label)

        # Time
        self.time_label = tk.Label(self.root, text="", font=('Helvetica', 10), bg='#000000', fg='white')
        self.canvas.create_window(850, 40, window=self.time_label)
        self.update_time()

        # Whisper model selection
        whisper_frame = ttk.Frame(self.root, style='TFrame')
        self.canvas.create_window(450, 610, window=whisper_frame)

        tk.Label(whisper_frame, text="Whisper Model:", bg='#000010', fg='white').pack(side='left')
        self.whisper_var = tk.StringVar()
        self.whisper_combo = ttk.Combobox(whisper_frame, textvariable=self.whisper_var, values=self.whisper_models, state='readonly', width=40)
        self.whisper_combo.pack(side='left', padx=(10, 0))
        self.whisper_var.set(self.selected_whisper_model)
        self.whisper_combo.bind('<<ComboboxSelected>>', self.on_whisper_change)

        # Microphone selection
        mic_frame = ttk.Frame(self.root, style='TFrame')
        self.canvas.create_window(450, 650, window=mic_frame)

        tk.Label(mic_frame, text="Microphone:", bg='#000010', fg='white').pack(side='left')
        self.mic_var = tk.StringVar()
        mic_values = self.microphones if self.microphones else ["No microphone detected"]
        self.mic_combo = ttk.Combobox(mic_frame, textvariable=self.mic_var, values=mic_values, state='readonly', width=40)
        self.mic_combo.pack(side='left', padx=(10, 0))
        if self.microphones:
            self.mic_var.set(self.microphones[self.selected_mic_index])
        else:
            self.mic_var.set("No microphone detected")
        self.mic_combo.bind('<<ComboboxSelected>>', self.on_mic_change_combo)

        # AI Model selection
        model_frame = ttk.Frame(self.root, style='TFrame')
        self.canvas.create_window(450, 690, window=model_frame)

        tk.Label(model_frame, text="AI Model:", bg='#000010', fg='white').pack(side='left')
        self.model_var = tk.StringVar()
        model_values = self.ollama_models if self.ollama_models else ["Ollama not running"]
        self.model_combo = ttk.Combobox(model_frame, textvariable=self.model_var, values=model_values, state='readonly', width=40)
        self.model_combo.pack(side='left', padx=(10, 0))
        if self.ollama_models:
            self.model_var.set(self.selected_model)
        else:
            self.model_var.set("Ollama not running")
        self.model_var.trace('w', self.on_model_change)

        # Status label
        self.status_label = tk.Label(self.root, text="Ready", font=('Helvetica', 12, 'bold'), bg='#000033', fg='yellow')
        self.canvas.create_window(450, 110, window=self.status_label)

        # Text area
        text_frame = ttk.Frame(self.root)
        self.canvas.create_window(250, 290, window=text_frame)

        tk.Label(text_frame, text="Transcribed Text:", bg='black', fg='white', font=('Helvetica', 10, 'bold')).pack(fill='x')
        self.text_area = scrolledtext.ScrolledText(text_frame, height=15, width=35, wrap=tk.WORD,
                                                    bg='black', fg='white', insertbackground='white',
                                                    font=('Consolas', 10), borderwidth=0, relief='flat')
        self.text_area.pack(fill='x', expand=False)

        # AI Response area
        ai_frame = ttk.Frame(self.root)
        self.canvas.create_window(650, 290, window=ai_frame)

        tk.Label(ai_frame, text="AI Response:", bg='black', fg='white', font=('Helvetica', 10, 'bold')).pack(fill='x')
        self.ai_text_area = scrolledtext.ScrolledText(ai_frame, height=15, width=35, wrap=tk.WORD,
                                                       bg='black', fg='white', insertbackground='white',
                                                       font=('Consolas', 10), borderwidth=0, relief='flat')
        self.ai_text_area.pack(fill='x', expand=False)

        # Buttons
        button_frame = ttk.Frame(self.root)
        self.canvas.create_window(450, 530, window=button_frame)

        self.start_button = ttk.Button(button_frame, text="🎙️ Start Dictation",
                                      command=self.start_dictation)
        self.start_button.pack(side='left', padx=5)

        self.stop_button = ttk.Button(button_frame, text="⏹️ Stop Dictation",
                                     command=self.stop_dictation, state='disabled')
        self.stop_button.pack(side='left', padx=5)

        self.copy_button = ttk.Button(button_frame, text="📋 Copy Text",
                                      command=self.copy_text)
        self.copy_button.pack(side='left', padx=5)

        self.send_ai_button = ttk.Button(button_frame, text="🤖 Query AI",
                                         command=self.send_to_ai)
        self.send_ai_button.pack(side='left', padx=5)

        self.stop_tts_button = ttk.Button(button_frame, text="Stop Speech",
                                          command=self.stop_tts)
        self.stop_tts_button.pack(side='left', padx=5)

        self.clear_button = ttk.Button(button_frame, text="🗑️ Clear",
                                       command=self.clear_text)
        self.clear_button.pack(side='left', padx=5)



    def on_mic_change_combo(self, event=None):
        value = self.mic_var.get()
        try:
            self.selected_mic_index = self.microphones.index(value)
            self.save_config()
            self.update_status(f"Selected: {value.split(' (')[0]}")
        except ValueError:
            pass

    def on_model_change(self, *args):
        self.selected_model = self.model_var.get()
        self.update_status(f"AI Model: {self.selected_model}")

    def on_whisper_change(self, event=None):
        old_model = self.selected_whisper_model
        self.selected_whisper_model = self.whisper_var.get()
        if self.selected_whisper_model != old_model:
            self.save_config()
            self.update_status(f"Loading Whisper model: {self.selected_whisper_model}...", "#ffaa00")
            threading.Thread(target=self.load_whisper_model, daemon=True).start()

    def update_status(self, message, color='gray'):
        self.status_label.config(text=message, fg=color)
        self.root.update_idletasks()

    def start_dictation(self):
        if not self.microphones:
            messagebox.showerror("Error", "No microphones found!")
            return

        self.is_listening = True
        self.current_text = ""
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, "🎙️ Listening... Speak now!\n\n")

        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.update_status("🎙️ Listening...", "#00aa00")

        # Start listening in background thread
        threading.Thread(target=self.listen_loop, daemon=True).start()

    def stop_dictation(self):
        self.is_listening = False
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')

        if self.current_text.strip():
            pyperclip.copy(self.current_text.strip())
            self.update_status("📋 Text copied to clipboard!", "#0066cc")
        else:
            self.update_status("Ready", "black")

        # Small delay to ensure audio stream is fully closed
        time.sleep(0.1)

    def copy_text(self):
        text = self.text_area.get(1.0, tk.END).strip()
        prompt = "🎙️ Listening... Speak now!\n\n"
        if text.startswith(prompt):
            text = text[len(prompt):].strip()
        if text:
            pyperclip.copy(text)
            self.update_status("📋 Text copied to clipboard!", "#0066cc")
        else:
            self.update_status("No text to copy", "black")

    def send_to_ai(self):
        text = self.text_area.get(1.0, tk.END).strip()
        if text:
            self.ai_text_area.delete(1.0, tk.END)
            self.update_status("🤖 Sending to AI...", "#ffaa00")
            threading.Thread(target=self.query_ollama_and_speak, args=(text,), daemon=True).start()
        else:
            self.update_status("No text to send to AI", "black")

    def query_ollama_and_speak(self, user_text):
        try:
            # Check if Ollama is running
            if not self.ollama_models:
                self.update_status("Ollama not running - start with 'ollama serve'", "red")
                return

            self.update_status("🤖 Querying AI...", "#ffaa00")
            # Query Ollama
            response = requests.post('http://localhost:11434/api/generate',
                                   json={
                                       "model": self.selected_model,
                                       "prompt": user_text,
                                       "stream": False
                                   },
                                   timeout=60)
            if response.status_code == 200:
                ai_response = response.json()['response'].strip()
                if ai_response:
                    # Display AI response
                    self.queue.put(("clear_ai",))
                    self.queue.put(("insert_ai", ai_response))
                    # Speak the response with gTTS
                    self.update_status("🎵 Generating speech...", "#00aa00")
                    self.speak_with_gtts(ai_response)
                    self.update_status("🤖 AI responded!", "#00aa00")
                else:
                    self.update_status("AI gave empty response", "orange")
            else:
                self.update_status(f"Ollama error: {response.status_code}", "red")
        except requests.exceptions.Timeout:
            self.update_status("AI timeout - model may be slow", "red")
        except requests.exceptions.ConnectionError:
            self.update_status("Cannot connect to Ollama - check if running", "red")
        except Exception as e:
            self.update_status(f"AI error: {str(e)[:50]}", "red")

    def speak_with_gtts(self, text):
        try:
            self.root.after(0, lambda: self.update_status("🔊 Speaking...", "#00aa00"))
            self.tts_playing = True
            tts = gTTS(text=text, lang='en', slow=False, tld='co.uk')
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
            tts.save(temp_file.name)
            pygame.mixer.music.load(temp_file.name)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy() and self.tts_playing:
                pygame.time.wait(100)
            pygame.mixer.music.stop()
            os.unlink(temp_file.name)
        except Exception as e:
            print(f"TTS error: {e}")
        finally:
            self.tts_playing = False
            self.queue.put(("update_status", "Ready", "white"))

    def stop_tts(self):
        self.tts_playing = False
        pygame.mixer.music.stop()
        self.update_status("TTS stopped", "orange")

    def clear_text(self):
        self.text_area.delete(1.0, tk.END)
        self.ai_text_area.delete(1.0, tk.END)
        self.current_text = ""
        self.update_status("Ready", "black")

    def listen_loop(self):
        try:
            device_index = self.get_mic_device_index(self.microphones[self.selected_mic_index])

            # Start audio stream - try different sample rates
            self.audio_frames = []
            sample_rates = [48000, 44100, 32000, 22050, 16000, 8000]  # Try common rates

            for rate in sample_rates:
                try:
                    self.audio_stream = self.audio.open(
                        format=pyaudio.paInt16,
                        channels=1,
                        rate=rate,
                        input=True,
                        input_device_index=device_index,
                        frames_per_buffer=1024,
                        stream_callback=self.audio_callback
                    )
                    self.sample_rate = rate
                    break
                except Exception as e:
                    print(f"Failed to open stream at {rate} Hz: {e}")
                    continue
            else:
                self.root.after(0, lambda: self.update_status("No audio device available - check microphone setup", "red"))
                return

            self.audio_stream.start_stream()
            self.queue.put(("update_status", "🎙️ Listening... (real-time)", "#00aa00"))

            processed_frames = 0
            chunk_duration = 2  # seconds for faster real-time display with good accuracy

            # Real-time transcription loop
            while self.is_listening:
                time.sleep(chunk_duration)

                # Check if we have new frames to process
                if len(self.audio_frames) > processed_frames:
                    chunk_frames = self.audio_frames[processed_frames:]
                    processed_frames = len(self.audio_frames)

                    # Process this chunk
                    self.queue.put(("update_status", "🔍 Recognizing...", "#ffaa00"))
                    try:
                        # Convert chunk to numpy and resample
                        audio_data = np.frombuffer(b''.join(chunk_frames), dtype=np.int16)
                        if self.sample_rate != 16000:
                            num_samples = len(audio_data)
                            target_samples = int(num_samples * 16000 / self.sample_rate)
                            audio_data = resample(audio_data, target_samples).astype(np.int16)

                        # Save chunk to temp WAV
                        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                            temp_filename = temp_file.name

                            with wave.open(temp_filename, 'wb') as wf:
                                wf.setnchannels(1)
                                wf.setsampwidth(2)
                                wf.setframerate(16000)
                                wf.writeframes(audio_data.tobytes())

                        # Transcribe chunk
                        segments, info = self.model.transcribe(temp_filename, language="en")
                        text = " ".join(segment.text for segment in segments).strip()

                        os.unlink(temp_filename)

                        if text:
                            self.current_text += text + " "
                            self.queue.put(("update_transcript", text))
                            self.queue.put(("update_status", "🎙️ Listening... (real-time)", "#00aa00"))
                        else:
                            self.queue.put(("update_status", "🎙️ Listening... (real-time)", "#00aa00"))

                    except Exception as e:
                        self.queue.put(("update_transcript", f"[Error: {e}]"))
                        self.queue.put(("update_status", "🎙️ Listening... (real-time)", "#00aa00"))

            # Stop recording
            if self.audio_stream:
                self.audio_stream.stop_stream()
                self.audio_stream.close()
                self.audio_stream = None

            # Process any remaining frames
            if len(self.audio_frames) > processed_frames:
                remaining_frames = self.audio_frames[processed_frames:]
                self.queue.put(("update_status", "🔍 Finalizing...", "#ffaa00"))
                try:
                    audio_data = np.frombuffer(b''.join(remaining_frames), dtype=np.int16)
                    if self.sample_rate != 16000:
                        num_samples = len(audio_data)
                        target_samples = int(num_samples * 16000 / self.sample_rate)
                        audio_data = resample(audio_data, target_samples).astype(np.int16)

                    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                        temp_filename = temp_file.name

                        with wave.open(temp_filename, 'wb') as wf:
                            wf.setnchannels(1)
                            wf.setsampwidth(2)
                            wf.setframerate(16000)
                            wf.writeframes(audio_data.tobytes())

                    segments, info = self.model.transcribe(temp_filename, language="en")
                    text = " ".join(segment.text for segment in segments).strip()

                    os.unlink(temp_filename)

                    if text:
                        self.current_text += text + " "
                        self.queue.put(("update_transcript", text))

                except Exception as e:
                    self.root.after(0, self.update_transcript, f"[Error: {e}]")

            self.root.after(0, lambda: self.update_status("Ready", "black"))

        except Exception as e:
            self.queue.put(("show_error", f"Recognition error: {e}"))
            self.queue.put(("stop_dictation",))

    def update_transcript(self, text):
        self.text_area.insert(tk.END, f"{text}\n")
        self.text_area.see(tk.END)
        self.root.update_idletasks()

def main():
    try:
        root = tk.Tk()
        app = VoiceApp(root)
        root.mainloop()
    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("Install required packages:")
        print("pip install SpeechRecognition pyperclip pyaudio pocketsphinx")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()