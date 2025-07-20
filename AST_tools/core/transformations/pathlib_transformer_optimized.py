#!/usr/bin/env python3

"""
Transformateur PathLib Converter - Version Optimisee avec Variable Tracking
===========================================================================

Ce transformateur modernise le code Python en convertissant l'ancienne 
manipulation de chemins avec os.path vers la nouvelle approche pathlib.

NOUVEAU: Tracking intelligent des variables Path pour eviter les repetitions.

Transformations effectuees:
- os.path.join() -> Path() / operator
- os.path.exists() -> Path().exists() OU var.exists() si var est deja Path
- os.path.isfile() -> Path().is_file() OU var.is_file() si var est deja Path
- os.path.isdir() -> Path().is_dir() OU var.is_dir() si var est deja Path
- os.path.basename() -> Path().name OU var.name si var est deja Path
- os.path.dirname() -> Path().parent OU var.parent si var est deja Path
- os.path.abspath() -> Path().resolve() OU var.resolve() si var est deja Path
- os.path.splitext() -> (Path().stem, Path().suffix)
- os.path.expanduser() -> Path().expanduser()
- open(path) -> Path(path).open() OU path.open() si path est deja Path
- Ajoute l'import pathlib si necessaire

Auteur: Systeme de Transformations AST
Version: 3.0 - Version Optimisee avec Variable Tracking
"""

import ast
import re
from typing import Dict, Any, List, Set
from core.base_transformer import BaseTransformer


