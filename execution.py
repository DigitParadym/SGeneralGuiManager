#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de correction automatique pour le projet SGeneralGuiManager.
Version 100% compatible sans caractères spéciaux.
"""

import os
from pathlib import Path

def appliquer_corrections():
    """Applique les deux corrections principales au projet."""
    
    base_path = Path(__file__).parent
    print(f"Lancement des corrections depuis la racine : {base_path}\n")
    
    # --- Cible 1: Supprimer le fichier de débogage cassé ---
    
    fichier_a_supprimer = base_path / "debug_integration.py"
    print(f"Verification de '{fichier_a_supprimer.name}'...")
    
    if fichier_a_supprimer.exists():
        try:
            os.remove(fichier_a_supprimer)
            print(f"  -> [SUCCES] : Le fichier '{fichier_a_supprimer.name}' a ete supprime.")
        except OSError as e:
            print(f"  -> [ERREUR] : Impossible de supprimer le fichier. Raison : {e}")
    else:
        # MODIFICATION: Emoji et accent retirés
        print(f"  -> [INFO] : Le fichier '{fichier_a_supprimer.name}' n'existe deja plus.")

    # --- Cible 2: Ajouter l'import manquant dans json_ai_processor.py ---
    
    fichier_a_patcher = base_path / "composants_browser" / "json_ai_processor.py"
    ligne_a_ajouter = "from modificateur_interactif import OrchestrateurAST\n"
    print(f"\nVerification de '{fichier_a_patcher.relative_to(base_path)}'...")

    if fichier_a_patcher.exists():
        try:
            # On lit le contenu existant
            with open(fichier_a_patcher, 'r', encoding='utf-8') as f:
                lignes = f.readlines()
                
            # On vérifie si l'import n'est pas déjà présent
            if any("OrchestrateurAST" in ligne for ligne in lignes):
                # MODIFICATION: Accent retiré
                print(f"  -> [INFO] : L'import necessaire existe deja.")
            else:
                # On trouve où insérer la nouvelle ligne
                index_insertion = 0
                for i, ligne in enumerate(lignes):
                    if ligne.strip().startswith("from ") or ligne.strip().startswith("import "):
                        index_insertion = i + 1
                
                lignes.insert(index_insertion, ligne_a_ajouter)
                
                # On réécrit le fichier en entier avec la modification
                with open(fichier_a_patcher, 'w', encoding='utf-8') as f:
                    f.writelines(lignes)
                # MODIFICATION: Accent retiré
                print(f"  -> [SUCCES] : L'import de 'OrchestrateurAST' a ete ajoute.")

        except IOError as e:
            # MODIFICATION: Accent retiré
            print(f"  -> [ERREUR] : Impossible de lire ou d'ecrire dans le fichier. Raison : {e}")
    else:
        # MODIFICATION: Accent retiré
        print(f"  -> [ERREUR] : Le fichier '{fichier_a_patcher.name}' est introuvable.")

    # MODIFICATION: Accent retiré
    print("\nCorrections terminees !")

if __name__ == "__main__":
    appliquer_corrections()