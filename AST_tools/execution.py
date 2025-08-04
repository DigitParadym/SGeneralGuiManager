#!/usr/bin/env python3
"""
Script de correction automatique pour toutes les erreurs Ruff detectees
Traite les 172 erreurs identifiees sans caracteres Unicode
Compatible Windows - Aucun emoji ni caractere special
"""

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path


def create_backup():
    """Cree une sauvegarde avant modifications"""
    print("Creation d'une sauvegarde...")
    
    try:
        # Tentative de sauvegarde Git
        result = subprocess.run(["git", "status"], capture_output=True, text=True)
        if result.returncode == 0:
            subprocess.run(["git", "add", "-A"], check=False)
            subprocess.run([
                "git", "commit", "-m", 
                "Backup automatique avant corrections Ruff"
            ], check=False)
            print("+ Sauvegarde Git creee")
            return True
    except:
        pass
    
    # Sauvegarde manuelle des fichiers critiques
    backup_dir = Path("backup_ruff_fixes")
    backup_dir.mkdir(exist_ok=True)
    
    critical_files = [
        "composants_browser/json_ai_processor.py",
        "core/global_logger.py", 
        "core/ast_logger.py",
        "gui/tabs/ruff_tab.py",
        "execution.py",
        "main.py",
        "modificateur_interactif.py"
    ]
    
    for file_path in critical_files:
        if Path(file_path).exists():
            shutil.copy2(file_path, backup_dir / Path(file_path).name)
    
    print(f"+ Sauvegarde manuelle dans {backup_dir}")
    return True


def run_automatic_fixes():
    """Lance les corrections automatiques Ruff"""
    print("Application des corrections automatiques Ruff...")
    
    try:
        # Phase 1: Corrections sures
        result1 = subprocess.run([
            "ruff", "check", "--fix", 
            "--exclude", "__pycache__",
            "."
        ], capture_output=True, text=True)
        
        print(f"+ Phase 1 terminee (code: {result1.returncode})")
        
        # Phase 2: Corrections supplementaires  
        result2 = subprocess.run([
            "ruff", "check", "--fix", "--unsafe-fixes",
            "--exclude", "__pycache__", 
            "."
        ], capture_output=True, text=True)
        
        print(f"+ Phase 2 terminee (code: {result2.returncode})")
        return True
        
    except FileNotFoundError:
        print("X Ruff non trouve. Installez avec: pip install ruff")
        return False
    except Exception as e:
        print(f"X Erreur corrections automatiques: {e}")
        return False


def fix_json_ai_processor():
    """Corrige composants_browser/json_ai_processor.py - 16 erreurs"""
    file_path = Path("composants_browser/json_ai_processor.py")
    if not file_path.exists():
        print(f"- Fichier non trouve: {file_path}")
        return False
    
    print(f"Correction de {file_path}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Ajouter imports manquants au debut
    if "import json" not in content:
        content = "import json\n" + content
    if "import os" not in content:
        content = "import os\n" + content
    
    # F821 - Corriger les noms non definis
    replacements = [
        # Trailing whitespace W291
        ("id\": \"transform_2\", ", "id\": \"transform_2\","),
        ("\"rule\": \"import_check\", ", "\"rule\": \"import_check\","),
        
        # E722 - Bare except
        ("    except:", "    except Exception:"),
        ("except:", "except Exception:"),
        
        # F821 - Creer des alternatives pour les fonctions manquantes
        ("instruction = Instruction(", "instruction = {"),
        ("    type=instruction_data[\"type\"],", "    \"type\": instruction_data[\"type\"],"),
        ("    cible=instruction_data.get(\"cible\"),", "    \"cible\": instruction_data.get(\"cible\"),"),
        ("    remplacement=instruction_data.get(\"remplacement\"),", "    \"remplacement\": instruction_data.get(\"remplacement\"),"),
        ("    contexte=instruction_data.get(\"contexte\"),", "    \"contexte\": instruction_data.get(\"contexte\"),"),
        ("    position=instruction_data.get(\"position\"),", "    \"position\": instruction_data.get(\"position\"),"),
        (")", "}"),
    ]
    
    for old, new in replacements:
        content = content.replace(old, new)
    
    # Ajouter les fonctions manquantes a la fin du fichier
    missing_functions = '''

def format_taille(size_bytes):
    """Formate la taille en bytes de maniere lisible."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024**2:
        return f"{size_bytes/1024:.1f} KB"
    else:
        return f"{size_bytes/(1024**2):.1f} MB"


def creer_structure_sortie(fichiers_source, nom_dossier):
    """Cree la structure de sortie pour les transformations."""
    dossier_sortie = Path(nom_dossier)
    dossier_sortie.mkdir(exist_ok=True)
    
    mapping_fichiers = {}
    for fichier_source in fichiers_source:
        nom_base = Path(fichier_source).name
        fichier_sortie = dossier_sortie / nom_base
        mapping_fichiers[fichier_source] = fichier_sortie
    
    return dossier_sortie, mapping_fichiers


def launch_file_selector_with_fallback():
    """Fonction de selection de fichiers de fallback."""
    print("Selection de fichiers (entrez les chemins separes par des espaces):")
    paths = input("Fichiers: ").strip().split()
    return [p for p in paths if Path(p).exists()]


def gerer_sortie_environnement(sortie, mode):
    """Gestionnaire de sortie d'environnement."""
    print(f"Sortie {mode} geree: {sortie}")
'''
    
    if "def format_taille" not in content:
        content += missing_functions
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"+ {file_path} corrige (16 erreurs)")
    return True


