# tests/unittests/core/test_models.py
"""
Tests unitaires pour les modeles Pydantic
"""

import pytest
import json
from pathlib import Path
from pydantic import ValidationError

# Ajouter le repertoire racine au path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from core.models import TransformationPlanModel, TransformationModel, validate_plan_file

class TestTransformationModel:
    """Tests pour le modele TransformationModel."""
    
    def test_transformation_valide(self):
        """Test qu'une transformation valide est acceptee."""
        data = {
            "type": "appel_plugin",
            "description": "Test plugin",
            "plugin_name": "print_to_logging_transform"
        }
        transform = TransformationModel(**data)
        assert transform.type == "appel_plugin"
        assert transform.plugin_name == "print_to_logging_transform"
    
    def test_plugin_inconnu_leve_erreur(self):
        """Test qu'un plugin inconnu leve une erreur."""
        data = {
            "type": "appel_plugin",
            "description": "Plugin invalide",
            "plugin_name": "plugin_inexistant"
        }
        with pytest.raises(ValidationError) as exc_info:
            TransformationModel(**data)
        assert "plugin_inexistant" in str(exc_info.value)
    
    def test_plugin_manquant_pour_appel_plugin(self):
        """Test que plugin_name est requis pour type appel_plugin."""
        data = {
            "type": "appel_plugin",
            "description": "Sans plugin"
        }
        with pytest.raises(ValidationError):
            TransformationModel(**data)
    
    def test_champ_supplementaire_rejete(self):
        """Test que les champs non reconnus sont rejetes (mode strict)."""
        data = {
            "type": "appel_plugin",
            "description": "Test",
            "plugin_name": "print_to_logging_transform",
            "champ_inconnu": "valeur"
        }
        with pytest.raises(ValidationError) as exc_info:
            TransformationModel(**data)
        assert "extra fields not permitted" in str(exc_info.value).lower()

class TestTransformationPlanModel:
    """Tests pour le modele TransformationPlanModel."""
    
    def test_plan_valide_charge_correctement(self):
        """Test qu'un plan conforme est parse sans erreur."""
        plan_data = {
            "name": "Plan de Test Valide",
            "description": "Un test.",
            "version": 1.0,
            "transformations": [{
                "type": "appel_plugin",
                "description": "Test plugin",
                "plugin_name": "print_to_logging_transform"
            }]
        }
        plan = TransformationPlanModel(**plan_data)
        assert plan.name == "Plan de Test Valide"
        assert len(plan.transformations) == 1
    
    def test_plan_sans_nom_leve_erreur(self):
        """Test qu'un champ requis manquant leve une ValidationError."""
        plan_data = {
            "description": "Plan sans nom.",
            "version": 1.0,
            "transformations": []
        }
        with pytest.raises(ValidationError):
            TransformationPlanModel(**plan_data)
    
    def test_plan_sans_transformations_leve_erreur(self):
        """Test qu'un plan sans transformations est rejete."""
        plan_data = {
            "name": "Plan vide",
            "description": "Aucune transformation",
            "version": 1.0,
            "transformations": []
        }
        with pytest.raises(ValidationError):
            TransformationPlanModel(**plan_data)
    
    def test_version_negative_rejetee(self):
        """Test que les versions negatives sont rejetees."""
        plan_data = {
            "name": "Plan",
            "description": "Test",
            "version": -1.0,
            "transformations": [{
                "type": "appel_plugin",
                "description": "Test",
                "plugin_name": "print_to_logging_transform"
            }]
        }
        with pytest.raises(ValidationError):
            TransformationPlanModel(**plan_data)

class TestValidatePlanFile:
    """Tests pour la fonction utilitaire validate_plan_file."""
    
    def test_fichier_valide(self, tmp_path):
        """Test avec un fichier JSON valide."""
        plan_file = tmp_path / "plan_valide.json"
        plan_data = {
            "name": "Test",
            "description": "Test",
            "transformations": [{
                "type": "appel_plugin",
                "description": "Test",
                "plugin_name": "print_to_logging_transform"
            }]
        }
        plan_file.write_text(json.dumps(plan_data))
        
        success, message = validate_plan_file(str(plan_file))
        assert success is True
        assert "Plan valide" in message
    
    def test_fichier_inexistant(self):
        """Test avec un fichier qui n'existe pas."""
        success, message = validate_plan_file("fichier_inexistant.json")
        assert success is False
        assert "introuvable" in message.lower()
