#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Systeme de Log Global pour AST_tools
Garde toujours la trace de la DERNIERE execution complete.
"""

import logging
import os
import sys
import shutil
from datetime import datetime
from pathlib import Path

# Configuration du logger global
_LOGGER = None
_LOG_FILE = "ast_tools.log"
_BACKUP_FILE = "ast_tools_previous.log"

def _setup_logger():
    """Configure le logger global pour AST_tools."""
    global _LOGGER
    
    if _LOGGER is not None:
        return _LOGGER
    
    # Creer le repertoire de logs si necessaire
    log_dir = Path(__file__).parent.parent
    log_path = log_dir / _LOG_FILE
    backup_path = log_dir / _BACKUP_FILE
    
    # Sauvegarder le log precedent si il existe
    if log_path.exists():
        shutil.copy2(log_path, backup_path)
    
    # Configuration du logger
    _LOGGER = logging.getLogger('AST_tools')
    _LOGGER.setLevel(logging.DEBUG)
    
    # Effacer les handlers existants
    for handler in _LOGGER.handlers[:]:
        _LOGGER.removeHandler(handler)
    
    # Handler pour fichier (ecrase a chaque fois)
    file_handler = logging.FileHandler(log_path, mode='w', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    
    # Handler pour console (optionnel, niveau INFO seulement)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    
    # Format detaille pour le fichier
    file_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Format simple pour la console
    console_formatter = logging.Formatter('%(levelname)s: %(message)s')
    
    file_handler.setFormatter(file_formatter)
    console_handler.setFormatter(console_formatter)
    
    _LOGGER.addHandler(file_handler)
    _LOGGER.addHandler(console_handler)
    
    return _LOGGER

def log_start(message):
    """Demarre une nouvelle session de log."""
    logger = _setup_logger()
    
    # En-tete de session
    logger.info("=" * 80)
    logger.info("DEBUT SESSION AST_TOOLS - %s" % datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    logger.info("=" * 80)
    logger.info(message)
    logger.info("-" * 80)

def log_info(message):
    """Log d'information generale."""
    logger = _setup_logger()
    logger.info(message)

def log_success(message):
    """Log de succes."""
    logger = _setup_logger()
    logger.info("SUCCESS: %s" % message)

def log_warning(message):
    """Log d'avertissement."""
    logger = _setup_logger()
    logger.warning("WARNING: %s" % message)

def log_error(message):
    """Log d'erreur."""
    logger = _setup_logger()
    logger.error("ERROR: %s" % message)

def log_debug(message):
    """Log de debug (seulement dans le fichier)."""
    logger = _setup_logger()
    logger.debug("DEBUG: %s" % message)

def log_transformation(transformer_name, file_path, success):
    """Log specialise pour les transformations."""
    logger = _setup_logger()
    status = "SUCCESS" if success else "FAILED"
    logger.info("TRANSFORM [%s] %s -> %s" % (status, transformer_name, os.path.basename(file_path)))

def log_plugin_load(plugin_name, version, success):
    """Log specialise pour le chargement de plugins."""
    logger = _setup_logger()
    if success:
        logger.info("PLUGIN LOADED: %s v%s" % (plugin_name, version))
    else:
        logger.error("PLUGIN FAILED: %s v%s" % (plugin_name, version))

def log_file_operation(operation, file_path, success):
    """Log specialise pour les operations fichiers."""
    logger = _setup_logger()
    status = "SUCCESS" if success else "FAILED"
    logger.info("FILE [%s] %s: %s" % (status, operation, os.path.basename(file_path)))

def log_end(message):
    """Termine la session de log."""
    logger = _setup_logger()
    
    logger.info("-" * 80)
    logger.info(message)
    logger.info("FIN SESSION AST_TOOLS - %s" % datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    logger.info("=" * 80)
    logger.info("")  # Ligne vide finale

def get_log_file_path():
    """Retourne le chemin du fichier de log actuel."""
    log_dir = Path(__file__).parent.parent
    return str(log_dir / _LOG_FILE)

def copy_log_for_debug(destination=None):
    """Copie le log actuel pour debug/partage."""
    if destination is None:
        destination = "ast_tools_debug_%s.log" % datetime.now().strftime('%Y%m%d_%H%M%S')
    
    log_path = get_log_file_path()
    if os.path.exists(log_path):
        shutil.copy2(log_path, destination)
        log_info("Log copie vers: %s" % destination)
        return destination
    else:
        log_error("Aucun fichier de log a copier")
        return None

# Test rapide si execute directement
if __name__ == "__main__":
    log_start("Test du systeme de log global")
    log_info("Test des differents niveaux de log")
    log_success("Operation reussie")
    log_warning("Attention a quelque chose")
    log_error("Une erreur de test")
    log_debug("Information de debug")
    log_transformation("TestTransformer", "test.py", True)
    log_plugin_load("TestPlugin", "1.0.0", True)
    log_file_operation("READ", "test.py", True)
    log_end("Test termine")
    
    print("Log cree dans: %s" % get_log_file_path())
