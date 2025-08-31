# core/models.py
"""
Modeles de donnees Pydantic pour la validation des plans de transformation
"""

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

# Liste des plugins disponibles
AVAILABLE_WRAPPERS = {
    "black_wrapper",
    "isort_wrapper",
    "ruff_wrapper",
    "autoflake_wrapper",
    "autopep8_wrapper",
    "pyupgrade_wrapper",
}

AVAILABLE_ARTISANS = {
    "add_docstrings_transform",
    "pathlib_transformer_optimized",
    "print_to_logging_transform",
    "unused_import_remover",
    "hello_user_transform",
}

AVAILABLE_GENERATORS = {"file_creator", "module_generator", "test_generator"}

AVAILABLE_PLUGINS = AVAILABLE_WRAPPERS | AVAILABLE_ARTISANS | AVAILABLE_GENERATORS


class TransformationModel(BaseModel):
    """
    Definit la structure d'une seule instruction de transformation.
    """

    type: Literal["appel_plugin", "remplacement_simple", "custom", "generator"]
    description: str
    plugin_name: Optional[str] = None
    params: Dict[str, Any] = Field(default_factory=dict)

    # Pydantic v2 : config stricte
    model_config = ConfigDict(extra="forbid")

    # Pydantic v2 : validation au niveau du modele (post-init)
    @model_validator(mode="after")
    def _check_plugin_requirements(self):
        if self.type in ("appel_plugin", "generator"):
            if not self.plugin_name:
                raise ValueError(f"Le champ 'plugin_name' est requis pour le type '{self.type}'.")
            if self.plugin_name not in AVAILABLE_PLUGINS:
                raise ValueError(
                    f"Le plugin '{self.plugin_name}' n'existe pas ou n'est pas charge."
                )
        return self


class TransformationPlanModel(BaseModel):
    """
    Definit la structure complete d'un plan de transformation JSON.
    """

    name: str = Field(..., min_length=1, description="Le nom du plan de transformation")
    description: str = Field(..., description="Description detaillee du plan")
    version: float = Field(default=1.0, ge=0.1, description="Version du plan")
    author: Optional[str] = Field(default=None, description="Auteur du plan")
    # v2: min_length (au lieu de min_items deprec.)
    transformations: List[TransformationModel] = Field(..., min_length=1)

    # Pydantic v2 : config stricte + exemple
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "name": "Plan de refactorisation",
                "description": "Convertit print en logging et ajoute des docstrings",
                "version": 1.0,
                "author": "AST Tools",
                "transformations": [
                    {
                        "type": "appel_plugin",
                        "description": "Conversion print vers logging",
                        "plugin_name": "print_to_logging_transform",
                    }
                ],
            }
        },
    )


def validate_plan_file(filepath: str) -> tuple[bool, str]:
    """
    Fonction utilitaire pour valider un fichier de plan JSON.
    Retourne (success: bool, message: str)
    """
    import json

    from pydantic import ValidationError

    try:
        with open(filepath, encoding="utf-8") as f:
            data = json.load(f)

        plan = TransformationPlanModel(**data)
        return True, f"Plan valide: {plan.name} v{plan.version}"

    except FileNotFoundError:
        return False, f"Fichier introuvable: {filepath}"
    except json.JSONDecodeError as e:
        return False, f"JSON invalide: {e}"
    except ValidationError as e:
        return False, f"Validation echouee: {e}"
    except Exception as e:
        return False, f"Erreur inattendue: {e}"
