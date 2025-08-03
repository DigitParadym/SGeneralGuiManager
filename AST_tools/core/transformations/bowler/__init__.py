"""
Module bowler - Integration avec Bowler de Meta pour les transformations AST.

Ce module fournit une interface pour utiliser Bowler, l'outil de refactoring
automatise de Meta, dans le systeme de transformation AST.
"""

# Imports principaux
from .bowler_integration import BowlerIntegration
from .bowler_transformers import BowlerTransformers
from .bowler_queries import BowlerQueries
from .bowler_utils import BowlerUtils

__all__ = [
    'BowlerIntegration',
    'BowlerTransformers', 
    'BowlerQueries',
    'BowlerUtils',
]

__version__ = "1.0.0"

# Verification de la disponibilite de Bowler
try:
    import bowler
    BOWLER_AVAILABLE = True
except ImportError:
    BOWLER_AVAILABLE = False
    print("Warning: Bowler n'est pas installe. Installez avec: pip install bowler")
