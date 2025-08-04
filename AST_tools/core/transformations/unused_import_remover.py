#!/usr/bin/env python3
"""
Transformation: Suppression des imports inutilises
Detecte et supprime les imports qui ne sont pas utilises dans le code
"""

import sys
from pathlib import Path

# S'assurer que le repertoire core est accessible
current_dir = Path(__file__).parent.parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))


import ast

from core.base_transformer import BaseTransformer


class UnusedImportRemover(BaseTransformer):
    """Supprime les imports inutilises"""

    def get_metadata(self):
        """Retourne les metadonnees du transformateur."""
        return {
            "name": "Unused Import Remover",
            "version": "1.0.0",
            "description": "Supprime les imports non utilises",
            "author": "AST_tools",
        }

    def can_transform(self, code):
        """Verifie si le code contient des imports"""
        return "import " in code

    def transform(self, code):
        """Applique la transformation"""
        try:
            tree = ast.parse(code)
            analyzer = ImportAnalyzer()
            analyzer.visit(tree)

            # Pour l'instant, retourner le code original
            # TODO: Implementer la suppression des imports inutilises
            return ast.unparse(tree)
        except Exception:
            return code


class ImportAnalyzer(ast.NodeVisitor):
    """Analyse les imports et leur utilisation"""

    def __init__(self):
        self.imports = set()
        self.used_names = set()

    def visit_Import(self, node):
        """Visite les imports"""
        for alias in node.names:
            name = alias.asname if alias.asname else alias.name
            self.imports.add(name)

    def visit_ImportFrom(self, node):
        """Visite les imports from"""
        for alias in node.names:
            name = alias.asname if alias.asname else alias.name
            self.imports.add(name)

    def visit_Name(self, node):
        """Visite les noms utilises"""
        if isinstance(node.ctx, ast.Load):
            self.used_names.add(node.id)
