#!/usr/bin/env python3
"""Lanceur garanti pour AST_Tools"""

import os
import sys

# Ajouter le répertoire au path
if os.path.dirname(__file__) not in sys.path:
    sys.path.insert(0, os.path.dirname(__file__))


def main():
    from PySide6.QtWidgets import QApplication

    # Importer APRÈS QApplication
    app = QApplication(sys.argv)

    # Désactiver temporairement les logs
    import logging

    logging.disable(logging.CRITICAL)

    # Importer la fenêtre
    from main import ASTMainWindow

    # Réactiver les logs
    logging.disable(logging.NOTSET)

    # Créer et afficher la fenêtre
    window = ASTMainWindow()
    window.show()

    print("=" * 60)
    print("FENÊTRE OUVERTE - Fermez-la pour quitter")
    print("=" * 60)

    # IMPORTANT: Boucle d'événements
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
