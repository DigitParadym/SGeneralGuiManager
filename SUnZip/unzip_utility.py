import sys
import os
import logging
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton, QMessageBox

# Configure logging
script_dir = os.path.dirname(os.path.abspath(__file__))  # P1 directory
log_dir = os.path.join(script_dir, "logs")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f"pointer_connector_{datetime.now().strftime('%Y%m%d')}.log")

logging.basicConfig(
    filename=log_file,
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Paths to utilities
UNZIP_UTILITY_PATH = os.path.join(script_dir, "..", "..", "SUnZip", "unzip_utility.py")
CONNECTOR_PRO_PATH = os.path.join(script_dir, "..", "..", "connectorpro", "main.py")

class PointerUnzipConnector(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle('P1: Unzip -> Run Connector')
        self.setGeometry(100, 100, 400, 200)

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Status labels
        self.unzip_status_label = QLabel("Unzip Status: Waiting to start...")
        layout.addWidget(self.unzip_status_label)

        self.connector_status_label = QLabel("Connector Status: Waiting for unzip...")
        layout.addWidget(self.connector_status_label)

        # Buttons
        self.run_button = QPushButton("Run Process")
        self.run_button.clicked.connect(self.run_process)
        layout.addWidget(self.run_button)

    def run_process(self):
        """Run the unzip and connector processes"""
        self.run_button.setEnabled(False)
        self.unzip_status_label.setText("Unzip Status: Running...")

        # Step 1: Trigger unzip utility
        unzip_success = self.trigger_unzip()
        if unzip_success:
            self.unzip_status_label.setText("Unzip Status: Completed successfully.")
            self.connector_status_label.setText("Connector Status: Running...")
            
            # Step 2: Trigger connector
            connector_success = self.trigger_connector()
            if connector_success:
                self.connector_status_label.setText("Connector Status: Completed successfully.")
                QMessageBox.information(self, "Success", "Process completed successfully!")
            else:
                self.connector_status_label.setText("Connector Status: Failed.")
                QMessageBox.critical(self, "Error", "Connector process failed.")
        else:
            self.unzip_status_label.setText("Unzip Status: Failed.")
            QMessageBox.critical(self, "Error", "Unzip process failed. Check logs for details.")

        self.run_button.setEnabled(True)

    def trigger_unzip(self):
        """Trigger the `unzip_utility.py` script and wait for a response"""
        try:
            import subprocess
            result = subprocess.run(
                ["python", UNZIP_UTILITY_PATH],
                capture_output=True,
                text=True,
                check=False  # Allow non-zero exit codes
            )
            if result.returncode == 1:  # Success
                logger.info(f"Unzip utility succeeded: {result.stdout}")
                return True
            elif result.returncode == 0:  # Failure
                logger.error(f"Unzip utility failed: {result.stderr}")
                self.display_error(f"Unzip Error: {result.stderr.strip()}")
                return False
            else:  # Unexpected response
                logger.error(f"Unzip utility returned unexpected code {result.returncode}: {result.stderr}")
                self.display_error(f"Unexpected Error: {result.stderr.strip()}")
                return False
        except Exception as e:
            logger.error(f"Error while triggering unzip utility: {str(e)}")
            self.display_error(f"Unexpected Error: {str(e)}")
            return False

    def trigger_connector(self):
        """Trigger the `connectorpro/main.py` script"""
        try:
            import subprocess
            result = subprocess.run(
                ["python", CONNECTOR_PRO_PATH],
                capture_output=True,
                text=True,
                check=True
            )
            logger.info(f"Connector process succeeded: {result.stdout}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Connector process failed: {e.stderr}")
            self.display_error(f"Connector Error: {e.stderr.strip()}")
            return False
        except Exception as e:
            logger.error(f"Error while triggering connector process: {str(e)}")
            self.display_error(f"Unexpected Error: {str(e)}")
            return False

    def display_error(self, message):
        """Display error message"""
        QMessageBox.critical(self, "Error", message)

def main():
    app = QApplication(sys.argv)
    window = PointerUnzipConnector()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
