#!/usr/bin/env python3
"""
Transformation pour convertir print() en logging
"""

import ast
import sys
from pathlib import Path

# Import depuis le dossier parent
parent_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(parent_dir))

from core.plugins.base.base_transformer import BaseTransformer


class PrintToLoggingTransform(BaseTransformer):
    """Convertit print() en logging.info()."""

    def __init__(self):
        super().__init__()
        self.name = "Print to Logging"
        self.description = "Convertit print() en logging.info()"
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
        """Transforme print en logging."""
        try:
            tree = ast.parse(code_source)
            transformer = PrintToLoggingTransformer()
            new_tree = transformer.visit(tree)

            # Ajouter import logging si necessaire
            code = ast.unparse(new_tree)
            if "logging." in code and "import logging" not in code:
                code = "import logging\n" + code

            return code

        except Exception as e:
            print(f"Erreur transformation: {e}")
            return code_source


class PrintToLoggingTransformer(ast.NodeTransformer):
    """Transformateur AST pour print vers logging."""

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name) and node.func.id == "print":
            # Remplacer print par logging.info
            return ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id="logging", ctx=ast.Load()), attr="info", ctx=ast.Load()
                ),
                args=node.args,
                keywords=[],
            )
        return node
