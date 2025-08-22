#!/usr/bin/env python3
"""
Script de nettoyage du projet AST_tools avant commit Git
Supprime les fichiers temporaires, backups et autres fichiers non necessaires
"""

import os
import shutil
from pathlib import Path
from typing import List, Set
import sys

class ProjectCleaner:
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.files_to_delete = []
        self.dirs_to_delete = []
        
        # Patterns de fichiers a supprimer
        self.backup_patterns = [
            "*.backup_*",
            "*_backup_*.py",
            "*.bak",
            "*.tmp",
            "*.temp"
        ]
        
        # Fichiers specifiques a supprimer
        self.specific_files = [
            "ast_tools.log",
            "ast_tools_previous.log",
            "errors.log"
        ]
        
        # Repertoires a nettoyer
        self.dirs_to_clean = [
            "__pycache__",
            ".pytest_cache",
            "*.egg-info",
            ".mypy_cache",
            ".ruff_cache"
        ]
        
        # Fichiers a garder absolument
        self.keep_files = {
            "__init__.py",
            "requirements.txt",
            "pyproject.toml",
            "README.md",
            ".gitignore",
            "setup.py",
            "setup.cfg"
        }

    def find_backup_files(self) -> List[Path]:
        """Trouve tous les fichiers de backup"""
        backup_files = []
        
        # Recherche des fichiers avec patterns de backup
        for pattern in self.backup_patterns:
            backup_files.extend(self.project_root.rglob(pattern))
        
        # Recherche specifique des backups de main.py
        main_backups = list(self.project_root.glob("main.py.backup_*"))
        backup_files.extend(main_backups)
        
        # Recherche des backups de modificateur_interactif
        mod_backups = list(self.project_root.glob("modificateur_interactif_backup_*.py"))
        backup_files.extend(mod_backups)
        
        return backup_files

    def find_log_files(self) -> List[Path]:
        """Trouve tous les fichiers de log temporaires"""
        log_files = []
        
        # Logs dans le repertoire racine
        for log_file in self.specific_files:
            file_path = self.project_root / log_file
            if file_path.exists():
                log_files.append(file_path)
        
        # Logs dans le dossier logs/
        logs_dir = self.project_root / "logs"
        if logs_dir.exists():
            # On garde seulement le dossier logs vide
            log_files.extend([f for f in logs_dir.glob("*.log")])
        
        return log_files

    def find_cache_dirs(self) -> List[Path]:
        """Trouve tous les repertoires de cache"""
        cache_dirs = []
        
        for dir_pattern in self.dirs_to_clean:
            cache_dirs.extend(self.project_root.rglob(dir_pattern))
        
        return cache_dirs

    def find_pyc_files(self) -> List[Path]:
        """Trouve tous les fichiers .pyc"""
        return list(self.project_root.rglob("*.pyc"))

    def find_duplicate_or_temp_files(self) -> List[Path]:
        """Trouve les fichiers temporaires ou dupliques potentiels"""
        temp_files = []
        
        # Fichiers .py~ (editeur vim/emacs)
        temp_files.extend(self.project_root.rglob("*.py~"))
        
        # Fichiers .swp (vim)
        temp_files.extend(self.project_root.rglob("*.swp"))
        
        # Fichiers .DS_Store (macOS)
        temp_files.extend(self.project_root.rglob(".DS_Store"))
        
        # Fichiers Thumbs.db (Windows)
        temp_files.extend(self.project_root.rglob("Thumbs.db"))
        
        return temp_files

    def analyze_project(self):
        """Analyse le projet et collecte tous les fichiers a supprimer"""
        print("[ANALYSE] Analyse du projet en cours...")
        print("=" * 50)
        
        # Collecte des fichiers
        backup_files = self.find_backup_files()
        log_files = self.find_log_files()
        cache_dirs = self.find_cache_dirs()
        pyc_files = self.find_pyc_files()
        temp_files = self.find_duplicate_or_temp_files()
        
        # Ajout a la liste de suppression
        self.files_to_delete.extend(backup_files)
        self.files_to_delete.extend(log_files)
        self.files_to_delete.extend(pyc_files)
        self.files_to_delete.extend(temp_files)
        self.dirs_to_delete.extend(cache_dirs)
        
        # Affichage du rapport
        self.display_report(backup_files, log_files, cache_dirs, pyc_files, temp_files)

    def display_report(self, backup_files, log_files, cache_dirs, pyc_files, temp_files):
        """Affiche un rapport detaille des fichiers trouves"""
        
        if backup_files:
            print(f"\n[BACKUP] Fichiers de backup trouves ({len(backup_files)}):")
            for f in backup_files[:10]:  # Limite l'affichage a 10
                print(f"  - {f.relative_to(self.project_root)}")
            if len(backup_files) > 10:
                print(f"  ... et {len(backup_files) - 10} autres")
        
        if log_files:
            print(f"\n[LOGS] Fichiers de log trouves ({len(log_files)}):")
            for f in log_files:
                print(f"  - {f.relative_to(self.project_root)}")
        
        if cache_dirs:
            print(f"\n[CACHE] Repertoires de cache trouves ({len(cache_dirs)}):")
            for d in cache_dirs:
                print(f"  - {d.relative_to(self.project_root)}")
        
        if pyc_files:
            print(f"\n[PYC] Fichiers .pyc trouves ({len(pyc_files)}):")
            if len(pyc_files) > 5:
                print(f"  Total: {len(pyc_files)} fichiers")
            else:
                for f in pyc_files:
                    print(f"  - {f.relative_to(self.project_root)}")
        
        if temp_files:
            print(f"\n[TEMP] Fichiers temporaires trouves ({len(temp_files)}):")
            for f in temp_files:
                print(f"  - {f.relative_to(self.project_root)}")
        
        total_files = len(self.files_to_delete)
        total_dirs = len(self.dirs_to_delete)
        
        print("\n" + "=" * 50)
        print(f"[RESUME] {total_files} fichiers et {total_dirs} repertoires a supprimer")
        
        if total_files + total_dirs > 0:
            # Calcul de la taille totale
            total_size = 0
            for f in self.files_to_delete:
                if f.exists():
                    total_size += f.stat().st_size
            
            print(f"[ESPACE] Espace a liberer: {self.format_size(total_size)}")
    
    def format_size(self, size_bytes):
        """Formate la taille en unite lisible"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"

    def clean(self, dry_run=False):
        """Nettoie le projet"""
        if not self.files_to_delete and not self.dirs_to_delete:
            print("\n[OK] Le projet est deja propre! Aucun fichier a supprimer.")
            return
        
        if dry_run:
            print("\n[INFO] MODE DRY-RUN: Aucun fichier ne sera supprime")
            return
        
        print("\n" + "=" * 50)
        print("[ATTENTION] Cette action est irreversible!")
        print("=" * 50)
        
        response = input("\n[?] Voulez-vous vraiment supprimer ces fichiers? (oui/non): ").lower()
        
        if response in ['oui', 'o', 'yes', 'y']:
            self.execute_cleanup()
        else:
            print("\n[ANNULE] Nettoyage annule.")

    def execute_cleanup(self):
        """Execute la suppression des fichiers"""
        print("\n[NETTOYAGE] Nettoyage en cours...")
        
        deleted_files = 0
        deleted_dirs = 0
        errors = []
        
        # Suppression des fichiers
        for file_path in self.files_to_delete:
            try:
                if file_path.exists():
                    file_path.unlink()
                    deleted_files += 1
                    print(f"  [OK] Supprime: {file_path.relative_to(self.project_root)}")
            except Exception as e:
                errors.append(f"Erreur avec {file_path}: {e}")
        
        # Suppression des repertoires
        for dir_path in self.dirs_to_delete:
            try:
                if dir_path.exists():
                    shutil.rmtree(dir_path)
                    deleted_dirs += 1
                    print(f"  [OK] Supprime: {dir_path.relative_to(self.project_root)}/")
            except Exception as e:
                errors.append(f"Erreur avec {dir_path}: {e}")
        
        # Rapport final
        print("\n" + "=" * 50)
        print("[TERMINE] Nettoyage termine!")
        print(f"  - {deleted_files} fichiers supprimes")
        print(f"  - {deleted_dirs} repertoires supprimes")
        
        if errors:
            print(f"\n[ERREURS] {len(errors)} erreurs rencontrees:")
            for error in errors[:5]:
                print(f"  - {error}")
        
        print("\n[INFO] Prochaines etapes:")
        print("  1. Verifiez que tout fonctionne: python main.py")
        print("  2. Ajoutez les fichiers a Git: git add .")
        print("  3. Committez: git commit -m 'Nettoyage du projet'")
        print("  4. Poussez sur GitHub: git push origin main")

    def create_gitignore(self):
        """Cree ou met a jour le fichier .gitignore"""
        gitignore_path = self.project_root / ".gitignore"
        
        gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
*.pyc
.Python
env/
venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Logs
*.log
logs/*.log

# Backups
*.backup_*
*_backup_*
*.bak
*.tmp
*.temp

# IDE
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store
Thumbs.db

# Testing
.pytest_cache/
.mypy_cache/
.ruff_cache/
.coverage
htmlcov/

# Documentation
docs/_build/
"""
        
        if not gitignore_path.exists():
            gitignore_path.write_text(gitignore_content)
            print(f"\n[OK] Fichier .gitignore cree")
        else:
            print(f"\n[INFO] .gitignore existe deja")


