"""
Generators - Creation de nouveaux fichiers depuis zero
Type 3 - Generation de code
"""

import sys  # noqa: F401
from pathlib import Path  # noqa: F401

# Ajouter le chemin parent pour les imports
sys.path.append(str(Path(__file__).parent.parent.parent))

generators = []

try:
    from .file_creator import FileCreator  # noqa: F401

    generators.append("FileCreator")
except ImportError:
    pass

try:
    from .module_generator import ModuleGenerator  # noqa: F401

    generators.append("ModuleGenerator")
except ImportError:
    pass

try:
    from .test_generator import TestFileGenerator  # noqa: F401

    generators.append("TestFileGenerator")
except ImportError:
    pass

__all__ = generators
