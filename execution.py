#!/usr/bin/env python3
"""
Script de diagnostic pour le bouton "Copy to clipboard" dans ruff_tab.py
Verifie pourquoi le bouton n'est pas visible
"""

import os
import re
from pathlib import Path


def check_file_exists():
    """Verifie que le fichier ruff_tab.py existe."""
    file_path = Path("gui/tabs/ruff_tab.py")
    
    if not file_path.exists():
        print("[X] ERREUR: Le fichier gui/tabs/ruff_tab.py n'existe pas!")
        return None
    
    print(f"[OK] Fichier trouve: {file_path}")
    print(f"    Taille: {file_path.stat().st_size} bytes")
    print(f"    Derniere modification: {file_path.stat().st_mtime}")
    
    return file_path


def check_copy_button_code(file_path):
    """Verifie si le code du bouton Copy existe dans le fichier."""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("\n" + "=" * 60)
    print("DIAGNOSTIC DU BOUTON COPY TO CLIPBOARD")
    print("=" * 60)
    
    # === VERIFICATIONS ===
    checks = {
        "1. Declaration du bouton": {
            "pattern": r'self\.copy_btn\s*=\s*QPushButton\("Copy to clipboard"\)',
            "found": False,
            "line": None
        },
        "2. Ajout au layout": {
            "pattern": r'right_layout\.addLayout\(copy_layout\)|right_layout\.addWidget\(self\.copy_btn\)',
            "found": False,
            "line": None
        },
        "3. Connexion du signal": {
            "pattern": r'self\.copy_btn\.clicked\.connect\(self\.copy_to_clipboard\)',
            "found": False,
            "line": None
        },
        "4. Methode copy_to_clipboard": {
            "pattern": r'def copy_to_clipboard\(self\):',
            "found": False,
            "line": None
        },
        "5. Label de statut": {
            "pattern": r'self\.copy_status_label\s*=\s*QLabel',
            "found": False,
            "line": None
        },
        "6. Copy layout": {
            "pattern": r'copy_layout\s*=\s*QHBoxLayout\(\)',
            "found": False,
            "line": None
        }
    }
    
    lines = content.split('\n')
    
    # Rechercher chaque pattern
    for check_name, check_info in checks.items():
        for i, line in enumerate(lines, 1):
            if re.search(check_info["pattern"], line):
                check_info["found"] = True
                check_info["line"] = i
                break
    
    # === RAPPORT ===
    print("\nRESULTATS DES VERIFICATIONS:")
    print("-" * 40)
    
    all_found = True
    for check_name, check_info in checks.items():
        if check_info["found"]:
            print(f"[OK] {check_name}")
            print(f"     Trouve ligne {check_info['line']}")
        else:
            print(f"[X] {check_name}")
            print(f"    NON TROUVE!")
            all_found = False
    
    # === ANALYSE DETAILLEE ===
    print("\n" + "=" * 60)
    print("ANALYSE DETAILLEE")
    print("=" * 60)
    
    # Chercher le panneau droit
    right_panel_start = None
    for i, line in enumerate(lines, 1):
        if "PANNEAU DROIT - RESULTATS" in line:
            right_panel_start = i
            print(f"[i] Panneau droit commence ligne {i}")
            break
    
    if right_panel_start:
        # Analyser les 50 lignes suivantes
        print("\n[i] Structure du panneau droit (20 lignes apres le debut):")
        print("-" * 40)
        for i in range(right_panel_start, min(right_panel_start + 20, len(lines))):
            line = lines[i-1]
            if any(keyword in line for keyword in ["QGroupBox", "QTextEdit", "QPushButton", "QLabel", "addWidget", "addLayout"]):
                print(f"    L{i}: {line.strip()[:80]}")
    
    # === DIAGNOSTIC FINAL ===
    print("\n" + "=" * 60)
    print("DIAGNOSTIC FINAL")
    print("=" * 60)
    
    if all_found:
        print("[OK] Tous les elements du bouton Copy sont presents dans le code!")
        print("\nPROBLEMES POSSIBLES:")
        print("1. Le fichier n'a pas ete sauvegarde")
        print("2. L'application n'a pas ete relancee")
        print("3. Un autre fichier ruff_tab.py est charge")
        print("\nSOLUTIONS:")
        print("1. Sauvegarder le fichier")
        print("2. Fermer et relancer: python run.py")
        print("3. Verifier qu'il n'y a qu'un seul ruff_tab.py")
    else:
        print("[X] Le code du bouton Copy n'est PAS complet!")
        print("\nSOLUTION: Le bouton doit etre ajoute au fichier.")
        print("Je vais generer le code a ajouter...")
        
        generate_missing_code(checks)
    
    return all_found, checks


