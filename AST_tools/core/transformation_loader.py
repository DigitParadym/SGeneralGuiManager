#!/usr/bin/env python3
"""
TransformationLoader - Version adaptee pour la nouvelle structure
Gere les deux types de plugins : Wrappers et Artisans
"""

import importlib.util
import sys
from pathlib import Path
from typing import Dict, List, Optional

from core.plugins.wrappers.pyupgrade_wrapper import PyupgradeWrapper

# Imports des wrappers specifiques
from core.plugins.wrappers.ruff_wrapper import RuffWrapper

# Registre des wrappers disponibles
WRAPPER_REGISTRY = {
    "ruff_wrapper": RuffWrapper,
    "pyupgrade_wrapper": PyupgradeWrapper,
}


class TransformationLoader:
    """Chargeur de transformations AST avec support des types."""

    def __init__(self):
        self.plugins_dir = Path(__file__).parent / "plugins"
        self.loaded_transformations = {}
        self.transformation_types = {"wrappers": {}, "artisans": {}, "generators": {}, "all": {}}
        self.metadata_cache = {}
        self._scan_all_transformations()

    def _scan_all_transformations(self):
        """Scanne les transformations par type."""
        # Scanner les plugins wrapper
        wrappers_dir = self.plugins_dir / "wrappers"
        if wrappers_dir.exists():
            self._scan_directory(wrappers_dir, "wrappers")

        # Scanner les plugins artisan
        artisans_dir = self.plugins_dir / "artisans"
        if artisans_dir.exists():
            self._scan_directory(artisans_dir, "artisans")

        # Scanner les plugins generator
        generators_dir = self.plugins_dir / "generators"
        if generators_dir.exists():
            self._scan_directory(generators_dir, "generators")

        # Fusionner dans all
        self.transformation_types["all"] = {
            **self.transformation_types["wrappers"],
            **self.transformation_types["artisans"],
            **self.transformation_types["generators"],
        }
        self.loaded_transformations = self.transformation_types["all"]

        # Message de confirmation
        total = len(self.transformation_types["all"])
        if total > 0:
            print(f"+ Systeme modulaire actif ({total} transformations chargees)")

    def _scan_directory(self, directory: Path, transform_type: str):
        """Scanne un repertoire de transformations."""
        if not directory.exists():
            return

        python_files = list(directory.glob("*.py"))
        transform_files = [f for f in python_files if not f.name.startswith("__")]

        for fichier in transform_files:
            nom_module = fichier.stem
            try:
                loaded_class = self._load_transformation_module(nom_module, fichier, transform_type)
                if loaded_class:
                    self.transformation_types[transform_type][nom_module] = loaded_class

                    # Cache metadata
                    try:
                        instance = loaded_class()
                        if hasattr(instance, "get_metadata"):
                            self.metadata_cache[nom_module] = instance.get_metadata()
                    except Exception:
                        pass

            except Exception as e:
                print(f"Avertissement: Impossible de charger {nom_module}: {e}")

    def _load_transformation_module(self, nom_module: str, fichier_path: Path, transform_type: str):
        """Charge un module de transformation."""
        full_module_name = f"ast_tools.transformations.{transform_type}.{nom_module}"

        spec = importlib.util.spec_from_file_location(full_module_name, fichier_path)
        if spec is None:
            return None

        module = importlib.util.module_from_spec(spec)
        sys.modules[full_module_name] = module
        spec.loader.exec_module(module)

        # Chercher la classe de transformation
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (
                isinstance(attr, type)
                and hasattr(attr, "transform")
                and hasattr(attr, "get_metadata")
                and attr.__name__ not in ["BaseTransformer", "WrapperBase", "ArtisanBase"]
            ):
                return attr

        return None

    def list_transformations(self, transform_type: str = "all") -> List[str]:
        """Liste des transformations."""
        return list(self.transformation_types.get(transform_type, {}).keys())

    def get_transformation(self, name: str):
        """Retourne une instance de transformation."""
        if name not in self.loaded_transformations:
            return None
        try:
            return self.loaded_transformations[name]()
        except Exception as e:
            print(f"Erreur instanciation {name}: {e}")
            return None

    def get_transformation_metadata(self, name: Optional[str] = None) -> Dict:
        """Retourne les metadonnees."""
        if name:
            return self.metadata_cache.get(name, {})
        return self.metadata_cache.copy()
