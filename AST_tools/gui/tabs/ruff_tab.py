#!/usr/bin/env python3
"""
Module Ruff Tab - Version Complete avec Analyser et Fix
Inclut selection recursive et nouveau bouton pour analyser + corriger automatiquement
Compatible Windows - Sans caracteres Unicode
"""

import json
import os
import subprocess
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class RuffWorker(QThread):
    """Worker pour executer Ruff en arriere-plan."""

    progress = Signal(str)
    finished = Signal(dict)
    file_progress = Signal(int, int)  # current, total

    def __init__(self, files, command="check", auto_fix=False):
        super().__init__()
        self.files = files
        self.command = command
        self.auto_fix = auto_fix  # Nouveau parametre pour --fix

    def run(self):
        """Execute Ruff sur les fichiers."""
        results = {"files": [], "total_issues": 0, "fixed_issues": 0}
        total_files = len(self.files)

        for index, file in enumerate(self.files, 1):
            self.file_progress.emit(index, total_files)
            self.progress.emit(
                f"Analyse de {os.path.basename(file)}... ({index}/{total_files})"
            )

            try:
                if self.command == "check":
                    # Construire la commande avec ou sans --fix
                    cmd = ["ruff", "check", file]
                    if self.auto_fix:
                        cmd.append("--fix")

                    # Premiere execution pour obtenir les stats
                    result = subprocess.run(
                        cmd + ["--format", "json"],
                        capture_output=True,
                        text=True,
                        timeout=30,
                    )

                    file_result = {
                        "file": file,
                        "output": result.stdout,
                        "errors": result.stderr,
                        "fixed": self.auto_fix,
                    }

                    # Compter les issues
                    try:
                        if result.stdout.strip():
                            issues = json.loads(result.stdout)
                            if isinstance(issues, list):
                                results["total_issues"] += len(issues)
                    except json.JSONDecodeError:
                        pass

                    # Si on a fait un fix, obtenir le nombre de corrections
                    if self.auto_fix and result.returncode == 0:
                        # Ruff retourne 0 si des corrections ont ete appliquees
                        file_result["fix_status"] = "success"
                        # Compter approximativement les corrections
                        if "Fixed" in result.stderr:
                            # Extraire le nombre si possible
                            results["fixed_issues"] += 1

                    results["files"].append(file_result)

                elif self.command == "format":
                    result = subprocess.run(
                        ["ruff", "format", file],
                        capture_output=True,
                        text=True,
                        timeout=30,
                    )
                    results["files"].append(
                        {
                            "file": file,
                            "formatted": result.returncode == 0,
                            "output": result.stdout,
                        }
                    )

            except subprocess.TimeoutExpired:
                results["files"].append({"file": file, "error": "Timeout (>30s)"})
            except Exception as e:
                results["files"].append({"file": file, "error": str(e)})

        self.finished.emit(results)


