import json
import logging
import os
import subprocess

from PyQt5.QtCore import QThread, pyqtSignal


class RuffWorker(QThread):
    """Worker thread pour executer Ruff en arriere-plan"""

    output_received = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    progress_updated = pyqtSignal(int)
    finished_successfully = pyqtSignal(dict)

    def __init__(self, command_type, target_path, options):
        super().__init__()
        self.command_type = command_type
        self.target_path = target_path
        self.options = options
        self.logger = logging.getLogger(__name__)

    def run(self):
        """Execute la commande Ruff appropriee"""
        try:
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
        """Execute ruff check"""
        cmd = ["ruff", "check", self.target_path]
        if self.options.get("fix", False):
            cmd.append("--fix")

        self.progress_updated.emit(50)
        result = self._execute_command(cmd)
        self.progress_updated.emit(100)

        if result["stdout"]:
            self.output_received.emit(result["stdout"])
        elif result["returncode"] == 0:
            self.output_received.emit("Aucun probleme detecte!")

        if result["stderr"]:
            self.error_occurred.emit(result["stderr"])

    def _run_format(self):
        """Execute ruff format"""
        cmd = ["ruff", "format", self.target_path]
        result = self._execute_command(cmd)

        if result["returncode"] == 0:
            self.output_received.emit("Formatage termine avec succes!")
        else:
            self.output_received.emit(result["stdout"] or "Formatage termine!")

        if result["stderr"]:
            self.error_occurred.emit(result["stderr"])

    def _run_analyze_for_ai(self):
        """Analyse pour l'IA"""
        cmd = ["ruff", "check", self.target_path, "--format=json"]
        result = self._execute_command(cmd)

        try:
            if result["stdout"].strip():
                issues = json.loads(result["stdout"])
                analysis = {
                    "total_issues": len(issues),
                    "issues": issues,
                    "target_path": self.target_path,
                }
                self.finished_successfully.emit(analysis)
            else:
                self.finished_successfully.emit(
                    {"total_issues": 0, "issues": [], "target_path": self.target_path}
                )
        except json.JSONDecodeError as e:
            self.error_occurred.emit(f"Erreur parsing JSON Ruff: {e}")
        except Exception as e:
            self.error_occurred.emit(f"Erreur analyse IA: {e}")

    def _execute_command(self, cmd):
        """Execute une commande avec gestion robuste de l'encodage"""
        try:
            # Configurer l'environnement pour UTF-8
            env = os.environ.copy()
            env["PYTHONIOENCODING"] = "utf-8"

            # Sur Windows, forcer l'encodage UTF-8
            if os.name == "nt":
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",  # Remplace les caracteres non decodables
                    timeout=300,
                    env=env,
                    creationflags=subprocess.CREATE_NO_WINDOW
                    if hasattr(subprocess, "CREATE_NO_WINDOW")
                    else 0,
                )
            else:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    timeout=300,
                    env=env,
                )

            return {
                "stdout": result.stdout or "",
                "stderr": result.stderr or "",
                "returncode": result.returncode,
            }

        except subprocess.TimeoutExpired:
            return {
                "stdout": "",
                "stderr": "Commande expiree (timeout 5 minutes)",
                "returncode": -1,
            }
        except FileNotFoundError:
            return {
                "stdout": "",
                "stderr": "Ruff non trouve. Installez avec: pip install ruff",
                "returncode": -1,
            }
        except UnicodeDecodeError as e:
            return {
                "stdout": "",
                "stderr": f"Erreur encodage Unicode: {e}",
                "returncode": -1,
            }
        except Exception as e:
            return {
                "stdout": "",
                "stderr": f"Erreur execution commande: {e}",
                "returncode": -1,
            }
