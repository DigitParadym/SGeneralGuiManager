
from PyQt5.QtWidgets import QApplication, QMainWindow
from connectorpro_gui import ConnectorProGUI

def main():
    app = QApplication([])
    window = ConnectorProGUI()
    window.show()
    app.exec_()

if __name__ == "__main__":
    main()
