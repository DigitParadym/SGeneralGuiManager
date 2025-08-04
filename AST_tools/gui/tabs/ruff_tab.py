from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTextEdit,
    QFileDialog,
    QCheckBox,
    QLabel,
    QProgressBar,
    QGroupBox,
)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QIcon, QFont
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))
from core.ruff_integration.ruff_worker import RuffWorker


class RuffIntegrationTab(QWidget):
    """Onglet d'integration Ruff avec bouton de reinitialisation"""

    ai_plan_ready = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_worker = None
        self.target_path = ""
        self.init_ui()

    def init_ui(self):
        """Initialise l'interface utilisateur"""
        layout = QVBoxLayout()

        # Section de selection de fichiers
        file_group = QGroupBox("Selection des Fichiers")
        file_layout = QVBoxLayout()

        path_layout = QHBoxLayout()
        self.path_label = QLabel("Aucun dossier selectionne")
        self.path_label.setStyleSheet("""
            QLabel {
                padding: 8px;
                border: 2px dashed #cccccc;
                border-radius: 4px;
                background-color: #f9f9f9;
                color: #666666;
            }
        """)

        self.select_folder_btn = QPushButton("Selectionner un Dossier")
        self.select_files_btn = QPushButton("Selectionner des Fichiers")

        # Styling des boutons de selection
        button_style = """
            QPushButton {
                padding: 8px 16px;
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: #f0f0f0;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
        """
        self.select_folder_btn.setStyleSheet(button_style)
        self.select_files_btn.setStyleSheet(button_style)

        self.select_folder_btn.clicked.connect(self.select_folder)
        self.select_files_btn.clicked.connect(self.select_files)

        path_layout.addWidget(self.path_label)
        path_layout.addWidget(self.select_folder_btn)
        path_layout.addWidget(self.select_files_btn)

        file_layout.addLayout(path_layout)
        file_group.setLayout(file_layout)

        # Section d'options
        options_group = QGroupBox("Options")
        options_layout = QVBoxLayout()

        self.fix_checkbox = QCheckBox("Appliquer les corrections automatiques (--fix)")
        self.fix_checkbox.setStyleSheet("""
            QCheckBox {
                font-weight: bold;
                padding: 4px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
        """)
        options_layout.addWidget(self.fix_checkbox)

        options_group.setLayout(options_layout)

        # Section des boutons d'action avec reinitialisation
        actions_group = QGroupBox("Actions")
        actions_layout = QHBoxLayout()

        # Premiere ligne de boutons
        main_actions_layout = QHBoxLayout()

        self.analyze_btn = QPushButton("Analyser le Code")
        self.format_btn = QPushButton("Formater le Code")
        self.ai_analyze_btn = QPushButton("Analyser pour IA")

        # Styling des boutons d'action principaux
        action_button_style = """
            QPushButton {
                padding: 10px 20px;
                border: 2px solid #4CAF50;
                border-radius: 6px;
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                border-color: #cccccc;
                color: #666666;
            }
        """

        self.analyze_btn.setStyleSheet(action_button_style)
        self.format_btn.setStyleSheet(
            action_button_style.replace("#4CAF50", "#2196F3")
            .replace("#45a049", "#1976D2")
            .replace("#3d8b40", "#1565C0")
        )
        self.ai_analyze_btn.setStyleSheet(
            action_button_style.replace("#4CAF50", "#FF9800")
            .replace("#45a049", "#F57C00")
            .replace("#3d8b40", "#E65100")
        )

        self.analyze_btn.clicked.connect(self.analyze_code)
        self.format_btn.clicked.connect(self.format_code)
        self.ai_analyze_btn.clicked.connect(self.analyze_for_ai)

        main_actions_layout.addWidget(self.analyze_btn)
        main_actions_layout.addWidget(self.format_btn)
        main_actions_layout.addWidget(self.ai_analyze_btn)

        # Bouton de reinitialisation (separe visuellement)
        reset_layout = QHBoxLayout()
        self.reset_btn = QPushButton("Reinitialiser")
        self.reset_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 16px;
                border: 2px solid #f44336;
                border-radius: 6px;
                background-color: #f44336;
                color: white;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
            QPushButton:pressed {
                background-color: #b71c1c;
            }
        """)
        self.reset_btn.clicked.connect(self.reset_state)

        reset_layout.addStretch()  # Pousser le bouton vers la droite
        reset_layout.addWidget(self.reset_btn)

        # Assembler les actions
        actions_main_layout = QVBoxLayout()
        actions_main_layout.addLayout(main_actions_layout)
        actions_main_layout.addLayout(reset_layout)

        actions_group.setLayout(actions_main_layout)

        # Barre de progression
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #cccccc;
                border-radius: 5px;
                text-align: center;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 3px;
            }
        """)

        # Zone d'affichage des resultats
        results_group = QGroupBox("Rapport Ruff")
        results_layout = QVBoxLayout()

        # Header du rapport avec info
        report_header = QHBoxLayout()
        self.report_info_label = QLabel("Pret pour l'analyse")
        self.report_info_label.setStyleSheet("""
            QLabel {
                color: #666666;
                font-style: italic;
                padding: 4px;
            }
        """)

        self.clear_report_btn = QPushButton("Vider")
        self.clear_report_btn.setStyleSheet("""
            QPushButton {
                padding: 4px 8px;
                border: 1px solid #ccc;
                border-radius: 3px;
                background-color: #f5f5f5;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #e5e5e5;
            }
        """)
        self.clear_report_btn.clicked.connect(self.clear_report)

        report_header.addWidget(self.report_info_label)
        report_header.addStretch()
        report_header.addWidget(self.clear_report_btn)

        # Zone de texte pour les resultats
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setMinimumHeight(300)
        self.results_text.setStyleSheet("""
            QTextEdit {
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 11px;
                background-color: #f8f8f8;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
            }
        """)

        # Placeholder text
        self.results_text.setPlaceholderText(
            "Les resultats de l'analyse Ruff apparaitront ici...\n\n"
            "- Selectionnez un dossier ou des fichiers\n"
            "- Choisissez vos options\n"
            "- Cliquez sur 'Analyser le Code' pour commencer"
        )

        results_layout.addLayout(report_header)
        results_layout.addWidget(self.results_text)
        results_group.setLayout(results_layout)

        # Assemblage final
        layout.addWidget(file_group)
        layout.addWidget(options_group)
        layout.addWidget(actions_group)
        layout.addWidget(self.progress_bar)
        layout.addWidget(results_group)

        self.setLayout(layout)

        # Etat initial des boutons
        self._update_buttons_state()

    def select_folder(self):
        """Selectionne un dossier cible"""
        folder = QFileDialog.getExistingDirectory(self, "Selectionner un dossier")
        if folder:
            self.target_path = folder
            self.path_label.setText(f"Dossier: {folder}")
            self.path_label.setStyleSheet("""
                QLabel {
                    padding: 8px;
                    border: 2px solid #4CAF50;
                    border-radius: 4px;
                    background-color: #e8f5e8;
                    color: #2e7d32;
                    font-weight: bold;
                }
            """)
            self._update_buttons_state()
            self._update_report_info(f"Dossier selectionne: {Path(folder).name}")

    def select_files(self):
        """Selectionne des fichiers Python specifiques"""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Selectionner des fichiers Python",
            "",
            "Python Files (*.py);;All Files (*)",
        )
        if files:
            self.target_path = " ".join(files)
            file_count = len(files)
            self.path_label.setText(f"Fichiers: {file_count} fichier(s) selectionne(s)")
            self.path_label.setStyleSheet("""
                QLabel {
                    padding: 8px;
                    border: 2px solid #2196F3;
                    border-radius: 4px;
                    background-color: #e3f2fd;
                    color: #1565c0;
                    font-weight: bold;
                }
            """)
            self._update_buttons_state()
            self._update_report_info(f"{file_count} fichier(s) selectionne(s)")

    def reset_state(self):
        """Reinitialise l'etat de l'interface"""
        # Effacer le chemin
        self.target_path = ""

        # Remettre le label par defaut
        self.path_label.setText("Aucun dossier selectionne")
        self.path_label.setStyleSheet("""
            QLabel {
                padding: 8px;
                border: 2px dashed #cccccc;
                border-radius: 4px;
                background-color: #f9f9f9;
                color: #666666;
            }
        """)

        # Decocher les options
        self.fix_checkbox.setChecked(False)

        # Vider le rapport
        self.results_text.clear()

        # Cacher la barre de progression si visible
        if self.progress_bar.isVisible():
            self.progress_bar.setVisible(False)

        # Arreter tout worker en cours
        if self.current_worker and self.current_worker.isRunning():
            self.current_worker.terminate()
            self.current_worker.wait()

        # Mettre a jour les boutons
        self._update_buttons_state()

        # Mettre a jour l'info du rapport
        self._update_report_info(
            "Interface reinitalisee - Pret pour une nouvelle analyse"
        )

        # Message de confirmation dans le rapport
        self.results_text.append("Interface reinitalisee avec succes!")
        self.results_text.append(
            "Vous pouvez maintenant selectionner de nouveaux fichiers."
        )

    def clear_report(self):
        """Vide uniquement la zone de rapport"""
        self.results_text.clear()
        self._update_report_info("Rapport vide - Pret pour l'analyse")

    def _update_report_info(self, message):
        """Met a jour le message d'info du rapport"""
        self.report_info_label.setText(message)

    def _update_buttons_state(self):
        """Met a jour l'etat des boutons selon la selection"""
        has_target = bool(self.target_path)

        self.analyze_btn.setEnabled(has_target)
        self.format_btn.setEnabled(has_target)
        self.ai_analyze_btn.setEnabled(has_target)

        # Le bouton de reinitialisation est toujours actif
        self.reset_btn.setEnabled(True)

    def analyze_code(self):
        """Lance l'analyse Ruff"""
        options = {"fix": self.fix_checkbox.isChecked()}
        self._start_worker("check", options)

    def format_code(self):
        """Lance le formatage Ruff"""
        self._start_worker("format", {})

    def analyze_for_ai(self):
        """Lance l'analyse pour l'IA"""
        self._start_worker("analyze_for_ai", {})

    def _start_worker(self, command_type, options):
        """Demarre un worker Ruff"""
        if self.current_worker and self.current_worker.isRunning():
            self.results_text.append("Une operation est deja en cours...")
            return

        self.current_worker = RuffWorker(command_type, self.target_path, options)

        # Connexion des signaux
        self.current_worker.output_received.connect(self._on_output_received)
        self.current_worker.error_occurred.connect(self._on_error_occurred)
        self.current_worker.progress_updated.connect(self._on_progress_updated)
        self.current_worker.finished_successfully.connect(self._on_ai_analysis_finished)

        # Interface de progression
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self._disable_buttons()

        # Message de demarrage
        operation_names = {
            "check": "Analyse du code",
            "format": "Formatage du code",
            "analyze_for_ai": "Analyse pour IA",
        }
        operation_name = operation_names.get(command_type, command_type)

        self.results_text.append(f"\n--- Demarrage: {operation_name} ---")
        self._update_report_info(f"En cours: {operation_name}...")

        self.current_worker.start()

    def _on_output_received(self, output):
        """Affiche la sortie standard"""
        self.results_text.append(output)
        self._operation_finished()

    def _on_error_occurred(self, error):
        """Affiche les erreurs"""
        self.results_text.append(f"ERREUR: {error}")
        self._operation_finished()

    def _on_progress_updated(self, value):
        """Met a jour la barre de progression"""
        self.progress_bar.setValue(value)

    def _on_ai_analysis_finished(self, analysis_data):
        """Traite les resultats de l'analyse pour l'IA"""
        self.results_text.append(f"\n--- Analyse terminee ---")
        self.results_text.append(
            f"Total des problemes: {analysis_data['total_issues']}"
        )

        if analysis_data["total_issues"] > 0:
            self.results_text.append("\nDonnees pretes pour generation du plan IA!")
            # Emettre le signal pour l'onglet transformations
            self.ai_plan_ready.emit(analysis_data)
        else:
            self.results_text.append("\nAucun probleme detecte!")

        self._operation_finished()

    def _disable_buttons(self):
        """Desactive les boutons pendant l'operation"""
        self.analyze_btn.setEnabled(False)
        self.format_btn.setEnabled(False)
        self.ai_analyze_btn.setEnabled(False)
        # Le bouton reset reste actif pour permettre l'annulation

    def _operation_finished(self):
        """Reactive l'interface apres l'operation"""
        self.progress_bar.setVisible(False)
        self._update_buttons_state()
        self._update_report_info("Operation terminee")
