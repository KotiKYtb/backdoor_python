from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QFormLayout, QComboBox, QProgressBar
from PyQt5.QtCore import QThread, pyqtSignal, QMutex
from PyQt5.QtGui import QIcon
from core.client_handler import ClientHandler
from utils.helpers import create_status_icon
import socket
import time
import concurrent.futures

class NetworkScannerWorker(QThread):
    client_found = pyqtSignal(str, int, bool)
    progress_updated = pyqtSignal(int)
    scan_completed = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.running = True
        self.mutex = QMutex()
        self.total_ips = 512  # 256 IPs dans chaque plage
        self.scanned_ips = 0
        
    def check_ip(self, ip_data):
        if not self.running:
            return None
            
        ip_prefix, ip_suffix = ip_data
        ip = f"{ip_prefix}.{ip_suffix}"
        PORT = 4444
        TIMEOUT = 0.1  # Timeout réduit à 0.1 seconde
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(TIMEOUT)
            result = sock.connect_ex((ip, PORT))
            is_available = (result == 0)
            sock.close()
            
            # Signaler le résultat si disponible
            if is_available:
                self.client_found.emit(ip, PORT, True)
                
            # Mettre à jour la progression
            self.mutex.lock()
            self.scanned_ips += 1
            progress = int((self.scanned_ips / self.total_ips) * 100)
            self.mutex.unlock()
            self.progress_updated.emit(progress)
            
            return ip if is_available else None
        except:
            # Mettre à jour la progression même en cas d'erreur
            self.mutex.lock()
            self.scanned_ips += 1
            progress = int((self.scanned_ips / self.total_ips) * 100)
            self.mutex.unlock()
            self.progress_updated.emit(progress)
            return None
        
    def run(self):
        # Préparer la liste des IPs à scanner
        ip_list = []
        for prefix in ["172.16.80", "172.16.81"]:
            for suffix in range(256):
                ip_list.append((prefix, suffix))
        
        # Utiliser un pool de threads pour scanner en parallèle
        with concurrent.futures.ThreadPoolExecutor(max_workers=25) as executor:
            futures = [executor.submit(self.check_ip, ip_data) for ip_data in ip_list]
            concurrent.futures.wait(futures)
        
        self.scan_completed.emit()
        
    def stop(self):
        self.running = False

class ConnectionTab(QWidget):
    def __init__(self):
        super().__init__()
        self.client_handler = None
        self.clients = {}  # Dictionnaire vide, sera rempli par le scanner
        self.client_icon_indexes = {}
        self.init_ui()
        self.start_network_scan()

    def init_ui(self):
        layout = QVBoxLayout()

        self.client_list = QComboBox()
        self.client_list.addItem("Sélectionner un client")
        self.client_list.currentIndexChanged.connect(self.fill_client_info)

        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("Entrez l'IP du client")

        self.port_input = QLineEdit()
        self.port_input.setPlaceholderText("Entrez le port")
        self.port_input.setText("4444")  # Port par défaut

        self.status_label = QLabel("🔴 Déconnecté")
        self.scan_status_label = QLabel("⏳ Scan du réseau en cours...")
        
        # Barre de progression pour le scan
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)

        self.connect_button = QPushButton("Se connecter")
        self.connect_button.clicked.connect(self.toggle_connection)
        
        self.rescan_button = QPushButton("Relancer le scan")
        self.rescan_button.clicked.connect(self.start_network_scan)

        form_layout = QFormLayout()
        form_layout.addRow("Choisir un client :", self.client_list)
        form_layout.addRow("IP:", self.ip_input)
        form_layout.addRow("Port:", self.port_input)

        layout.addLayout(form_layout)
        layout.addWidget(self.status_label)
        layout.addWidget(self.scan_status_label)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.connect_button)
        layout.addWidget(self.rescan_button)

        self.setLayout(layout)

    def start_network_scan(self):
        # Reset de la liste des clients
        self.client_list.clear()
        self.client_list.addItem("Sélectionner un client")
        self.clients = {}
        self.client_icon_indexes = {}
        self.scan_status_label.setText("⏳ Scan du réseau en cours...")
        self.progress_bar.setValue(0)
        
        # Démarrage du scanner réseau
        self.network_scanner = NetworkScannerWorker()
        self.network_scanner.client_found.connect(self.add_client_if_available)
        self.network_scanner.progress_updated.connect(self.update_progress)
        self.network_scanner.scan_completed.connect(self.on_scan_completed)
        self.network_scanner.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)
        
    def on_scan_completed(self):
        client_count = len(self.clients)
        self.scan_status_label.setText(f"✅ Scan terminé - {client_count} client(s) trouvé(s)")
        self.progress_bar.setValue(100)
        
    def add_client_if_available(self, ip, port, is_available):
        client_name = f"Client {ip}"
        self.clients[client_name] = (ip, port)
        
        index = self.client_list.count()
        self.client_list.addItem(create_status_icon("green"), client_name)
        self.client_icon_indexes[client_name] = index

    def fill_client_info(self):
        index = self.client_list.currentIndex()
        if index <= 0:
            self.ip_input.clear()
            self.port_input.setText("4444")
            return

        client_name = self.client_list.currentText()
        if client_name in self.clients:
            ip, port = self.clients[client_name]
            self.ip_input.setText(ip)
            self.port_input.setText(str(port))

    def toggle_connection(self):
        if self.client_handler:
            self.client_handler.disconnect()
            self.client_handler = None
            self.status_label.setText("🔴 Déconnecté")
            self.connect_button.setText("Se connecter")
        else:
            ip = self.ip_input.text()
            try:
                port = int(self.port_input.text())
                self.client_handler = ClientHandler(ip, port)
                if self.client_handler.connect():
                    self.status_label.setText("🟢 Connecté")
                    self.connect_button.setText("Se déconnecter")
                else:
                    self.status_label.setText("🔴 Échec de connexion")
            except ValueError:
                self.status_label.setText("🔴 Port invalide")
    
    def closeEvent(self, event):
        # Arrêter proprement le thread de scan lors de la fermeture
        if hasattr(self, 'network_scanner') and self.network_scanner.isRunning():
            self.network_scanner.stop()
            self.network_scanner.wait()
        super().closeEvent(event)