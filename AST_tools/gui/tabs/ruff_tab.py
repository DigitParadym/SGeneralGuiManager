#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module Ruff Tab - Version Minimale Fonctionnelle
"""

from datetime import datetime
import json
from pathlib import Path
import subprocess

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QLabel,
    QFileDialog, QGroupBox, QListWidget,
    QSplitter, QComboBox, QProgressBar
)
from PySide6.QtCore import Qt, Signal, QThread


class RuffWorker(QThread):
    """Worker pour exécuter Ruff en arrière-plan."""
    progress = Signal(str)
    finished = Signal(dict)
    
    def __init__(self, files, command="check"):
        super().__init__()
        self.files = files
        self.command = command
    
    def run(self):
        """Exécute Ruff sur les fichiers."""
        results = {"files": [], "total_issues": 0}
        
        for file in self.files:
            self.progress.emit(f"Analyse de {file}...")
            try:
                if self.command == "check":
                    result = subprocess.run(
                        ["ruff", "check", file, "--format", "json"],
                        capture_output=True, text=True
                    )
                    results["files"].append({
                        "file": file,
                        "output": result.stdout,
                        "errors": result.stderr
                    })
                    # Compter les issues (approximatif)
                    if "[" in result.stdout:
                        results["total_issues"] += result.stdout.count('"')//10
                        
                elif self.command == "format":
                    result = subprocess.run(
                        ["ruff", "format", file],
                        capture_output=True, text=True
                    )
                    results["files"].append({
                        "file": file,
                        "formatted": result.returncode == 0
                    })
                    
            except Exception as e:
                results["files"].append({
                    "file": file,
                    "error": str(e)
                })
        
        self.finished.emit(results)


class RuffIntegrationTab(QWidget):
    """Onglet d'intégration Ruff minimaliste mais fonctionnel."""
    
    ai_plan_ready = Signal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.last_analysis_data = {}
        self.setup_ui()
        self.check_ruff_availability()
    
    def setup_ui(self):
        """Crée l'interface utilisateur."""
        layout = QVBoxLayout(self)
        
        # En-tête
        header = QLabel("🔧 Analyse et Formatage avec Ruff")
        header.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        layout.addWidget(header)
        
        # Splitter principal
        splitter = QSplitter(Qt.Horizontal)
        
        # Panneau gauche - Contrôles
        left_panel = QGroupBox("Contrôles")
        left_layout = QVBoxLayout(left_panel)
        
        # Sélection de fichiers
        self.files_list = QListWidget()
        left_layout.addWidget(QLabel("Fichiers à analyser:"))
        left_layout.addWidget(self.files_list)
        
        # Boutons
        btn_layout = QHBoxLayout()
        self.add_files_btn = QPushButton("+ Fichiers")
        self.clear_btn = QPushButton("Vider")
        btn_layout.addWidget(self.add_files_btn)
        btn_layout.addWidget(self.clear_btn)
        left_layout.addLayout(btn_layout)
        
        # Actions
        self.check_btn = QPushButton("🔍 Analyser (ruff check)")
        self.format_btn = QPushButton("✨ Formater (ruff format)")
        self.export_btn = QPushButton("💾 Exporter")
        
        left_layout.addWidget(self.check_btn)
        left_layout.addWidget(self.format_btn)
        left_layout.addWidget(self.export_btn)
        
        # Progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        left_layout.addWidget(self.progress_bar)
        
        left_layout.addStretch()
        
        # Panneau droit - Résultats
        right_panel = QGroupBox("Résultats")
        right_layout = QVBoxLayout(right_panel)
        
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        right_layout.addWidget(self.output_text)
        
        # Ajouter les panneaux au splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([300, 500])
        
        layout.addWidget(splitter)
        
        # Connexions
        self.add_files_btn.clicked.connect(self.add_files)
        self.clear_btn.clicked.connect(self.clear_files)
        self.check_btn.clicked.connect(self.run_check)
        self.format_btn.clicked.connect(self.run_format)
        self.export_btn.clicked.connect(self.export_results)
    
    def check_ruff_availability(self):
        """Vérifie si Ruff est installé."""
        try:
            result = subprocess.run(["ruff", "--version"], capture_output=True, text=True)
            self.log_message(f"✓ Ruff disponible: {result.stdout.strip()}")
        except:
            self.log_message("✗ Ruff non installé. Installez avec: pip install ruff")
            self.check_btn.setEnabled(False)
            self.format_btn.setEnabled(False)
    
    def add_files(self):
        """Ajoute des fichiers à analyser."""
        files, _ = QFileDialog.getOpenFileNames(
            self, "Sélectionner des fichiers Python", "", "Python (*.py)"
        )
        for file in files:
            self.files_list.addItem(file)
        self.log_message(f"{len(files)} fichier(s) ajouté(s)")
    
    def clear_files(self):
        """Vide la liste des fichiers."""
        self.files_list.clear()
        self.log_message("Liste vidée")
    
    def run_check(self):
        """Lance l'analyse Ruff."""
        files = [self.files_list.item(i).text() for i in range(self.files_list.count())]
        if not files:
            self.log_message("Aucun fichier à analyser")
            return
        
        self.progress_bar.setVisible(True)
        self.worker = RuffWorker(files, "check")
        self.worker.progress.connect(self.log_message)
        self.worker.finished.connect(self.on_check_finished)
        self.worker.start()
    
    def run_format(self):
        """Lance le formatage Ruff."""
        files = [self.files_list.item(i).text() for i in range(self.files_list.count())]
        if not files:
            self.log_message("Aucun fichier à formater")
            return
        
        self.progress_bar.setVisible(True)
        self.worker = RuffWorker(files, "format")
        self.worker.progress.connect(self.log_message)
        self.worker.finished.connect(self.on_format_finished)
        self.worker.start()
    
    def on_check_finished(self, results):
        """Traite les résultats de l'analyse."""
        self.progress_bar.setVisible(False)
        
        self.last_analysis_data = {
            "timestamp": datetime.now().isoformat(),
            "total_issues": results["total_issues"],
            "files_analyzed": len(results["files"]),
            "results": results
        }
        
        self.log_message(f"\nAnalyse terminée: {results['total_issues']} problème(s) trouvé(s)")
        
        # Émettre le signal pour l'IA si nécessaire
        if results["total_issues"] > 0:
            self.ai_plan_ready.emit(self.last_analysis_data)
    
    def on_format_finished(self, results):
        """Traite les résultats du formatage."""
        self.progress_bar.setVisible(False)
        
        success = sum(1 for r in results["files"] if r.get("formatted", False))
        self.log_message(f"\nFormatage terminé: {success}/{len(results['files'])} fichier(s) formaté(s)")
    
    def export_results(self):
        """Exporte les résultats de l'analyse."""
        if not self.last_analysis_data:
            self.log_message("Aucun résultat à exporter")
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_file = f"ruff_export_{timestamp}.json"
        
        # Créer le dossier si nécessaire
        export_dir = Path("data/ruff_reports")
        export_dir.mkdir(parents=True, exist_ok=True)
        export_path = export_dir / export_file
        
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(self.last_analysis_data, f, indent=2)
        
        self.log_message(f"Résultats exportés: {export_path}")
        return str(export_path)
    
    def log_message(self, message):
        """Affiche un message dans la zone de sortie."""
        self.output_text.append(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
