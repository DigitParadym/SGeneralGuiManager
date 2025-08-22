# core/models.py
"""
Modeles de donnees Pydantic pour la validation des plans de transformation
"""

from pydantic import BaseModel, Field, validator
from typing import List, Literal, Dict, Any, Optional

# Liste des plugins disponibles (a terme, charger depuis TransformationLoader)
AVAILABLE_PLUGINS = {
    "print_to_logging_transform",
    "add_docstrings_transform", 
    "unused_import_remover",
    "pathlib_transformer_optimized",
    "exemple_working_transform",
    "json_ai_transformer"
}

class TransformationModel(BaseModel):
    """
    Definit la structure d'une seule instruction de transformation.
    """
    type: Literal['appel_plugin', 'remplacement_simple', 'custom']
    description: str
    plugin_name: Optional[str] = None
    params: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('plugin_name', always=True)
    def validate_plugin(cls, plugin_name_value, values):
        """Validateur metier : verifie que le plugin existe si le type est 'appel_plugin'."""
        transformation_type = values.get('type')
        
        if transformation_type == 'appel_plugin':
            if not plugin_name_value:
                raise ValueError("Le champ 'plugin_name' est requis pour le type 'appel_plugin'.")
            if plugin_name_value not in AVAILABLE_PLUGINS:
                raise ValueError(f"Le plugin '{plugin_name_value}' n'existe pas ou n'est pas charge.")
        return plugin_name_value
    
    class Config:
        extra = "forbid"  # Rejette les champs non reconnus

class TransformationPlanModel(BaseModel):
    """
    Definit la structure complete d'un plan de transformation JSON.
    """
    name: str = Field(..., min_length=1, description="Le nom du plan de transformation")
    description: str = Field(..., description="Description detaillee du plan")
    version: float = Field(default=1.0, ge=0.1, description="Version du plan")
    author: Optional[str] = Field(default=None, description="Auteur du plan")
    transformations: List[TransformationModel] = Field(..., min_items=1)
    
    class Config:
        extra = "forbid"  # Mode strict : rejette les champs non reconnus
        json_schema_extra = {
            "example": {
                "name": "Plan de refactorisation",
                "description": "Convertit print en logging et ajoute des docstrings",
                "version": 1.0,
                "author": "AST Tools",
                "transformations": [
                    {
                        "type": "appel_plugin",
                        "description": "Conversion print vers logging",
                        "plugin_name": "print_to_logging_transform"
                    }
                ]
            }
        }

def validate_plan_file(filepath: str) -> tuple[bool, str]:
    """
    Fonction utilitaire pour valider un fichier de plan JSON.
    Retourne (success: bool, message: str)
    """
    import json
    from pydantic import ValidationError
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
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
