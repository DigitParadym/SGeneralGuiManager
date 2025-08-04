#!/usr/bin/env python3
"""
Transformation: Conversion vers pathlib
Convertit os.path vers pathlib.Path
"""

import sys
from pathlib import Path

# S'assurer que le repertoire core est accessible
current_dir = Path(__file__).parent.parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))


import ast

from core.base_transformer import BaseTransformer


class PathlibTransformerOptimized(BaseTransformer):
    """Convertit os.path vers pathlib.Path"""

    def get_metadata(self):
        """Retourne les metadonnees du transformateur."""
        return {
            "name": "Pathlib Transformer",
            "version": "1.0.0",
            "description": "Convertit os.path vers pathlib.Path",
            "author": "AST_tools",
        }

    def can_transform(self, code):
        """Verifie si le code utilise os.path"""
        return "os.path" in code or "import os" in code

    def transform(self, code):
        """Applique la transformation"""
        try:
            tree = ast.parse(code)
            # Pour l'instant, retourner le code original
            # TODO: Implementer la conversion os.path -> pathlib
            return ast.unparse(tree)
        except Exception:
            return code