def main():
    """Fonction principale"""
    print("""
+==================================================+
|     NETTOYEUR DE PROJET AST_TOOLS               |
|     Prepare votre projet pour GitHub            |
+==================================================+
    """)
    
    # Verification du repertoire
    if not Path("AST.py").exists():
        print("[ERREUR] Ce script doit etre execute depuis la racine du projet AST_tools!")
        sys.exit(1)
    
    cleaner = ProjectCleaner()
    
    # Menu
    print("Options disponibles:")
    print("  1. Analyser seulement (dry-run)")
    print("  2. Nettoyer le projet")
    print("  3. Creer/Mettre a jour .gitignore")
    print("  4. Tout faire (nettoyer + .gitignore)")
    print("  0. Quitter")
    
    choice = input("\nVotre choix (0-4): ").strip()
    
    if choice == "1":
        cleaner.analyze_project()
        cleaner.clean(dry_run=True)
    elif choice == "2":
        cleaner.analyze_project()
        cleaner.clean(dry_run=False)
    elif choice == "3":
        cleaner.create_gitignore()
    elif choice == "4":
        cleaner.analyze_project()
        cleaner.clean(dry_run=False)
        cleaner.create_gitignore()
    elif choice == "0":
        print("\n[AU REVOIR] A bientot!")
    else:
        print("\n[ERREUR] Choix invalide")


if __name__ == "__main__":
    main()