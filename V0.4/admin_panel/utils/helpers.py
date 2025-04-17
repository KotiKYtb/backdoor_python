import socket
from PyQt5.QtGui import QPixmap, QPainter, QBrush, QColor, QIcon
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


def create_status_icon(color):
    """
    Crée une icône ronde de couleur spécifiée pour indiquer l'état de connexion.
    """
    size = 12
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setBrush(QBrush(QColor(color)))
    painter.setPen(Qt.NoPen)
    painter.drawEllipse(0, 0, size, size)
    painter.end()

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