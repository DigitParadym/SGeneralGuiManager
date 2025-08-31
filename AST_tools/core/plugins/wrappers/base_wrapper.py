#!/usr/bin/env python3
"""Base Wrapper generique pour tous les outils CLI"""

import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from core.plugins.base.base_transformer import BaseTransformer


class BaseWrapper(BaseTransformer):
    """
    Classe de base generique pour tous les wrappers d'outils CLI.

    Cette classe fournit une implementation generique qui peut gerer
    n'importe quel outil CLI avec n'importe quels parametres, sans
    avoir besoin de coder explicitement chaque option.
    """

    def __init__(self, tool_name):
        super().__init__()
        self.tool_name = tool_name
        self._setup_metadata()

    def _setup_metadata(self):
        """Configure les metadonnees par defaut (peut etre surcharge)."""
        self.name = f"{self.tool_name.capitalize()} Wrapper"
        self.description = f"Wrapper generique pour {self.tool_name}"
        self.version = "3.0"
        self.author = "AST Tools"

    def get_metadata(self):
        """Retourne les metadonnees du wrapper."""
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "author": self.author,
            "type": "wrapper",
            "tool": self.tool_name,
        }

    def transform(self, code_source, params=None):
        """
        Applique l'outil externe avec les parametres fournis.

        Args:
            code_source (str): Le code source a transformer
            params (dict): Les parametres a passer a l'outil

        Returns:
            str: Le code transforme
        """
        if params is None:
            params = {}

        try:
            # Creer un fichier temporaire avec le code source
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=self._get_file_suffix(), delete=False, encoding="utf-8"
            ) as tmp:
                tmp.write(code_source)
                tmp_path = tmp.name

            # Construire et executer la commande
            cmd = self._build_command(tmp_path, params)

            print(f"[DEBUG] Commande {self.tool_name}: {' '.join(cmd)}")

            result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")

            # Gerer les erreurs potentielles
            if result.returncode != 0:
                if result.stderr:
                    print(f"[WARNING] {self.tool_name} stderr: {result.stderr}")
                if self._should_return_original_on_error(params):
                    print("[INFO] Retour du code original suite a l'erreur")
                    Path(tmp_path).unlink()
                    return code_source

            # Lire le code transforme
            with open(tmp_path, encoding="utf-8") as f:
                transformed_code = f.read()

            # Nettoyer
            Path(tmp_path).unlink()

            return transformed_code

        except subprocess.SubprocessError as e:
            print(f"[ERROR] Erreur d'execution {self.tool_name}: {e}")
            return code_source
        except Exception as e:
            print(f"[ERROR] Erreur inattendue {self.tool_name}: {e}")
            return code_source

    def _build_command(self, file_path, params):
        """
        Construit la commande de facon totalement generique.

        Cette methode convertit automatiquement un dictionnaire de parametres
        en arguments de ligne de commande, en gerant intelligemment les types.
        """
        cmd = [self.tool_name]

        # Gerer les sous-commandes (ex: ruff check, ruff format)
        if "command" in params:
            cmd.append(params["command"])
            params_to_process = {k: v for k, v in params.items() if k != "command"}
        else:
            params_to_process = params.copy()

        # Gerer les arguments positionnels (sans --key)
        if "positional_args" in params_to_process:
            positional = params_to_process.pop("positional_args")
            if isinstance(positional, list):
                cmd.extend(str(arg) for arg in positional)
            else:
                cmd.append(str(positional))

        # Construire dynamiquement les arguments nommes
        for key, value in params_to_process.items():
            # Ignorer les cles speciales
            if key.startswith("_"):
                continue

            # Convertir les underscores en tirets (convention Python -> CLI)
            cli_key = key.replace("_", "-")

            # Gerer differents types de valeurs
            if isinstance(value, bool):
                if value:  # Seulement ajouter le flag si True
                    # Certains outils utilisent un seul tiret pour les options courtes
                    if len(cli_key) == 1:
                        cmd.append(f"-{cli_key}")
                    else:
                        cmd.append(f"--{cli_key}")

            elif isinstance(value, list):
                # Pour les listes, ajouter l'option suivie de chaque valeur
                if len(value) > 0:
                    if len(cli_key) == 1:
                        cmd.append(f"-{cli_key}")
                    else:
                        cmd.append(f"--{cli_key}")
                    cmd.extend(str(v) for v in value)

            elif isinstance(value, dict):
                # Pour les dictionnaires, les convertir en key=value
                for sub_key, sub_value in value.items():
                    if len(cli_key) == 1:
                        cmd.append(f"-{cli_key}")
                    else:
                        cmd.append(f"--{cli_key}")
                    cmd.append(f"{sub_key}={sub_value}")

            elif value is not None:
                # Pour les valeurs simples (string, int, etc.)
                if len(cli_key) == 1:
                    cmd.append(f"-{cli_key}")
                else:
                    cmd.append(f"--{cli_key}")
                cmd.append(str(value))

        # Ajouter le fichier a la fin (sauf configuration speciale)
        if params.get("_file_position") != "start":
            cmd.append(file_path)
        else:
            cmd.insert(1, file_path)

        return cmd

    def _get_file_suffix(self):
        """Retourne l'extension de fichier appropriee."""
        return ".py"

    def _should_return_original_on_error(self, params):
        """Determine si on doit retourner le code original en cas d'erreur."""
        return params.get("_return_original_on_error", True)
