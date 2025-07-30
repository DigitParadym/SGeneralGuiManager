#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Transformateur: Print vers Logging
Convertit les appels print() en logging.info()
"""

import ast
from core.base_transformer import BaseTransformer


class PrintToLoggingTransformer(BaseTransformer):
    """Transforme les appels print() en logging.info()."""
    
    def get_metadata(self):
        """Retourne les metadonnees du transformateur."""
        return {
            'name': 'Print to Logging',
            'version': '1.0.0',
            'description': 'Convertit print() en logging.info()',
            'author': 'AST Tools',
            'category': 'refactoring'
        }
    
    def can_transform(self, source_code):
        """Verifie si le code contient des appels print()."""
        try:
            tree = ast.parse(source_code)
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name) and node.func.id == 'print':
                        return True
            return False
        except:
            return False
    
    def transform(self, source_code):
        """Transforme le code source."""
        try:
            tree = ast.parse(source_code)
            transformer = PrintToLoggingVisitor()
            new_tree = transformer.visit(tree)
            
            # Ajouter l'import logging si des transformations ont eu lieu
            if transformer.transformations > 0:
                new_tree = self._add_logging_import(new_tree)
            
            return ast.unparse(new_tree)
        except Exception as e:
            print(f"Erreur transformation: {e}")
            return source_code
    
    def _add_logging_import(self, tree):
        """Ajoute l'import logging au debut du fichier."""
        import_node = ast.Import(names=[ast.alias(name='logging', asname=None)])
        
        # Chercher s'il y a deja un import logging
        has_logging_import = False
        for node in tree.body:
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name == 'logging':
                        has_logging_import = True
                        break
        
        if not has_logging_import:
            tree.body.insert(0, import_node)
        
        return tree


class PrintToLoggingVisitor(ast.NodeTransformer):
    """Visiteur AST pour transformer print() en logging.info()."""
    
    def __init__(self):
        self.transformations = 0
    
    def visit_Call(self, node):
        """Visite les appels de fonction."""
        self.generic_visit(node)
        
        # Transformer print() en logging.info()
        if isinstance(node.func, ast.Name) and node.func.id == 'print':
            self.transformations += 1
            return ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id='logging', ctx=ast.Load()),
                    attr='info',
                    ctx=ast.Load()
                ),
                args=node.args,
                keywords=node.keywords
            )
        
        return node


# Point d'entree pour le systeme modulaire
def get_transformer():
    """Retourne une instance du transformateur."""
    return PrintToLoggingTransformer()
