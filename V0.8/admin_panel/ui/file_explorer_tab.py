import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QPushButton, 
                            QInputDialog, QFileDialog, QMessageBox, QHeaderView)
from PyQt5.QtCore import QDir
from PyQt5.QtGui import QIcon

class FileExplorerTab(QWidget):
    def __init__(self, connection_tab):
        super().__init__()
        self.connection_tab = connection_tab
        # Correction: utiliser clients au lieu de client
        self.current_path = "C:\\"  # Chemin par défaut sur la machine distante
        
        self.layout = QVBoxLayout()
        
        # Création de la vue d'arborescence personnalisée
        self.tree_view = QTreeWidget()
        self.tree_view.setHeaderLabels(["Nom", "Type"])
        self.tree_view.header().setSectionResizeMode(0, QHeaderView.Stretch)
        
        # Création des boutons
        self.path_button = QPushButton("Choisir un dossier")
        self.path_button.clicked.connect(self.change_directory)
        
        self.refresh_button = QPushButton("Actualiser")
        self.refresh_button.clicked.connect(self.refresh_directory)
        
        self.open_button = QPushButton("Ouvrir un fichier texte")
        self.open_button.clicked.connect(self.open_text_file)
        
        self.download_button = QPushButton("Télécharger un dossier")
        self.download_button.clicked.connect(self.download_directory)
        
        self.download_file_button = QPushButton("Télécharger un fichier")
        self.download_file_button.clicked.connect(self.download_file)
        
        # Navigation
        self.back_button = QPushButton("Dossier parent")
        self.back_button.clicked.connect(self.go_to_parent)
        
        # Double-clic pour naviguer dans les dossiers
        self.tree_view.itemDoubleClicked.connect(self.handle_double_click)
        
        # Ajout des widgets à la disposition
        self.layout.addWidget(self.path_button)
        self.layout.addWidget(self.refresh_button)
        self.layout.addWidget(self.back_button)
        self.layout.addWidget(self.open_button)
        self.layout.addWidget(self.download_button)
        self.layout.addWidget(self.download_file_button)
        self.layout.addWidget(self.tree_view)
        self.setLayout(self.layout)
    
    def handle_double_click(self, item, column):
        # Si c'est un dossier, on y entre
        if item.text(1) == "Dossier":
            new_path = os.path.join(self.current_path, item.text(0))
            self.current_path = new_path
            self.refresh_directory()
    
    def go_to_parent(self):
        # Remonter au dossier parent
        parent_path = os.path.dirname(self.current_path)
        if parent_path and parent_path != self.current_path:  # Éviter de remonter au-delà de la racine
            self.current_path = parent_path
            self.refresh_directory()
    
    def change_directory(self):
        # Ouvre un dialogue pour demander un chemin de répertoire à l'utilisateur
        path, ok = QInputDialog.getText(self, "Choisir un répertoire", 
                                         "Entrez le chemin du répertoire sur la machine distante:",
                                         text=self.current_path)
        
        if ok and path:
            # Met à jour l'arborescence en fonction du nouveau chemin distant
            self.current_path = path
            self.refresh_directory()
    
    def refresh_directory(self):
        # Vérifier qu'un client est sélectionné
        selected_client = self.connection_tab.get_selected_client()
        if not selected_client:
            QMessageBox.warning(self, "Erreur", "Aucun client sélectionné.")
            return
        
        # Effacer l'arborescence actuelle
        self.tree_view.clear()
        
        # Demander la liste des fichiers et dossiers au client distant
        result = selected_client.send_command(f"LIST_DIR {self.current_path}")
        
        try:
            import json
            files_list = json.loads(result)
            
            # Vérifier s'il y a une erreur
            if isinstance(files_list, dict) and "error" in files_list:
                QMessageBox.warning(self, "Erreur", f"Impossible d'accéder au dossier: {files_list['error']}")
                return
            
            # Ajouter les éléments à l'arborescence
            for file_info in files_list:
                item = QTreeWidgetItem(self.tree_view)
                item.setText(0, file_info["name"])
                item.setText(1, "Dossier" if file_info["is_dir"] else "Fichier")
                
                # Optionnel: ajouter des icônes différentes pour les dossiers et fichiers
                # item.setIcon(0, QIcon("folder.png") if file_info["is_dir"] else QIcon("file.png"))
            
        except Exception as e:
            QMessageBox.warning(self, "Erreur", f"Erreur lors de la lecture du répertoire distant: {e}")
    
    def open_text_file(self):
        # Vérifier qu'un client est sélectionné
        selected_client = self.connection_tab.get_selected_client()
        if not selected_client:
            QMessageBox.warning(self, "Erreur", "Aucun client sélectionné.")
            return
            
        # Récupérer l'élément sélectionné
        selected_items = self.tree_view.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un fichier.")
            return
            
        selected_item = selected_items[0]
        file_name = selected_item.text(0)
        file_type = selected_item.text(1)
        
        if file_type != "Fichier" or not file_name.endswith(".txt"):
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un fichier texte (.txt).")
            return
        
        file_path = os.path.join(self.current_path, file_name)
        
        # Demander au client de lire le contenu du fichier
        result = selected_client.send_command(f"READ_FILE {file_path}")
        
        # Afficher le contenu
        QMessageBox.information(self, "Contenu du fichier", result)

    def download_directory(self):
        # Vérifier qu'un client est sélectionné
        selected_client = self.connection_tab.get_selected_client()
        if not selected_client:
            QMessageBox.warning(self, "Erreur", "Aucun client sélectionné.")
            return
            
        # Récupérer l'élément sélectionné
        selected_items = self.tree_view.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un dossier.")
            return
            
        selected_item = selected_items[0]
        dir_name = selected_item.text(0)
        dir_type = selected_item.text(1)
        
        if dir_type != "Dossier":
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un dossier.")
            return
        
        dir_path = os.path.join(self.current_path, dir_name)
        
        # Ouvrir une fenêtre pour choisir où enregistrer le dossier téléchargé
        save_dir = QFileDialog.getExistingDirectory(self, "Choisir le répertoire de sauvegarde")
        
        if save_dir:
            # Télécharger le dossier et son contenu
            QMessageBox.information(self, "Téléchargement", 
                                    "La fonctionnalité de téléchargement de dossier n'est pas encore implémentée.\n"
                                    f"Elle téléchargerait {dir_path} vers {save_dir}")
            # TODO: Implémenter la fonctionnalité de téléchargement de dossier

    def download_file(self):
        # Vérifier qu'un client est sélectionné
        selected_client = self.connection_tab.get_selected_client()
        if not selected_client:
            QMessageBox.warning(self, "Erreur", "Aucun client sélectionné.")
            return
            
        # Récupérer l'élément sélectionné
        selected_items = self.tree_view.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un fichier.")
            return
            
        selected_item = selected_items[0]
        file_name = selected_item.text(0)
        file_type = selected_item.text(1)
        
        if file_type != "Fichier":
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un fichier.")
            return
        
        file_path = os.path.join(self.current_path, file_name)
        
        # Ouvrir une fenêtre pour choisir où enregistrer le fichier téléchargé
        save_path, _ = QFileDialog.getSaveFileName(self, "Choisir l'emplacement de sauvegarde", file_name)
        
        if save_path:
            # Télécharger le fichier
            self.send_file(file_path, save_path)

    def send_file(self, file_path, save_path):
        # Vérifier qu'un client est sélectionné
        selected_client = self.connection_tab.get_selected_client()
        if not selected_client:
            QMessageBox.warning(self, "Erreur", "Aucun client sélectionné.")
            return
            
        # Cette fonction enverra une commande au client pour télécharger un fichier
        try:
            # Demander au client d'envoyer le fichier
            selected_client.send_command(f"FILE_DOWNLOAD {file_path} {save_path}")
            QMessageBox.information(self, "Téléchargement", f"Fichier téléchargé avec succès.")
        except Exception as e:
            QMessageBox.warning(self, "Erreur", f"Impossible de télécharger le fichier: {e}")