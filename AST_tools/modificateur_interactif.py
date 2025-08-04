# ===================================================================
# FICHIER : modificateur_interactif.py (Version complete et corrigee)
# ===================================================================
import ast
import json
import os
import sys
from typing import List

from core.global_logger import (
    log_success,
    log_warning,
)

# ... (Toute autre detection d'environnement que vous avez) ...
print("*** Environnement Terminal detecte ***")


# ==============================================================================
# CLASSE AnalyseurCode (NECESSAIRE)
# ==============================================================================
class AnalyseurCode:
    """Analyseur de code Python utilisant AST."""

    def __init__(self):
        self.reset()

    def reset(self):
        """Remet a zero l'analyseur."""
        self.fonctions = []
        self.classes = []
        self.imports = []
        self.print_calls = []
        self.erreurs = []

    def analyser_code(self, code_source):
        """Analyse le code source Python."""
        try:
            self.reset()
            arbre = ast.parse(code_source)
            for noeud in ast.walk(arbre):
                if isinstance(noeud, ast.FunctionDef):
                    self.fonctions.append({"nom": noeud.name, "ligne": noeud.lineno})
                elif isinstance(noeud, ast.ClassDef):
                    self.classes.append({"nom": noeud.name, "ligne": noeud.lineno})
                elif isinstance(noeud, ast.Call):
                    if isinstance(noeud.func, ast.Name) and noeud.func.id == "print":
                        self.print_calls.append({"ligne": noeud.lineno})
            return True
        except Exception as e:
            self.erreurs.append(f"Erreur analyse: {e}")
            return False

    def obtenir_rapport(self):
        """Genere un rapport d'analyse."""
        return {
            "fonctions": len(self.fonctions),
            "classes": len(self.classes),
            "print_calls": len(self.print_calls),
            "erreurs": len(self.erreurs),
        }


# ==============================================================================
# CLASSE TransformateurAST (NECESSAIRE)
# ==============================================================================
class TransformateurAST(ast.NodeTransformer):
    """Transformateur AST pour convertir print() en logging."""

    def __init__(self):
        self.transformations = 0

    def visit_Call(self, node):
        """Visite les appels de fonction."""
        self.generic_visit(node)
        if isinstance(node.func, ast.Name) and node.func.id == "print":
            self.transformations += 1
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


# ==============================================================================
# ORCHESTRATEUR PRINCIPAL (CORRIGÉ)
# ==============================================================================
class OrchestrateurAST:
    """Orchestrateur principal pour les transformations AST."""

    def __init__(self, mode_colab=False):
        self.mode_colab = mode_colab
        self.analyseur = (
            AnalyseurCode()
        )  # Cette ligne a besoin que AnalyseurCode existe
        self.historique = []

        self.transformation_loader = None
        self._init_modular_system()

    def _init_modular_system(self):
        """Initialise le systeme modulaire."""
        from pathlib import Path

        current_dir = Path(__file__).parent
        if str(current_dir) not in sys.path:
            sys.path.insert(0, str(current_dir))

        try:
            from core.transformation_loader import TransformationLoader

            self.transformation_loader = TransformationLoader()
            plugins_info = self.transformation_loader.get_transformation_metadata()
            if plugins_info:
                log_success(
                    f"Systeme modulaire actif: {len(plugins_info)} transformation(s)"
                )
            else:
                log_success(
                    "Systeme modulaire actif (aucune transformation dans core/)"
                )
        except ImportError:
            log_warning("Systeme modulaire non disponible (dossier core/ manquant)")
        except Exception as e:
            log_warning(f"Erreur systeme modulaire: {e}")

    def executer_plan(self, chemin_plan_json: str, fichiers_cibles: List[str]):
        """
        Execute un plan de transformation complet a partir d'un fichier JSON.
        """
        self.log_message(f"Execution du plan : {os.path.basename(chemin_plan_json)}")

        try:
            with open(chemin_plan_json, encoding="utf-8") as f:
                plan = json.load(f)
        except Exception as e:
            self.log_message(f"ERREUR: Impossible de lire le plan JSON : {e}")
            return

        instructions = plan.get("transformations", [])
        if not instructions:
            self.log_message(
                "AVERTISSEMENT: Le plan ne contient aucune instruction de transformation."
            )
            return

        self.log_message(
            f"{len(instructions)} instruction(s) a executer sur {len(fichiers_cibles)} fichier(s)."
        )

        for i, instruction in enumerate(instructions, 1):
            self.log_message(
                f"\n--- Instruction {i}/{len(instructions)}: {instruction.get('description', 'N/A')} ---"
            )

            instruction_type = instruction.get("type")

            if instruction_type == "appel_plugin":
                plugin_name = instruction.get("plugin_name")
                if not plugin_name:
                    self.log_message(
                        "ERREUR: 'plugin_name' manquant pour 'appel_plugin'."
                    )
                    continue

                for fichier in fichiers_cibles:
                    self.appliquer_transformation_modulaire(
                        fichier, fichier, plugin_name
                    )

            elif instruction_type == "remplacement_simple":
                self.log_message(
                    "INFO: Le type 'remplacement_simple' n'est pas encore implemente."
                )

            else:
                self.log_message(
                    f"AVERTISSEMENT: Type d'instruction inconnu '{instruction_type}'."
                )

        self.log_message("\nPlan de transformation termine.")

    def appliquer_transformation_modulaire(
        self, fichier_source, fichier_sortie, transformation_name
    ):
        """Applique une transformation modulaire."""
        if not self.transformation_loader:
            self.log_message("ERREUR: Systeme modulaire non disponible")
            return False

        transformer = self.transformation_loader.get_transformation(transformation_name)
        if not transformer:
            self.log_message(
                f"ERREUR: Transformation '{transformation_name}' non trouvee"
            )
            return False

        try:
            with open(fichier_source, encoding="utf-8") as f:
                code_source = f.read()

            self.log_message(
                f"  -> Application de '{transformation_name}' sur {os.path.basename(fichier_source)}"
            )
            code_transforme = transformer.transform(code_source)

            with open(fichier_sortie, "w", encoding="utf-8") as f:
                f.write(code_transforme)

            return True

        except Exception as e:
            self.log_message(
                f"ERREUR pendant la transformation de {os.path.basename(fichier_source)}: {e}"
            )
            return False

    def lister_transformations_modulaires(self):
        """Liste les transformations modulaires si disponibles."""
        if not self.transformation_loader:
            return []

        transformations = []
        plugins_metadata = self.transformation_loader.get_transformation_metadata()
        for plugin_name, metadata in plugins_metadata.items():
            transformations.append(
                {
                    "name": plugin_name,
                    "display_name": metadata["name"],
                    "description": metadata["description"],
                    "version": metadata["version"],
                }
            )
        return transformations

    def log_message(self, message):
        """Methode de logging simple pour le moteur."""
        print(message)
