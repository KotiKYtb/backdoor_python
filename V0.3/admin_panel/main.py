import sys
from PyQt5.QtWidgets import QApplication
from command_center import CommandCenter

def main():
    app = QApplication(sys.argv)
    window = CommandCenter()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()