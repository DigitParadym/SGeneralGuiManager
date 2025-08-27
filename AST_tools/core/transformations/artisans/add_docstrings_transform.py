#!/usr/bin/env python3
"""
Transformation pour ajouter des docstrings aux fonctions et classes
"""

import ast
import sys
from pathlib import Path

# Import depuis le dossier parent
parent_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(parent_dir))

from core.transformations.base.base_transformer import BaseTransformer


class AddDocstringsTransform(BaseTransformer):
    """Ajoute des docstrings aux fonctions et classes."""
    
    def __init__(self):
        super().__init__()
        self.name = "Add Docstrings"
        self.description = "Ajoute des docstrings aux fonctions et classes"
        self.version = "1.0"
        self.author = "AST Tools"
    
    def get_metadata(self):
        return {
            'name': self.name,
            'description': self.description,
            'version': self.version,
            'author': self.author
        }
    
    def transform(self, code_source):
        """Ajoute des docstrings au code."""
        try:
            tree = ast.parse(code_source)
            self._add_docstrings(tree)
            return ast.unparse(tree)
        except Exception as e:
            print(f"Erreur transformation: {e}")
            return code_source
    
    def _add_docstrings(self, node):
        """Ajoute recursivement des docstrings."""
        for child in ast.walk(node):
            if isinstance(child, ast.FunctionDef):
                if not ast.get_docstring(child):
                    docstring = f'"""Fonction {child.name}."""'
                    child.body.insert(0, ast.Expr(value=ast.Constant(value=docstring)))
            elif isinstance(child, ast.ClassDef):
                if not ast.get_docstring(child):
                    docstring = f'"""Classe {child.name}."""'
                    child.body.insert(0, ast.Expr(value=ast.Constant(value=docstring)))