def generate_missing_code(checks):
    """Genere le code manquant pour le bouton Copy."""
    
    print("\n" + "=" * 60)
    print("CODE A AJOUTER DANS ruff_tab.py")
    print("=" * 60)
    
    if not checks["6. Copy layout"]["found"]:
        print("\n# 1. AJOUTER APRES self.output_text (dans le panneau droit):")
        print("-" * 40)
        print("""
        # NOUVEAU: Bouton Copy to clipboard
        copy_layout = QHBoxLayout()
        self.copy_btn = QPushButton("Copy to clipboard")
        self.copy_btn.setToolTip("Copier tous les resultats dans le presse-papiers")
        self.copy_btn.setStyleSheet('''
            QPushButton {
                background-color: #337ab7;
                color: white;
                font-weight: bold;
                padding: 6px;
            }
            QPushButton:hover {
                background-color: #286090;
            }
        ''')
        self.copy_status_label = QLabel("")
        self.copy_status_label.setStyleSheet("color: green; font-style: italic;")
        copy_layout.addWidget(self.copy_btn)
        copy_layout.addWidget(self.copy_status_label)
        copy_layout.addStretch()
        right_layout.addLayout(copy_layout)
""")
    
    if not checks["3. Connexion du signal"]["found"]:
        print("\n# 2. AJOUTER DANS LES CONNEXIONS (chercher '=== CONNEXIONS ==='):")
        print("-" * 40)
        print("""
        self.copy_btn.clicked.connect(self.copy_to_clipboard)
""")
    
    if not checks["4. Methode copy_to_clipboard"]["found"]:
        print("\n# 3. AJOUTER LA METHODE (a la fin de la classe):")
        print("-" * 40)
        print("""
    def copy_to_clipboard(self):
        '''Copie le contenu des resultats dans le presse-papiers.'''
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import QTimer
        
        text_content = self.output_text.toPlainText()
        
        if not text_content:
            self.copy_status_label.setText("Rien a copier")
            QTimer.singleShot(2000, lambda: self.copy_status_label.setText(""))
            return
        
        header = "=== RESULTATS ANALYSE RUFF ===\\n"
        header += f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\\n"
        header += f"Nombre de fichiers: {self.files_list.count()}\\n"
        header += "=" * 50 + "\\n\\n"
        
        full_content = header + text_content
        
        clipboard = QApplication.clipboard()
        clipboard.setText(full_content)
        
        self.copy_status_label.setText("[OK] Copie dans le presse-papiers!")
        self.log_message("[COPIE] Resultats copies dans le presse-papiers")
        
        QTimer.singleShot(3000, lambda: self.copy_status_label.setText(""))
""")


def check_multiple_files():
    """Verifie s'il y a plusieurs fichiers ruff_tab.py."""
    
    print("\n" + "=" * 60)
    print("RECHERCHE DE FICHIERS DUPLIQUES")
    print("=" * 60)
    
    ruff_files = list(Path(".").rglob("ruff_tab.py"))
    
    if len(ruff_files) == 0:
        print("[X] Aucun fichier ruff_tab.py trouve!")
    elif len(ruff_files) == 1:
        print(f"[OK] Un seul fichier trouve: {ruff_files[0]}")
    else:
        print(f"[!] ATTENTION: {len(ruff_files)} fichiers ruff_tab.py trouves!")
        for f in ruff_files:
            print(f"    - {f}")
        print("\nCela peut causer des conflits!")


def test_import():
    """Teste l'import du module."""
    
    print("\n" + "=" * 60)
    print("TEST D'IMPORT DU MODULE")
    print("=" * 60)
    
    try:
        import sys
        sys.path.insert(0, str(Path.cwd()))
        
        from gui.tabs.ruff_tab import RuffIntegrationTab
        print("[OK] Import reussi!")
        
        # Verifier les attributs
        if hasattr(RuffIntegrationTab, 'copy_to_clipboard'):
            print("[OK] Methode copy_to_clipboard existe dans la classe")
        else:
            print("[X] Methode copy_to_clipboard NON trouvee dans la classe")
            
    except ImportError as e:
        print(f"[X] Erreur d'import: {e}")
    except Exception as e:
        print(f"[X] Erreur: {e}")


def main():
    """Fonction principale de diagnostic."""
    
    print("=" * 60)
    print("DIAGNOSTIC DU BOUTON COPY TO CLIPBOARD")
    print("=" * 60)
    
    # 1. Verifier que le fichier existe
    file_path = check_file_exists()
    if not file_path:
        return
    
    # 2. Verifier le contenu du fichier
    all_found, checks = check_copy_button_code(file_path)
    
    # 3. Verifier les doublons
    check_multiple_files()
    
    # 4. Tester l'import
    test_import()
    
    # === RESUME FINAL ===
    print("\n" + "=" * 60)
    print("RESUME ET ACTIONS RECOMMANDEES")
    print("=" * 60)
    
    if all_found:
        print("[i] Le code semble correct. Essayez:")
        print("    1. Fermer completement l'application")
        print("    2. Relancer avec: python run.py")
        print("    3. Aller dans l'onglet 'Analyse et Formatage (Ruff)'")
        print("    4. Le bouton devrait etre sous la zone de texte des resultats")
    else:
        print("[!] Le code du bouton est incomplet!")
        print("    1. Copiez le code genere ci-dessus")
        print("    2. Ajoutez-le dans gui/tabs/ruff_tab.py")
        print("    3. Sauvegardez le fichier")
        print("    4. Relancez l'application")
    
    print("\n[?] Si le probleme persiste, verifiez:")
    print("    - Que vous editez le BON fichier ruff_tab.py")
    print("    - Que le fichier est bien sauvegarde")
    print("    - Qu'il n'y a pas d'erreurs Python au lancement")


if __name__ == "__main__":
    main()