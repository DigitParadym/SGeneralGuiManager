
import os
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QGroupBox, QHBoxLayout, QFileDialog, QMessageBox
from PyQt5.QtCore import QSettings

class ConnectorProGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = QSettings("ConnectorPro", "FileManager")
        self.setWindowTitle("ConnectorPro GUI")
        self.setGeometry(100, 100, 800, 600)
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        layout = QVBoxLayout(self.central_widget)

        # Source Folder setup
        source_layout = QHBoxLayout()
        source_layout.addWidget(QLabel("Source Folder:"))
        self.source_input = QLineEdit(os.path.expanduser("~/Downloads"))
        source_layout.addWidget(self.source_input)
        source_button = QPushButton("Browse")
        source_button.clicked.connect(self.browse_source_folder)
        source_layout.addWidget(source_button)
        layout.addLayout(source_layout)

        # Destination Folder setup
        dest_layout = QHBoxLayout()
        dest_layout.addWidget(QLabel("Destination Folder:"))
        self.dest_input = QLineEdit()
        dest_layout.addWidget(self.dest_input)
        dest_button = QPushButton("Browse")
        dest_button.clicked.connect(self.browse_dest_folder)
        dest_layout.addWidget(dest_button)
        layout.addLayout(dest_layout)

        # Run button
        run_button = QPushButton("Run Connector")
        run_button.clicked.connect(self.run_connector)
        layout.addWidget(run_button)

    def browse_source_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Source Folder", self.source_input.text())
        if folder:
            self.source_input.setText(folder)

    def browse_dest_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Destination Folder", self.dest_input.text())
        if folder:
            self.dest_input.setText(folder)

    def load_settings(self):
        self.source_input.setText(self.settings.value('source_folder', self.source_input.text()))
        self.dest_input.setText(self.settings.value('destination_folder', ''))

    def closeEvent(self, event):
        self.settings.setValue('source_folder', self.source_input.text())
        self.settings.setValue('destination_folder', self.dest_input.text())
        super().closeEvent(event)

    def run_connector(self):
        if not os.path.exists(self.source_input.text()) or not os.path.exists(self.dest_input.text()):
            QMessageBox.critical(self, "Error", "Please specify valid source and destination folders.")
            return
        config = {
            'source_folder': self.source_input.text(),
            'destination_folder': self.dest_input.text(),
            'backup_folder': os.path.join(self.dest_input.text(), 'backups')
        }
        from connectorpro_core import ConnectorPro
        connector = ConnectorPro(config)
        moved_files = connector.process_and_move_files()
        if moved_files:
            QMessageBox.information(self, "Success", f"Processed {len(moved_files)} files.")
        else:
            QMessageBox.warning(self, "Warning", "No files were processed.")
