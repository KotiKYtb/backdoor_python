import socket

class ClientHandler:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.conn = None
        self.hostname = None  # Nouvelle propriété pour stocker le hostname

    def connect(self):
        try:
            self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.conn.connect((self.ip, self.port))
            
            # Récupérer le hostname du client après connexion
            self.hostname = self.send_command("hostname").strip()
            
            return True
        except Exception as e:
            print(f"Erreur lors de la connexion: {e}")
            return False

    def send_command(self, command):
        try:
            self.conn.send(command.encode('utf-8'))
            return self.conn.recv(4096).decode('utf-8')
        except:
            return "[!] Erreur d'exécution"
        
    def list_directory(self, path):
        return self.send_command(f"LIST_DIR {path}")

    def disconnect(self):
        if self.conn:
            self.conn.close()
            self.conn = None
            self.hostname = None