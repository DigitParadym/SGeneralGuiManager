#!/usr/bin/env python3
"""Pyupgrade Wrapper generique avec support complet des parametres"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from core.plugins.wrappers.base_wrapper import BaseWrapper


class PyupgradeWrapper(BaseWrapper):
    """
    Wrapper generique pour Pyupgrade.

    Supporte automatiquement TOUTES les options de Pyupgrade.
    """

    def __init__(self):
        super().__init__(tool_name="pyupgrade")
        self.name = "Pyupgrade Wrapper (Generic)"
        self.description = "Modernise le code Python avec support generique des parametres"
        self.version = "3.0"
        self.author = "AST Tools"

    def _build_command(self, file_path, params):
        """
        Surcharge pour gerer les specificites de Pyupgrade.

        Pyupgrade utilise des flags comme --py38-plus, --py39-plus, etc.
        """
        cmd = [self.tool_name]

        # Gerer la version Python cible de maniere intelligente
        if "python_version" in params:
            version = params["python_version"]
            cmd.append(f"--py{version}-plus")
            params_to_process = {k: v for k, v in params.items() if k != "python_version"}
        else:
            # Par defaut, utiliser une version safe
            if not any(k.endswith("-plus") for k in params):
                cmd.append("--py36-plus")
            params_to_process = params.copy()

        # Traiter les autres parametres de maniere generique
        for key, value in params_to_process.items():
            if key.startswith("_"):
                continue

            cli_key = key.replace("_", "-")

            if isinstance(value, bool) and value:
                cmd.append(f"--{cli_key}")
            elif isinstance(value, list):
                for v in value:
                    cmd.append(f"--{cli_key}")
                    cmd.append(str(v))
            elif value is not None and not isinstance(value, bool):
                cmd.append(f"--{cli_key}")
                cmd.append(str(value))

        # Pyupgrade attend le fichier a la fin
        cmd.append(file_path)

        return cmd
