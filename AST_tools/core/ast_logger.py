# AST_tools/core/ast_logger.py
"""
Module de logging robuste pour AST_tools
"""

import logging
import sys
from datetime import datetime
from pathlib import Path


def setup_logging():
    """Configure le logging avec une config robuste par defaut."""
    project_root = Path(__file__).parent.parent
    logs_dir = project_root / "logs"
    logs_dir.mkdir(exist_ok=True)

    # Format detaille
    detailed_format = "%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s"

    # Configuration du logger principal
    logger = logging.getLogger("ast_tools")
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
    main_file = logs_dir / "ast_tools.log"
    file_handler = logging.FileHandler(main_file, mode="w", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(console_formatter)
    logger.addHandler(file_handler)

    # Handler erreurs
    error_file = logs_dir / "errors.log"
    error_handler = logging.FileHandler(error_file, mode="a", encoding="utf-8")
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(console_formatter)
    logger.addHandler(error_handler)

    logger.propagate = False
    print("+ Systeme de logging configure")
    return True


# Initialiser au chargement
setup_logging()
log = logging.getLogger("ast_tools")


# Fonctions simplifiees
def log_info(message):
    log.info(str(message))


def log_success(message):
    log.info(f"SUCCESS: {message!s}")


def log_warning(message):
    log.warning(f"WARNING: {message!s}")


def log_error(message, exc_info=False):
    log.error(f"ERROR: {message!s}", exc_info=exc_info)


def log_start(operation_name):
    separator = "=" * 80
    log.info(separator)
    log.info("DEBUT SESSION AST_TOOLS - {}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    log.info(separator)
    log.info(f"{operation_name!s}")
    log.info("-" * 80)


def log_end(operation_name):
    log.info("-" * 80)
    log.info(f"FIN: {operation_name!s}")
    log.info("=" * 80)


def log_transformation(transformer_name, filename, success=True, details=""):
    status = "SUCCESS" if success else "FAILED"
    message = f"TRANSFORMATION: {transformer_name} sur {filename} - {status}"
    if details:
        message += f" - {details}"

    if success:
        log.info(message)
    else:
        log.error(message)


def log_plan_info(plan_data, plan_file):
    log.info("=== PLAN DE TRANSFORMATION ===")
    log.info(f"Fichier: {plan_file}")
    log.info("Nom: {}".format(plan_data.get("name", "N/A")))
    log.info("Description: {}".format(plan_data.get("description", "N/A")))
    transformations = plan_data.get("transformations", [])
    log.info(f"Nombre de transformations: {len(transformations)}")
    log.info("=" * 50)


def log_exception(operation, exception):
    import traceback

    log.error(f"EXCEPTION pendant {operation}: {exception!s}")
    log.error("Traceback complet:")
    log.error(traceback.format_exc())


# Message de confirmation
log.info("Module ast_logger initialise")
