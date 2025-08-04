import sys
from pathlib import Path

from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QVBoxLayout, QWidget

sys.path.append(str(Path(__file__).parent.parent))

try:
    from gui.tabs.ruff_tab import RuffIntegrationTab
except ImportError:
    print("Erreur: Impossible d'importer RuffIntegrationTab")
    RuffIntegrationTab = None


class MainWindow(QMainWindow):
    """Fenetre principale avec onglet Ruff"""

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """Initialise l'interface"""
        self.setWindowTitle("AST_tools - Transformation et Analyse avec Ruff")
        self.setGeometry(100, 100, 1200, 800)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Onglets
        self.tab_widget = QTabWidget()

        # Onglet Ruff
        if RuffIntegrationTab:
            self.ruff_tab = RuffIntegrationTab()
            self.tab_widget.addTab(self.ruff_tab, "Analyse & Formatage (Ruff)")

        layout.addWidget(self.tab_widget)


def main():
    """Lance l'application"""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