class PathLibConverterTransform(BaseTransformer):
    """Convertit les appels os.path vers pathlib.Path - Version Optimisee avec Variable Tracking."""
    
    def __init__(self):
        super().__init__()
        self.needs_pathlib_import = False
        self.transformations_count = 0
        self.optimizations_count = 0
        
        # Mapping des transformations os.path vers pathlib
        self.path_mappings = {
            'join': self._handle_join,
            'exists': self._handle_exists,
            'isfile': self._handle_isfile,
            'isdir': self._handle_isdir, 
            'basename': self._handle_basename,
            'dirname': self._handle_dirname,
            'abspath': self._handle_abspath,
            'splitext': self._handle_splitext,
            'expanduser': self._handle_expanduser
        }
        
    def get_metadata(self) -> Dict[str, Any]:
        """Retourne les metadonnees du transformateur."""
        return {
            'name': 'PathLib Converter Optimized',
            'description': 'Convertit os.path vers pathlib.Path avec optimisation variable tracking',
            'version': '3.0',
            'author': 'Systeme AST Optimise'
        }
    
    def can_transform(self, code_source: str) -> bool:
        """Verifie si le code contient des appels os.path a convertir."""
        os_path_patterns = [
            r'os\.path\.',
            r'from os\.path import',
            r'import os\.path'
        ]
        
        for pattern in os_path_patterns:
            if re.search(pattern, code_source):
                return True
        return False
    
    def get_imports_required(self) -> List[str]:
        """Retourne les imports requis."""
        return ["from pathlib import Path"]
    
    def transform(self, code_source: str) -> str:
        """Applique la transformation os.path vers pathlib avec optimisations."""
        try:
            # Reset des compteurs
            self.needs_pathlib_import = False
            self.transformations_count = 0
            self.optimizations_count = 0
            
            # Parser le code en AST
            tree = ast.parse(code_source)
            
            # Phase 1: Analyser et identifier les variables Path
            analyzer = PathVariableAnalyzer()
            analyzer.visit(tree)
            
            # Phase 2: Transformer avec connaissance des variables Path
            transformer = PathLibNodeTransformerOptimized(self, analyzer.path_variables)
            new_tree = transformer.visit(tree)
            
            # Fixer les locations manquantes
            ast.fix_missing_locations(new_tree)
            
            # Reconvertir en code
            new_code = ast.unparse(new_tree)
            
            # Ajouter l'import pathlib si necessaire
            if self.needs_pathlib_import:
                new_code = self._add_pathlib_import(new_code)
            
            # Nettoyage final
            new_code = self._cleanup_code(new_code)
            
            print(f"+ PathLib Converter: {self.transformations_count} transformation(s) appliquee(s)")
            print(f"+ Optimisations: {self.optimizations_count} repetition(s) evitee(s)")
            
            return new_code
            
        except Exception as e:
            print(f"X Erreur transformation pathlib: {e}")
            return code_source
    
    def _add_pathlib_import(self, code: str) -> str:
        """Ajoute l'import pathlib si necessaire."""
        lines = code.split('\n')
        
        # Verifier si pathlib est deja importe
        has_pathlib = any('from pathlib import Path' in line or 
                         'import pathlib' in line for line in lines)
        
        if has_pathlib:
            return code
        
        # Trouver ou inserer l'import
        import_line = 0
        for i, line in enumerate(lines):
            if line.strip().startswith('import ') or line.strip().startswith('from '):
                import_line = i + 1
            elif line.strip() and not line.strip().startswith('#'):
                break
        
        # Inserer l'import
        lines.insert(import_line, 'from pathlib import Path')
        
        return '\n'.join(lines)
    
    def _cleanup_code(self, code: str) -> str:
        """Nettoie le code genere."""
        # Supprimer les imports os.path inutiles si plus utilises
        lines = code.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Supprimer import os.path si plus utilise
            if ('import os.path' in line and 
                'os.path.' not in code.replace(line, '')):
                continue
            # Supprimer from os.path import si plus utilise  
            elif ('from os.path import' in line and
                  not any(f'os.path.{func}' in code for func in self.path_mappings.keys())):
                continue
            cleaned_lines.append(line)
        
        # Supprimer les lignes vides en exces
        result = '\n'.join(cleaned_lines)
        result = re.sub(r'\n\s*\n\s*\n', '\n\n', result)
        
        return result
    
    def _handle_join(self, args):
        """Gere os.path.join() -> Path() / operator."""
        if not args:
            return ast.Call(func=ast.Name(id='Path', ctx=ast.Load()), args=[], keywords=[])
        
        # Commencer par Path(premier_arg)
        result = ast.Call(
            func=ast.Name(id='Path', ctx=ast.Load()),
            args=[args[0]],
            keywords=[]
        )
        
        # Ajouter / arg pour chaque argument suivant
        for arg in args[1:]:
            result = ast.BinOp(
                left=result,
                op=ast.Div(),  # Operateur /
                right=arg
            )
        
        return result
    
    def _handle_exists(self, args):
        """Gere os.path.exists() -> Path().exists()."""
        if not args:
            return None
        
        path_call = ast.Call(
            func=ast.Name(id='Path', ctx=ast.Load()),
            args=[args[0]],
            keywords=[]
        )
        
        return ast.Call(
            func=ast.Attribute(value=path_call, attr='exists', ctx=ast.Load()),
            args=[],
            keywords=[]
        )
    
    def _handle_isfile(self, args):
        """Gere os.path.isfile() -> Path().is_file()."""
        if not args:
            return None
        
        path_call = ast.Call(
            func=ast.Name(id='Path', ctx=ast.Load()),
            args=[args[0]],
            keywords=[]
        )
        
        return ast.Call(
            func=ast.Attribute(value=path_call, attr='is_file', ctx=ast.Load()),
            args=[],
            keywords=[]
        )
    
    def _handle_isdir(self, args):
        """Gere os.path.isdir() -> Path().is_dir()."""
        if not args:
            return None
        
        path_call = ast.Call(
            func=ast.Name(id='Path', ctx=ast.Load()),
            args=[args[0]],
            keywords=[]
        )
        
        return ast.Call(
            func=ast.Attribute(value=path_call, attr='is_dir', ctx=ast.Load()),
            args=[],
            keywords=[]
        )
    
    def _handle_basename(self, args):
        """Gere os.path.basename() -> Path().name."""
        if not args:
            return None
        
        path_call = ast.Call(
            func=ast.Name(id='Path', ctx=ast.Load()),
            args=[args[0]],
            keywords=[]
        )
        
        return ast.Attribute(value=path_call, attr='name', ctx=ast.Load())
    
    def _handle_dirname(self, args):
        """Gere os.path.dirname() -> Path().parent."""
        if not args:
            return None
        
        path_call = ast.Call(
            func=ast.Name(id='Path', ctx=ast.Load()),
            args=[args[0]],
            keywords=[]
        )
        
        return ast.Attribute(value=path_call, attr='parent', ctx=ast.Load())
    
    def _handle_abspath(self, args):
        """Gere os.path.abspath() -> Path().resolve()."""
        if not args:
            return None
        
        path_call = ast.Call(
            func=ast.Name(id='Path', ctx=ast.Load()),
            args=[args[0]],
            keywords=[]
        )
        
        return ast.Call(
            func=ast.Attribute(value=path_call, attr='resolve', ctx=ast.Load()),
            args=[],
            keywords=[]
        )
    
    def _handle_splitext(self, args):
        """Gere os.path.splitext() -> (Path().stem, Path().suffix)."""
        if not args:
            return None
        
        path_call = ast.Call(
            func=ast.Name(id='Path', ctx=ast.Load()),
            args=[args[0]],
            keywords=[]
        )
        
        # Retourner un tuple (stem, suffix)
        stem = ast.Attribute(value=path_call, attr='stem', ctx=ast.Load())
        suffix = ast.Attribute(
            value=ast.Call(func=ast.Name(id='Path', ctx=ast.Load()), args=[args[0]], keywords=[]),
            attr='suffix', 
            ctx=ast.Load()
        )
        
        return ast.Tuple(elts=[stem, suffix], ctx=ast.Load())
    
    def _handle_expanduser(self, args):
        """Gere os.path.expanduser() -> Path().expanduser()."""
        if not args:
            return None
        
        path_call = ast.Call(
            func=ast.Name(id='Path', ctx=ast.Load()),
            args=[args[0]],
            keywords=[]
        )
        
        return ast.Call(
            func=ast.Attribute(value=path_call, attr='expanduser', ctx=ast.Load()),
            args=[],
            keywords=[]
        )
    
    def preview_changes(self, code_source: str) -> Dict[str, Any]:
        """Previsualise les changements."""
        os_path_count = len(re.findall(r'os\.path\.', code_source))
        detected_functions = []
        
        for func_name in self.path_mappings.keys():
            pattern = f'os\\.path\\.{func_name}'
            if re.search(pattern, code_source):
                detected_functions.append(func_name)
        
        return {
            'applicable': self.can_transform(code_source),
            'description': f'Conversion optimisee de {os_path_count} appel(s) os.path vers pathlib.Path',
            'estimated_changes': os_path_count,
            'details': {
                'functions_detected': detected_functions,
                'total_os_path_calls': os_path_count,
                'optimization': 'Variable tracking pour eviter les repetitions'
            },
            'impact': 'Modernisation du code avec optimisations de performance'
        }


