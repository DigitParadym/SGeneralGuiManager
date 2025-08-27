"""
Wrappers pour outils externes de transformation Python.
Type 1 - Intelligence Externe
"""

from pathlib import Path
import sys

# Ajouter le chemin parent pour les imports
sys.path.append(str(Path(__file__).parent.parent.parent))

# Import des wrappers disponibles
wrappers = []

try:
    from .black_wrapper import BlackWrapper
    wrappers.append('BlackWrapper')
except ImportError:
    pass

try:
    from .isort_wrapper import IsortWrapper
    wrappers.append('IsortWrapper')
except ImportError:
    pass

try:
    from .ruff_wrapper import RuffWrapper
    wrappers.append('RuffWrapper')
except ImportError:
    pass

try:
    from .autoflake_wrapper import AutoflakeWrapper
    wrappers.append('AutoflakeWrapper')
except ImportError:
    pass

try:
    from .autopep8_wrapper import Autopep8Wrapper
    wrappers.append('Autopep8Wrapper')
except ImportError:
    pass

try:
    from .pyupgrade_wrapper import PyupgradeWrapper
    wrappers.append('PyupgradeWrapper')
except ImportError:
    pass

__all__ = wrappers
