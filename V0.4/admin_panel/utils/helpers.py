import socket
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor, QBrush
from PyQt5.QtCore import Qt


def check_connection(ip, port, timeout=1):
    """
    Vérifie si une connexion avec le client est possible.
    Retourne `True` si la connexion est établie, `False` sinon.
    """
    try:
        with socket.create_connection((ip, port), timeout):
            return True
    except (socket.timeout, ConnectionRefusedError):
        return False



def create_status_icon(status):
    """
    Crée une icône de statut (QIcon) en fonction de l'état
    
    Args:
        status (str): "green", "red", "yellow", "gray"
    
    Returns:
        QIcon: L'icône correspondant au statut
    """
    colors = {
        "green": "#23d18b",    # Vert - en ligne
        "red": "#ff3860",      # Rouge - hors ligne
        "yellow": "#e6c800",   # Jaune - en attente
        "gray": "#6b7280",     # Gris - inconnu
    }
    
    color = colors.get(status.lower(), colors["gray"])
    
    # Créer un pixmap de 12x12 pixels
    pixmap = QPixmap(12, 12)
    pixmap.fill(QColor(0, 0, 0, 0))  # Transparent
    
    # Dessiner un cercle coloré
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setBrush(QBrush(QColor(color)))
    painter.setPen(QColor(color).darker(120))  # Bordure légèrement plus foncée
    painter.drawEllipse(1, 1, 10, 10)  # Cercle de 10x10 avec 1px de marge
    painter.end()
    
    # Créer une QIcon à partir du pixmap
    return QIcon(pixmap)

def format_output(output):
    """
    Nettoie et formate la sortie des commandes avant de l'afficher.
    Gère l'encodage/décodage et supprime les caractères parasites.
    """
    try:
        return output.decode("utf-8", errors="replace").strip()
    except AttributeError:  # Si output est déjà une chaîne
        return output.strip()