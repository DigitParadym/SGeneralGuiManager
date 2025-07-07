from PyQt5.QtWidgets import QApplication
from connectorpro_gui import ConnectorProGUI  # Import aligned with root name

def main():
    app = QApplication([])
    window = ConnectorProGUI()  # No config parameter is passed here
    window.show()
    app.exec_()

if __name__ == "__main__":
    main()
