#!/usr/bin/env python3
"""
Script de nettoyage du projet AST_tools
Supprime tous les fichiers non necessaires et temporaires
"""

import os
import shutil
from pathlib import Path


def get_size_format(bytes):
    """Formate la taille en bytes de maniere lisible."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024.0:
            return f"{bytes:.1f} {unit}"
        bytes /= 1024.0
    return f"{bytes:.1f} TB"


def calculate_size(path):
    """Calcule la taille d'un fichier ou dossier."""
    total = 0
    if os.path.isfile(path):
        total = os.path.getsize(path)
    elif os.path.isdir(path):
        for dirpath, _, filenames in os.walk(path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                if os.path.exists(fp):
                    total += os.path.getsize(fp)
    return total


def cleanup_project():
    """Nettoie le projet en supprimant les fichiers non necessaires."""
    
    print("=" * 60)
    print("NETTOYAGE DU PROJET AST_TOOLS")
    print("=" * 60)
    
    # Liste des elements a supprimer
    to_delete = {
        # === DOSSIERS A SUPPRIMER ===
        "dirs": [
            ".ruff_cache",           # Cache Ruff (peut etre regenere)
            "__pycache__",           # Cache Python
            ".pytest_cache",         # Cache pytest si present
            "logs/ruff",            # Logs Ruff temporaires
            "data/ruff_reports/cache",  # Cache des rapports
        ],
        
        # === FICHIERS TEMPORAIRES A SUPPRIMER ===
        "files": [
            # Fichiers de diagnostic/reparation anciens
            "diagnostic_report_20250805_214017.json",
            "repair_report_20250805_214316.txt",
            "ruff_diagnostic_20250805_180737.txt",
            "ast_tools_debug_20250802_162356.log",
            
            # Fichiers de reparation temporaires
            "auto_repair.py",
            
            # Logs precedents (on garde seulement le log actuel)
            "ast_tools_previous.log",
            
            # Fichiers de vision/documentation temporaire
            "AST_Vision_Global.txt",
        ],
        
        # === PATTERNS DE FICHIERS A SUPPRIMER ===
        "patterns": [
            "*.pyc",                 # Fichiers Python compiles
            "*.pyo",                 # Fichiers Python optimises
            "*.pyd",                 # Extensions Python Windows
            "*~",                    # Fichiers temporaires editeur
            ".DS_Store",             # Fichiers macOS
            "Thumbs.db",             # Fichiers Windows
            "*.backup*",             # Tous les fichiers backup
            "*.bak",                 # Fichiers backup
            "*_old.py",              # Anciennes versions
            "*_backup.py",           # Backups Python
        ]
    }
    
    # Statistiques
    total_size = 0
    deleted_items = []
    
    print("\n[1] ANALYSE DES FICHIERS A SUPPRIMER...")
    print("-" * 40)
    
    # === SUPPRESSION DES DOSSIERS ===
    for dir_path in to_delete["dirs"]:
        if os.path.exists(dir_path) and os.path.isdir(dir_path):
            size = calculate_size(dir_path)
            total_size += size
            print(f"  Dossier: {dir_path} ({get_size_format(size)})")
            deleted_items.append(("dir", dir_path, size))
    
    # === SUPPRESSION DES FICHIERS SPECIFIQUES ===
    for file_path in to_delete["files"]:
        if os.path.exists(file_path) and os.path.isfile(file_path):
            size = os.path.getsize(file_path)
            total_size += size
            print(f"  Fichier: {file_path} ({get_size_format(size)})")
            deleted_items.append(("file", file_path, size))
    
    # === RECHERCHE PAR PATTERNS ===
    for pattern in to_delete["patterns"]:
        for path in Path(".").rglob(pattern):
            if path.is_file():
                size = path.stat().st_size
                total_size += size
                print(f"  Pattern: {path} ({get_size_format(size)})")
                deleted_items.append(("file", str(path), size))
    
    # === RECHERCHE DES DOSSIERS __pycache__ PARTOUT ===
    for pycache in Path(".").rglob("__pycache__"):
        if pycache.is_dir():
            size = calculate_size(str(pycache))
            total_size += size
            print(f"  PyCache: {pycache} ({get_size_format(size)})")
            deleted_items.append(("dir", str(pycache), size))
    
    if not deleted_items:
        print("\n[OK] Aucun fichier temporaire a supprimer!")
        print("     Le projet est deja propre.")
        return
    
    # === RESUME ===
    print("\n" + "=" * 60)
    print("RESUME")
    print("=" * 60)
    print(f"Elements a supprimer: {len(deleted_items)}")
    print(f"Espace a liberer: {get_size_format(total_size)}")
    
    # === CONFIRMATION ===
    print("\n" + "=" * 60)
    print("[!] ATTENTION: Cette action est IRREVERSIBLE!")
    print("=" * 60)
    response = input("\nVoulez-vous vraiment supprimer ces fichiers? (yes/no): ").strip().lower()
    
    if response not in ['yes', 'y', 'oui', 'o']:
        print("\n[ANNULE] Aucun fichier supprime.")
        return
    
    # === SUPPRESSION EFFECTIVE ===
    print("\n[2] SUPPRESSION EN COURS...")
    print("-" * 40)
    
    success_count = 0
    error_count = 0
    
    for item_type, item_path, _ in deleted_items:
        try:
            if item_type == "dir":
                shutil.rmtree(item_path)
                print(f"  [OK] Dossier supprime: {item_path}")
            else:
                os.remove(item_path)
                print(f"  [OK] Fichier supprime: {item_path}")
            success_count += 1
        except Exception as e:
            print(f"  [X] Erreur: {item_path} - {str(e)}")
            error_count += 1
    
    # === RAPPORT FINAL ===
    print("\n" + "=" * 60)
    print("NETTOYAGE TERMINE")
    print("=" * 60)
    print(f"[OK] {success_count} element(s) supprime(s)")
    if error_count > 0:
        print(f"[X] {error_count} erreur(s)")
    print(f"[i] Espace libere: {get_size_format(total_size)}")
    
    # === CONSEILS POST-NETTOYAGE ===
    print("\n" + "=" * 60)
    print("PROCHAINES ETAPES RECOMMANDEES")
    print("=" * 60)
    print("1. Verifier que l'application fonctionne: python run.py")
    print("2. Faire un commit Git: git add . && git commit -m 'cleanup: suppression fichiers temporaires'")
    print("3. Relancer Ruff pour verifier: ruff check .")


def list_files_only():
    """Liste les fichiers qui seraient supprimes sans les supprimer."""
    
    print("=" * 60)
    print("MODE PREVIEW - AUCUNE SUPPRESSION")
    print("=" * 60)
    
    # Meme logique mais sans suppression
    to_check = {
        "dirs": [".ruff_cache", "__pycache__", ".pytest_cache", "logs/ruff", "data/ruff_reports/cache"],
        "files": [
            "diagnostic_report_20250805_214017.json",
            "repair_report_20250805_214316.txt",
            "ruff_diagnostic_20250805_180737.txt",
            "ast_tools_debug_20250802_162356.log",
            "auto_repair.py",
            "ast_tools_previous.log",
            "AST_Vision_Global.txt",
        ],
        "patterns": ["*.pyc", "*.pyo", "*.pyd", "*~", ".DS_Store", "Thumbs.db", "*.backup*", "*.bak"]
    }
    
    total_size = 0
    count = 0
    
    print("\nFichiers/Dossiers qui seraient supprimes:")
    print("-" * 40)
    
    for dir_path in to_check["dirs"]:
        if os.path.exists(dir_path) and os.path.isdir(dir_path):
            size = calculate_size(dir_path)
            total_size += size
            count += 1
            print(f"  [D] {dir_path} ({get_size_format(size)})")
    
    for file_path in to_check["files"]:
        if os.path.exists(file_path) and os.path.isfile(file_path):
            size = os.path.getsize(file_path)
            total_size += size
            count += 1
            print(f"  [F] {file_path} ({get_size_format(size)})")
    
    print(f"\nTotal: {count} elements, {get_size_format(total_size)}")


def main():
    """Point d'entree principal."""
    
    print("SCRIPT DE NETTOYAGE AST_TOOLS")
    print("=" * 60)
    print("Options:")
    print("  1. Nettoyer le projet (suppression)")
    print("  2. Preview (voir sans supprimer)")
    print("  3. Annuler")
    
    choice = input("\nChoix (1/2/3): ").strip()
    
    if choice == "1":
        cleanup_project()
    elif choice == "2":
        list_files_only()
    else:
        print("\n[ANNULE] Aucune action effectuee.")


if __name__ == "__main__":
    main()