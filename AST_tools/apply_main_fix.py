#!/usr/bin/env python3
"""
apply_main_fix.py - Corrige main.py pour utiliser le filtre
"""

import shutil
from datetime import datetime
from pathlib import Path


def fix_main_py():
    main_path = Path("main.py")

    if not main_path.exists():
        print("[ERREUR] main.py non trouve!")
        return False

    # Backup
    backup_name = f"main_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
    shutil.copy2(main_path, backup_name)
    print(f"[OK] Backup cree: {backup_name}")

    # Lire le contenu
    with open(main_path, encoding="utf-8") as f:
        lines = f.readlines()

    # Verifier si deja patche
    has_filter_import = False
    for line in lines:
        if "ProfessionalFileFilter" in line:
            has_filter_import = True
            break

    if has_filter_import:
        print("[INFO] main.py utilise deja ProfessionalFileFilter")

    # Modifier les lignes
    new_lines = []
    import_added = False
    init_modified = False

    for i, line in enumerate(lines):
        # Ajouter l'import apres les autres imports
        if not import_added and line.startswith("from") and "QtWidgets" in line:
            new_lines.append(line)
            new_lines.append("from professional_file_filter import ProfessionalFileFilter\n")
            import_added = True
            continue

        # Modifier __init__ pour ajouter le filtre
        if "def __init__(self):" in line and not init_modified:
            new_lines.append(line)
            if i + 1 < len(lines) and "super().__init__()" in lines[i + 1]:
                new_lines.append(lines[i + 1])
                new_lines.append(
                    "        self.file_filter = ProfessionalFileFilter()  # FILTRE AJOUTE\n"
                )
                init_modified = True
                continue

        # Remplacer la methode add_target_folder
        if "def add_target_folder(self):" in line:
            # Ajouter la nouvelle version de la methode
            new_lines.append(line)
            new_lines.append(
                '        """Ajoute les fichiers Python d\'un dossier AVEC FILTRE."""\n'
            )
            new_lines.append(
                '        folder_path = QFileDialog.getExistingDirectory(self, "Selectionner dossier")\n'
            )
            new_lines.append("        if folder_path:\n")
            new_lines.append(
                "            # Utiliser le filtre pour obtenir uniquement les fichiers du projet\n"
            )
            new_lines.append('            if hasattr(self, "file_filter"):\n')
            new_lines.append(
                "                all_project_files = self.file_filter.get_project_files()\n"
            )
            new_lines.append("                folder_path_obj = Path(folder_path)\n")
            new_lines.append("                py_files = []\n")
            new_lines.append("                for file_path in all_project_files:\n")
            new_lines.append("                    try:\n")
            new_lines.append(
                "                        # Verifier si le fichier est dans le dossier selectionne\n"
            )
            new_lines.append("                        file_path.relative_to(folder_path_obj)\n")
            new_lines.append("                        py_files.append(str(file_path))\n")
            new_lines.append("                    except ValueError:\n")
            new_lines.append("                        continue\n")
            new_lines.append("            else:\n")
            new_lines.append("                # Fallback: ancienne methode\n")
            new_lines.append(
                '                py_files = [str(p) for p in Path(folder_path).rglob("*.py")]\n'
            )
            new_lines.append("            \n")
            new_lines.append("            added = 0\n")
            new_lines.append("            for file_path in py_files:\n")
            new_lines.append("                if file_path not in self.target_files:\n")
            new_lines.append("                    self.target_files.append(file_path)\n")
            new_lines.append("                    self.files_list.addItem(\n")
            new_lines.append(
                "                        QListWidgetItem(os.path.basename(file_path))\n"
            )
            new_lines.append("                    )\n")
            new_lines.append("                    added += 1\n")
            new_lines.append("            self.update_execute_button()\n")
            new_lines.append(
                '            self.log_message(f"{added} fichier(s) ajoute(s) du dossier (AVEC FILTRE).")\n'
            )

            # Sauter l'ancienne implementation
            skip_until_next_def = True
            continue

        # Continuer a sauter jusqu'a la prochaine methode
        if skip_until_next_def:
            if line.strip().startswith("def ") and "add_target_folder" not in line:
                skip_until_next_def = False
                new_lines.append(line)
            continue

        new_lines.append(line)

    # Ecrire le fichier corrige
    with open("main_fixed.py", "w", encoding="utf-8") as f:
        f.writelines(new_lines)

    print("[OK] main_fixed.py cree avec le filtre")
    print("")
    print("POUR APPLIQUER LE CORRECTIF:")
    print("1. Testez d'abord: python main_fixed.py")
    print("2. Si OK: mv main_fixed.py main.py")
    print("")
    print("Le filtre va maintenant:")
    print("- Ne charger que les fichiers du projet (~60 fichiers)")
    print("- Ignorer automatiquement venv/ et __pycache__/")

    return True


if __name__ == "__main__":
    fix_main_py()
