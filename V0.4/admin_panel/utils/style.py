from PyQt5.QtGui import QColor, QFont, QPalette, QBrush, QLinearGradient, QIcon, QPixmap, QPainter

def apply_style(app):
    """
    Applique un style unifié "hacker professionnel" à l'application avec dominante bleue
    """
    # Palette de couleurs principale (accentuée sur le bleu)
    colors = {
        "background": "#0a0e17",          # Fond principal très sombre avec teinte bleue
        "secondary_bg": "#121a28",         # Fond secondaire plus bleu
        "tertiary_bg": "#1a2538",          # Fond tertiaire (pour les widgets)
        "accent": "#2b84ea",               # Couleur d'accent principale (bleu cybersécurité)
        "accent_hover": "#3b94fa",         # Couleur d'accent au survol
        "accent_pressed": "#1a64c0",       # Couleur d'accent quand pressé
        "secondary_accent": "#00b8d4",     # Accent secondaire (bleu clair)
        "warning": "#e6c800",              # Jaune pour les alertes
        "danger": "#ff3860",               # Rouge pour les erreurs/dangers
        "success": "#23d18b",              # Vert pour les succès
        "text_primary": "#f0f6fc",         # Texte principal clair
        "text_secondary": "#a9b7c6",       # Texte secondaire légèrement grisé
        "border": "#2a3652",               # Couleur des bordures (plus bleue)
        "grid_line": "#1c2840",            # Lignes de grille
        "selection": "#214283",            # Couleur de sélection
        "tab_active": "#1c4174",           # Tab active
        "tab_hover": "#183456",            # Tab hover
        "tab_inactive": "#152638",         # Tab inactive
        "input_bg": "#060b16",             # Background pour les zones de texte
        "scrollbar": "#2a3652",            # Couleur des scrollbars
        "terminal_blue": "#4fc3f7",        # Bleu terminal
    }
    
    # Polices
    fonts = {
        "main": QFont("Segoe UI", 9),
        "monospace": QFont("Consolas", 9),
        "bold": QFont("Segoe UI", 9, QFont.Bold),
        "title": QFont("Segoe UI", 10, QFont.Bold),
        "large": QFont("Segoe UI", 11, QFont.Bold),
    }
    
    # Appliquer les polices par défaut
    app.setFont(fonts["main"])
    
    # Style général de l'application
    app.setStyleSheet(f"""
        /* Styles généraux */
        QMainWindow, QDialog, QWidget {{
            background-color: {colors["background"]};
            color: {colors["text_primary"]};
        }}
        
        /* Onglets */
        QTabWidget::pane {{
            border: 1px solid {colors["border"]};
            background-color: {colors["secondary_bg"]};
            border-radius: 4px;
        }}
        
        QTabBar::tab {{
            background-color: {colors["tab_inactive"]};
            color: {colors["text_secondary"]};
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
            padding: 8px 16px;
            margin-right: 2px;
            margin-bottom: -2px;
            border-bottom: 2px solid transparent;
        }}
        
        QTabBar::tab:selected {{
            background-color: {colors["tab_active"]};
            color: {colors["text_primary"]};
            border-bottom: 2px solid {colors["accent"]};
        }}
        
        QTabBar::tab:hover:!selected {{
            background-color: {colors["tab_hover"]};
            color: {colors["text_primary"]};
        }}
        
        /* Boutons */
        QPushButton {{
            background-color: {colors["tertiary_bg"]};
            color: {colors["text_primary"]};
            border: 1px solid {colors["border"]};
            border-radius: 4px;
            padding: 6px 16px;
            font-weight: bold;
            outline: none;
        }}
        
        QPushButton:hover {{
            background-color: {colors["secondary_bg"]};
            border: 1px solid {colors["accent"]};
        }}
        
        QPushButton:pressed {{
            background-color: {colors["border"]};
        }}
        
        /* Boutons d'action primaire */
        QPushButton#capture_button, QPushButton#connect_button, QPushButton#execute_button, QPushButton#track_button {{
            background-color: {colors["accent"]};
            color: white;
            border: none;
        }}
        
        QPushButton#capture_button:hover, QPushButton#connect_button:hover, QPushButton#execute_button:hover, QPushButton#track_button:hover {{
            background-color: {colors["accent_hover"]};
        }}
        
        QPushButton#capture_button:pressed, QPushButton#connect_button:pressed, QPushButton#execute_button:pressed, QPushButton#track_button:pressed {{
            background-color: {colors["accent_pressed"]};
        }}
        
        /* Boutons secondaires */
        QPushButton#refresh_button {{
            background-color: {colors["tertiary_bg"]};
            color: {colors["text_primary"]};
            border: 1px solid {colors["border"]};
        }}
        
        QPushButton#refresh_button:hover {{
            border-color: {colors["secondary_accent"]};
            color: {colors["secondary_accent"]};
        }}
        
        /* Zone de texte */
        QTextEdit, QLineEdit {{
            background-color: {colors["input_bg"]};
            color: {colors["text_primary"]};
            border: 1px solid {colors["border"]};
            border-radius: 4px;
            padding: 6px;
            selection-background-color: {colors["selection"]};
        }}
        
        QTextEdit:focus, QLineEdit:focus {{
            border: 1px solid {colors["accent"]};
        }}
        
        /* Terminal */
        #output_display {{
            background-color: #000;
            color: {colors["terminal_blue"]};
            font-family: "Consolas", monospace;
            border: 1px solid #1a1a1a;
            border-radius: 4px;
        }}
        
        /* Combobox */
        QComboBox {{
            background-color: {colors["tertiary_bg"]};
            color: {colors["text_primary"]};
            padding: 6px;
            border-radius: 4px;
            border: 1px solid {colors["border"]};
            min-width: 6em;
        }}
        
        QComboBox::drop-down {{
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 20px;
            border-left: 1px solid {colors["border"]};
            border-top-right-radius: 3px;
            border-bottom-right-radius: 3px;
        }}
        
        QComboBox:on {{
            padding-top: 3px;
            padding-left: 4px;
        }}
        
        QComboBox QAbstractItemView {{
            background-color: {colors["tertiary_bg"]};
            color: {colors["text_primary"]};
            border: 1px solid {colors["border"]};
            border-radius: 0px;
            selection-background-color: {colors["selection"]};
            outline: 0px;
        }}
        
        /* Scrollbar */
        QScrollBar:vertical {{
            background: {colors["secondary_bg"]};
            width: 12px;
            margin: 0px;
            border-radius: 6px;
        }}
        
        QScrollBar::handle:vertical {{
            background: {colors["scrollbar"]};
            min-height: 20px;
            border-radius: 5px;
            margin: 2px;
        }}
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        
        QScrollBar:horizontal {{
            background: {colors["secondary_bg"]};
            height: 12px;
            border-radius: 6px;
        }}
        
        QScrollBar::handle:horizontal {{
            background: {colors["scrollbar"]};
            min-width: 20px;
            border-radius: 5px;
            margin: 2px;
        }}
        
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            width: 0px;
        }}
        
        /* Labels */
        QLabel {{
            color: {colors["text_primary"]};
        }}
        
        QLabel#status_label {{
            font-weight: bold;
            color: {colors["text_secondary"]};
        }}
        
        /* Status indicators */
        QLabel#status_indicator {{
            min-width: 16px;
            min-height: 16px;
            max-width: 16px;
            max-height: 16px;
            border-radius: 8px;
        }}
        
        /* Groupbox */
        QGroupBox {{
            background-color: {colors["secondary_bg"]};
            border: 1px solid {colors["border"]};
            border-radius: 6px;
            margin-top: 14px;
            padding-top: 8px;
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 5px;
            background-color: transparent;
            color: {colors["accent"]};
            font-weight: bold;
        }}
        
        /* Frames */
        QFrame {{
            border: none;
        }}
        
        QFrame#card {{
            background-color: {colors["secondary_bg"]};
            border: 1px solid {colors["border"]};
            border-radius: 6px;
            padding: 8px;  
        }}
        
        QFrame#line {{
            background-color: {colors["border"]};
            max-height: 1px;
        }}
        
        /* Séparateur pour terminal */
        QFrame#command_separator {{
            color: {colors["border"]};
            background-color: {colors["border"]};
        }}
        
        /* Section d'en-tête pour les onglets */
        QFrame#header {{
            background-color: {colors["tertiary_bg"]};
            border-radius: 6px;
            padding: 8px;
        }}
        
        /* Conteneur de screenshot */
        QFrame {{
            border-radius: 4px;
        }}
        
        /* Statut de connexion */
        QLabel#status_label[connected="true"] {{
            color: {colors["success"]};
        }}
        
        QLabel#status_label[connected="false"] {{
            color: {colors["danger"]};
        }}
        
        /* Style pour les screenshots */
        QFrame#screenshot_item {{
            background-color: {colors["secondary_bg"]};
            border: 1px solid {colors["border"]};
            border-radius: 6px;
            padding: 8px;
        }}
        
        QFrame#screenshot_item:hover {{
            border: 1px solid {colors["accent"]};
        }}
        
        /* Style pour historique fenêtres */
        QFrame#history_item {{
            background-color: {colors["tertiary_bg"]};
            border-left: 3px solid {colors["accent"]};
            padding: 4px;
            margin-bottom: 2px;
        }}
        
        /* Style spécial pour le terminal */
        #command_input {{
            font-family: Consolas, monospace;
            background-color: #000;
            color: #fff;
            border: 1px solid #333;
        }}
    """)
    
    return True