import socket

class ClientHandler:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.conn = None

    def connect(self):
        try:
            self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.conn.connect((self.ip, self.port))
            return True
        except:
            return False

    def send_command(self, command):
        try:
            self.conn.send(command.encode())
            return self.conn.recv(4096).decode('utf-8')
        except:
            return "[!] Erreur d'exécution"

    def disconnect(self):
        if self.conn:
            self.conn.close()
            self.conn = None
