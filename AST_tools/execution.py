#!/usr/bin/env python3
"""
Script d'intégration automatique de mypy dans AST_tools
Ajoute la fonctionnalité mypy à votre ruff_tab.py existant
SANS CASSER votre interface AST actuelle
"""

import os
import shutil
from datetime import datetime
from pathlib import Path


def add_mypy_to_ruff_tab():
    """Ajoute automatiquement mypy à ruff_tab.py existant."""

    file_path = Path("gui/tabs/ruff_tab.py")

    if not file_path.exists():
        print("[X] Erreur: gui/tabs/ruff_tab.py non trouvé!")
        print("    Assurez-vous d'être dans le dossier AST_tools")
        return False

    print("=" * 60)
    print("INTEGRATION AUTOMATIQUE DE MYPY DANS AST_TOOLS")
    print("=" * 60)

    # Faire un backup
    backup_path = file_path.with_suffix(
        f".py.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )
    shutil.copy2(file_path, backup_path)
    print(f"[OK] Backup créé: {backup_path}")

    # Lire le fichier
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    print(f"[i] Fichier chargé: {len(lines)} lignes")

    # ========================================
    # 1. AJOUTER LA CLASSE MypyWorker
    # ========================================
    print("\n[1] Ajout de la classe MypyWorker...")

    # Trouver où insérer MypyWorker (après RuffWorker)
    insert_position = None
    for i, line in enumerate(lines):
        if "class RuffIntegrationTab" in line:
            insert_position = i
            print(f"    Position trouvée: ligne {i}")
            break

    if insert_position:
        mypy_worker_code = '''

class MypyWorker(QThread):
    """Worker pour executer mypy en arriere-plan."""
    
    progress = Signal(str)
    finished = Signal(dict)
    file_progress = Signal(int, int)
    
    def __init__(self, files, strict_mode=False):
        super().__init__()
        self.files = files
        self.strict_mode = strict_mode
    
    def run(self):
        """Execute mypy sur les fichiers."""
        results = {"files": [], "total_errors": 0, "total_warnings": 0, "total_notes": 0}
        total_files = len(self.files)
        
        for index, file in enumerate(self.files, 1):
            self.file_progress.emit(index, total_files)
            self.progress.emit(
                f"Verification des types de {os.path.basename(file)}... ({index}/{total_files})"
            )
            
            try:
                cmd = ["mypy", "--no-error-summary", "--show-column-numbers", 
                       "--no-pretty", "--show-error-codes"]
                
                if self.strict_mode:
                    cmd.append("--strict")
                
                cmd.append(file)
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                file_result = {
                    "file": file,
                    "output": result.stdout,
                    "errors": result.stderr,
                    "return_code": result.returncode
                }
                
                lines = result.stdout.split('\\n')
                for line in lines:
                    if ": error:" in line:
                        results["total_errors"] += 1
                    elif ": warning:" in line:
                        results["total_warnings"] += 1
                    elif ": note:" in line:
                        results["total_notes"] += 1
                
                results["files"].append(file_result)
                
            except subprocess.TimeoutExpired:
                results["files"].append({"file": file, "error": "Timeout (>30s)"})
            except FileNotFoundError:
                self.progress.emit("[X] mypy non installe. Installez avec: pip install mypy")
                break
            except Exception as e:
                results["files"].append({"file": file, "error": str(e)})
        
        self.finished.emit(results)

'''
        lines.insert(insert_position, mypy_worker_code)
        print("    [OK] Classe MypyWorker ajoutée")

    # ========================================
    # 2. AJOUTER LES BOUTONS MYPY DANS setup_ui
    # ========================================
    print("\n[2] Ajout des boutons mypy dans l'interface...")

    # Trouver où ajouter les boutons (après format_btn)
    button_position = None
    for i, line in enumerate(lines):
        if "left_layout.addWidget(self.format_btn)" in line:
            button_position = i + 1
            print(f"    Position trouvée: ligne {i}")
            break

    if button_position:
        mypy_buttons_code = '''
        # === SECTION MYPY (AJOUT AUTOMATIQUE) ===
        mypy_label = QLabel("mypy (Verification de Types):")
        mypy_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        left_layout.addWidget(mypy_label)

        # Bouton Mypy normal
        self.mypy_btn = QPushButton("Verifier les Types (mypy)")
        self.mypy_btn.setToolTip("Lancer l'analyse des types avec mypy")
        self.mypy_btn.setStyleSheet("""
            QPushButton {
                padding: 8px;
                font-weight: bold;
                background-color: #0078d4;
                color: white;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
        """)
        left_layout.addWidget(self.mypy_btn)

        # Bouton Mypy strict
        self.mypy_strict_btn = QPushButton("Verifier (mode strict)")
        self.mypy_strict_btn.setToolTip("Lancer mypy en mode strict")
        self.mypy_strict_btn.setStyleSheet("""
            QPushButton {
                padding: 8px;
                font-weight: bold;
                background-color: #d9534f;
                color: white;
            }
            QPushButton:hover {
                background-color: #c9302c;
            }
        """)
        left_layout.addWidget(self.mypy_strict_btn)

'''
        lines.insert(button_position, mypy_buttons_code)
        print("    [OK] Boutons mypy ajoutés")

    # ========================================
    # 3. AJOUTER LES CONNEXIONS
    # ========================================
    print("\n[3] Ajout des connexions des boutons...")

    # Trouver où ajouter les connexions
    for i, line in enumerate(lines):
        if "self.cancel_btn.clicked.connect(self.cancel_operation)" in line:
            connection_position = i + 1
            connections_code = """        self.mypy_btn.clicked.connect(self.run_mypy)
        self.mypy_strict_btn.clicked.connect(self.run_mypy_strict)
"""
            lines.insert(connection_position, connections_code)
            print("    [OK] Connexions ajoutées")
            break

    # ========================================
    # 4. AJOUTER LES MÉTHODES run_mypy
    # ========================================
    print("\n[4] Ajout des méthodes run_mypy...")

    # Trouver la fin de la classe (avant le dernier def ou à la fin)
    method_position = None
    for i in range(len(lines) - 1, -1, -1):
        if lines[i].strip().startswith("def log_message"):
            for j in range(i + 1, len(lines)):
                if j == len(lines) - 1:
                    method_position = j + 1
                    break
                elif lines[j].strip() and not lines[j].startswith(" "):
                    method_position = j
                    break
            break

    if method_position is None:
        method_position = len(lines)

    mypy_methods_code = '''
    def run_mypy(self):
        """Lance l'analyse de types avec mypy."""
        files = self.get_selected_files()
        if not files:
            self.log_message("[!] Aucun fichier a analyser")
            return
        
        self.show_progress(True)
        self.log_message(f"Demarrage de l'analyse mypy sur {len(files)} fichier(s)...")
        self.log_message("[INFO] Mode: Verification de types standard")
        
        self.current_worker = MypyWorker(files, strict_mode=False)
        self.current_worker.progress.connect(self.log_message)
        self.current_worker.file_progress.connect(self.update_progress)
        self.current_worker.finished.connect(self.on_mypy_finished)
        self.current_worker.start()

    def run_mypy_strict(self):
        """Lance l'analyse de types avec mypy en mode strict."""
        files = self.get_selected_files()
        if not files:
            self.log_message("[!] Aucun fichier a analyser")
            return
        
        self.show_progress(True)
        self.log_message(f"Demarrage de l'analyse mypy STRICT sur {len(files)} fichier(s)...")
        self.log_message("[INFO] Mode: Verification de types STRICT")
        
        self.current_worker = MypyWorker(files, strict_mode=True)
        self.current_worker.progress.connect(self.log_message)
        self.current_worker.file_progress.connect(self.update_progress)
        self.current_worker.finished.connect(self.on_mypy_finished)
        self.current_worker.start()

    def on_mypy_finished(self, results):
        """Traite les resultats de l'analyse mypy."""
        self.show_progress(False)
        
        self.last_analysis_data["mypy_results"] = {
            "timestamp": datetime.now().isoformat(),
            "tool": "mypy",
            "total_errors": results["total_errors"],
            "total_warnings": results["total_warnings"],
            "total_notes": results["total_notes"],
            "files_analyzed": len(results["files"]),
            "results": results,
        }
        
        self.log_message(f"\\n{'=' * 50}")
        self.log_message(f"VERIFICATION DES TYPES TERMINEE (mypy)")
        self.log_message(f"Fichiers analyses: {len(results['files'])}")
        self.log_message(f"Erreurs de types: {results['total_errors']}")
        self.log_message(f"Avertissements: {results['total_warnings']}")
        self.log_message(f"Notes: {results['total_notes']}")
        
        for file_result in results['files']:
            if file_result.get('output'):
                self.log_message(f"\\n--- {os.path.basename(file_result['file'])} ---")
                for line in file_result['output'].split('\\n'):
                    if line.strip():
                        self.log_message(f"  {line}")
        
        self.stats_label.setText(
            f"Mypy: {results['total_errors']} erreur(s), "
            f"{results['total_warnings']} avertissement(s)"
        )
'''

    lines.insert(method_position, mypy_methods_code)
    print("    [OK] Méthodes ajoutées")

    # ========================================
    # 5. MODIFIER check_ruff_availability
    # ========================================
    print("\n[5] Mise à jour de la vérification des outils...")

    for i, line in enumerate(lines):
        if "def check_ruff_availability(self):" in line:
            # Renommer la méthode
            lines[i] = line.replace(
                "check_ruff_availability", "check_tools_availability"
            )

            # Trouver la fin de la méthode et ajouter la vérification mypy
            for j in range(i + 1, len(lines)):
                if "self.log_message" in lines[j] and "Ruff non installe" in lines[j]:
                    # Insérer après la vérification Ruff
                    for k in range(j + 1, len(lines)):
                        if lines[k].strip() and not lines[k].startswith(" "):
                            mypy_check = """
        # Verification mypy (AJOUT AUTOMATIQUE)
        try:
            result = subprocess.run(
                ["mypy", "--version"], capture_output=True, text=True
            )
            self.log_message(f"[OK] Mypy disponible: {result.stdout.strip()}")
            self.mypy_btn.setEnabled(True)
            self.mypy_strict_btn.setEnabled(True)
        except (FileNotFoundError, subprocess.SubprocessError):
            self.log_message("[X] Mypy non installe. Installez avec: pip install mypy")
            self.mypy_btn.setEnabled(False)
            self.mypy_strict_btn.setEnabled(False)

"""
                            lines.insert(k, mypy_check)
                            print("    [OK] Vérification mypy ajoutée")
                            break
                    break
            break

    # ========================================
    # 6. METTRE À JOUR update_file_count
    # ========================================
    print("\n[6] Mise à jour de update_file_count...")

    for i, line in enumerate(lines):
        if "def update_file_count(self):" in line:
            # Trouver où ajouter les lignes
            for j in range(i + 1, len(lines)):
                if "self.format_btn.setEnabled(has_files)" in lines[j]:
                    lines.insert(j + 1, "        self.mypy_btn.setEnabled(has_files)\n")
                    lines.insert(
                        j + 2, "        self.mypy_strict_btn.setEnabled(has_files)\n"
                    )
                    print("    [OK] update_file_count mise à jour")
                    break
            break

    # ========================================
    # 7. METTRE À JOUR show_progress
    # ========================================
    print("\n[7] Mise à jour de show_progress...")

    for i, line in enumerate(lines):
        if "def show_progress(self, show):" in line:
            for j in range(i + 1, len(lines)):
                if "self.format_btn.setEnabled(not show)" in lines[j]:
                    lines.insert(j + 1, "        self.mypy_btn.setEnabled(not show)\n")
                    lines.insert(
                        j + 2, "        self.mypy_strict_btn.setEnabled(not show)\n"
                    )
                    print("    [OK] show_progress mise à jour")
                    break
            break

    # ========================================
    # 8. CORRIGER L'APPEL À check_tools_availability
    # ========================================
    print("\n[8] Correction de l'appel initial...")

    for i, line in enumerate(lines):
        if "self.check_ruff_availability()" in line:
            lines[i] = line.replace(
                "check_ruff_availability", "check_tools_availability"
            )
            print("    [OK] Appel corrigé")
            break

    # ========================================
    # SAUVEGARDER LE FICHIER
    # ========================================
    print("\n[9] Sauvegarde du fichier modifié...")

    with open(file_path, "w", encoding="utf-8") as f:
        f.writelines(lines)

    print(f"    [OK] Fichier modifié sauvegardé")

    return True


def verify_integration():
    """Vérifie que l'intégration a réussi."""

    print("\n" + "=" * 60)
    print("VERIFICATION DE L'INTEGRATION")
    print("=" * 60)

    file_path = Path("gui/tabs/ruff_tab.py")

    if not file_path.exists():
        print("[X] Fichier non trouvé")
        return False

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    checks = [
        ("Classe MypyWorker", "class MypyWorker"),
        ("Bouton mypy", "self.mypy_btn"),
        ("Bouton mypy strict", "self.mypy_strict_btn"),
        ("Méthode run_mypy", "def run_mypy(self):"),
        ("Méthode on_mypy_finished", "def on_mypy_finished"),
        ("Vérification mypy", "mypy --version"),
    ]

    all_ok = True
    for check_name, pattern in checks:
        if pattern in content:
            print(f"[OK] {check_name}")
        else:
            print(f"[X] {check_name} - NON TROUVÉ")
            all_ok = False

    return all_ok


def install_mypy():
    """Propose d'installer mypy si nécessaire."""

    print("\n" + "=" * 60)
    print("INSTALLATION DE MYPY")
    print("=" * 60)

    import subprocess

    try:
        result = subprocess.run(["mypy", "--version"], capture_output=True, text=True)
        print(f"[OK] mypy déjà installé: {result.stdout.strip()}")
        return True
    except FileNotFoundError:
        print("[!] mypy n'est pas installé")

        response = (
            input("\nVoulez-vous installer mypy maintenant? (yes/no): ").strip().lower()
        )

        if response in ["yes", "y", "oui", "o"]:
            print("\nInstallation de mypy...")
            try:
                subprocess.run(["pip", "install", "mypy"], check=True)
                print("[OK] mypy installé avec succès!")
                return True
            except subprocess.CalledProcessError:
                print("[X] Erreur lors de l'installation")
                print("    Installez manuellement avec: pip install mypy")
                return False
        else:
            print("\n[INFO] Installez mypy plus tard avec: pip install mypy")
            return False


def main():
    """Fonction principale."""

    print("INTEGRATION DE MYPY DANS AST_TOOLS")
    print("=" * 60)
    print("Ce script va ajouter la fonctionnalité mypy à votre")
    print("interface RuffIntegrationTab existante.")
    print("\nCela inclut:")
    print("- Classe MypyWorker pour l'exécution en arrière-plan")
    print("- Deux boutons: vérification normale et stricte")
    print("- Méthodes de traitement des résultats")
    print("- Intégration complète avec votre interface AST")
    print("=" * 60)

    # Vérifier qu'on est dans le bon dossier
    if not Path("gui/tabs/ruff_tab.py").exists():
        print("\n[X] ERREUR: gui/tabs/ruff_tab.py non trouvé!")
        print("    Assurez-vous d'exécuter ce script depuis le dossier AST_tools")

        # Chercher AST_tools
        if Path("AST_tools/gui/tabs/ruff_tab.py").exists():
            print("\n[!] Le dossier AST_tools a été trouvé.")
            print("    Changez de dossier avec: cd AST_tools")
            print("    Puis relancez ce script.")

        return

    response = (
        input("\nVoulez-vous procéder à l'intégration? (yes/no): ").strip().lower()
    )

    if response not in ["yes", "y", "oui", "o"]:
        print("\n[ANNULÉ] Aucune modification effectuée")
        return

    # Faire l'intégration
    if add_mypy_to_ruff_tab():
        print("\n" + "=" * 60)
        print("[OK] INTEGRATION TERMINÉE AVEC SUCCÈS!")
        print("=" * 60)

        # Vérifier
        if verify_integration():
            print("\n[OK] Tous les éléments ont été correctement ajoutés!")

            # Proposer d'installer mypy
            install_mypy()

            print("\nPROCHAINES ÉTAPES:")
            print("1. Lancer AST_tools avec: python AST.py")
            print("2. Aller dans l'onglet 'Analyse & Formatage (Ruff)'")
            print("3. Les boutons mypy seront visibles!")
            print("\nNOUVELLES FONCTIONNALITÉS:")
            print("- Bouton 'Vérifier les Types (mypy)' - analyse standard")
            print("- Bouton 'Vérifier (mode strict)' - analyse stricte")
            print("- Résultats intégrés dans la même interface")
        else:
            print("\n[!] Certains éléments semblent manquer")
            print("    Vérifiez manuellement le fichier")
    else:
        print("\n[X] Erreur lors de l'intégration")
        print("    Un backup a été créé, vous pouvez le restaurer si nécessaire")


if __name__ == "__main__":
    main()
