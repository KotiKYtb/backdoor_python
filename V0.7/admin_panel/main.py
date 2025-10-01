# Dans utils/main.py
from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow
from utils.style import apply_style
import sys

def main():
    app = QApplication(sys.argv)
    
    # Appliquer le style unifié
    apply_style(app)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()