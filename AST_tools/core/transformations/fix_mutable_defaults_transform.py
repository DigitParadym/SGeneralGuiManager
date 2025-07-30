#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Transformateur: Fix Mutable Defaults
Corrige les arguments par defaut mutables dans les fonctions
"""

import ast
from core.base_transformer import BaseTransformer


class FixMutableDefaultsTransformer(BaseTransformer):
    """Corrige les arguments par defaut mutables."""
    
    def get_metadata(self):
        """Retourne les metadonnees du transformateur."""
        return {
            'name': 'Fix Mutable Defaults',
            'version': '1.0.0',
            'description': 'Corrige les arguments par defaut mutables (list, dict, set)',
            'author': 'AST Tools',
            'category': 'bug_fixes'
        }
    
    def can_transform(self, source_code):
        """Verifie si le code contient des arguments mutables par defaut."""
        try:
            tree = ast.parse(source_code)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    for default in node.args.defaults:
                        if self._is_mutable_default(default):
                            return True
            return False
        except:
            return False
    
    def transform(self, source_code):
        """Transforme le code source."""
        try:
            tree = ast.parse(source_code)
            transformer = MutableDefaultsVisitor()
            new_tree = transformer.visit(tree)
            return ast.unparse(new_tree)
        except Exception as e:
            print(f"Erreur transformation: {e}")
            return source_code
    
    def _is_mutable_default(self, node):
        """Verifie si un noeud represente un argument mutable par defaut."""
        # Liste vide []
        if isinstance(node, ast.List) and len(node.elts) == 0:
            return True
        # Dictionnaire vide {}
        if isinstance(node, ast.Dict) and len(node.keys) == 0:
            return True
        # Set vide set()
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == 'set':
                if len(node.args) == 0:
                    return True
        return False


class MutableDefaultsVisitor(ast.NodeTransformer):
    """Visiteur AST pour corriger les arguments mutables par defaut."""
    
    def visit_FunctionDef(self, node):
        """Visite les definitions de fonction."""
        self.generic_visit(node)
        
        # Corriger les arguments par defaut
        new_defaults = []
        body_modifications = []
        
        for i, default in enumerate(node.args.defaults):
            if self._is_mutable_default(default):
                # Remplacer par None
                new_defaults.append(ast.Constant(value=None))
                
                # Ajouter une verification au debut de la fonction
                arg_name = node.args.args[-(len(node.args.defaults)-i)].arg
                
                if isinstance(default, ast.List):
                    # if arg is None: arg = []
                    check = self._create_none_check(arg_name, ast.List(elts=[], ctx=ast.Load()))
                elif isinstance(default, ast.Dict):
                    # if arg is None: arg = {}
                    check = self._create_none_check(arg_name, ast.Dict(keys=[], values=[]))
                elif isinstance(default, ast.Call) and isinstance(default.func, ast.Name) and default.func.id == 'set':
                    # if arg is None: arg = set()
                    check = self._create_none_check(arg_name, ast.Call(
                        func=ast.Name(id='set', ctx=ast.Load()),
                        args=[],
                        keywords=[]
                    ))
                else:
                    continue
                
                body_modifications.append(check)
            else:
                new_defaults.append(default)
        
        # Mettre a jour les defaults
        node.args.defaults = new_defaults
        
        # Ajouter les verifications au debut du corps de la fonction
        node.body = body_modifications + node.body
        
        return node
    
    def visit_AsyncFunctionDef(self, node):
        """Visite les definitions de fonction asynchrone."""
        return self.visit_FunctionDef(node)
    
    def _is_mutable_default(self, node):
        """Verifie si un noeud represente un argument mutable par defaut."""
        if isinstance(node, ast.List) and len(node.elts) == 0:
            return True
        if isinstance(node, ast.Dict) and len(node.keys) == 0:
            return True
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == 'set':
                if len(node.args) == 0:
                    return True
        return False
    
    def _create_none_check(self, arg_name, default_value):
        """Cree un noeud if arg is None: arg = default_value."""
        return ast.If(
            test=ast.Compare(
                left=ast.Name(id=arg_name, ctx=ast.Load()),
                ops=[ast.Is()],
                comparators=[ast.Constant(value=None)]
            ),
            body=[
                ast.Assign(
                    targets=[ast.Name(id=arg_name, ctx=ast.Store())],
                    value=default_value
                )
            ],
            orelse=[]
        )


# Point d'entree pour le systeme modulaire
def get_transformer():
    """Retourne une instance du transformateur."""
    return FixMutableDefaultsTransformer()
