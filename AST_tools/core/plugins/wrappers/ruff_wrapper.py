#!/usr/bin/env python3
"""Ruff Wrapper generique avec support complet des parametres"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from core.plugins.wrappers.base_wrapper import BaseWrapper


class RuffWrapper(BaseWrapper):
    """
    Wrapper generique pour Ruff.

    Supporte automatiquement TOUTES les options de Ruff sans modification du code.
    Les parametres sont passes directement depuis le JSON.
    """

    def __init__(self):
        super().__init__(tool_name="ruff")
        self.name = "Ruff Wrapper (Generic)"
        self.description = "Applique Ruff avec support generique de tous les parametres"
        self.version = "3.0"
        self.author = "AST Tools"

    def _build_command(self, file_path, params):
        """
        Surcharge pour gerer les specificites de Ruff si necessaire.

        Ruff a quelques particularites :
        - Les sous-commandes (check, format) viennent en premier
        - Certaines options sont specifiques a certaines sous-commandes
        """
        # Utiliser la methode parent qui gere deja tout ca
        cmd = super()._build_command(file_path, params)

        # Ajustements specifiques a Ruff si necessaire
        # (actuellement, la methode parent gere deja tout correctement)

        return cmd
