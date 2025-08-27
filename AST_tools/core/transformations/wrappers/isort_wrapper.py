#!/usr/bin/env python3
"""
Isort Wrapper pour AST_tools
Encapsule l'outil externe Isort
"""

import subprocess
import tempfile
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
from transformations.base.base_transformer import BaseTransformer


class IsortWrapper(BaseTransformer):
    """Wrapper pour l'outil Isort."""
    
    def __init__(self):
        super().__init__()
        self.name = "Isort Wrapper"
        self.description = "Applique Isort au code Python"
        self.version = "1.0"
        self.author = "AST Tools Team"
        self.tool_name = "isort"
        self.required_package = "isort"
    
    def get_metadata(self):
        return {
            'name': self.name,
            'description': self.description,
            'version': self.version,
            'author': self.author,
            'type': 'wrapper',
            'tool': self.tool_name
        }
    
    def transform(self, code_source):
        """Applique Isort au code source."""
        try:
            # Creer un fichier temporaire
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as tmp:
                tmp.write(code_source)
                tmp_path = tmp.name
            
            # Executer l'outil
            result = subprocess.run(
                [self.tool_name, tmp_path],
                capture_output=True,
                text=True
            )
            
            # Lire le resultat
            with open(tmp_path, 'r') as f:
                transformed_code = f.read()
            
            # Nettoyer
            Path(tmp_path).unlink()
            
            return transformed_code
            
        except Exception as e:
            print(f"Erreur Isort: {e}")
            return code_source
