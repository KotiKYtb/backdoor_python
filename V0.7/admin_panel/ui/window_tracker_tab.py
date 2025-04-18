from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, 
                            QGroupBox, QGridLayout, QHBoxLayout, QFrame,
                            QScrollArea)
from PyQt5.QtCore import QTimer, Qt
from core.window_tracker_handler import WindowTrackerHandler

class WindowTrackerTab(QWidget):
    def __init__(self, connection_tab):
        super().__init__()
        self.connection_tab = connection_tab
        self.tracking = False
        self.tracked_data = {}
        self.update_timer = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)

        header = QFrame()
        header.setStyleSheet("QFrame { background-color: #1E293B; border-radius: 10px; padding: 10px; }")
        header_layout = QHBoxLayout(header)

        self.status_indicator = QLabel()
        self.status_indicator.setFixedSize(16, 16)
        self._update_status_indicator(False)

        self.status_label = QLabel("Cliquez sur le bouton pour démarrer le suivi de la fenêtre active")
        self.status_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        
        self.track_button = QPushButton("Démarrer le suivi")
        self.track_button.setFixedWidth(150)
        self.track_button.clicked.connect(self.toggle_tracking)
        
        header_layout.addWidget(self.status_indicator)
        header_layout.addWidget(self.status_label, 1)
        header_layout.addWidget(self.track_button)
        
        layout.addWidget(header)

        info_container = QWidget()
        info_container.setStyleSheet("background-color: transparent;")
        info_layout = QGridLayout(info_container)
        info_layout.setColumnStretch(1, 1)
        info_layout.setVerticalSpacing(10)
        info_layout.setHorizontalSpacing(15)
        
        title_label = QLabel("Titre:")
        title_label.setStyleSheet("font-weight: bold;")
        self.title_value = QLabel("Non disponible")
        self.title_value.setWordWrap(True)
        self.title_value.setTextInteractionFlags(Qt.TextSelectableByMouse)
        info_layout.addWidget(title_label, 0, 0)
        info_layout.addWidget(self.title_value, 0, 1)
        
        process_label = QLabel("Processus:")
        process_label.setStyleSheet("font-weight: bold;")
        self.process_value = QLabel("Non disponible")
        self.process_value.setTextInteractionFlags(Qt.TextSelectableByMouse)
        info_layout.addWidget(process_label, 1, 0)
        info_layout.addWidget(self.process_value, 1, 1)
        
        pid_label = QLabel("PID:")
        pid_label.setStyleSheet("font-weight: bold;")
        self.pid_value = QLabel("Non disponible")
        self.pid_value.setTextInteractionFlags(Qt.TextSelectableByMouse)
        info_layout.addWidget(pid_label, 2, 0)
        info_layout.addWidget(self.pid_value, 2, 1)
        
        path_label = QLabel("Exécutable:")
        path_label.setStyleSheet("font-weight: bold;")
        self.path_value = QLabel("Non disponible")
        self.path_value.setWordWrap(True)
        self.path_value.setTextInteractionFlags(Qt.TextSelectableByMouse)
        info_layout.addWidget(path_label, 3, 0)
        info_layout.addWidget(self.path_value, 3, 1)
        
        layout.addWidget(info_container)

        history_container = QWidget()
        history_container.setStyleSheet("background-color: transparent;")
        history_layout = QVBoxLayout(history_container)
        
        history_title = QLabel("Historique des fenêtres")
        history_title.setStyleSheet("font-weight: bold; font-size: 14px; color: #3B82F6; margin-top: 10px;")
        history_layout.addWidget(history_title)
        
        self.history_container = QWidget()
        self.history_layout = QVBoxLayout(self.history_container)
        self.history_layout.setContentsMargins(0, 0, 0, 0)
        self.history_layout.setSpacing(5)
        
        history_layout.addWidget(self.history_container)
        layout.addWidget(history_container)
        
        layout.addStretch(1)
        self.setLayout(layout)

    def _update_status_indicator(self, is_active):
        color = "#4ADE80" if is_active else "#FF4444"
        self.status_indicator.setStyleSheet(f"""
            background-color: {color};
            border-radius: 8px;
        """)

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
        self._update_status_indicator(True)
        self.track_button.setText("Arrêter le suivi")
        self.status_label.setText("Suivi de la fenêtre active en cours...")

        self.window_history = []
        self._update_history_widget()

        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_window_info)
        self.update_timer.start(1000)

        self.update_window_info()

    def stop_tracking(self):
        self.tracking = False
        self._update_status_indicator(False)
        self.track_button.setText("Démarrer le suivi")
        self.status_label.setText("Suivi arrêté.")

        if self.update_timer:
            self.update_timer.stop()

    def update_window_info(self):
        if not self.tracking or not self.connection_tab.client_handler:
            return

        handler = WindowTrackerHandler(self.connection_tab.client_handler)
        window_info = handler.get_active_window_info()
        
        if not window_info or window_info.startswith("[!]"):
            self.status_label.setText(f"Erreur: {window_info}")
            return
            
        data = {}
        for line in window_info.splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                data[key.strip()] = value.strip()
        
        self.title_value.setText(data.get("Titre", "Non disponible"))
        self.process_value.setText(data.get("Processus", "Non disponible"))
        self.pid_value.setText(data.get("PID", "Non disponible"))
        self.path_value.setText(data.get("Exécutable", "Non disponible"))

        current_window = data.get("Titre", "")
        if current_window and (not self.window_history or current_window != self.window_history[0]):
            self.window_history.insert(0, current_window)
            self.window_history = self.window_history[:10]
            self._update_history_widget()

    def _update_history_widget(self):
        while self.history_layout.count():
            item = self.history_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        if not self.window_history:
            placeholder = QLabel("L'historique apparaîtra une fois le suivi démarré")
            self.history_layout.addWidget(placeholder)
            return
            
        for i, window_title in enumerate(self.window_history):
            entry = QFrame()
            entry_layout = QHBoxLayout(entry)
            entry_layout.setContentsMargins(8, 8, 8, 8)

            time_label = QLabel(f"#{i+1}")
            time_label.setFixedWidth(30)

            title_label = QLabel(window_title)
            title_label.setWordWrap(True)
            title_label.setTextInteractionFlags(Qt.TextSelectableByMouse)

            entry_layout.addWidget(time_label)
            entry_layout.addWidget(title_label)

            self.history_layout.addWidget(entry)