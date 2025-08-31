#!/usr/bin/env python3
"""
Transformation pour supprimer les imports inutilises
"""

import ast
import sys
from pathlib import Path

# Import depuis le dossier parent
parent_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(parent_dir))

from core.plugins.base.base_transformer import BaseTransformer


class UnusedImportRemover(BaseTransformer):
    """Supprime les imports non utilises."""

    def __init__(self):
        super().__init__()
        self.name = "Unused Import Remover"
        self.description = "Supprime les imports non utilises"
        self.version = "1.0"
        self.author = "AST Tools"

    def get_metadata(self):
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "author": self.author,
        }

    def transform(self, code_source):
        """Supprime les imports non utilises."""
        try:
            tree = ast.parse(code_source)

            # Collecter tous les noms utilises
            used_names = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Name):
                    used_names.add(node.id)

            # Filtrer les imports
            new_body = []
            for node in tree.body:
                if isinstance(node, ast.Import):
                    # Garder seulement les imports utilises
                    new_names = []
                    for alias in node.names:
                        name = alias.asname if alias.asname else alias.name
                        if name in used_names:
                            new_names.append(alias)
                    if new_names:
                        node.names = new_names
                        new_body.append(node)
                elif isinstance(node, ast.ImportFrom):
                    # Garder seulement les imports from utilises
                    new_names = []
                    for alias in node.names:
                        name = alias.asname if alias.asname else alias.name
                        if name in used_names:
                            new_names.append(alias)
                    if new_names:
                        node.names = new_names
                        new_body.append(node)
                else:
                    new_body.append(node)

            tree.body = new_body
            return ast.unparse(tree)

        except Exception as e:
            print(f"Erreur transformation: {e}")
            return code_source
