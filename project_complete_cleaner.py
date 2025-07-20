#!/usr/bin/env python3
"""
Nettoyeur MASSIF recursif pour tout le projet SGeneralGuiManager
Nettoie TOUS les backups et logs dans TOUS les sous-dossiers
Version sans Unicode - 100% ASCII
"""

import os
import shutil
from datetime import datetime

def find_all_files_recursive(start_dir):
    """Trouve TOUS les fichiers backup et logs recursivement"""
    
    backup_files = []
    log_files = []
    
    # Patterns de fichiers backup
    backup_patterns = [
        '.backup_', '.backup', '_backup_', '_backup',
        '.unicode_backup_', '.clean_backup_', '.recursive_backup_',
        '.ascii_clean_', 'backup_', '_20241', '_20250'  # patterns de date
    ]
    
    # Patterns de fichiers logs  
    log_patterns = ['.log', '_log', 'log_', '.out', '.err']
    
    # Dossiers a ignorer completement
    ignore_dirs = {'.git', '__pycache__', 'node_modules', '.venv', 'venv'}
    
    # Fichiers principaux a PRESERVER absolument
    preserve_files = {
        'copypaste_manager.py',
        'main.py', 
        'gui_main.py',
        'run_app.py',
        '__init__.py'
    }
    
    print(f"Balayage recursif depuis : {start_dir}")
    
    for root, dirs, files in os.walk(start_dir):
        # Filtrer les dossiers a ignorer
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        
        # Afficher le dossier en cours
        rel_path = os.path.relpath(root, start_dir)
        if rel_path != '.':
            print(f"  Analyse : {rel_path}/")
        
        for filename in files:
            file_path = os.path.join(root, filename)
            file_size = os.path.getsize(file_path)
            rel_file_path = os.path.relpath(file_path, start_dir)
            
            # PROTEGER les fichiers principaux
            if filename in preserve_files:
                continue
            
            # Detecter les backups
            is_backup = False
            for pattern in backup_patterns:
                if pattern in filename:
                    is_backup = True
                    break
            
            if is_backup:
                backup_files.append({
                    'name': rel_file_path,
                    'path': file_path,
                    'size': file_size,
                    'dir': rel_path
                })
                continue
            
            # Detecter les logs
            is_log = False
            for pattern in log_patterns:
                if filename.lower().endswith(pattern):
                    is_log = True
                    break
            
            # Dossiers speciaux qui sont forcement des logs
            if any(log_dir in rel_path.lower() for log_dir in ['logs', 'log', '.srun']):
                if filename.endswith(('.log', '.txt', '')):  # fichiers dans dossiers logs
                    is_log = True
            
            if is_log:
                log_files.append({
                    'name': rel_file_path,
                    'path': file_path, 
                    'size': file_size,
                    'dir': rel_path
                })
    
    return backup_files, log_files

def analyze_by_directory(backup_files, log_files):
    """Analyse les fichiers par repertoire"""
    
    dir_stats = {}
    
    # Analyser backups
    for f in backup_files:
        dir_name = f['dir']
        if dir_name not in dir_stats:
            dir_stats[dir_name] = {'backups': 0, 'logs': 0, 'backup_size': 0, 'log_size': 0}
        dir_stats[dir_name]['backups'] += 1
        dir_stats[dir_name]['backup_size'] += f['size']
    
    # Analyser logs
    for f in log_files:
        dir_name = f['dir']
        if dir_name not in dir_stats:
            dir_stats[dir_name] = {'backups': 0, 'logs': 0, 'backup_size': 0, 'log_size': 0}
        dir_stats[dir_name]['logs'] += 1
        dir_stats[dir_name]['log_size'] += f['size']
    
    return dir_stats