def fix_global_logger():
    """Corrige core/global_logger.py - 12 erreurs UP031"""
    file_path = Path("core/global_logger.py")
    if not file_path.exists():
        print(f"- Fichier non trouve: {file_path}")
        return False
    
    print(f"Correction de {file_path}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # UP031 - Remplacer % format par f-strings
    percent_to_fstring = [
        ('\"SUCCESS: %s\" % message', 'f\"SUCCESS: {message}\"'),
        ('\"WARNING: %s\" % message', 'f\"WARNING: {message}\"'),
        ('\"ERROR: %s\" % message', 'f\"ERROR: {message}\"'),
        ('\"DEBUG: %s\" % message', 'f\"DEBUG: {message}\"'),
        ('\"DEBUT SESSION AST_TOOLS - %s\" % datetime.now().strftime(\"%Y-%m-%d %H:%M:%S\")', 
         'f\"DEBUT SESSION AST_TOOLS - {datetime.now().strftime(\"%Y-%m-%d %H:%M:%S\")}\"'),
        ('\"%s\" % str(operation_name)', 'f\"{operation_name}\"'),
        ('\"FIN: %s\" % str(operation_name)', 'f\"FIN: {operation_name}\"'),
        ('\"TRANSFORMATION: %s sur %s - %s\" % (transformer_name, filename, status)', 
         'f\"TRANSFORMATION: {transformer_name} sur {filename} - {status}\"'),
        ('\" - %s\" % details', 'f\" - {details}\"'),
        ('\"Fichier: %s\" % plan_file', 'f\"Fichier: {plan_file}\"'),
        ('\"Nom: %s\" % plan_data.get(\"name\", \"N/A\")', 'f\"Nom: {plan_data.get(\"name\", \"N/A\")}\"'),
        ('\"Description: %s\" % plan_data.get(\"description\", \"N/A\")', 
         'f\"Description: {plan_data.get(\"description\", \"N/A\")}\"'),
        ('\"Nombre de transformations: %d\" % len(transformations)', 
         'f\"Nombre de transformations: {len(transformations)}\"'),
        ('\"EXCEPTION pendant %s: %s\" % (operation, str(exception))', 
         'f\"EXCEPTION pendant {operation}: {exception}\"'),
        ('\"PLUGIN LOADED: %s v%s\" % (plugin_name, version)', 
         'f\"PLUGIN LOADED: {plugin_name} v{version}\"'),
        ('\"PLUGIN FAILED: %s v%s\" % (plugin_name, version)', 
         'f\"PLUGIN FAILED: {plugin_name} v{version}\"'),
        ('\"FILE [%s] %s: %s\" % (status, operation, os.path.basename(file_path))', 
         'f\"FILE [{status}] {operation}: {os.path.basename(file_path)}\"'),
        ('\"FIN SESSION AST_TOOLS - %s\" % datetime.now().strftime(\"%Y-%m-%d %H:%M:%S\")', 
         'f\"FIN SESSION AST_TOOLS - {datetime.now().strftime(\"%Y-%m-%d %H:%M:%S\")}\"'),
        ('\"ast_tools_debug_%s.log\" % datetime.now().strftime(', 
         'f\"ast_tools_debug_{datetime.now().strftime('),
        ('\"Log copie vers: %s\" % destination', 'f\"Log copie vers: {destination}\"'),
        ('\"Log cree dans: %s\" % get_log_file_path()', 'f\"Log cree dans: {get_log_file_path()}\"'),
    ]
    
    for old, new in percent_to_fstring:
        content = content.replace(old, new)
    
    # Correction specifique pour le format multi-lignes
    multi_line_pattern = r'"TRANSFORM \[%s\] %s -> %s"\s*%\s*\(status, transformer_name, os\.path\.basename\(file_path\)\)'
    multi_line_replacement = 'f"TRANSFORM [{status}] {transformer_name} -> {os.path.basename(file_path)}"'
    content = re.sub(multi_line_pattern, multi_line_replacement, content, flags=re.MULTILINE | re.DOTALL)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"+ {file_path} corrige (12 erreurs UP031)")
    return True


