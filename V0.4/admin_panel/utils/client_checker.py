from PyQt5.QtCore import QThread, pyqtSignal
import socket
import time

class ClientStatusChecker(QThread):
    status_checked = pyqtSignal(str, bool)

    def __init__(self, clients, timeout=1):
        super().__init__()
        self.clients = clients
        self.timeout = timeout

    def run(self):
        for name, (ip, port) in self.clients.items():
            is_online = self.test_connection(ip, port)
            self.status_checked.emit(name, is_online)
            time.sleep(0.1)  # légère pause pour éviter de freeze même sur gros réseau

    def test_connection(self, ip, port):
        try:
            with socket.create_connection((ip, port), timeout=self.timeout):
                return True
        except:
            return False