def format_file_size(size_bytes):
    """Formate la taille du fichier"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"

def show_detailed_analysis(dir_stats):
    """Affiche une analyse detaillee par repertoire"""
    
    print(f"\n{'='*80}")
    print("ANALYSE DETAILLEE PAR REPERTOIRE")
    print("="*80)
    
    total_backups = sum(stats['backups'] for stats in dir_stats.values())
    total_logs = sum(stats['logs'] for stats in dir_stats.values())
    total_backup_size = sum(stats['backup_size'] for stats in dir_stats.values())
    total_log_size = sum(stats['log_size'] for stats in dir_stats.values())
    
    # Trier par nombre total de fichiers
    sorted_dirs = sorted(dir_stats.items(), 
                        key=lambda x: x[1]['backups'] + x[1]['logs'], 
                        reverse=True)
    
    for dir_name, stats in sorted_dirs:
        if stats['backups'] + stats['logs'] == 0:
            continue
            
        total_files = stats['backups'] + stats['logs']
        total_size = stats['backup_size'] + stats['log_size']
        
        print(f"\n{dir_name or 'RACINE'}/")
        print(f"  Backups : {stats['backups']} fichiers ({format_file_size(stats['backup_size'])})")
        print(f"  Logs    : {stats['logs']} fichiers ({format_file_size(stats['log_size'])})")
        print(f"  TOTAL   : {total_files} fichiers ({format_file_size(total_size)})")
    
    print(f"\n{'='*50}")
    print("RESUME GLOBAL")
    print("="*50)
    print(f"Total backups : {total_backups} fichiers ({format_file_size(total_backup_size)})")
    print(f"Total logs    : {total_logs} fichiers ({format_file_size(total_log_size)})")
    print(f"GRAND TOTAL   : {total_backups + total_logs} fichiers ({format_file_size(total_backup_size + total_log_size)})")

def create_final_backup(main_file="copypaste_manager.py"):
    """Cree une sauvegarde finale du fichier principal"""
    
    if not os.path.exists(main_file):
        return None
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    final_backup = f"{main_file}.FINAL_BEFORE_MASSIVE_CLEANUP_{timestamp}"
    
    try:
        shutil.copy2(main_file, final_backup)
        print(f"Sauvegarde finale CRITIQUE creee : {final_backup}")
        return final_backup
    except Exception as e:
        print(f"ERREUR creation sauvegarde finale : {e}")
        return None

def ask_user_confirmation(total_files, total_size, top_dirs):
    """Demande confirmation pour suppression massive"""
    
    print(f"\n{'!'*60}")
    print("ATTENTION : SUPPRESSION MASSIVE !")
    print("!"*60)
    print(f"Vous allez supprimer {total_files} fichier(s)")
    print(f"Espace total libere : {format_file_size(total_size)}")
    print(f"Repertoires les plus touches :")
    
    for dir_name, count in top_dirs[:5]:
        print(f"  - {dir_name or 'RACINE'} : {count} fichiers")
    
    print(f"\n{'!'*60}")
    print("CETTE OPERATION EST IRREVERSIBLE !")
    print("Tous les logs et backups du projet seront DEFINITIVEMENT supprimes")
    print("!"*60)
    
    while True:
        print(f"\nTapez 'SUPPRIMER' (en majuscules) pour confirmer")
        print("Ou 'annuler' pour abandonner :")
        response = input("> ").strip()
        
        if response == "SUPPRIMER":
            return True
        elif response.lower() in ['annuler', 'non', 'n', 'cancel']:
            return False
        else:
            print("Repondez 'SUPPRIMER' ou 'annuler'")

def delete_files_by_type(files_list, file_type):
    """Supprime une liste de fichiers avec rapport detaille"""
    
    deleted_count = 0
    failed_count = 0
    total_size_deleted = 0
    
    print(f"\nSuppression des {file_type}...")
    print("-" * 50)
    
    # Grouper par repertoire pour un affichage organise
    by_dir = {}
    for f in files_list:
        dir_name = f['dir']
        if dir_name not in by_dir:
            by_dir[dir_name] = []
        by_dir[dir_name].append(f)
    
    for dir_name, dir_files in by_dir.items():
        if dir_files:
            print(f"\n{dir_name or 'RACINE'}/")
            
            for file_info in dir_files:
                try:
                    os.remove(file_info['path'])
                    print(f"  - Supprime : {os.path.basename(file_info['name'])}")
                    deleted_count += 1
                    total_size_deleted += file_info['size']
                except Exception as e:
                    print(f"  - ECHEC : {os.path.basename(file_info['name'])} - {e}")
                    failed_count += 1
    
    return deleted_count, failed_count, total_size_deleted

def remove_empty_directories(start_dir):
    """Supprime les repertoires vides apres nettoyage"""
    
    removed_dirs = []
    
    # Parcourir de bas en haut pour supprimer les dossiers vides
    for root, dirs, files in os.walk(start_dir, topdown=False):
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            try:
                # Essayer de supprimer le dossier s'il est vide
                if not os.listdir(dir_path):
                    os.rmdir(dir_path)
                    rel_path = os.path.relpath(dir_path, start_dir)
                    removed_dirs.append(rel_path)
                    print(f"  - Dossier vide supprime : {rel_path}/")
            except OSError:
                pass  # Dossier non vide ou erreur
    
    return removed_dirs

def main():
    """Fonction principale de nettoyage massif"""
    
    print("="*80)
    print("  NETTOYEUR MASSIF RECURSIF - PROJET COMPLET")
    print("="*80)
    print("Nettoie TOUS les backups et logs dans TOUT le projet")
    print("Analyse recursive de tous les sous-dossiers")
    print("="*80)
    
    start_dir = os.getcwd()
    
    # 1. Recherche recursive de TOUS les fichiers
    print("\nPhase 1 : BALAYAGE RECURSIF COMPLET")
    print("="*50)
    
    backup_files, log_files = find_all_files_recursive(start_dir)
    
    # 2. Analyse par repertoire
    dir_stats = analyze_by_directory(backup_files, log_files)
    
    # 3. Affichage de l'analyse detaillee
    show_detailed_analysis(dir_stats)
    
    total_files = len(backup_files) + len(log_files)
    total_size = sum(f['size'] for f in backup_files + log_files)
    
    # 4. Si aucun fichier trouve
    if total_files == 0:
        print("\nAucun fichier backup ou log trouve !")
        print("Projet deja parfaitement propre.")
        return
    
    # 5. Top des repertoires les plus touches
    top_dirs = sorted([(dir_name, stats['backups'] + stats['logs']) 
                      for dir_name, stats in dir_stats.items()], 
                     key=lambda x: x[1], reverse=True)
    
    # 6. Demander confirmation pour suppression massive
    if not ask_user_confirmation(total_files, total_size, top_dirs):
        print("\nSuppression annulee par l'utilisateur.")
        print("Aucun fichier n'a ete supprime.")
        return
    
    # 7. Creer une sauvegarde finale critique
    print(f"\n{'='*60}")
    print("CREATION SAUVEGARDE FINALE")
    print("="*60)
    final_backup = create_final_backup()
    
    # 8. Suppression massive
    print(f"\n{'='*60}")
    print("SUPPRESSION MASSIVE EN COURS")
    print("="*60)
    
    backup_deleted, backup_failed, backup_size_deleted = delete_files_by_type(backup_files, "BACKUPS")
    log_deleted, log_failed, log_size_deleted = delete_files_by_type(log_files, "LOGS")
    
    # 9. Suppression des dossiers vides
    print(f"\nSuppression des dossiers vides...")
    removed_dirs = remove_empty_directories(start_dir)
    
    # 10. Rapport final massif
    print(f"\n{'='*70}")
    print("RAPPORT FINAL DE NETTOYAGE MASSIF")
    print("="*70)
    
    print(f"BACKUPS supprimes    : {backup_deleted}/{len(backup_files)} ({format_file_size(backup_size_deleted)})")
    print(f"LOGS supprimes       : {log_deleted}/{len(log_files)} ({format_file_size(log_size_deleted)})")
    print(f"Dossiers vides       : {len(removed_dirs)} supprimes")
    print(f"Total fichiers       : {backup_deleted + log_deleted}/{total_files}")
    print(f"Espace libere        : {format_file_size(backup_size_deleted + log_size_deleted)}")
    print(f"Echecs               : {backup_failed + log_failed}")
    
    if final_backup:
        print(f"Sauvegarde finale    : {final_backup}")
    
    success_rate = ((backup_deleted + log_deleted) / total_files) * 100 if total_files > 0 else 100
    print(f"Taux de reussite     : {success_rate:.1f}%")
    
    if backup_failed + log_failed == 0:
        print(f"\n{'='*50}")
        print("NETTOYAGE MASSIF TERMINE AVEC SUCCES !")
        print("PROJET COMPLETEMENT NETTOYE !")
        print("="*50)
        print("Votre projet est maintenant propre et organise.")
        print("Espace disque libere avec succes.")
    else:
        print(f"\nNETTOYAGE TERMINE AVEC {backup_failed + log_failed} ERREUR(S)")
        print("Verifiez les fichiers qui n'ont pas pu etre supprimes")
    
    print("="*70)

if __name__ == "__main__":
    main()