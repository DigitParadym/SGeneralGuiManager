"""Fichier de test propre."""

import logging

logger = logging.getLogger(__name__)


def good_function(x: int, y: int) -> str:
    """Fonction bien formatee."""
    result = f"Result: {x + y}"

    if x is True:
        logger.info("Processing")

    return result
