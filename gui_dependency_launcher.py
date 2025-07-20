import sys
import subprocess
import json
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout,
    QFileDialog, QMessageBox
)

class DependencyAnalyzer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dependency Analyzer")
        self.setGeometry(200, 200, 400, 150)
        layout = QVBoxLayout()

        btn = QPushButton("Run Dependency Analysis")
        btn.clicked.connect(self.run_analysis)

        layout.addWidget(btn)
        self.setLayout(layout)

    def run_analysis(self):
        folder = QFileDialog.getExistingDirectory(self, "Select folder")
        if not folder:
            return
        try:
            subprocess.run(["python", "import_mapper/import_mapper.py", folder], check=True)
            report = Path(folder) / "dependency_map.json"
            if report.exists():
                with open(report, encoding="utf-8") as f:
                    data = json.load(f)
                files = data["metadata"].get("files_analyzed", "Unknown")
                top = list(data["statistics"].get("most_imported_modules", {}).keys())[:3]
                msg = f"Analysis successful.\nFiles: {files}\nTop modules: {', '.join(top) if top else 'None'}"
                QMessageBox.information(self, "Analysis", msg)
            else:
                QMessageBox.warning(self, "Warning", "No report found.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DependencyAnalyzer()
    window.show()
    sys.exit(app.exec_())