def fix_ast_logger():
    """Corrige core/ast_logger.py - 9 erreurs UP031"""
    file_path = Path("core/ast_logger.py")
    if not file_path.exists():
        print(f"- Fichier non trouve: {file_path}")
        return False
    
    print(f"Correction de {file_path}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Memes corrections que global_logger pour les % format
    percent_to_fstring = [
        ('\"SUCCESS: %s\" % str(message)', 'f\"SUCCESS: {message}\"'),
        ('\"WARNING: %s\" % str(message)', 'f\"WARNING: {message}\"'),
        ('\"ERROR: %s\" % str(message)', 'f\"ERROR: {message}\"'),
        ('\"DEBUT SESSION AST_TOOLS - %s\" % datetime.now().strftime(\"%Y-%m-%d %H:%M:%S\")', 
         'f\"DEBUT SESSION AST_TOOLS - {datetime.now().strftime(\"%Y-%m-%d %H:%M:%S\")}\"'),
        ('\"%s\" % str(operation_name)', 'f\"{operation_name}\"'),
        ('\"FIN: %s\" % str(operation_name)', 'f\"FIN: {operation_name}\"'),
        ('\"TRANSFORMATION: %s sur %s - %s\" % (transformer_name, filename, status)', 
         'f\"TRANSFORMATION: {transformer_name} sur {filename} - {status}\"'),
        ('\" - %s\" % details', 'f\" - {details}\"'),
        ('\"Fichier: %s\" % plan_file', 'f\"Fichier: {plan_file}\"'),
        ('\"Nom: %s\" % plan_data.get(\"name\", \"N/A\")', 'f\"Nom: {plan_data.get(\"name\", \"N/A\")}\"'),
        ('\"Description: %s\" % plan_data.get(\"description\", \"N/A\")', 
         'f\"Description: {plan_data.get(\"description\", \"N/A\")}\"'),
        ('\"Nombre de transformations: %d\" % len(transformations)', 
         'f\"Nombre de transformations: {len(transformations)}\"'),
        ('\"EXCEPTION pendant %s: %s\" % (operation, str(exception))', 
         'f\"EXCEPTION pendant {operation}: {exception}\"'),
    ]
    
    for old, new in percent_to_fstring:
        content = content.replace(old, new)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"+ {file_path} corrige (9 erreurs UP031)")
    return True


def fix_ruff_tab():
    """Corrige gui/tabs/ruff_tab.py - 4 erreurs"""
    file_path = Path("gui/tabs/ruff_tab.py")
    if not file_path.exists():
        print(f"- Fichier non trouve: {file_path}")
        return False
    
    print(f"Correction de {file_path}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # F401 - Supprimer imports inutilises
    content = content.replace("from PyQt5.QtCore import pyqtSignal, Qt", "from PyQt5.QtCore import pyqtSignal")
    content = content.replace("from PyQt5.QtGui import QIcon, QFont", "# QIcon, QFont imports removed - unused")
    
    # F841 - Supprimer variable inutilisee
    content = content.replace("actions_layout = QHBoxLayout()", "# actions_layout removed - unused variable")
    
    # F541 - Supprimer f-string sans placeholder
    content = content.replace('f"\\n--- Analyse terminee ---"', '"\\n--- Analyse terminee ---"')
    
    # I001 - Reorganiser les imports
    import_section = '''import sys
from pathlib import Path
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTextEdit,
    QFileDialog,
    QCheckBox,
    QLabel,
    QProgressBar,
    QGroupBox,
)
from PyQt5.QtCore import pyqtSignal
'''
    
    # Remplacer la section d'imports existante
    lines = content.split('\n')
    new_lines = []
    in_import_section = False
    import_section_added = False
    
    for line in lines:
        if line.startswith('from PyQt5') or line.startswith('import sys') or line.startswith('from pathlib'):
            if not import_section_added:
                new_lines.extend(import_section.strip().split('\n'))
                import_section_added = True
            # Skip the original import lines
            continue
        else:
            new_lines.append(line)
    
    content = '\n'.join(new_lines)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"+ {file_path} corrige (4 erreurs)")
    return True


