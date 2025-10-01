from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QFormLayout, QComboBox
from PyQt5.QtCore import QThread
from PyQt5.QtGui import QIcon
from core.client_handler import ClientHandler
from utils.helpers import create_status_icon
from utils.client_checker import ClientStatusChecker  # nouveau fichier

class ConnectionTab(QWidget):
    def __init__(self):
        super().__init__()
        self.client_handler = None
        self.clients = {
            "Client 1": ("172.16.80.233", 5555),
            "Client 2": ("192.168.1.20", 4444),
            "Client 3": ("10.0.0.5", 4444)
        }
        self.client_icon_indexes = {}
        self.init_ui()
        self.start_client_status_check()

    def init_ui(self):
        layout = QVBoxLayout()

        self.client_list = QComboBox()
        self.client_list.addItem("Sélectionner un client")

        for name in self.clients.keys():
            index = self.client_list.count()
            self.client_list.addItem(create_status_icon("gray"), name)
            self.client_icon_indexes[name] = index

        self.client_list.currentIndexChanged.connect(self.fill_client_info)

        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("Entrez l'IP du client")

        self.port_input = QLineEdit()
        self.port_input.setPlaceholderText("Entrez le port")

        self.status_label = QLabel("🔴 Déconnecté")

        self.connect_button = QPushButton("Se connecter")
        self.connect_button.clicked.connect(self.toggle_connection)

        form_layout = QFormLayout()
        form_layout.addRow("Choisir un client :", self.client_list)
        form_layout.addRow("IP:", self.ip_input)
        form_layout.addRow("Port:", self.port_input)

        layout.addLayout(form_layout)
        layout.addWidget(self.status_label)
        layout.addWidget(self.connect_button)

        self.setLayout(layout)

    def start_client_status_check(self):
        self.checker_thread = ClientStatusChecker(self.clients)
        self.checker_thread.status_checked.connect(self.update_client_icon)
        self.checker_thread.start()

    def update_client_icon(self, client_name, is_online):
        icon = create_status_icon("green" if is_online else "red")
        index = self.client_icon_indexes[client_name]
        self.client_list.setItemIcon(index, icon)

    def fill_client_info(self):
        index = self.client_list.currentIndex()
        if index <= 0:
            self.ip_input.clear()
            self.port_input.clear()
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
            port = int(self.port_input.text())
            self.client_handler = ClientHandler(ip, port)
            if self.client_handler.connect():
                self.status_label.setText("🟢 Connecté")
                self.connect_button.setText("Se déconnecter")