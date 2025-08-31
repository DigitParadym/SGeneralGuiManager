"""
Transformations artisanales avec logique interne.
Type 2 - Intelligence Interne
"""

import sys  # noqa: F401
from pathlib import Path  # noqa: F401

# Ajouter le chemin parent pour les imports
sys.path.append(str(Path(__file__).parent.parent.parent))

# Import des transformations artisanales
artisans = []

try:
    from .add_docstrings_transform import AddDocstringsTransform  # noqa: F401

    artisans.append("AddDocstringsTransform")
except ImportError:
    pass

try:
    from .pathlib_transformer_optimized import PathlibTransformer  # noqa: F401

    artisans.append("PathlibTransformer")
except ImportError:
    pass

try:
    from .print_to_logging_transform import PrintToLoggingTransform  # noqa: F401

    artisans.append("PrintToLoggingTransform")
except ImportError:
    pass

try:
    from .unused_import_remover import UnusedImportRemover  # noqa: F401

    artisans.append("UnusedImportRemover")
except ImportError:
    pass

__all__ = artisans