class RuffIntegrationTab(QWidget):
    """Onglet d'integration Ruff avec selection recursive et auto-fix."""

    ai_plan_ready = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.last_analysis_data = {}
        self.current_worker = None
        self.setup_ui()
        self.check_ruff_availability()

    def setup_ui(self):
        """Cree l'interface utilisateur amelioree."""
        layout = QVBoxLayout(self)

        # En-tete
        header = QLabel("Analyse et Formatage avec Ruff")
        header.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        layout.addWidget(header)

        # Splitter principal
        splitter = QSplitter(Qt.Horizontal)

        # === PANNEAU GAUCHE - CONTROLES ===
        left_panel = QGroupBox("Controles")
        left_layout = QVBoxLayout(left_panel)

        # Section: Fichiers a analyser
        files_label = QLabel("Fichiers a analyser:")
        files_label.setStyleSheet("font-weight: bold; margin-top: 5px;")
        left_layout.addWidget(files_label)

        self.files_list = QListWidget()
        self.files_list.setToolTip("Liste des fichiers Python a analyser")
        left_layout.addWidget(self.files_list)

        # Compteur de fichiers
        self.file_count_label = QLabel("0 fichier(s)")
        self.file_count_label.setStyleSheet("color: gray; font-size: 10px;")
        left_layout.addWidget(self.file_count_label)

        # === BOUTONS DE SELECTION ===
        selection_layout = QVBoxLayout()

        # Ligne 1: Fichiers individuels
        file_btn_layout = QHBoxLayout()
        self.add_files_btn = QPushButton("+ Fichiers")
        self.add_files_btn.setToolTip("Selectionner des fichiers Python individuels")
        self.clear_btn = QPushButton("Vider")
        self.clear_btn.setToolTip("Vider la liste des fichiers")
        file_btn_layout.addWidget(self.add_files_btn)
        file_btn_layout.addWidget(self.clear_btn)

        # Ligne 2: Selection de dossier
        folder_btn_layout = QHBoxLayout()
        self.add_folder_btn = QPushButton("+ Dossier (Recursif)")
        self.add_folder_btn.setToolTip(
            "Selectionner un dossier et inclure tous les fichiers Python recursivement"
        )
        self.add_folder_btn.setStyleSheet("""
            QPushButton {
                background-color: #2b5797;
                color: white;
                font-weight: bold;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #3a6ba8;
            }
        """)
        folder_btn_layout.addWidget(self.add_folder_btn)

        selection_layout.addLayout(file_btn_layout)
        selection_layout.addLayout(folder_btn_layout)
        left_layout.addLayout(selection_layout)

        # Separateur visuel
        left_layout.addWidget(QLabel(""))  # Espace

        # === BOUTONS D'ACTION ===
        # Bouton Analyser (check seulement)
        self.check_btn = QPushButton("Analyser (ruff check)")
        self.check_btn.setToolTip(
            "Lancer l'analyse Ruff sur les fichiers selectionnes (diagnostic seulement)"
        )

        # NOUVEAU: Bouton Analyser et Fix
        self.check_fix_btn = QPushButton("Analyser et Fix (--fix)")
        self.check_fix_btn.setToolTip(
            "Analyser ET corriger automatiquement les erreurs reparables"
        )
        self.check_fix_btn.setStyleSheet("""
            QPushButton {
                background-color: #5cb85c;
                color: white;
                font-weight: bold;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #4cae4c;
            }
        """)

        # Bouton Formater
        self.format_btn = QPushButton("Formater (ruff format)")
        self.format_btn.setToolTip("Formater automatiquement les fichiers selectionnes")

        # Bouton Exporter
        self.export_btn = QPushButton("Exporter")
        self.export_btn.setToolTip("Exporter les resultats de l'analyse")

        # Style pour les boutons d'action
        action_style = """
            QPushButton {
                padding: 8px;
                font-weight: bold;
            }
        """
        self.check_btn.setStyleSheet(action_style)
        self.format_btn.setStyleSheet(action_style)
        self.export_btn.setStyleSheet(action_style)

        left_layout.addWidget(self.check_btn)
        left_layout.addWidget(self.check_fix_btn)  # NOUVEAU bouton
        left_layout.addWidget(self.format_btn)
        left_layout.addWidget(self.export_btn)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        left_layout.addWidget(self.progress_bar)

        # Label de progression
        self.progress_label = QLabel("")
        self.progress_label.setVisible(False)
        self.progress_label.setStyleSheet("font-size: 10px; color: gray;")
        left_layout.addWidget(self.progress_label)

        # Bouton d'annulation
        self.cancel_btn = QPushButton("Annuler")
        self.cancel_btn.setVisible(False)
        self.cancel_btn.setStyleSheet("background-color: #d9534f; color: white;")
        left_layout.addWidget(self.cancel_btn)

        left_layout.addStretch()

        # === PANNEAU DROIT - RESULTATS ===
        right_panel = QGroupBox("Resultats")
        right_layout = QVBoxLayout(right_panel)

        # Zone de texte pour les resultats
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setFont(self.font())
        right_layout.addWidget(self.output_text)

        # Statistiques
        self.stats_label = QLabel("Statistiques: -")
        self.stats_label.setStyleSheet("font-weight: bold; padding: 5px;")
        right_layout.addWidget(self.stats_label)

        # Ajouter les panneaux au splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([350, 550])

        layout.addWidget(splitter)

        # === CONNEXIONS ===
        self.add_files_btn.clicked.connect(self.add_files)
        self.add_folder_btn.clicked.connect(self.add_folder_recursive)
        self.clear_btn.clicked.connect(self.clear_files)
        self.check_btn.clicked.connect(self.run_check)
        self.check_fix_btn.clicked.connect(self.run_check_fix)  # NOUVEAU
        self.format_btn.clicked.connect(self.run_format)
        self.export_btn.clicked.connect(self.export_results)
        self.cancel_btn.clicked.connect(self.cancel_operation)

    def check_ruff_availability(self):
        """Verifie si Ruff est installe."""
        try:
            result = subprocess.run(
                ["ruff", "--version"], capture_output=True, text=True
            )
            self.log_message(f"[OK] Ruff disponible: {result.stdout.strip()}")
        except (FileNotFoundError, subprocess.SubprocessError, Exception):
            self.log_message("[X] Ruff non installe. Installez avec: pip install ruff")
            self.check_btn.setEnabled(False)
            self.check_fix_btn.setEnabled(False)
            self.format_btn.setEnabled(False)

    def add_files(self):
        """Ajoute des fichiers individuels a analyser."""
        files, _ = QFileDialog.getOpenFileNames(
            self, "Selectionner des fichiers Python", "", "Python (*.py)"
        )
        added_count = 0
        for file in files:
            if not self.is_file_in_list(file):
                item = QListWidgetItem(self.get_display_path(file))
                item.setData(Qt.UserRole, file)
                self.files_list.addItem(item)
                added_count += 1

        if added_count > 0:
            self.log_message(f"[OK] {added_count} fichier(s) ajoute(s)")
            self.update_file_count()

    def add_folder_recursive(self):
        """Ajoute tous les fichiers Python d'un dossier recursivement."""
        folder = QFileDialog.getExistingDirectory(
            self, "Selectionner un dossier a analyser recursivement"
        )

        if not folder:
            return

        self.log_message(f"Recherche des fichiers Python dans: {folder}")

        py_files = []
        excluded_dirs = {
            ".venv",
            "venv",
            "__pycache__",
            ".git",
            "node_modules",
            ".ruff_cache",
        }

        for root, dirs, files in os.walk(folder):
            dirs[:] = [d for d in dirs if d not in excluded_dirs]

            for file in files:
                if file.endswith(".py"):
                    full_path = os.path.join(root, file)
                    py_files.append(full_path)

        added_count = 0
        for file_path in py_files:
            if not self.is_file_in_list(file_path):
                display_path = self.get_relative_path(file_path, folder)
                item = QListWidgetItem(display_path)
                item.setData(Qt.UserRole, file_path)
                item.setToolTip(file_path)
                self.files_list.addItem(item)
                added_count += 1

        if added_count > 0:
            self.log_message(
                f"[OK] {added_count} fichier(s) Python trouve(s) et ajoute(s)"
            )
        else:
            self.log_message(f"[!] Aucun nouveau fichier Python trouve dans {folder}")

        self.update_file_count()

    def is_file_in_list(self, file_path):
        """Verifie si un fichier est deja dans la liste."""
        for i in range(self.files_list.count()):
            if self.files_list.item(i).data(Qt.UserRole) == file_path:
                return True
        return False

    def get_display_path(self, file_path):
        """Retourne un chemin d'affichage simplifie."""
        try:
            return os.path.relpath(file_path)
        except ValueError:
            return os.path.basename(file_path)

    def get_relative_path(self, file_path, base_folder):
        """Retourne le chemin relatif d'un fichier par rapport a un dossier de base."""
        try:
            return os.path.relpath(file_path, base_folder)
        except ValueError:
            return os.path.basename(file_path)

    def update_file_count(self):
        """Met a jour le compteur de fichiers."""
        count = self.files_list.count()
        self.file_count_label.setText(f"{count} fichier(s)")

        has_files = count > 0
        self.check_btn.setEnabled(has_files)
        self.check_fix_btn.setEnabled(has_files)
        self.format_btn.setEnabled(has_files)

    def clear_files(self):
        """Vide la liste des fichiers."""
        self.files_list.clear()
        self.log_message("Liste videe")
        self.update_file_count()

    def get_selected_files(self):
        """Recupere la liste des chemins complets des fichiers."""
        files = []
        for i in range(self.files_list.count()):
            item = self.files_list.item(i)
            file_path = item.data(Qt.UserRole)
            if file_path:
                files.append(file_path)
        return files

    def run_check(self):
        """Lance l'analyse Ruff SANS correction automatique."""
        files = self.get_selected_files()
        if not files:
            self.log_message("[!] Aucun fichier a analyser")
            return

        self.show_progress(True)
        self.log_message(f"Demarrage de l'analyse sur {len(files)} fichier(s)...")
        self.log_message("[INFO] Mode: Diagnostic seulement (pas de correction)")

        self.current_worker = RuffWorker(files, "check", auto_fix=False)
        self.current_worker.progress.connect(self.log_message)
        self.current_worker.file_progress.connect(self.update_progress)
        self.current_worker.finished.connect(self.on_check_finished)
        self.current_worker.start()

    def run_check_fix(self):
        """NOUVEAU: Lance l'analyse Ruff AVEC correction automatique (--fix)."""
        files = self.get_selected_files()
        if not files:
            self.log_message("[!] Aucun fichier a analyser")
            return

        # Confirmation avant de modifier les fichiers
        reply = QMessageBox.question(
            self,
            "Confirmation",
            f"Analyser et corriger automatiquement {len(files)} fichier(s) ?\n\n"
            "Cette action va modifier directement les fichiers pour corriger "
            "les erreurs reparables automatiquement.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply != QMessageBox.Yes:
            return

        self.show_progress(True)
        self.log_message(
            f"Demarrage de l'analyse avec correction sur {len(files)} fichier(s)..."
        )
        self.log_message("[INFO] Mode: Analyse et correction automatique (--fix)")

        self.current_worker = RuffWorker(files, "check", auto_fix=True)
        self.current_worker.progress.connect(self.log_message)
        self.current_worker.file_progress.connect(self.update_progress)
        self.current_worker.finished.connect(self.on_check_fix_finished)
        self.current_worker.start()

    def run_format(self):
        """Lance le formatage Ruff."""
        files = self.get_selected_files()
        if not files:
            self.log_message("[!] Aucun fichier a formater")
            return

        reply = QMessageBox.question(
            self,
            "Confirmation",
            f"Formater {len(files)} fichier(s) ?\n\nCette action modifiera directement les fichiers.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply != QMessageBox.Yes:
            return

        self.show_progress(True)
        self.log_message(f"Demarrage du formatage sur {len(files)} fichier(s)...")

        self.current_worker = RuffWorker(files, "format")
        self.current_worker.progress.connect(self.log_message)
        self.current_worker.file_progress.connect(self.update_progress)
        self.current_worker.finished.connect(self.on_format_finished)
        self.current_worker.start()

    def show_progress(self, show):
        """Affiche ou cache les elements de progression."""
        self.progress_bar.setVisible(show)
        self.progress_label.setVisible(show)
        self.cancel_btn.setVisible(show)

        self.check_btn.setEnabled(not show)
        self.check_fix_btn.setEnabled(not show)
        self.format_btn.setEnabled(not show)
        self.add_files_btn.setEnabled(not show)
        self.add_folder_btn.setEnabled(not show)

        if show:
            self.progress_bar.setValue(0)

    def update_progress(self, current, total):
        """Met a jour la barre de progression."""
        if total > 0:
            progress = int((current / total) * 100)
            self.progress_bar.setValue(progress)
            self.progress_label.setText(f"{current}/{total} fichiers traites")

    def cancel_operation(self):
        """Annule l'operation en cours."""
        if self.current_worker and self.current_worker.isRunning():
            self.current_worker.terminate()
            self.log_message("[!] Operation annulee")
            self.show_progress(False)

    def on_check_finished(self, results):
        """Traite les resultats de l'analyse SANS fix."""
        self.show_progress(False)

        self.last_analysis_data = {
            "timestamp": datetime.now().isoformat(),
            "total_issues": results["total_issues"],
            "files_analyzed": len(results["files"]),
            "results": results,
        }

        self.log_message(f"\n{'=' * 50}")
        self.log_message(f"ANALYSE TERMINEE (Diagnostic)")
        self.log_message(f"Fichiers analyses: {len(results['files'])}")
        self.log_message(f"Problemes trouves: {results['total_issues']}")

        if results["total_issues"] > 0:
            self.log_message(
                f"[TIP] Utilisez 'Analyser et Fix' pour corriger automatiquement"
            )

        self.stats_label.setText(
            f"Statistiques: {len(results['files'])} fichiers, "
            f"{results['total_issues']} probleme(s)"
        )

        if results["total_issues"] > 0:
            self.ai_plan_ready.emit(self.last_analysis_data)
            self.log_message("[DATA] Donnees pretes pour generation du plan IA")

    def on_check_fix_finished(self, results):
        """NOUVEAU: Traite les resultats de l'analyse AVEC fix."""
        self.show_progress(False)

        self.last_analysis_data = {
            "timestamp": datetime.now().isoformat(),
            "total_issues": results["total_issues"],
            "fixed_issues": results.get("fixed_issues", 0),
            "files_analyzed": len(results["files"]),
            "results": results,
        }

        self.log_message(f"\n{'=' * 50}")
        self.log_message(f"ANALYSE ET CORRECTION TERMINEE")
        self.log_message(f"Fichiers traites: {len(results['files'])}")
        self.log_message(f"Problemes restants: {results['total_issues']}")

        # Compter les fichiers corriges
        fixed_files = sum(1 for f in results["files"] if f.get("fixed"))
        if fixed_files > 0:
            self.log_message(f"[OK] {fixed_files} fichier(s) corrige(s) avec succes")

        self.stats_label.setText(
            f"Statistiques: {len(results['files'])} fichiers traites, "
            f"{fixed_files} corrige(s), "
            f"{results['total_issues']} probleme(s) restant(s)"
        )

        if results["total_issues"] > 0:
            self.log_message(
                "[INFO] Certains problemes ne peuvent pas etre corriges automatiquement"
            )

    def on_format_finished(self, results):
        """Traite les resultats du formatage."""
        self.show_progress(False)

        success = sum(1 for r in results["files"] if r.get("formatted", False))
        failed = len(results["files"]) - success

        self.log_message(f"\n{'=' * 50}")
        self.log_message(f"FORMATAGE TERMINE")
        self.log_message(f"[OK] {success} fichier(s) formate(s) avec succes")
        if failed > 0:
            self.log_message(f"[X] {failed} fichier(s) ont echoue")

        self.stats_label.setText(f"Statistiques: {success} succes, {failed} echec(s)")

    def export_results(self):
        """Exporte les resultats de l'analyse."""
        if not self.last_analysis_data:
            self.log_message("[!] Aucun resultat a exporter")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_file = f"ruff_export_{timestamp}.json"

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Exporter les resultats", export_file, "JSON Files (*.json)"
        )

        if not file_path:
            return

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(self.last_analysis_data, f, indent=2)

            self.log_message(f"[OK] Resultats exportes: {file_path}")
        except Exception as e:
            self.log_message(f"[X] Erreur lors de l'export: {str(e)}")

    def log_message(self, message):
        """Affiche un message dans la zone de sortie."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.output_text.append(f"[{timestamp}] {message}")
        scrollbar = self.output_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
