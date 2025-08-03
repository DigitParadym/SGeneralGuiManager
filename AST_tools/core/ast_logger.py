# AST_tools/core/ast_logger.py
"""
Module de logging robuste pour AST_tools
"""

import logging
import os
import sys
from pathlib import Path
from datetime import datetime

def setup_logging():
    """Configure le logging avec une config robuste par defaut."""
    project_root = Path(__file__).parent.parent
    logs_dir = project_root / 'logs'
    logs_dir.mkdir(exist_ok=True)
    
    # Format detaille
    detailed_format = '%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s'
    
    # Configuration du logger principal
    logger = logging.getLogger('ast_tools')
    logger.setLevel(logging.DEBUG)
    
    # Supprimer handlers existants
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Handler console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(detailed_format)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # Handler fichier principal
    main_file = logs_dir / 'ast_tools.log'
    file_handler = logging.FileHandler(main_file, mode='w', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(console_formatter)
    logger.addHandler(file_handler)
    
    # Handler erreurs
    error_file = logs_dir / 'errors.log'
    error_handler = logging.FileHandler(error_file, mode='a', encoding='utf-8')
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(console_formatter)
    logger.addHandler(error_handler)
    
    logger.propagate = False
    print("+ Systeme de logging configure")
    return True

# Initialiser au chargement
setup_logging()
log = logging.getLogger('ast_tools')

# Fonctions simplifiees
def log_info(message):
    log.info(str(message))

def log_success(message):
    log.info("SUCCESS: %s" % str(message))

def log_warning(message):
    log.warning("WARNING: %s" % str(message))

def log_error(message, exc_info=False):
    log.error("ERROR: %s" % str(message), exc_info=exc_info)

def log_start(operation_name):
    separator = "=" * 80
    log.info(separator)
    log.info("DEBUT SESSION AST_TOOLS - %s" % datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    log.info(separator)
    log.info("%s" % str(operation_name))
    log.info("-" * 80)

def log_end(operation_name):
    log.info("-" * 80)
    log.info("FIN: %s" % str(operation_name))
    log.info("=" * 80)

def log_transformation(transformer_name, filename, success=True, details=""):
    status = "SUCCESS" if success else "FAILED"
    message = "TRANSFORMATION: %s sur %s - %s" % (transformer_name, filename, status)
    if details:
        message += " - %s" % details
    
    if success:
        log.info(message)
    else:
        log.error(message)

def log_plan_info(plan_data, plan_file):
    log.info("=== PLAN DE TRANSFORMATION ===")
    log.info("Fichier: %s" % plan_file)
    log.info("Nom: %s" % plan_data.get('name', 'N/A'))
    log.info("Description: %s" % plan_data.get('description', 'N/A'))
    transformations = plan_data.get('transformations', [])
    log.info("Nombre de transformations: %d" % len(transformations))
    log.info("=" * 50)

def log_exception(operation, exception):
    import traceback
    log.error("EXCEPTION pendant %s: %s" % (operation, str(exception)))
    log.error("Traceback complet:")
    log.error(traceback.format_exc())

# Message de confirmation
log.info("Module ast_logger initialise")
