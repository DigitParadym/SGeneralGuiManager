#!/usr/bin/env python3
"""
Correction de models.py pour declarer hello_user_transform
"""

from pathlib import Path
import re


def fix_models_py(base_path):
    """Corrige models.py pour inclure hello_user_transform."""
    print("=" * 60)
    print("CORRECTION DE MODELS.PY")
    print("=" * 60)
    
    models_file = base_path / "core" / "models.py"
    
    if not models_file.exists():
        print("  [ERREUR] models.py non trouve")
        return False
    
    content = models_file.read_text(encoding='utf-8')
    
    # Chercher et corriger AVAILABLE_ARTISANS
    new_content = re.sub(
        r'AVAILABLE_ARTISANS = \{([^}]+)\}',
        lambda m: 'AVAILABLE_ARTISANS = {\n' + 
                  '    "add_docstrings_transform",\n' +
                  '    "pathlib_transformer_optimized",\n' +
                  '    "print_to_logging_transform",\n' +
                  '    "unused_import_remover",\n' +
                  '    "hello_user_transform"\n' +
                  '}',
        content,
        flags=re.DOTALL
    )
    
    # Si pas trouve, essayer un autre pattern
    if new_content == content:
        # Chercher juste la ligne AVAILABLE_ARTISANS
        lines = content.split('\n')
        new_lines = []
        in_artisans = False
        fixed = False
        
        for line in lines:
            if 'AVAILABLE_ARTISANS' in line and '{' in line:
                in_artisans = True
                new_lines.append(line)
            elif in_artisans and '}' in line and not fixed:
                # Ajouter hello_user_transform avant la fermeture
                if '"hello_user_transform"' not in content:
                    new_lines.append('    "hello_user_transform",')
                new_lines.append(line)
                in_artisans = False
                fixed = True
            else:
                new_lines.append(line)
        
        new_content = '\n'.join(new_lines)
    
    # Verifier que AVAILABLE_PLUGINS est mis a jour aussi
    if 'AVAILABLE_PLUGINS = AVAILABLE_WRAPPERS | AVAILABLE_ARTISANS' not in new_content:
        # Chercher AVAILABLE_PLUGINS et le corriger
        new_content = re.sub(
            r'AVAILABLE_PLUGINS = \{[^}]+\}',
            'AVAILABLE_PLUGINS = AVAILABLE_WRAPPERS | AVAILABLE_ARTISANS',
            new_content,
            flags=re.DOTALL
        )
    
    # Ecrire le fichier
    models_file.write_text(new_content, encoding='utf-8')
    
    # Verifier le resultat
    if 'hello_user_transform' in new_content:
        print("  [OK] hello_user_transform ajoute dans AVAILABLE_ARTISANS")
    else:
        print("  [ERREUR] Echec de l'ajout")
        return False
    
    return True


def verify_models(base_path):
    """Verifie le contenu de models.py."""
    print("\n" + "=" * 60)
    print("VERIFICATION DE MODELS.PY")
    print("=" * 60)
    
    models_file = base_path / "core" / "models.py"
    content = models_file.read_text(encoding='utf-8')
    
    # Extraire AVAILABLE_ARTISANS
    match = re.search(r'AVAILABLE_ARTISANS = \{([^}]+)\}', content, re.DOTALL)
    
    if match:
        artisans = match.group(1)
        print("  AVAILABLE_ARTISANS contient:")
        for line in artisans.split('\n'):
            if line.strip() and not line.strip().startswith('#'):
                print(f"    {line.strip()}")
        
        if 'hello_user_transform' in artisans:
            print("\n  [OK] hello_user_transform est bien declare")
        else:
            print("\n  [ERREUR] hello_user_transform manquant")
    else:
        print("  [ERREUR] AVAILABLE_ARTISANS non trouve")
    
    return True


def test_validation(base_path):
    """Teste la validation du plan."""
    print("\n" + "=" * 60)
    print("TEST DE VALIDATION")
    print("=" * 60)
    
    import subprocess
    import sys
    
    test_code = '''
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from core.models import AVAILABLE_PLUGINS, AVAILABLE_ARTISANS

print(f"  Artisans disponibles: {len(AVAILABLE_ARTISANS)}")
for artisan in sorted(AVAILABLE_ARTISANS):
    print(f"    - {artisan}")

if "hello_user_transform" in AVAILABLE_ARTISANS:
    print("\\n  [OK] hello_user_transform est dans AVAILABLE_ARTISANS")
else:
    print("\\n  [ERREUR] hello_user_transform non trouve dans AVAILABLE_ARTISANS")

print(f"\\n  Total plugins: {len(AVAILABLE_PLUGINS)}")
'''
    
    test_file = base_path / "test_models.py"
    test_file.write_text(test_code)
    
    result = subprocess.run(
        [sys.executable, str(test_file)],
        capture_output=True,
        text=True,
        cwd=str(base_path)
    )
    
    print(result.stdout)
    if result.stderr:
        print("Erreurs:", result.stderr)
    
    test_file.unlink()
    
    return "[OK]" in result.stdout


def main():
    """Fonction principale."""
    print("\n" + "=" * 60)
    print("CORRECTION MODELS.PY POUR HELLO_USER_TRANSFORM")
    print("=" * 60)
    
    base_path = Path.cwd()
    
    if not (base_path / "core").exists():
        print("ERREUR: Execute depuis la racine du projet")
        return 1
    
    print(f"Repertoire: {base_path}")
    
    # Corriger models.py
    if not fix_models_py(base_path):
        return 1
    
    # Verifier
    verify_models(base_path)
    
    # Tester
    if not test_validation(base_path):
        print("\nERREUR: Validation echouee")
        return 1
    
    print("\n" + "=" * 60)
    print("CORRECTION TERMINEE")
    print("=" * 60)
    print("\nLe plan JSON devrait maintenant fonctionner")
    
    return 0


if __name__ == "__main__":
    exit(main())