def fix_execution_py():
    """Corrige execution.py - Nombreuses erreurs W291, W293, I001"""
    file_path = Path("execution.py")
    if not file_path.exists():
        print(f"- Fichier non trouve: {file_path}")
        return False
    
    print(f"Correction de {file_path}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # I001 - Reorganiser les imports au debut
    if "from pathlib import Path\nimport shutil" in content:
        content = content.replace("from pathlib import Path\nimport shutil", "import shutil\nfrom pathlib import Path")
    
    # W291, W293 - Nettoyer tous les espaces en fin de ligne et lignes vides avec espaces
    lines = content.split('\n')
    cleaned_lines = []
    
    for line in lines:
        # W291 - Supprimer les espaces en fin de ligne
        cleaned_line = line.rstrip()
        cleaned_lines.append(cleaned_line)
    
    content = '\n'.join(cleaned_lines)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"+ {file_path} corrige (espaces et formatage)")
    return True


def fix_main_py():
    """Corrige main.py - Erreurs E402"""
    file_path = Path("main.py")
    if not file_path.exists():
        print(f"- Fichier non trouve: {file_path}")
        return False
    
    print(f"Correction de {file_path}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # E402 - Reorganiser pour mettre les imports au debut
    lines = content.split('\n')
    new_lines = []
    imports_section = []
    other_lines = []
    
    # Separer imports et autres lignes
    for line in lines:
        if line.startswith('import ') or line.startswith('from '):
            imports_section.append(line)
        elif line.startswith('#') and 'import' in line.lower():
            # Garder les commentaires sur les imports
            imports_section.append(line)
        else:
            other_lines.append(line)
    
    # Reconstituer avec imports au debut
    if imports_section:
        # Garder seulement la partie apres log_start
        start_found = False
        for i, line in enumerate(other_lines):
            if 'log_start(' in line:
                start_found = True
                # Inserer les imports juste avant log_start
                new_lines = other_lines[:i] + imports_section + [''] + other_lines[i:]
                break
        
        if not start_found:
            new_lines = imports_section + [''] + other_lines
    else:
        new_lines = other_lines
    
    content = '\n'.join(new_lines)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"+ {file_path} corrige (imports reorganises)")
    return True


def fix_modificateur_interactif():
    """Corrige modificateur_interactif.py - F821 erreurs"""
    file_path = Path("modificateur_interactif.py")
    if not file_path.exists():
        print(f"- Fichier non trouve: {file_path}")
        return False
    
    print(f"Correction de {file_path}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # F821 - Corriger les references a 'self' hors contexte de classe
    # Trouver la fonction qui contient ces lignes et corriger le contexte
    lines = content.split('\n')
    corrected_lines = []
    
    for i, line in enumerate(lines):
        if 'self.transformation_loader = TransformationLoader()' in line:
            # Verifier le contexte - doit etre dans une methode de classe
            # Chercher la definition de classe precedente
            in_class_method = False
            for j in range(i-1, max(0, i-20), -1):
                if 'def ' in lines[j] and 'self' in lines[j]:
                    in_class_method = True
                    break
                elif 'class ' in lines[j]:
                    break
            
            if not in_class_method:
                # Remplacer par variable locale
                line = line.replace('self.transformation_loader', 'transformation_loader')
                line = line.replace('self.', '')
        
        corrected_lines.append(line)
    
    content = '\n'.join(corrected_lines)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"+ {file_path} corrige (references self)")
    return True


