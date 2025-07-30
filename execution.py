#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AST Tools - Point d'entrée principal
Interface pour la plateforme de refactorisation dirigée par IA
"""

import sys
import os
from pathlib import Path

def setup_environment():
    """Configure l'environnement Python pour le projet."""
    # Ajouter le répertoire courant au path
    current_dir = Path(__file__).parent
    if str(current_dir) not in sys.path:
        sys.path.insert(0, str(current_dir))
    
    print(f"Répertoire de travail: {current_dir}")
    return current_dir

def check_dependencies():
    """Vérifie les dépendances requises."""
    dependencies = []
    
    # Verification des modules systeme
    try:
        import ast
        dependencies.append(("ast", "OK"))
    except ImportError:
        dependencies.append(("ast", "ERREUR"))
    
    try:
        import json
        dependencies.append(("json", "OK"))
    except ImportError:
        dependencies.append(("json", "ERREUR"))
    
    # Verification des modules du projet
    try:
        from modificateur_interactif import OrchestrateurAST
        dependencies.append(("OrchestrateurAST", "OK"))
    except ImportError as e:
        dependencies.append(("OrchestrateurAST", f"ERREUR ({e})"))
    
    try:
        from core.transformation_loader import TransformationLoader
        dependencies.append(("TransformationLoader", "OK"))
    except ImportError as e:
        dependencies.append(("TransformationLoader", f"ERREUR ({e})"))
    
    return dependencies

def show_project_info():
    """Affiche les informations du projet."""
    print("=" * 60)
    print("AST TOOLS - Plateforme de Refactorisation Python")
    print("=" * 60)
    print("Version: 2.4.0")
    print("Description: Outils de transformation de code Python par AST")
    print("=" * 60)

def show_menu():
    """Affiche le menu principal."""
    print("\nOptions disponibles:")
    print("1. Lancer l'interface graphique")
    print("2. Mode interactif (terminal)")
    print("3. Test rapide du système")
    print("4. Diagnostic complet")
    print("5. Créer un fichier d'exemple")
    print("0. Quitter")
    print("-" * 40)

def launch_gui():
    """Lance l'interface graphique."""
    try:
        # Vérifier si PySide6 est disponible
        try:
            from PySide6.QtWidgets import QApplication
            use_pyside = True
        except ImportError:
            use_pyside = False
            print("PySide6 non disponible, utilisation de l'interface Tkinter...")
        
        if use_pyside:
            print("Lancement de l'interface PySide6...")
            # Code pour PySide6 si disponible
            print("Interface PySide6 non encore implémentée.")
            print("Utilisation de l'interface Tkinter à la place...")
        
        # Interface Tkinter de secours
        if os.path.exists("composants_browser/interface_gui_principale.py"):
            print("Lancement de l'interface Tkinter...")
            import subprocess
            subprocess.run([sys.executable, "composants_browser/interface_gui_principale.py"])
        elif os.path.exists("lancer_interface.py"):
            print("Lancement via lancer_interface.py...")
            import subprocess
            subprocess.run([sys.executable, "lancer_interface.py"])
        else:
            print("Aucune interface graphique trouvée!")
            return False
        
        return True
    except Exception as e:
        print(f"Erreur lancement interface: {e}")
        return False

def launch_interactive():
    """Lance le mode interactif."""
    try:
        from modificateur_interactif import OrchestrateurAST
        print("Initialisation du mode interactif...")
        orchestrateur = OrchestrateurAST()
        
        print("Mode interactif disponible:")
        print("- orchestrateur.lister_transformations_modulaires()")
        print("- orchestrateur.executer_plan(plan_path, files)")
        
        # Simple REPL pour tester
        print("\nEntrez 'quit' pour sortir")
        while True:
            try:
                cmd = input(">>> ")
                if cmd.lower() in ['quit', 'exit', 'q']:
                    break
                elif cmd == 'help':
                    print("Commandes disponibles:")
                    print("- list : Lister les transformations")
                    print("- quit : Quitter")
                elif cmd == 'list':
                    transformations = orchestrateur.lister_transformations_modulaires()
                    print(f"Transformations disponibles: {len(transformations)}")
                    for t in transformations:
                        print(f"  - {t['display_name']} v{t['version']}")
                else:
                    exec(cmd)
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Erreur: {e}")
        
        return True
    except Exception as e:
        print(f"Erreur mode interactif: {e}")
        return False

