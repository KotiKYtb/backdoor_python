# window_tracker.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from core.window_tracker_handler import WindowTrackerHandler

class WindowTrackerTab(QWidget):
    def __init__(self, connection_tab):
        super().__init__()
        self.connection_tab = connection_tab
        self.tracking = False
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.status_label = QLabel("Cliquez sur le bouton pour démarrer le suivi de la fenêtre active.")
        self.track_button = QPushButton("Démarrer le suivi")
        self.track_button.clicked.connect(self.toggle_tracking)
        
        self.window_info_label = QLabel("Aucune information de fenêtre disponible")
        self.window_info_label.setWordWrap(True)

        layout.addWidget(self.status_label)
        layout.addWidget(self.track_button)
        layout.addWidget(self.window_info_label)
        self.setLayout(layout)

    def toggle_tracking(self):
        if not self.connection_tab.client_handler:
            self.status_label.setText("[!] Pas de connexion active.")
            return

        if self.tracking:
            self.stop_tracking()
        else:
            self.start_tracking()

    def start_tracking(self):
        self.tracking = True
        self.track_button.setText("Arrêter le suivi")
        self.status_label.setText("Suivi de la fenêtre active en cours...")
        self.update_window_info()

    def stop_tracking(self):
        self.tracking = False
        self.track_button.setText("Démarrer le suivi")
        self.status_label.setText("Suivi arrêté.")
        self.window_info_label.setText("Aucune information de fenêtre disponible")

    def update_window_info(self):
        if not self.tracking or not self.connection_tab.client_handler:
            return

        handler = WindowTrackerHandler(self.connection_tab.client_handler)
        window_info = handler.get_active_window_info()
        
        if window_info:
            self.window_info_label.setText(window_info)
        
        # Planifier la prochaine mise à jour après 1 seconde
        if self.tracking:
            from PyQt5.QtCore import QTimer
            QTimer.singleShot(1000, self.update_window_info)