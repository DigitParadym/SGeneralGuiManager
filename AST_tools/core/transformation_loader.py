"""
TransformationLoader - Version corrigee
"""

import importlib.util
from pathlib import Path
from typing import Dict, List


class TransformationLoader:
    """Chargeur de transformations AST."""

    def __init__(self):
        self.transformations_dir = Path(__file__).parent / "transformations"
        self.loaded_transformations = {}
        self._scan_transformations()

    def _scan_transformations(self):
        """Scanne les transformations disponibles."""
        if not self.transformations_dir.exists():
            print(f"! Aucune transformation trouvee dans {self.transformations_dir}")
            return

        python_files = list(self.transformations_dir.glob("*.py"))
        transform_files = [f for f in python_files if not f.name.startswith("__")]

        for fichier in transform_files:
            nom_module = fichier.stem
            try:
                self._load_transformation_module(nom_module, fichier)
            except Exception as e:
                print(f"Avertissement transformations.__init__: {e}")

    def _load_transformation_module(self, nom_module: str, fichier_path: Path):
        """Charge un module de transformation."""
        spec = importlib.util.spec_from_file_location(nom_module, fichier_path)
        if spec is None:
            raise ImportError(f"Spec impossible pour {nom_module}")

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Chercher classe de transformation
        transformation_class = None
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (
                isinstance(attr, type)
                and hasattr(attr, "transform")
                and hasattr(attr, "get_metadata")
            ):
                transformation_class = attr
                break

        if transformation_class:
            self.loaded_transformations[nom_module] = transformation_class
        else:
            raise ImportError(f"Pas de classe valide dans {nom_module}")

    def list_transformations(self) -> List[str]:
        """Liste des transformations disponibles."""
        return list(self.loaded_transformations.keys())

    def get_transformation(self, name: str):
        """Retourne une instance de transformation."""
        if name not in self.loaded_transformations:
            return None
        try:
            return self.loaded_transformations[name]()
        except Exception as e:
            print(f"Erreur instanciation {name}: {e}")
            return None

    def get_transformation_metadata(self) -> Dict:
        """Metadonnees des transformations."""
        metadata = {}
        for name in self.loaded_transformations:
            try:
                instance = self.get_transformation(name)
                if instance and hasattr(instance, "get_metadata"):
                    metadata[name] = instance.get_metadata()
            except Exception as e:
                print(f"Erreur metadonnees {name}: {e}")
        return metadata
