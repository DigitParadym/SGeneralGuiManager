"""
Wrappers generiques pour outils externes de transformation Python.
Version 3.0 - Architecture totalement flexible et extensible.
"""

import sys  # noqa: F401
from pathlib import Path  # noqa: F401

# Ajouter le chemin parent pour les imports
sys.path.append(str(Path(__file__).parent.parent.parent))

wrappers = []

try:
    from .base_wrapper import BaseWrapper  # noqa: F401

    wrappers.append("BaseWrapper")
except ImportError:
    pass

try:
    from .ruff_wrapper import RuffWrapper  # noqa: F401

    wrappers.append("RuffWrapper")
except ImportError:
    pass

try:
    from .pyupgrade_wrapper import PyupgradeWrapper  # noqa: F401

    wrappers.append("PyupgradeWrapper")
except ImportError:
    pass

__all__ = wrappers