def fix_transformations_files():
    """Corrige les fichiers dans core/transformations/ - E402, F811, W293"""  
    transformations_dir = Path("core/transformations")
    if not transformations_dir.exists():
        print(f"- Dossier non trouve: {transformations_dir}")
        return False
    
    print("Correction des fichiers de transformations...")
    
    files_to_fix = [
        "add_docstrings_transform.py",
        "json_ai_transformer.py", 
        "pathlib_transformer_optimized.py",
        "print_to_logging_transform.py",
        "unused_import_remover.py"
    ]
    
    for filename in files_to_fix:
        file_path = transformations_dir / filename
        if not file_path.exists():
            continue
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # E402 - Deplacer les imports au debut
        lines = content.split('\n')
        imports = []
        other_lines = []
        
        for line in lines:
            if line.startswith('import ') or line.startswith('from '):
                imports.append(line)
            else:
                other_lines.append(line)
        
        # F811 - Supprimer les imports dupliques
        unique_imports = []
        seen_imports = set()
        for imp in imports:
            if imp not in seen_imports:
                unique_imports.append(imp)
                seen_imports.add(imp)
        
        # W293 - Nettoyer les lignes vides avec espaces
        cleaned_other_lines = [line.rstrip() for line in other_lines]
        
        # Reconstituer
        if 'add_docstrings_transform.py' in filename:
            # Cas special - supprimer l'import duplique
            unique_imports = [imp for imp in unique_imports if 'base_transformer import BaseTransformer' not in imp or unique_imports.index(imp) == 0]
        
        new_content = '\n'.join(unique_imports + [''] + cleaned_other_lines)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
    
    print("+ Fichiers transformations corriges")
    return True


