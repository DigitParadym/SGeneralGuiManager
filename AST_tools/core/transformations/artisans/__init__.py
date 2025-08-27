"""
Transformations artisanales avec logique interne.
Type 2 - Intelligence Interne
"""

from pathlib import Path
import sys

# Ajouter le chemin parent pour les imports
sys.path.append(str(Path(__file__).parent.parent.parent))

# Import des transformations artisanales
artisans = []

try:
    from .add_docstrings_transform import AddDocstringsTransform
    artisans.append('AddDocstringsTransform')
except ImportError:
    pass

try:
    from .pathlib_transformer_optimized import PathlibTransformer
    artisans.append('PathlibTransformer')
except ImportError:
    pass

try:
    from .print_to_logging_transform import PrintToLoggingTransform
    artisans.append('PrintToLoggingTransform')
except ImportError:
    pass

try:
    from .unused_import_remover import UnusedImportRemover
    artisans.append('UnusedImportRemover')
except ImportError:
    pass

__all__ = artisans
