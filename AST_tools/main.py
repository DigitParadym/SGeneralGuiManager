#!/usr/bin/env python3
"""
AST Tools - Interface PySide6 Complete
Interface moderne pour la plateforme de refactorisation dirgee par IA
"""

# Import du logger global pour la derniere execution
from core.global_logger import log_end, log_start

# Demarrage du log de l'execution
log_start("AST_tools - Nouvelle execution")

# Import du logger global pour la derniere execution
from core.global_logger import log_start

# Demarrage du log de l'execution
log_start("AST_tools - Nouvelle execution")

import json
import os
import sys
import traceback
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSplitter,
    QStatusBar,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


# --- Worker pour l'execution en arriere-plan ---
class TransformationWorker(QThread):
    progress_update = Signal(int, str)  # Pourcentage, nom du fichier
    log_message = Signal(str)
    transformation_complete = Signal(bool, str, dict)

    def __init__(self, orchestrateur, plan_path, target_files, parent=None):
        super().__init__(parent)
        self.orchestrateur = orchestrateur
        self.plan_path = plan_path
        self.target_files = target_files
        self.is_cancelled = False
        self.stats = {"files_processed": 0, "files_successful": 0, "files_failed": 0}

    def run(self):
        try:
            total_files = len(self.target_files)
            if total_files == 0:
                self.transformation_complete.emit(
                    False, "Aucun fichier a traiter", self.stats
                )
                return

            self.log_message.emit(
                f"Debut des transformations sur {total_files} fichier(s)"
            )

            for i, file_path in enumerate(self.target_files):
                if self.is_cancelled:
                    self.log_message.emit("Transformations annulees par l'utilisateur")
                    break

                filename = os.path.basename(file_path)
                progress = int(((i + 1) / total_files) * 100)
                self.progress_update.emit(progress, filename)

                # Note: La methode executer_plan de l'orchestrateur devrait etre adaptee
                # pour retourner un boolean de succes et des logs detailles.
                # Pour l'instant, on suppose qu'elle modifie le fichier sur place.
                success = self.orchestrateur.executer_plan(self.plan_path, [file_path])

                self.stats["files_processed"] += 1
                if success:
                    self.stats["files_successful"] += 1
                    self.log_message.emit(f"  [SUCCES] {filename}")
                else:
                    self.stats["files_failed"] += 1
                    self.log_message.emit(f"  [ECHEC] {filename}")

                self.msleep(50)  # Petite pause pour la reactivite de l'UI

            if self.is_cancelled:
                self.transformation_complete.emit(
                    False, "Transformations annulees", self.stats
                )
            else:
                self.transformation_complete.emit(
                    True, "Transformations terminees", self.stats
                )

        except Exception as e:
            self.log_message.emit(f"ERREUR CRITIQUE dans le worker: {e}")
            self.transformation_complete.emit(
                False, f"Erreur critique: {e}", self.stats
            )

    def cancel(self):
        self.is_cancelled = True


