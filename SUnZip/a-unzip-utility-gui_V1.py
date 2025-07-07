import os
import zipfile
from PyQt5 import QtWidgets, QtCore

class UnzipUtility(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Unzip Utility")
        self.setGeometry(100, 100, 400, 300)
        
        # Set the downloads folder path
        self.downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
        self.zip_files = []
        
        self.setup_ui()
        self.scan_for_zip_files()  # Automatically scan on startup

    def setup_ui(self):
        self.layout = QtWidgets.QVBoxLayout(self)
        
        # List Widget to show found ZIP files
        self.file_list_widget = QtWidgets.QListWidget()
        self.layout.addWidget(self.file_list_widget)
        
        # Status label
        self.status_label = QtWidgets.QLabel()
        self.layout.addWidget(self.status_label)
        
        # Button to rescan for ZIP files
        self.scan_button = QtWidgets.QPushButton("Scan for ZIP Files")
        self.scan_button.clicked.connect(self.scan_for_zip_files)
        self.layout.addWidget(self.scan_button)
        
        # Button to unzip selected files
        self.run_button = QtWidgets.QPushButton("Run")
        self.run_button.clicked.connect(self.run_unzip)
        self.layout.addWidget(self.run_button)

    def scan_for_zip_files(self):
        """Scan the Downloads folder for ZIP files and display them."""
        self.zip_files = [
            f for f in os.listdir(self.downloads_folder) if f.endswith('.zip')
        ]
        self.file_list_widget.clear()
        
        if self.zip_files:
            self.file_list_widget.addItems(self.zip_files)
            self.status_label.setText(f"Found {len(self.zip_files)} ZIP file(s) in Downloads.")
        else:
            self.status_label.setText("No ZIP files found in Downloads.")

    def run_unzip(self):
        """Unzip all listed ZIP files to the Downloads directory."""
        if not self.zip_files:
            self.status_label.setText("No ZIP files to unzip.")
            return
        
        for zip_file in self.zip_files:
            zip_path = os.path.join(self.downloads_folder, zip_file)
            try:
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(self.downloads_folder)
                self.status_label.setText("All files unzipped successfully!")
            except Exception as e:
                self.status_label.setText(f"Failed to unzip {zip_file}: {str(e)}")
                break

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = UnzipUtility()
    window.show()
    app.exec_()
