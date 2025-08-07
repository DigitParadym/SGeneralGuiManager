#!/usr/bin/env python3
"""
Script pour ajouter automatiquement le bouton Copy to clipboard dans ruff_tab.py
"""

import os
from pathlib import Path


def add_copy_button():
    """Ajoute automatiquement le bouton Copy to clipboard."""
    
    file_path = Path("gui/tabs/ruff_tab.py")
    
    if not file_path.exists():
        print("[X] Erreur: gui/tabs/ruff_tab.py non trouve!")
        return False
    
    print("=" * 60)
    print("AJOUT AUTOMATIQUE DU BOUTON COPY TO CLIPBOARD")
    print("=" * 60)
    
    # Lire le fichier
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"[i] Fichier charge: {len(lines)} lignes")
    
    # === 1. TROUVER ET AJOUTER LE BOUTON DANS LE PANNEAU DROIT ===
    print("\n[1] Ajout du bouton dans le panneau droit...")
    
    # Chercher l'endroit ou ajouter le bouton (apres self.output_text)
    insert_position = None
    for i, line in enumerate(lines):
        if "right_layout.addWidget(self.output_text)" in line:
            insert_position = i + 1
            print(f"    Position trouvee: ligne {i+1}")
            break
    
    if insert_position:
        # Code a inserer pour le bouton
        button_code = """
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

"""
        lines.insert(insert_position, button_code)
        print("    [OK] Code du bouton insere")
    else:
        print("    [X] Position non trouvee pour le bouton")
        return False
    
    # === 2. AJOUTER LA CONNEXION DU SIGNAL ===
    print("\n[2] Ajout de la connexion du signal...")
    
    # Chercher la section des connexions
    connection_position = None
    for i, line in enumerate(lines):
        if "self.cancel_btn.clicked.connect(self.cancel_operation)" in line:
            connection_position = i + 1
            print(f"    Position trouvee: ligne {i+1}")
            break
    
    if connection_position:
        connection_code = "        self.copy_btn.clicked.connect(self.copy_to_clipboard)\n"
        lines.insert(connection_position, connection_code)
        print("    [OK] Connexion ajoutee")
    else:
        print("    [X] Position non trouvee pour la connexion")
    
    # === 3. AJOUTER LA METHODE copy_to_clipboard ===
    print("\n[3] Ajout de la methode copy_to_clipboard...")
    
    # Trouver la fin de la classe (avant le dernier def ou a la fin)
    method_position = None
    for i in range(len(lines) - 1, -1, -1):
        if lines[i].strip().startswith("def log_message"):
            # Trouver la fin de cette methode
            indent_count = len(lines[i]) - len(lines[i].lstrip())
            for j in range(i + 1, len(lines)):
                if j == len(lines) - 1:  # Derniere ligne
                    method_position = j + 1
                    break
                elif lines[j].strip() and not lines[j].startswith(" " * (indent_count + 4)):
                    method_position = j
                    break
            break
    
    if method_position is None:
        method_position = len(lines)  # Ajouter a la fin si pas trouve
    
    print(f"    Position trouvee: ligne {method_position}")
    
    # Code de la methode
    method_code = """
    def copy_to_clipboard(self):
        '''Copie le contenu des resultats dans le presse-papiers.'''
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import QTimer
        from datetime import datetime
        
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
"""
    
    lines.insert(method_position, method_code)
    print("    [OK] Methode ajoutee")
    
    # === 4. SAUVEGARDER LE FICHIER ===
    print("\n[4] Sauvegarde du fichier...")
    
    # Backup du fichier original
    backup_path = file_path.with_suffix('.py.backup_before_copy_button')
    with open(backup_path, 'w', encoding='utf-8') as f:
        with open(file_path, 'r', encoding='utf-8') as original:
            f.write(original.read())
    print(f"    [OK] Backup cree: {backup_path}")
    
    # Ecrire le fichier modifie
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print(f"    [OK] Fichier modifie sauvegarde")
    
    return True


def verify_installation():
    """Verifie que le bouton a bien ete ajoute."""
    
    print("\n" + "=" * 60)
    print("VERIFICATION DE L'INSTALLATION")
    print("=" * 60)
    
    file_path = Path("gui/tabs/ruff_tab.py")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = [
        ("Bouton declare", "self.copy_btn = QPushButton"),
        ("Layout cree", "copy_layout = QHBoxLayout()"),
        ("Signal connecte", "self.copy_btn.clicked.connect"),
        ("Methode presente", "def copy_to_clipboard(self):"),
    ]
    
    all_ok = True
    for check_name, pattern in checks:
        if pattern in content:
            print(f"[OK] {check_name}")
        else:
            print(f"[X] {check_name} - NON TROUVE")
            all_ok = False
    
    return all_ok


def main():
    """Fonction principale."""
    
    print("INSTALLATION DU BOUTON COPY TO CLIPBOARD")
    print("=" * 60)
    
    response = input("\nVoulez-vous installer le bouton automatiquement? (yes/no): ").strip().lower()
    
    if response not in ['yes', 'y', 'oui', 'o']:
        print("\n[ANNULE] Aucune modification effectuee")
        return
    
    # Ajouter le bouton
    if add_copy_button():
        print("\n" + "=" * 60)
        print("[OK] INSTALLATION TERMINEE AVEC SUCCES!")
        print("=" * 60)
        
        # Verifier
        if verify_installation():
            print("\n[OK] Tous les elements ont ete correctement ajoutes!")
            print("\nPROCHAINES ETAPES:")
            print("1. Fermer l'application si elle est ouverte")
            print("2. Relancer avec: python run.py")
            print("3. Aller dans l'onglet 'Analyse et Formatage (Ruff)'")
            print("4. Le bouton 'Copy to clipboard' sera visible!")
        else:
            print("\n[!] Certains elements semblent manquer")
            print("    Verifiez manuellement le fichier")
    else:
        print("\n[X] Erreur lors de l'installation")
        print("    Verifiez le fichier manuellement")


if __name__ == "__main__":
    main()