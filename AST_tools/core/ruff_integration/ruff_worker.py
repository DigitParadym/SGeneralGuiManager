#!/usr/bin/env python3
"""
RuffWorker - Version PySide6 Complete (Sans Unicode)
===================================================
Worker thread pour executer Ruff en arriere-plan avec PySide6.
Version sans caracteres Unicode pour compatibilite maximale.
"""

import json
import logging
import os
import subprocess

from PySide6.QtCore import QThread, Signal


class RuffWorker(QThread):
    """Worker thread pour executer Ruff en arriere-plan."""

    # Signaux PySide6
    output_received = Signal(str)
    error_occurred = Signal(str)
    progress_updated = Signal(int)
    finished_successfully = Signal(dict)

    def __init__(self, command_type, target_path, options):
        super().__init__()
        self.command_type = command_type
        self.target_path = target_path
        self.options = options
        self.is_cancelled = False
        self.logger = logging.getLogger(__name__)

    def run(self):
        """Execute la commande Ruff."""
        try:
            self.logger.info(f"Demarrage RuffWorker: {self.command_type}")

            if self.command_type == "check":
                self._run_check()
            elif self.command_type == "format":
                self._run_format()
            elif self.command_type == "analyze_for_ai":
                self._run_analyze_for_ai()
        except Exception as e:
            self.logger.error(f"Erreur dans RuffWorker: {e}")
            self.error_occurred.emit(str(e))

    def _run_check(self):
        """Execute ruff check."""
        cmd = ["ruff", "check", self.target_path]
        if self.options.get("fix", False):
            cmd.append("--fix")

        self.progress_updated.emit(50)
        result = self._execute_command(cmd)
        self.progress_updated.emit(100)

        if result["returncode"] == 0:
            if result["stdout"].strip():
                self.output_received.emit(result["stdout"])
            else:
                self.output_received.emit("[SUCCES] Aucun probleme detecte par Ruff !")
        else:
            if result["stdout"].strip():
                self.output_received.emit(result["stdout"])
            else:
                self.output_received.emit("Analyse terminee avec des avertissements")

        if result["stderr"]:
            self.error_occurred.emit(result["stderr"])

    def _run_format(self):
        """Execute ruff format."""
        cmd = ["ruff", "format", self.target_path]

        if self.options.get("preview", False):
            cmd.append("--diff")

        result = self._execute_command(cmd)

        if result["returncode"] == 0:
            if result["stdout"].strip():
                self.output_received.emit(
                    f"[SUCCES] Formatage termine:\n{result['stdout']}"
                )
            else:
                self.output_received.emit("[SUCCES] Formatage termine avec succes !")
        else:
            if result["stdout"].strip():
                self.output_received.emit(
                    f"[AVERTISSEMENT] Formatage avec avertissements:\n{result['stdout']}"
                )
            else:
                self.output_received.emit("[ERREUR] Erreur durant le formatage")

        if result["stderr"]:
            self.error_occurred.emit(result["stderr"])

    def _run_analyze_for_ai(self):
        """Execute l'analyse pour l'IA."""
        cmd = ["ruff", "check", self.target_path, "--format=json"]
        result = self._execute_command(cmd)

        try:
            if result["stdout"].strip():
                issues = json.loads(result["stdout"])
                analysis = {
                    "total_issues": len(issues),
                    "issues": issues,
                    "target_path": self.target_path,
                    "categories": self._categorize_issues(issues),
                    "severity_summary": self._analyze_severity(issues),
                }
            else:
                analysis = {
                    "total_issues": 0,
                    "issues": [],
                    "target_path": self.target_path,
                    "categories": {},
                    "severity_summary": {"error": 0, "warning": 0, "info": 0},
                }

            self.logger.info(
                f"Analyse IA terminee: {analysis['total_issues']} problemes"
            )
            self.finished_successfully.emit(analysis)

        except json.JSONDecodeError as e:
            self.logger.error(f"Erreur JSON: {e}")
            self.error_occurred.emit(f"Erreur de parsing JSON: {str(e)}")
        except Exception as e:
            self.logger.error(f"Erreur analyse IA: {e}")
            self.error_occurred.emit(f"Erreur durant l'analyse IA: {str(e)}")

    def _categorize_issues(self, issues):
        """Categorise les problemes par type."""
        categories = {}
        for issue in issues:
            code = issue.get("code", "UNKNOWN")
            category = self._get_issue_category(code)
            if category not in categories:
                categories[category] = []
            categories[category].append(issue)
        return categories

    def _get_issue_category(self, code):
        """Determine la categorie d'un code d'erreur."""
        if code.startswith("E"):
            return "Style et Formatage"
        elif code.startswith("F"):
            return "Erreurs Python"
        elif code.startswith("W"):
            return "Avertissements"
        elif code.startswith("I"):
            return "Imports"
        elif code.startswith("N"):
            return "Nommage"
        elif code.startswith("D"):
            return "Documentation"
        else:
            return "Autres"

    def _analyze_severity(self, issues):
        """Analyse la severite des problemes."""
        severity_count = {"error": 0, "warning": 0, "info": 0}
        for issue in issues:
            code = issue.get("code", "")
            if code.startswith("F") or code.startswith("E9"):
                severity_count["error"] += 1
            elif code.startswith("W") or code.startswith("E"):
                severity_count["warning"] += 1
            else:
                severity_count["info"] += 1
        return severity_count

    def _execute_command(self, cmd):
        """Execute une commande avec gestion robuste."""
        try:
            self.logger.info(f"Execution: {' '.join(cmd)}")

            # Configuration environnement UTF-8
            env = os.environ.copy()
            env["PYTHONIOENCODING"] = "utf-8"

            # Arguments communs
            common_args = {
                "capture_output": True,
                "text": True,
                "encoding": "utf-8",
                "errors": "replace",
                "timeout": 300,
                "env": env,
            }

            # Windows: configuration specifique
            if os.name == "nt":
                common_args["creationflags"] = (
                    subprocess.CREATE_NO_WINDOW
                    if hasattr(subprocess, "CREATE_NO_WINDOW")
                    else 0
                )

            # Verification annulation
            if self.is_cancelled:
                return {"stdout": "", "stderr": "Operation annulee", "returncode": -1}

            # Execution
            result = subprocess.run(cmd, **common_args)

            self.logger.info(f"Commande terminee: code {result.returncode}")

            return {
                "stdout": result.stdout or "",
                "stderr": result.stderr or "",
                "returncode": result.returncode,
            }

        except subprocess.TimeoutExpired:
            self.logger.warning("Timeout commande Ruff")
            return {
                "stdout": "",
                "stderr": "Commande expiree (timeout 5 minutes)",
                "returncode": -1,
            }
        except FileNotFoundError:
            self.logger.error("Ruff non trouve")
            return {
                "stdout": "",
                "stderr": "Ruff non trouve. Installez avec: pip install ruff",
                "returncode": -1,
            }
        except UnicodeDecodeError as e:
            self.logger.error(f"Erreur encodage: {e}")
            return {
                "stdout": "",
                "stderr": f"Erreur encodage Unicode: {str(e)}",
                "returncode": -1,
            }
        except Exception as e:
            self.logger.error(f"Erreur inattendue: {e}")
            return {
                "stdout": "",
                "stderr": f"Erreur execution: {str(e)}",
                "returncode": -1,
            }

    def cancel(self):
        """Annule l'operation."""
        self.is_cancelled = True
        self.logger.info("Annulation demandee")