class PathVariableAnalyzer(ast.NodeVisitor):
    """Analyse le code pour identifier les variables qui deviendront des objets Path."""
    
    def __init__(self):
        self.path_variables: Set[str] = set()
        self.potential_path_variables: Set[str] = set()
        
    def visit_Assign(self, node):
        """Analyse les assignations pour identifier les variables Path."""
        
        # Cas 1: var = os.path.join(...)
        if (isinstance(node.value, ast.Call) and
            isinstance(node.value.func, ast.Attribute) and
            isinstance(node.value.func.value, ast.Attribute) and
            isinstance(node.value.func.value.value, ast.Name) and
            node.value.func.value.value.id == 'os' and
            node.value.func.value.attr == 'path'):
            
            # Cette variable deviendra un Path
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self.path_variables.add(target.id)
                    print(f"  * Variable identifiee comme Path: {target.id}")
        
        # Cas 2: var = Path(...)
        elif (isinstance(node.value, ast.Call) and
              isinstance(node.value.func, ast.Name) and
              node.value.func.id == 'Path'):
            
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self.path_variables.add(target.id)
                    print(f"  * Variable identifiee comme Path: {target.id}")
        
        # Cas 3: var = autre_path_var.parent / autre_path_var.name (attributs Path)
        elif (isinstance(node.value, ast.Attribute) and
              isinstance(node.value.value, ast.Name) and
              node.value.value.id in self.path_variables and
              node.value.attr in ['parent', 'name', 'stem', 'suffix']):
            
            for target in node.targets:
                if isinstance(target, ast.Name):
                    if node.value.attr in ['parent']:  # parent retourne aussi un Path
                        self.path_variables.add(target.id)
                        print(f"  * Variable derivee identifiee comme Path: {target.id}")
        
        # Cas 4: var = path_var / "something" (division avec Path)
        elif (isinstance(node.value, ast.BinOp) and
              isinstance(node.value.op, ast.Div) and
              isinstance(node.value.left, ast.Name) and
              node.value.left.id in self.path_variables):
            
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self.path_variables.add(target.id)
                    print(f"  * Variable derivee identifiee comme Path: {target.id}")
        
        self.generic_visit(node)