# --- Fenetre Principale ---
class ASTMainWindow(QMainWindow):
    """Fenetre principale AST Tools en PySide6."""

    def __init__(self):
        super().__init__()
        self.orchestrateur = None
        self.target_files = []
        self.current_plan = None
        self.current_preview_file = None
        self.transformation_worker = None

        self.setup_window()
        self.create_interface()
        self.connect_signals()
        self.init_ast_engine()

    def setup_window(self):
        self.setWindowTitle("AST Tools - Plateforme de Refactorisation IA")
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(900, 600)
        # Le style irait ici

    def create_interface(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        self.create_title_section(main_layout)
        self.create_tab_interface(main_layout)
        self.create_progress_section(main_layout)
        self.create_status_bar()

    def create_title_section(self, layout):
        title_label = QLabel("AST Tools - Plateforme de Refactorisation IA")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

    def create_tab_interface(self, layout):
        self.tab_widget = QTabWidget()
        main_tab = self.create_main_tab()
        self.tab_widget.addTab(main_tab, "Transformations")
        plugins_tab = self.create_plugins_tab()
        self.tab_widget.addTab(plugins_tab, "Plugins")
        logs_tab = self.create_logs_tab()
        self.tab_widget.addTab(logs_tab, "Logs")
        layout.addWidget(self.tab_widget)

    def create_main_tab(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        splitter = QSplitter(Qt.Horizontal)

        left_panel = self.create_left_panel()
        right_panel = self.create_right_panel()

        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([500, 700])
        main_layout.addWidget(splitter)

        action_layout = QHBoxLayout()
        self.validate_btn = QPushButton("Valider Plan")
        self.execute_btn = QPushButton("EXECUTER TRANSFORMATIONS")
        self.execute_btn.setEnabled(False)
        action_layout.addWidget(self.validate_btn)
        action_layout.addStretch()
        action_layout.addWidget(self.execute_btn)
        main_layout.addLayout(action_layout)

        return main_widget

    def create_left_panel(self):
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        plan_group = QGroupBox("1. Plan de Transformation JSON")
        plan_layout = QVBoxLayout(plan_group)
        file_layout = QHBoxLayout()
        self.plan_line_edit = QLineEdit()
        self.plan_line_edit.setPlaceholderText("Selectionnez un plan JSON...")
        self.browse_plan_btn = QPushButton("Parcourir")
        file_layout.addWidget(self.plan_line_edit)
        file_layout.addWidget(self.browse_plan_btn)
        plan_layout.addLayout(file_layout)
        self.plan_info = QTextEdit()
        self.plan_info.setReadOnly(True)
        self.plan_info.setMaximumHeight(100)
        plan_layout.addWidget(self.plan_info)
        left_layout.addWidget(plan_group)

        files_group = QGroupBox("2. Fichiers Cibles")
        files_layout = QVBoxLayout(files_group)
        files_buttons = QHBoxLayout()
        self.add_files_btn = QPushButton("+ Fichiers")
        self.add_folder_btn = QPushButton("+ Dossier")
        self.clear_files_btn = QPushButton("Vider")
        files_buttons.addWidget(self.add_files_btn)
        files_buttons.addWidget(self.add_folder_btn)
        files_buttons.addWidget(self.clear_files_btn)
        files_buttons.addStretch()
        files_layout.addLayout(files_buttons)

        self.files_list = QListWidget()
        files_layout.addWidget(self.files_list)
        left_layout.addWidget(files_group)

        return left_widget

    def create_right_panel(self):
        right_splitter = QSplitter(Qt.Vertical)

        preview_panel = QGroupBox("Apercu des Transformations")
        preview_layout = QVBoxLayout(preview_panel)
        self.preview_text = QTextEdit()
        self.preview_text.setPlaceholderText("L'apercu apparaitra ici...")
        preview_layout.addWidget(self.preview_text)

        content_panel = QGroupBox("Contenu du Fichier Selectionne")
        content_layout = QVBoxLayout(content_panel)
        content_header = QHBoxLayout()
        self.current_file_label = QLabel("Aucun fichier selectionne")
        self.refresh_content_btn = QPushButton("Actualiser")
        content_header.addWidget(self.current_file_label)
        content_header.addStretch()
        content_header.addWidget(self.refresh_content_btn)
        self.file_content_text = QTextEdit()
        self.file_content_text.setReadOnly(True)
        content_layout.addLayout(content_header)
        content_layout.addWidget(self.file_content_text)

        right_splitter.addWidget(preview_panel)
        right_splitter.addWidget(content_panel)
        right_splitter.setSizes([200, 300])

        return right_splitter

    def create_plugins_tab(self):
        # ... (Logique de l'onglet Plugins)
        return QWidget()

    def create_logs_tab(self):
        # ... (Logique de l'onglet Logs)
        logs_widget = QWidget()
        logs_layout = QVBoxLayout(logs_widget)
        self.logs_text = QTextEdit()
        self.logs_text.setReadOnly(True)
        logs_layout.addWidget(self.logs_text)
        return logs_widget

    def create_progress_section(self, layout):
        self.progress_frame = QFrame()
        progress_layout = QHBoxLayout(self.progress_frame)
        self.progress_label = QLabel("Pret")
        self.progress_bar = QProgressBar()
        self.cancel_btn = QPushButton("Annuler")
        progress_layout.addWidget(self.progress_label)
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.cancel_btn)
        self.progress_bar.setVisible(False)
        self.cancel_btn.setVisible(False)
        layout.addWidget(self.progress_frame)

    def create_status_bar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.engine_status = QLabel("Moteur: Non connecte")
        self.status_bar.addPermanentWidget(self.engine_status)

    def connect_signals(self):
        self.browse_plan_btn.clicked.connect(self.browse_plan_file)
        self.add_files_btn.clicked.connect(self.add_target_files)
        self.add_folder_btn.clicked.connect(self.add_target_folder)
        self.clear_files_btn.clicked.connect(self.clear_target_files)
        self.validate_btn.clicked.connect(self.validate_plan)
        self.execute_btn.clicked.connect(self.execute_transformations)
        self.files_list.currentItemChanged.connect(self.on_file_selection_changed)
        self.refresh_content_btn.clicked.connect(self.refresh_current_file_content)

    def init_ast_engine(self):
        try:
            # S'assure que le repertoire parent est dans le path
            parent_dir = Path(__file__).parent.parent
            if str(parent_dir) not in sys.path:
                sys.path.insert(0, str(parent_dir))

            from modificateur_interactif import OrchestrateurAST

            self.orchestrateur = OrchestrateurAST()
            self.engine_status.setText("Moteur: Connecte")
            self.log_message("Moteur AST initialise")
        except Exception as e:
            self.engine_status.setText("Moteur: ERREUR")
            self.log_message(f"Erreur initialisation: {e}\n{traceback.format_exc()}")

    def log_message(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.logs_text.append(log_entry)

    def browse_plan_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Selectionner un plan JSON", "", "Fichiers JSON (*.json)"
        )
        if file_path:
            self.plan_line_edit.setText(file_path)
            self.load_plan_info(file_path)

    def load_plan_info(self, plan_path):
        try:
            with open(plan_path, encoding="utf-8") as f:
                plan_data = json.load(f)
            self.current_plan = plan_data
            info_text = f"Nom: {plan_data.get('name', 'N/A')}\n"
            info_text += f"Description: {plan_data.get('description', 'N/A')}\n"
            info_text += f"Transformations: {len(plan_data.get('transformations', []))}"
            self.plan_info.setText(info_text)
            self.update_execute_button()
            self.log_message(f"Plan charge: {os.path.basename(plan_path)}")
        except Exception as e:
            self.current_plan = None
            self.plan_info.setText(f"ERREUR: {e}")
            self.log_message(f"Erreur chargement plan: {e}")

    def add_target_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Selectionner fichiers Python", "", "Fichiers Python (*.py)"
        )
        if files:
            for file_path in files:
                if file_path not in self.target_files:
                    self.target_files.append(file_path)
                    self.files_list.addItem(
                        QListWidgetItem(os.path.basename(file_path))
                    )
            self.update_execute_button()
            self.log_message(f"{len(files)} fichier(s) ajoute(s)")

    def add_target_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Selectionner dossier")
        if folder_path:
            py_files = [str(p) for p in Path(folder_path).rglob("*.py")]
            added = 0
            for file_path in py_files:
                if file_path not in self.target_files:
                    self.target_files.append(file_path)
                    self.files_list.addItem(
                        QListWidgetItem(os.path.basename(file_path))
                    )
                    added += 1
            self.update_execute_button()
            self.log_message(f"{added} fichier(s) ajoute(s) du dossier.")

    def clear_target_files(self):
        self.target_files.clear()
        self.files_list.clear()
        self.update_execute_button()
        self.log_message("Liste des fichiers videe")

    def update_execute_button(self):
        can_execute = bool(self.target_files and self.current_plan)
        self.execute_btn.setEnabled(can_execute)

    def validate_plan(self):
        # ... Logique de validation
        QMessageBox.information(self, "Validation", "Plan valide!")

    def execute_transformations(self):
        if not all([self.orchestrateur, self.current_plan, self.target_files]):
            QMessageBox.warning(self, "Avertissement", "Plan ou fichiers manquants")
            return

        reply = QMessageBox.question(
            self,
            "Confirmation",
            f"Executer le plan sur {len(self.target_files)} fichier(s)?",
        )
        if reply == QMessageBox.Yes:
            self.start_transformations()

    def start_transformations(self):
        self.worker = TransformationWorker(
            self.orchestrateur, self.plan_line_edit.text(), self.target_files
        )
        self.worker.progress_update.connect(self.on_progress_update)
        self.worker.log_message.connect(self.log_message)
        self.worker.transformation_complete.connect(self.on_transformations_complete)
        self.cancel_btn.clicked.connect(self.worker.cancel)
        self.show_progress_interface(True)
        self.worker.start()

    def show_progress_interface(self, show):
        self.progress_bar.setVisible(show)
        self.cancel_btn.setVisible(show)
        self.execute_btn.setEnabled(not show)
        self.progress_label.setText("Transformation en cours..." if show else "Pret")

    def on_progress_update(self, value, filename):
        self.progress_bar.setValue(value)
        self.progress_label.setText(f"Traitement: {filename} ({value}%)")

    def on_transformations_complete(self, success, message, stats):
        self.show_progress_interface(False)
        report = f"{message}\n\nSucces: {stats['files_successful']}, Echecs: {stats['files_failed']}"
        QMessageBox.information(self, "Termine", report)
        self.log_message("=== RAPPORT FINAL ===")
        self.log_message(report)

    def on_file_selection_changed(self, current_item, previous_item):
        if current_item:
            # Trouver le chemin complet a partir du nom de base
            filename = current_item.text()
            full_path = next(
                (
                    path
                    for path in self.target_files
                    if os.path.basename(path) == filename
                ),
                None,
            )
            if full_path:
                self.load_file_content(full_path)

    def load_file_content(self, file_path):
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read(10000)  # Limite a 10000 caracteres
            self.file_content_text.setPlainText(content)
            self.current_file_label.setText(f"Fichier: {os.path.basename(file_path)}")
            self.current_preview_file = file_path
        except Exception as e:
            self.file_content_text.setPlainText(f"Erreur lecture: {e}")

    def refresh_current_file_content(self):
        if self.current_preview_file:
            self.load_file_content(self.current_preview_file)
            self.log_message("Contenu du fichier rafraichi.")

    # ... (autres methodes comme refresh_plugins, etc.)


def main():
    """Point d'entree principal."""
    app = QApplication(sys.argv)
    window = ASTMainWindow()
    window.show()
    result = app.exec()
    log_end("AST_tools - Fin execution")
    sys.exit(result)


if __name__ == "__main__":
    main()
