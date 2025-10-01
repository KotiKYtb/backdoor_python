from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from core.screenshot_handler import ScreenshotHandler

class ScreenshotTab(QWidget):
    def __init__(self, connection_tab):
        super().__init__()
        self.connection_tab = connection_tab
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.status_label = QLabel("Cliquez sur le bouton pour capturer l'écran.")
        self.capture_button = QPushButton("Capturer l'écran")
        self.capture_button.clicked.connect(self.capture_screenshot)

        layout.addWidget(self.status_label)
        layout.addWidget(self.capture_button)
        self.setLayout(layout)

    def capture_screenshot(self):
        if not self.connection_tab.client_handler:
            self.status_label.setText("[!] Pas de connexion active.")
            return

        handler = ScreenshotHandler(self.connection_tab.client_handler)
        result = handler.capture()
        self.status_label.setText(result)