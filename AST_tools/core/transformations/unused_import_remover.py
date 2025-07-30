#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Transformateur: Unused Import Remover
Supprime les imports non utilises
"""

import ast
from core.base_transformer import BaseTransformer


class UnusedImportRemoverTransformer(BaseTransformer):
    """Supprime les imports non utilises."""
    
    def get_metadata(self):
        """Retourne les metadonnees du transformateur."""
        return {
            'name': 'Unused Import Remover',
            'version': '1.0.0',
            'description': 'Supprime les imports non utilises dans le code',
            'author': 'AST Tools',
            'category': 'optimization'
        }
    
    def can_transform(self, source_code):
        """Verifie si le code contient des imports potentiellement non utilises."""
        try:
            tree = ast.parse(source_code)
            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    return True
            return False
        except:
            return False
    
    def transform(self, source_code):
        """Transforme le code source."""
        try:
            tree = ast.parse(source_code)
            
            # Analyser les imports et leur utilisation
            analyzer = ImportUsageAnalyzer()
            analyzer.visit(tree)
            
            # Supprimer les imports non utilises
            remover = UnusedImportRemover(analyzer.used_names)
            new_tree = remover.visit(tree)
            
            return ast.unparse(new_tree)
        except Exception as e:
            print(f"Erreur transformation: {e}")
            return source_code


class ImportUsageAnalyzer(ast.NodeVisitor):
    """Analyse l'utilisation des imports dans le code."""
    
    def __init__(self):
        self.imported_names = set()
        self.used_names = set()
        self.in_import = False
    
    def visit_Import(self, node):
        """Visite les imports directs."""
        self.in_import = True
        for alias in node.names:
            name = alias.asname if alias.asname else alias.name
            self.imported_names.add(name)
        self.in_import = False
    
    def visit_ImportFrom(self, node):
        """Visite les imports from."""
        self.in_import = True
        for alias in node.names:
            if alias.name == '*':
                continue  # Skip wildcard imports
            name = alias.asname if alias.asname else alias.name
            self.imported_names.add(name)
        self.in_import = False
    
    def visit_Name(self, node):
        """Visite les noms utilises."""
        if not self.in_import and isinstance(node.ctx, ast.Load):
            self.used_names.add(node.id)
        self.generic_visit(node)
    
    def visit_Attribute(self, node):
        """Visite les attributs."""
        if isinstance(node.value, ast.Name):
            self.used_names.add(node.value.id)
        self.generic_visit(node)


class UnusedImportRemover(ast.NodeTransformer):
    """Supprime les imports non utilises."""
    
    def __init__(self, used_names):
        self.used_names = used_names
    
    def visit_Import(self, node):
        """Visite les imports directs."""
        # Filtrer les alias non utilises
        new_names = []
        for alias in node.names:
            name = alias.asname if alias.asname else alias.name
            if name in self.used_names:
                new_names.append(alias)
        
        if new_names:
            node.names = new_names
            return node
        else:
            return None  # Supprimer l'import entier
    
    def visit_ImportFrom(self, node):
        """Visite les imports from."""
        # Filtrer les alias non utilises
        new_names = []
        for alias in node.names:
            if alias.name == '*':
                new_names.append(alias)  # Garder les wildcard imports
                continue
            
            name = alias.asname if alias.asname else alias.name
            if name in self.used_names:
                new_names.append(alias)
        
        if new_names:
            node.names = new_names
            return node
        else:
            return None  # Supprimer l'import entier


# Point d'entree pour le systeme modulaire
def get_transformer():
    """Retourne une instance du transformateur."""
    return UnusedImportRemoverTransformer()