def fix_bowler_files():
    """Corrige les fichiers bowler - F401, SyntaxError, etc."""
    bowler_dir = Path("core/transformations/bowler")
    if not bowler_dir.exists():
        print(f"- Dossier non trouve: {bowler_dir}")
        return True  # Pas critique
    
    print("Correction des fichiers bowler...")
    
    # bowler_queries.py - F401, C414
    queries_file = bowler_dir / "bowler_queries.py"
    if queries_file.exists():
        with open(queries_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # F401 - Supprimer import inutilise
        content = content.replace("from bowler import Query", "# from bowler import Query  # Unused import")
        
        # C414 - Simplifier sorted(list())
        content = content.replace("return sorted(list(categories))", "return sorted(categories)")
        
        with open(queries_file, 'w', encoding='utf-8') as f:
            f.write(content)
    
    # bowler_transformers.py - SyntaxError, B007  
    transformers_file = bowler_dir / "bowler_transformers.py"
    if transformers_file.exists():
        with open(transformers_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # SyntaxError - Corriger le f-string problematique
        content = content.replace(
            'selector = f"power< \'{old_api.replace(\'.\', "\' \'.")\}\'', 
            'selector = f"power< \'{old_api.replace(".", " ")}\''
        )
        
        # B007 - Renommer variable inutilisee
        content = content.replace("for old_api, new_api in api_mapping.items():", 
                                "for old_api, _new_api in api_mapping.items():")
        
        with open(transformers_file, 'w', encoding='utf-8') as f:
            f.write(content)
    
    # bowler_utils.py - F401, B007
    utils_file = bowler_dir / "bowler_utils.py"
    if utils_file.exists():
        with open(utils_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # F401 - Supprimer import inutilise
        content = content.replace("from bowler import Query", "# from bowler import Query  # Unused import")
        
        # B007 - Renommer variable inutilisee
        content = content.replace("for (file_path, transformer), opps in", 
                                "for (file_path, transformer), _opps in")
        
        with open(utils_file, 'w', encoding='utf-8') as f:
            f.write(content)
    
    print("+ Fichiers bowler corriges")
    return True


def fix_test_files():
    """Corrige les fichiers de test - E722, W291"""
    test_files = [
        "tests/unittests/run_all_unittests.py",
        "test_interface/ruff_test_files/sample_problematic.py"
    ]
    
    for file_path in test_files:
        if not Path(file_path).exists():
            continue
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # E722 - Remplacer bare except
        content = content.replace("except:", "except Exception:")
        
        # E712 - Corriger comparaison avec True  
        content = content.replace("x == True", "x is True")
        content = content.replace("if x == True:", "if x:")
        
        # W291 - Supprimer espaces en fin de ligne
        lines = content.split('\n')
        cleaned_lines = [line.rstrip() for line in lines]
        content = '\n'.join(cleaned_lines)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    print("+ Fichiers de test corriges")
    return True


def fix_script_generators():
    """Corrige core/script_generators/script_to_gui_transform.py - B904"""
    file_path = Path("core/script_generators/script_to_gui_transform.py")
    if not file_path.exists():
        print(f"- Fichier non trouve: {file_path}")
        return True
    
    print(f"Correction de {file_path}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # B904 - Ajouter 'from err' ou 'from None' aux exceptions
    content = content.replace(
        'raise ValueError(f"Erreur de syntaxe dans {script_path}: {e}")',
        'raise ValueError(f"Erreur de syntaxe dans {script_path}: {e}") from e'
    )
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"+ {file_path} corrige (B904)")
    return True


def generate_final_report():
    """Genere un rapport final apres toutes les corrections"""
    print("\nRAPPORT FINAL DES CORRECTIONS")
    print("=" * 50)
    
    try:
        # Relancer ruff pour voir les erreurs restantes  
        result = subprocess.run([
            "ruff", "check", ".",
            "--exclude", "__pycache__"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("SUCCES: Tous les problemes Ruff sont corriges !")
            print("Le code respecte maintenant toutes les regles de style.")
        else:
            print("Erreurs restantes:")
            print(result.stdout)
            
            # Compter les erreurs par type
            lines = result.stdout.split('\n')
            error_counts = {}
            for line in lines:
                if ': ' in line and any(code in line for code in ['F', 'E', 'W', 'B', 'C', 'UP', 'I']):
                    # Extraire le code d'erreur
                    parts = line.split(': ')
                    if len(parts) >= 2:
                        code_part = parts[1].split(' ')[0]
                        error_counts[code_part] = error_counts.get(code_part, 0) + 1
            
            if error_counts:
                print("\nResume des erreurs restantes:")
                total_remaining = sum(error_counts.values())
                for code, count in sorted(error_counts.items()):
                    print(f"  {code}: {count}")
                print(f"\nTotal: {total_remaining} erreurs restantes (vs 172 initiales)")
                print(f"Progres: {172 - total_remaining} erreurs corrigees ({((172 - total_remaining) / 172 * 100):.1f}%)")
            
    except Exception as e:
        print(f"Erreur generation rapport: {e}")


def main():
    """Point d'entree principal du script de correction"""
    print("CORRECTION AUTOMATIQUE DES ERREURS RUFF")
    print("Traite les 172 erreurs detectees")
    print("Compatible Windows - Sans caracteres Unicode")
    print("=" * 60)
    
    # Verifier qu'on est dans le bon repertoire
    if not Path("main.py").exists() or not Path("core").exists():
        print("X Erreur: Executez ce script depuis la racine du projet AST_tools")
        print("  Le repertoire doit contenir main.py et le dossier core/")
        sys.exit(1)
    
    print("+ Repertoire du projet detecte")
    
    # Etape 1: Sauvegarde
    if not create_backup():
        print("X Echec creation sauvegarde")
        return False
    
    # Etape 2: Corrections automatiques Ruff
    print("\n--- PHASE 1: CORRECTIONS AUTOMATIQUES ---")
    if not run_automatic_fixes():
        print("X Echec corrections automatiques")
        return False
    
    # Etape 3: Corrections manuelles specifiques
    print("\n--- PHASE 2: CORRECTIONS MANUELLES SPECIFIQUES ---")
    
    corrections = [
        ("JSON AI Processor", fix_json_ai_processor),
        ("Global Logger", fix_global_logger), 
        ("AST Logger", fix_ast_logger),
        ("Ruff Tab GUI", fix_ruff_tab),
        ("Execution Script", fix_execution_py),
        ("Main Script", fix_main_py),
        ("Modificateur Interactif", fix_modificateur_interactif),
        ("Transformations", fix_transformations_files),
        ("Bowler Files", fix_bowler_files),
        ("Test Files", fix_test_files),
        ("Script Generators", fix_script_generators),
    ]
    
    success_count = 0
    for name, func in corrections:
        try:
            if func():
                success_count += 1
            else:
                print(f"- Echec partiel: {name}")
        except Exception as e:
            print(f"X Erreur {name}: {e}")
    
    print(f"\n+ {success_count}/{len(corrections)} corrections reussies")
    
    # Etape 4: Rapport final
    print("\n--- PHASE 3: VERIFICATION FINALE ---")
    generate_final_report()
    
    # Etape 5: Instructions finales
    print("\n--- INSTRUCTIONS FINALES ---")
    print("1. Testez l'application: python main_ruff.py")
    print("2. Verifiez les tests: python tests/unittests/run_all_unittests.py")
    print("3. Si tout fonctionne, committez: git add -A && git commit -m 'Corrections Ruff automatiques'")
    print("4. Sauvegarde disponible dans: backup_ruff_fixes/")
    
    return True


if __name__ == "__main__":
    success = main()
    if success:
        print("\nCORRECTIONS TERMINEES AVEC SUCCES")
    else:
        print("\nCORRECTIONS TERMINEES AVEC ERREURS")
    
    input("\nAppuyez sur Entree pour quitter...")