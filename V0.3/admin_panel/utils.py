import socket
from PyQt5.QtGui import QPixmap, QPainter, QBrush, QColor, QIcon
from PyQt5.QtCore import Qt


def check_connection(ip, port):
    """Tente une connexion socket pour vérifier si le client est accessible."""
    try:
        test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        test_socket.settimeout(1)  # Timeout pour éviter les blocages
        test_socket.connect((ip, port))
        test_socket.close()
        return True
    except:
        return False


def create_status_icon(color):
    """Crée une icône ronde avec la couleur spécifiée."""
    size = 12  # Taille de l'icône
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)  # Fond transparent

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)  # Lissage des bords
    painter.setBrush(QBrush(QColor(color)))  # Couleur du rond
    painter.setPen(Qt.NoPen)  # Pas de contour
    painter.drawEllipse(0, 0, size, size)  # Dessine un cercle
    painter.end()

    return QIcon(pixmap)