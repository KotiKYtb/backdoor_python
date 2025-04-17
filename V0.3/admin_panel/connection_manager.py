import socket

class ConnectionManager:
    def __init__(self):
        self.conn = None

    def connect(self, host, port):
        try:
            self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.conn.connect((host, int(port)))
            return True
        except Exception as e:
            print(f"[!] Erreur de connexion: {str(e)}")
            self.conn = None
            return False

    def disconnect(self):
        if self.conn:
            self.conn.close()
            self.conn = None
import socket

class ConnectionManager:
    def __init__(self):
        self.conn = None

    def connect(self, host, port):
        try:
            self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.conn.connect((host, int(port)))
            return True
        except Exception as e:
            print(f"[!] Erreur de connexion: {str(e)}")
            self.conn = None
            return False

    def disconnect(self):
        if self.conn:
            self.conn.close()
            self.conn = None