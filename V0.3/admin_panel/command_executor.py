class CommandExecutor:
    def __init__(self, conn_manager):
        self.conn_manager = conn_manager

    def execute(self, command):
        if not self.conn_manager.conn:
            return "[!] Pas de connexion établie."

        try:
            self.conn_manager.conn.send(command.encode())
            result = self.conn_manager.conn.recv(4096)
            return result.decode('utf-8', errors='replace')
        except Exception as e:
            return f"[!] Erreur lors de l'exécution: {str(e)}"