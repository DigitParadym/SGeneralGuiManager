#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Plugin de Transformation : Suppresseur d'Imports Inutilises
===========================================================

Supprime automatiquement les imports inutilises du code Python.
Version stable sans erreurs de syntaxe.
"""

import ast
import sys
import os
from pathlib import Path
from typing import Dict, Any, List, Set

# Import classe de base
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

try:
    from core.base_transformer import BaseTransformer
except ImportError:
    try:
        from base_transformer import BaseTransformer
    except ImportError:
        from abc import ABC, abstractmethod
        
        class BaseTransformer(ABC):
            @abstractmethod
            def get_metadata(self) -> Dict[str, Any]:
                pass
            
            @abstractmethod
            def transform(self, code_source: str) -> str:
                pass
            
            def can_transform(self, code_source: str) -> bool:
                return True

class UnusedImportRemoverTransform(BaseTransformer):
    """Suppresseur d'imports inutilises."""
    
    def __init__(self):
        super().__init__()
        self.name = "Suppresseur d'Imports Inutilises"
        self.description = "Supprime les imports non utilises"
        self.version = "1.0"
        self.author = "Systeme AST"
        self.imports_removed = 0
        
        # Modules a preserver
        self.preserve_modules = {
            'logging', 'warnings', 'signal', 'threading',
            'multiprocessing', 'django', 'flask', 'pytest'
        }
    
    def get_metadata(self) -> Dict[str, Any]:
        """Retourne les metadonnees."""
        return {
            'name': self.name,
            'description': self.description,
            'version': self.version,
            'author': self.author
        }
    
    def can_transform(self, code_source: str) -> bool:
        """Verifie si transformation applicable."""
        try:
            tree = ast.parse(code_source)
            collector = ImportCollector()
            collector.visit(tree)
            
            unused = collector.imported_names - collector.used_names
            unused = unused - self.preserve_modules
            
            return len(unused) > 0
            
        except:
            return False
    
    def transform(self, code_source: str) -> str:
        """Applique la transformation."""
        try:
            self.imports_removed = 0
            tree = ast.parse(code_source)
            
            # Analyser
            collector = ImportCollector()
            collector.visit(tree)
            
            unused_imports = collector.imported_names - collector.used_names
            unused_imports = unused_imports - self.preserve_modules
            
            if not unused_imports:
                return code_source
            
            # Supprimer
            remover = ImportRemover(unused_imports, self)
            modified_tree = remover.visit(tree)
            
            ast.fix_missing_locations(modified_tree)
            result = ast.unparse(modified_tree)
            
            return self.cleanup_lines(result)
            
        except Exception as e:
            print(f"Erreur transformation: {e}")
            return code_source
    
    def cleanup_lines(self, code: str) -> str:
        """Nettoie les lignes vides."""
        lines = code.split('\\n')
        cleaned = []
        empty_count = 0
        
        for line in lines:
            stripped = line.strip()
            
            if stripped.startswith('#'):
                cleaned.append(line)
                empty_count = 0
            elif stripped == '':
                empty_count += 1
                if empty_count <= 1:
                    cleaned.append(line)
            else:
                empty_count = 0
                cleaned.append(line)
        
        return '\\n'.join(cleaned)
    
    def preview_changes(self, code_source: str) -> Dict[str, Any]:
        """Previsualise les changements."""
        try:
            tree = ast.parse(code_source)
            collector = ImportCollector()
            collector.visit(tree)
            
            unused = collector.imported_names - collector.used_names
            removable = unused - self.preserve_modules
            
            return {
                'applicable': len(removable) > 0,
                'description': f"Supprimera {len(removable)} import(s)",
                'estimated_changes': len(removable),
                'details': {
                    'removable_imports': len(removable),
                    'removable_list': list(removable)
                }
            }
            
        except:
            return {
                'applicable': False,
                'description': "Erreur d'analyse",
                'estimated_changes': 0
            }

class ImportCollector(ast.NodeVisitor):
    """Collecte imports et noms utilises."""
    
    def __init__(self):
        self.imported_names: Set[str] = set()
        self.used_names: Set[str] = set()
        
    def visit_Import(self, node):
        """Visite imports simples."""
        for alias in node.names:
            name = alias.asname or alias.name
            self.imported_names.add(name)
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node):
        """Visite imports from."""
        if node.names[0].name == '*':
            return
        
        for alias in node.names:
            name = alias.asname or alias.name
            self.imported_names.add(name)
        self.generic_visit(node)
    
    def visit_Name(self, node):
        """Visite noms utilises."""
        if isinstance(node.ctx, ast.Load):
            self.used_names.add(node.id)
            
            # Detection typing
            typing_names = {'Optional', 'Dict', 'List', 'Tuple', 'Union', 'Any'}
            if node.id in typing_names:
                self.used_names.add('typing')
        
        self.generic_visit(node)
    
    def visit_Attribute(self, node):
        """Visite attributs."""
        if isinstance(node.value, ast.Name):
            self.used_names.add(node.value.id)
        self.generic_visit(node)

class ImportRemover(ast.NodeTransformer):
    """Supprime les imports inutilises."""
    
    def __init__(self, unused_imports: Set[str], parent):
        self.unused_imports = unused_imports
        self.parent = parent
    
    def visit_Import(self, node):
        """Supprime imports simples."""
        original_count = len(node.names)
        
        node.names = [
            alias for alias in node.names 
            if (alias.asname or alias.name) not in self.unused_imports
        ]
        
        removed = original_count - len(node.names)
        self.parent.imports_removed += removed
        
        return node if node.names else None
    
    def visit_ImportFrom(self, node):
        """Supprime imports from."""
        if node.names[0].name == '*':
            return node
        
        original_count = len(node.names)
        
        node.names = [
            alias for alias in node.names 
            if (alias.asname or alias.name) not in self.unused_imports
        ]
        
        removed = original_count - len(node.names)
        self.parent.imports_removed += removed
        
        return node if node.names else None

# Test du plugin
if __name__ == "__main__":
    transformer = UnusedImportRemoverTransform()
    
    test_code = """
import os
import sys
import json

def main():
    print(sys.version)
"""
    
    print("Test du plugin:")
    if transformer.can_transform(test_code):
        result = transformer.transform(test_code)
        print("Transformation reussie")
        print(result)
    else:
        print("Transformation non applicable")
