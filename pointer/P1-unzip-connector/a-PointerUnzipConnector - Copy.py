import sys
import os
import logging
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QFileDialog, QMessageBox, QProgressBar, QLabel
from PyQt5.QtCore import Qt

# Setup correct paths
script_dir = os.path.dirname(os.path.abspath(__file__))  # P1-unzip-connector directory
pointer_dir = os.path.dirname(script_dir)                # pointer directory
manager_dir = os.path.dirname(pointer_dir)               # SGeneralGuiManager directory

# Add SGeneralGuiManager directory to Python path
if manager_dir not in sys.path:
    sys.path.insert(0, manager_dir)

# Configure logging
log_dir = os.path.join(script_dir, "logs")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f"pointer_connector_{datetime.now().strftime('%Y%m%d')}.log")

logging.basicConfig(
    filename=log_file,
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

try:
    from SUnZip.unzip_utility import UnzipUtility
    from connectorpro.connectorpro_core import ConnectorPro
    logger.info("Successfully imported UnzipUtility and ConnectorPro")
except ImportError as e:
    logger.error(f"Import error: {str(e)}")
    print(f"Error: Make sure SUnZip and connectorpro modules are in {manager_dir}")
    raise

class PointerUnzipConnector(QMainWindow):
    def __init__(self):
        super().__init__()
        self.unzip_utility = UnzipUtility()
        self.connector = ConnectorPro()
        self.init_ui()
        self.extract_path = None
        logger.info("PointerUnzipConnector initialized")

    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle('P1: Unzip -> Run Connector')
        self.setGeometry(100, 100, 500, 250)

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Step 1 Label
        self.step1_label = QLabel("Step 1: Select and Unzip")
        self.step1_label.setStyleSheet("font-weight: bold;")
        
        # Create the main run button
        self.run_button = QPushButton('Select ZIP File', self)
        self.run_button.clicked.connect(self.start_unzip_process)

        # Create progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)

        # Status for Unzip
        self.unzip_status = QLabel("Unzip Status: Waiting for file selection")
        self.unzip_status.setStyleSheet("color: black;")

        # Step 2 Label
        self.step2_label = QLabel("Step 2: Run Connector")
        self.step2_label.setStyleSheet("font-weight: bold;")

        # Run Connector Button (initially disabled)
        self.connector_button = QPushButton('Run Connector', self)
        self.connector_button.clicked.connect(self.run_connector_process)
        self.connector_button.setEnabled(False)

        # Status for Connector
        self.connector_status = QLabel("Connector Status: Waiting for unzip")
        self.connector_status.setStyleSheet("color: black;")

        # Add widgets to layout
        layout.addWidget(self.step1_label)
        layout.addWidget(self.run_button)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.unzip_status)
        layout.addSpacing(20)
        layout.addWidget(self.step2_label)
        layout.addWidget(self.connector_button)
        layout.addWidget(self.connector_status)

    def update_unzip_status(self, message, is_error=False):
        """Update unzip status with message"""
        color = "red" if is_error else "green" if "success" in message.lower() else "black"
        self.unzip_status.setStyleSheet(f"color: {color};")
        self.unzip_status.setText(f"Unzip Status: {message}")
        logger.info(f"Unzip status updated: {message}")

    def update_connector_status(self, message, is_error=False):
        """Update connector status with message"""
        color = "red" if is_error else "green" if "success" in message.lower() else "black"
        self.connector_status.setStyleSheet(f"color: {color};")
        self.connector_status.setText(f"Connector Status: {message}")
        logger.info(f"Connector status updated: {message}")

    def start_unzip_process(self):
        """Handle the unzip process"""
        try:
            # Get ZIP file
            zip_path = self.get_zip_file()
            if not zip_path:
                return

            logger.info(f"Selected ZIP file: {zip_path}")
            self.run_button.setEnabled(False)
            self.update_unzip_status("Starting unzip process...")
            
            # Show progress bar
            self.progress_bar.setVisible(True)
            self.extract_path = os.path.dirname(zip_path)
            
            # Start unzip
            success = self.unzip_utility.extract_file(
                zip_path, 
                self.extract_path,
                progress_callback=self.update_progress
            )

            if success:
                logger.info("Unzip successful")
                self.update_unzip_status("Unzip completed successfully!")
                # Enable connector button after successful unzip
                self.connector_button.setEnabled(True)
                self.update_connector_status("Ready to run connector")
                # Show success message
                self.show_info_message("Unzip completed successfully!")
            else:
                logger.error("Unzip failed")
                self.update_unzip_status("Failed to extract ZIP file", is_error=True)
                self.show_error_message("Failed to extract ZIP file")

        except Exception as e:
            logger.error(f"Error in unzip process: {str(e)}")
            self.update_unzip_status(f"Error: {str(e)}", is_error=True)
            self.show_error_message(f"An error occurred: {str(e)}")
        finally:
            self.progress_bar.setVisible(False)
            self.run_button.setEnabled(True)

    def run_connector_process(self):
        """Handle the connector process"""
        try:
            if not self.extract_path:
                self.update_connector_status("No extracted path available", is_error=True)
                return

            self.connector_button.setEnabled(False)
            self.update_connector_status("Running connector...")
            
            # Run connector
            self.connector.initialize(self.extract_path)
            success = self.connector.process_files()

            if success:
                logger.info("Connector process successful")
                self.update_connector_status("Connector completed successfully!")
                self.show_info_message("Connector process completed successfully!")
            else:
                logger.error("Connector process failed")
                self.update_connector_status("Connector process failed", is_error=True)
                self.show_error_message("Connector process failed")

        except Exception as e:
            logger.error(f"Error in connector process: {str(e)}")
            self.update_connector_status(f"Error: {str(e)}", is_error=True)
            self.show_error_message(f"Connector error: {str(e)}")
        finally:
            self.connector_button.setEnabled(True)

    def get_zip_file(self):
        """Open file dialog for ZIP selection"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select ZIP File",
            "",
            "ZIP files (*.zip)"
        )
        if file_path:
            logger.info(f"ZIP file selected: {file_path}")
        return file_path

    def update_progress(self, value):
        """Update the progress bar"""
        self.progress_bar.setValue(value)

    def show_error_message(self, message):
        """Display error message dialog"""
        QMessageBox.critical(self, "Error", message)

    def show_info_message(self, message):
        """Display information message dialog"""
        QMessageBox.information(self, "Success", message)

def main():
    try:
        app = QApplication(sys.argv)
        window = PointerUnzipConnector()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        print(f"An error occurred. Check the log at: {log_file}")
        sys.exit(1)

if __name__ == "__main__":
    main()
