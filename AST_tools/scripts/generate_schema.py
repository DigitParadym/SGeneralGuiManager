# scripts/generate_schema.py
"""
Script de generation du schema JSON pour les plans de transformation
"""

import json
import sys
from pathlib import Path

# Ajouter le repertoire racine au path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from core.models import TransformationPlanModel

def generate_schema():
    """Genere le JSON Schema et le sauvegarde dans le dossier de documentation."""
    # Creer le dossier docs s'il n'existe pas
    output_path = Path("docs/transformation_plan_schema.json")
    output_path.parent.mkdir(exist_ok=True)
    
    # Generer le schema
    schema = TransformationPlanModel.model_json_schema()
    
    # Ajouter des informations supplementaires
    schema["title"] = "AST Tools Transformation Plan Schema"
    schema["description"] = "Schema JSON pour les plans de transformation AST Tools"
    
    # Sauvegarder le schema
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=2, ensure_ascii=False)
    
    print(f"[OK] Schema JSON genere dans : {output_path}")
    
    # Generer aussi une version markdown de la documentation
    generate_markdown_doc(schema, output_path.parent / "transformation_plan_schema.md")
    
    return output_path

def generate_markdown_doc(schema, output_path):
    """Genere une documentation Markdown du schema."""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("# Schema des Plans de Transformation AST Tools\n\n")
        f.write(f"## Description\n{schema.get('description', '')}\n\n")
        
        f.write("## Structure du Plan\n\n")
        f.write("### Champs principaux\n\n")
        
        if "properties" in schema:
            for prop_name, prop_schema in schema["properties"].items():
                required = prop_name in schema.get("required", [])
                f.write(f"- **{prop_name}**")
                if required:
                    f.write(" (requis)")
                f.write(f": {prop_schema.get('description', prop_schema.get('type', ''))}\n")
        
        f.write("\n## Exemple de Plan Valide\n\n")
        f.write("```json\n")
        example = {
            "name": "Plan de refactorisation complet",
            "description": "Applique plusieurs transformations pour ameliorer le code",
            "version": 1.0,
            "author": "Equipe AST Tools",
            "transformations": [
                {
                    "type": "appel_plugin",
                    "description": "Conversion des print en logging",
                    "plugin_name": "print_to_logging_transform"
                },
                {
                    "type": "appel_plugin",
                    "description": "Ajout de docstrings",
                    "plugin_name": "add_docstrings_transform"
                }
            ]
        }
        f.write(json.dumps(example, indent=2))
        f.write("\n```\n")
    
    print(f"[OK] Documentation Markdown generee dans : {output_path}")

if __name__ == "__main__":
    generate_schema()
