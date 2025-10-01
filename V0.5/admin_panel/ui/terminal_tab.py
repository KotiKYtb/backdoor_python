from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton
from PyQt5.QtCore import QThread, pyqtSignal, QEventLoop
import time

class TerminalThread(QThread):
    output_signal = pyqtSignal(str)

    def __init__(self, client_handler, command):
        super().__init__()
        self.client_handler = client_handler
        self.command = command

    def run(self):
        response = self.client_handler.send_command(self.command)
        self.output_signal.emit(response)

class TerminalTab(QWidget):
    def __init__(self, connection_tab):
        super().__init__()
        self.connection_tab = connection_tab
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.command_input = QTextEdit()
        self.command_input.setPlaceholderText("Entrez des commandes (séparées par des sauts de ligne ou des ;)...")
        self.output_display = QTextEdit()
        self.output_display.setReadOnly(True)

        self.execute_button = QPushButton("Exécuter")
        self.execute_button.clicked.connect(self.execute_command)

        layout.addWidget(self.command_input)
        layout.addWidget(self.execute_button)
        layout.addWidget(self.output_display)

        self.setLayout(layout)

    def execute_command(self):
        if not self.connection_tab.client_handler:
            self.output_display.append("[!] Pas de connexion active.")
            return

        commands = self.command_input.toPlainText().strip().splitlines()  # Découper les commandes par ligne

        if not commands:
            return

        self.output_display.append(f"Exécution des commandes...")
        self.run_commands_sequentially(commands)

    def run_commands_sequentially(self, commands):
        # Ajouter un "event loop" pour attendre la fin de chaque thread avant de lancer le suivant
        for command in commands:
            self.output_display.append(f"Exécution de : {command}")
            self.thread = TerminalThread(self.connection_tab.client_handler, command)
            self.thread.output_signal.connect(self.update_output)
            self.thread.start()

            # Créer un event loop pour attendre la fin du thread actuel
            loop = QEventLoop()
            self.thread.finished.connect(loop.quit)
            loop.exec_()

    def update_output(self, output):
        # Cette méthode sera appelée lorsque la commande est terminée.
        self.output_display.append(output)
        self.output_display.append("-" * 40)  # Ajoute un séparateur pour chaque commande.