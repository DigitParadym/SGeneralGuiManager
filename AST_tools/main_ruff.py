#!/usr/bin/env python3
"""
Point d'entree principal pour AST_tools avec Ruff
Lance depuis AST_tools: python main_ruff.py
"""

import sys
from pathlib import Path

# Ajouter le repertoire actuel au path
sys.path.insert(0, str(Path(__file__).parent))


def main():
    """Lance l'application AST_tools avec Ruff"""
    try:
        from PyQt5.QtWidgets import QApplication

        from gui.main_window import MainWindow

        app = QApplication(sys.argv)
        app.setApplicationName("AST_tools")

        window = MainWindow()
        window.show()

        sys.exit(app.exec_())

    except ImportError as e:
        print(f"Erreur d'import: {e}")
        print("Installez les dependances: pip install PyQt5 ruff")
        sys.exit(1)
    except Exception as e:
        print(f"Erreur: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
