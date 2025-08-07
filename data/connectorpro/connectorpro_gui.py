import os
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QGroupBox, QHBoxLayout, QFileDialog, QMessageBox
from PyQt5.QtCore import QSettings

class ConnectorProGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = QSettings("ConnectorPro", "FileManager")
        self.setWindowTitle("File Management")
        self.setGeometry(100, 100, 400, 250)  # Smaller window dimensions for compact layout
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        layout = QVBoxLayout(self.central_widget)

        # Group box for folders selection, compact style
        folder_group = QGroupBox("Root Name")
        folder_layout = QVBoxLayout(folder_group)

        # Source Folder setup
        source_hbox = QHBoxLayout()
        source_hbox.addWidget(QLabel("Source:"))
        self.source_input = QLineEdit(os.path.expanduser("~/Downloads"))
        self.source_input.setFixedHeight(24)
        source_hbox.addWidget(self.source_input)
        source_button = QPushButton("Browse")
        source_button.setFixedSize(60, 24)
        source_button.clicked.connect(self.browse_source_folder)
        source_hbox.addWidget(source_button)
        folder_layout.addLayout(source_hbox)

        # Destination Folder setup
        dest_hbox = QHBoxLayout()
        dest_hbox.addWidget(QLabel("Destination:"))
        self.dest_input = QLineEdit()
        self.dest_input.setFixedHeight(24)
        dest_hbox.addWidget(self.dest_input)
        dest_button = QPushButton("Browse")
        dest_button.setFixedSize(60, 24)
        dest_button.clicked.connect(self.browse_dest_folder)
        dest_hbox.addWidget(dest_button)
        folder_layout.addLayout(dest_hbox)

        layout.addWidget(folder_group)

        # Run button for processing files
        run_button = QPushButton("Run Connector")
        run_button.setFixedHeight(30)
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
        # Load the saved folder paths from previous sessions
        self.source_input.setText(self.settings.value('source_folder', self.source_input.text()))
        self.dest_input.setText(self.settings.value('destination_folder', ''))

    def closeEvent(self, event):
        # Save settings on close
        self.settings.setValue('source_folder', self.source_input.text())
        self.settings.setValue('destination_folder', self.dest_input.text())
        super().closeEvent(event)

    def run_connector(self):
        # Check if folders are valid
        if not os.path.exists(self.source_input.text()) or not os.path.exists(self.dest_input.text()):
            QMessageBox.critical(self, "Error", "Please specify valid source and destination folders.")
            return
        
        # Configuration for the core processor
        config = {
            'source_folder': self.source_input.text(),
            'destination_folder': self.dest_input.text(),
            'backup_folder': os.path.join(self.dest_input.text(), 'backups')
        }

        # Import and run the core processing logic
        from connectorpro_core import ConnectorPro
        connector = ConnectorPro(config)
        moved_files = connector.process_and_move_files()
        
        # Feedback to the user
        if moved_files:
            QMessageBox.information(self, "Success", f"Processed {len(moved_files)} files.")
        else:
            QMessageBox.warning(self, "Warning", "No files were processed.")
