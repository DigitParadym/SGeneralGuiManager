#!/usr/bin/env python3
"""
Transformation pour convertir os.path vers pathlib
"""

import ast
import sys
from pathlib import Path

# Import depuis le dossier parent
parent_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(parent_dir))

from core.transformations.base.base_transformer import BaseTransformer


class PathlibTransformer(BaseTransformer):
    """Convertit os.path vers pathlib."""
    
    def __init__(self):
        super().__init__()
        self.name = "Pathlib Transformer"
        self.description = "Convertit os.path vers pathlib"
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
        """Transforme os.path en pathlib."""
        try:
            # Remplacements simples
            code = code_source
            replacements = [
                ('os.path.join(', 'Path('),
                ('os.path.exists(', 'Path('),
                ('os.path.isfile(', 'Path('),
                ('os.path.isdir(', 'Path('),
                ('os.path.dirname(', 'Path('),
                ('os.path.basename(', 'Path('),
                ('os.path.abspath(', 'Path('),
            ]
            
            for old, new in replacements:
                if old in code:
                    code = code.replace(old, new)
                    # Corriger les parentheses
                    code = code.replace(new + ')', new.rstrip('(') + ').exists()')
            
            # Ajouter import si necessaire
            if 'Path(' in code and 'from pathlib import Path' not in code:
                lines = code.split('\n')
                lines.insert(0, 'from pathlib import Path')
                code = '\n'.join(lines)
            
            return code
            
        except Exception as e:
            print(f"Erreur transformation: {e}")
            return code_source