def run_quick_test():
    """Lance un test rapide du système."""
    try:
        if os.path.exists("diagnostic.py"):
            print("Lancement du diagnostic rapide...")
            import subprocess
            subprocess.run([sys.executable, "diagnostic.py"])
        else:
            print("Test rapide manuel...")
            deps = check_dependencies()
            print("\nÉtat des dépendances:")
            for name, status in deps:
                print(f"  {name}: {status}")
        return True
    except Exception as e:
        print(f"Erreur test rapide: {e}")
        return False

def run_full_diagnostic():
    """Lance un diagnostic complet."""
    try:
        print("=== DIAGNOSTIC COMPLET ===")
        
        # 1. Vérification de l'environnement
        print("\n1. Environnement:")
        print(f"   Python: {sys.version}")
        print(f"   Répertoire: {Path.cwd()}")
        
        # 2. Vérification des fichiers
        print("\n2. Fichiers principaux:")
        files_to_check = [
            "modificateur_interactif.py",
            "core/transformation_loader.py",
            "core/base_transformer.py",
            "composants_browser/interface_gui_principale.py"
        ]
        
        for file_path in files_to_check:
            if os.path.exists(file_path):
                print(f"   [OK] {file_path}")
            else:
                print(f"   [MANQUANT] {file_path}")
        
        # 3. Test des dépendances
        print("\n3. Dépendances:")
        deps = check_dependencies()
        for name, status in deps:
            print(f"   {name}: {status}")
        
        # 4. Test du systeme modulaire
        print("\n4. Systeme modulaire:")
        try:
            from modificateur_interactif import OrchestrateurAST
            orchestrateur = OrchestrateurAST()
            transformations = orchestrateur.lister_transformations_modulaires()
            print(f"   [OK] {len(transformations)} transformation(s) detectee(s)")
        except Exception as e:
            print(f"   [ERREUR] {e}")
        
        return True
    except Exception as e:
        print(f"Erreur diagnostic: {e}")
        return False

def create_example_file():
    """Crée un fichier d'exemple pour tester."""
    try:
        # Créer le dossier tests s'il n'existe pas
        os.makedirs("tests", exist_ok=True)
        
        example_code = '''#!/usr/bin/env python3
"""
Fichier d'exemple pour tester les transformations AST
"""

def example_function():
    """Fonction d'exemple avec des prints à transformer."""
    print("Début de la fonction")
    
    for i in range(3):
        print(f"Itération {i}")
    
    print("Fin de la fonction")
    return True

class ExampleClass:
    """Classe d'exemple."""
    
    def __init__(self, name):
        self.name = name
        print(f"Création de {name}")
    
    def display_info(self):
        print(f"Nom: {self.name}")

if __name__ == "__main__":
    print("Lancement du fichier d'exemple")
    obj = ExampleClass("test")
    obj.display_info()
    example_function()
    print("Fin du fichier d'exemple")
'''
        
        file_path = "tests/example_file.py"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(example_code)
        
        print(f"[OK] Fichier d'exemple cree: {file_path}")
        return True
    except Exception as e:
        print(f"Erreur creation fichier: {e}")
        return False

def main():
    """Point d'entrée principal."""
    # Configuration de l'environnement
    current_dir = setup_environment()
    
    # Affichage des informations
    show_project_info()
    
    # Verification rapide
    print("Verification des dependances...")
    deps = check_dependencies()
    critical_missing = [name for name, status in deps if "ERREUR" in status and name in ["OrchestrateurAST"]]
    
    if critical_missing:
        print(f"ATTENTION: Modules critiques manquants: {', '.join(critical_missing)}")
        print("Utilisation du mode diagnostic uniquement.")
    
    # Boucle principale
    while True:
        show_menu()
        try:
            choice = input("Votre choix (0-5): ").strip()
            
            if choice == "0":
                print("Au revoir!")
                break
            elif choice == "1":
                launch_gui()
            elif choice == "2":
                if not critical_missing:
                    launch_interactive()
                else:
                    print("Mode interactif non disponible (modules manquants)")
            elif choice == "3":
                run_quick_test()
            elif choice == "4":
                run_full_diagnostic()
            elif choice == "5":
                create_example_file()
            else:
                print("Choix invalide")
            
            input("\nAppuyez sur Entrée pour continuer...")
            
        except KeyboardInterrupt:
            print("\nInterruption par l'utilisateur")
            break
        except Exception as e:
            print(f"Erreur: {e}")

if __name__ == "__main__":
    main()