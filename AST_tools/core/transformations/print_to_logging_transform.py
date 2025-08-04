import sys
from pathlib import Path
import ast
from core.base_transformer import BaseTransformer

#!/usr/bin/env python3
"""
Transformation: Conversion print() vers logging
Convertit tous les appels print() en appels logging.info()
"""


# S'assurer que le repertoire core est accessible
current_dir = Path(__file__).parent.parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))





class PrintToLoggingTransform(BaseTransformer):
    """Transforme les print() en logging.info()"""

    def get_metadata(self):
        """Retourne les metadonnees du transformateur."""
        return {
            "name": "Print to Logging Transform",
            "version": "1.0.0",
            "description": "Convertit print() en logging.info()",
            "author": "AST_tools",
        }

    def can_transform(self, code):
        """Verifie si le code contient des print()"""
        return "print(" in code

    def transform(self, code):
        """Applique la transformation"""
        try:
            tree = ast.parse(code)
            transformer = PrintToLoggingVisitor()
            new_tree = transformer.visit(tree)

            # Ajouter import logging si necessaire
            if transformer.transformations > 0:
                # Ajouter import en haut
                import_node = ast.Import(names=[ast.alias(name="logging", asname=None)])
                new_tree.body.insert(0, import_node)

            return ast.unparse(new_tree)
        except Exception:
            return code  # Retourner le code original en cas d'erreur


class PrintToLoggingVisitor(ast.NodeTransformer):
    """Visiteur AST pour transformer print() en logging.info()"""

    def __init__(self):
        self.transformations = 0

    def visit_Call(self, node):
        """Visite les appels de fonction"""
        self.generic_visit(node)

        if isinstance(node.func, ast.Name) and node.func.id == "print":
            self.transformations += 1
            # Transformer print() en logging.info()
            return ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id="logging", ctx=ast.Load()),
                    attr="info",
                    ctx=ast.Load(),
                ),
                args=node.args,
                keywords=node.keywords,
            )
        return node