class PathLibNodeTransformerOptimized(ast.NodeTransformer):
    """Transformateur AST optimise avec connaissance des variables Path."""
    
    def __init__(self, parent_transformer, path_variables: Set[str]):
        self.parent = parent_transformer
        self.path_variables = path_variables
    
    def visit_Assign(self, node):
        """Gere les assignations et met a jour le tracking des variables."""
        
        # Traiter d'abord les enfants
        node = self.generic_visit(node)
        
        # Si on assigne le resultat d'une transformation os.path.join -> Path() / 
        # Alors marquer la variable comme Path
        if (isinstance(node.value, ast.BinOp) and
            isinstance(node.value.op, ast.Div) and
            isinstance(node.value.left, ast.Call) and
            isinstance(node.value.left.func, ast.Name) and
            node.value.left.func.id == 'Path'):
            
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self.path_variables.add(target.id)
                    print(f"  * Nouvelle variable Path trackee: {target.id}")
        
        return node
    
    def visit_Call(self, node):
        """Convertit les appels de fonction os.path.* avec optimisations."""
        
        # Gerer os.path.function(args) avec optimisation
        if (isinstance(node.func, ast.Attribute) and
            isinstance(node.func.value, ast.Attribute) and
            isinstance(node.func.value.value, ast.Name) and
            node.func.value.value.id == 'os' and
            node.func.value.attr == 'path'):
            
            func_name = node.func.attr
            
            if func_name in self.parent.path_mappings:
                self.parent.needs_pathlib_import = True
                self.parent.transformations_count += 1
                
                # OPTIMISATION: Si l'argument est deja une variable Path connue
                if (len(node.args) > 0 and
                    isinstance(node.args[0], ast.Name) and
                    node.args[0].id in self.path_variables):
                    
                    # Utiliser directement la variable sans recreer Path()
                    var_name = node.args[0].id
                    self.parent.optimizations_count += 1
                    
                    result = self._create_optimized_call(var_name, func_name)
                    if result:
                        print(f"  + OPTIMISE: {var_name}.{self._get_pathlib_method(func_name)}() (evite Path({var_name}))")
                        return result
                
                # Transformation normale si pas d'optimisation possible
                handler = self.parent.path_mappings[func_name]
                result = handler(node.args)
                
                if result:
                    print(f"  + Transforme os.path.{func_name}() -> Path().{func_name}()")
                    return result
        
        # Gerer open(path, ...) -> Path(path).open(...) avec optimisation
        elif (isinstance(node.func, ast.Name) and 
              node.func.id == 'open' and 
              len(node.args) > 0):
            
            # OPTIMISATION: Si l'argument est deja une variable Path
            if (isinstance(node.args[0], ast.Name) and
                node.args[0].id in self.path_variables):
                
                self.parent.needs_pathlib_import = True
                self.parent.transformations_count += 1
                self.parent.optimizations_count += 1
                
                var_name = node.args[0].id
                result = ast.Call(
                    func=ast.Attribute(
                        value=ast.Name(id=var_name, ctx=ast.Load()),
                        attr='open',
                        ctx=ast.Load()
                    ),
                    args=node.args[1:],  # Tous les arguments sauf le premier
                    keywords=node.keywords
                )
                
                print(f"  + OPTIMISE: {var_name}.open() (evite Path({var_name}).open())")
                return result
            
            # Transformation normale si le chemin ressemble a un path
            elif self._looks_like_path(node.args[0]):
                self.parent.needs_pathlib_import = True
                self.parent.transformations_count += 1
                
                path_call = ast.Call(
                    func=ast.Name(id='Path', ctx=ast.Load()),
                    args=[node.args[0]],
                    keywords=[]
                )
                
                result = ast.Call(
                    func=ast.Attribute(value=path_call, attr='open', ctx=ast.Load()),
                    args=node.args[1:],
                    keywords=node.keywords
                )
                
                print(f"  + Transforme open() -> Path().open()")
                return result
        
        return self.generic_visit(node)
    
    def _create_optimized_call(self, var_name: str, os_path_func: str):
        """Cree un appel optimise pour une variable Path existante."""
        
        # Mapping des fonctions os.path vers les methodes/attributs pathlib
        pathlib_mapping = {
            'exists': ('exists', True),    # (nom_methode, est_methode)
            'isfile': ('is_file', True),
            'isdir': ('is_dir', True),
            'basename': ('name', False),   # Attribut, pas methode
            'dirname': ('parent', False),
            'abspath': ('resolve', True),
            'expanduser': ('expanduser', True)
        }
        
        if os_path_func not in pathlib_mapping:
            return None
        
        pathlib_attr, is_method = pathlib_mapping[os_path_func]
        
        var_node = ast.Name(id=var_name, ctx=ast.Load())
        attr_node = ast.Attribute(value=var_node, attr=pathlib_attr, ctx=ast.Load())
        
        if is_method:
            # Retourner un appel de methode: var.method()
            return ast.Call(func=attr_node, args=[], keywords=[])
        else:
            # Retourner un attribut: var.attribute
            return attr_node
    
    def _get_pathlib_method(self, os_path_func: str) -> str:
        """Retourne le nom de la methode pathlib correspondante."""
        mapping = {
            'exists': 'exists',
            'isfile': 'is_file',
            'isdir': 'is_dir',
            'basename': 'name',
            'dirname': 'parent',
            'abspath': 'resolve',
            'expanduser': 'expanduser'
        }
        return mapping.get(os_path_func, os_path_func)
    
    def _looks_like_path(self, node):
        """Heuristique pour detecter si un argument ressemble a un chemin."""
        # String litterale contenant / ou \ ou .
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return ('/' in node.value or '\\' in node.value or 
                   '.' in node.value or node.value.startswith('~'))
        
        # Variable avec nom suggerant un chemin
        elif isinstance(node, ast.Name):
            path_keywords = ['path', 'file', 'dir', 'folder', 'chemin', 'fichier', 'filename']
            return any(keyword in node.id.lower() for keyword in path_keywords)
        
        return False


