#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lanceur independant pour Interface AST
Genere automatiquement par le diagnostic
"""

import os
import sys
from pathlib import Path

def launch_ast_interface():
    """Lance l'interface AST avec la bonne configuration."""
    try:
        # Repertoire de ce script
        script_dir = Path(__file__).parent
        
        # Chemin vers l'interface AST
        ast_dir = script_dir / "AST_tools"
        gui_dir = ast_dir / "composants_browser"
        gui_file = gui_dir / "interface_gui_principale.py"
        
        print("Lancement de l'interface AST...")
        print("Repertoire AST: " + str(ast_dir))
        print("Fichier GUI: " + str(gui_file))
        
        # Verifier que le fichier existe
        if not gui_file.exists():
            print("ERREUR: " + str(gui_file) + " n'existe pas")
            return False
        
        # Changer vers le bon repertoire
        original_cwd = os.getcwd()
        os.chdir(gui_dir)
        
        # Ajouter les chemins necessaires
        sys.path.insert(0, str(ast_dir))
        sys.path.insert(0, str(gui_dir))
        
        # Importer et lancer
        import interface_gui_principale
        
        print("Interface AST lancee avec succes!")
        interface_gui_principale.main()
        
        # Revenir au repertoire original
        os.chdir(original_cwd)
        return True
        
    except Exception as e:
        print("ERREUR lancement: " + str(e))
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    launch_ast_interface()