# Exemple d'utilisation pour les tests
if __name__ == "__main__":
    transformer = PathLibConverterTransform()
    
    # Code d'exemple a transformer
    sample_code = '''
import os
import os.path

def process_files(base_dir, filename):
    # Test de toutes les fonctions os.path avec repetitions
    full_path = os.path.join(base_dir, filename)
    
    if os.path.exists(full_path):
        if os.path.isfile(full_path):
            # Ouvrir le fichier - devrait etre optimise
            with open(full_path, 'r') as f:
                content = f.read()
            
            # Extraire les informations du chemin - devrait etre optimise
            backup_dir = os.path.dirname(full_path)
            file_name = os.path.basename(full_path)
            absolute_path = os.path.abspath(full_path)
            
            # Operations sur le nom de fichier
            name_only, extension = os.path.splitext(file_name)
            
            # Chemin utilisateur
            home_path = os.path.expanduser("~/documents")
            
            # Test sur une variable derivee
            if os.path.exists(backup_dir):
                print("Backup dir exists")
            
            return content
        elif os.path.isdir(full_path):
            print("C'est un dossier")
    
    return None

def main():
    result = process_files("/home/user", "data.txt")
    print(result)
'''
    
    print("=== CODE ORIGINAL ===")
    print(sample_code)
    print("\n" + "="*50 + "\n")
    
    if transformer.can_transform(sample_code):
        print("=== APERCU DES CHANGEMENTS ===")
        preview = transformer.preview_changes(sample_code)
        print(f"Description: {preview['description']}")
        print(f"Fonctions detectees: {preview['details']['functions_detected']}")
        print(f"Optimisation: {preview['details']['optimization']}")
        print(f"Impact: {preview['impact']}")
        
        print("\n=== ANALYSE ET TRANSFORMATION OPTIMISEE ===")
        transformed = transformer.transform(sample_code)
        print("\n=== CODE TRANSFORME OPTIMISE ===")
        print(transformed)
    else:
        print("Aucune transformation necessaire")
