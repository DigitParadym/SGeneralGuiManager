
import sys
import os
from PyQt5 import QtWidgets, QtCore, QtGui
from srename_interface import Ui_MainWindow  # Updated import
import logging
from datetime import datetime

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, obj=None, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.num_files = 8
        self.setup_logging()
        
        # Store original filenames and paths
        self.original_filenames = {}
        self.file_paths = {}
        
        # Connect buttons to functions
        for i in range(1, self.num_files + 1):
            getattr(self, f'rename_browse{i}').clicked.connect(
                lambda checked, x=i: self.browse_rename_file(x))
            getattr(self, f'rename_file{i}').clicked.connect(
                lambda checked, x=i: self.rename_file(x))
            
            # Connect textChanged signal for new_name_input
            getattr(self, f'new_name_input{i}').textChanged.connect(
                lambda text, x=i: self.on_root_name_changed(x, text))

        # Connect reset button
        self.reset_button.clicked.connect(self.reset_root_names)

    def setup_logging(self):
        """Set up logging configuration"""
        log_dir = 'logs'
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        log_file = os.path.join(log_dir, f'rename_system_{datetime.now().strftime("%Y%m%d")}.log')
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        logging.info("Application started")

    def browse_rename_file(self, file_number):
        """Handle file selection for renaming"""
        try:
            file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
                self, 
                f"Select File {file_number} to Rename",
                "",
                "All Files (*)"
            )
            
            if file_path:
                current_name = os.path.basename(file_path)
                rename_input = getattr(self, f'rename_input{file_number}')
                new_name_input = getattr(self, f'new_name_input{file_number}')
                
                # Store the original filename and path
                self.original_filenames[file_number] = current_name
                self.file_paths[file_number] = file_path
                
                # Set the file path
                rename_input.setText(file_path)
                
                # Only set the new name if it's empty (preserve root name if already set)
                if not new_name_input.text():
                    new_name_input.setText(current_name)
                
                logging.info(f"File selected for slot {file_number}: {file_path}")
                self.show_success(f"File loaded successfully in slot {file_number}")
        except Exception as e:
            self.show_error(f"Error selecting file: {str(e)}")
            logging.error(f"File selection error: {str(e)}")

    def rename_file(self, file_number):
        """Handle file renaming operation"""
        try:
            new_name = getattr(self, f'new_name_input{file_number}').text()
            full_path = getattr(self, f'rename_input{file_number}').text()
            
            if not new_name:
                self.show_error(f"Please enter a new name for file {file_number}")
                return
            
            if not full_path:
                self.show_error(f"Please select a file to rename for file {file_number}")
                return
            
            # Check if the extension is preserved
            old_ext = os.path.splitext(full_path)[1]
            if not new_name.endswith(old_ext):
                new_name += old_ext
            
            new_path = self.rename_file_logic(full_path, new_name)
            getattr(self, f'rename_input{file_number}').setText(new_path)
            self.file_paths[file_number] = new_path
            
            self.show_success(f"File {file_number} renamed successfully to {new_name}")
            logging.info(f"File {file_number} renamed: {full_path} -> {new_path}")
            
        except Exception as e:
            self.show_error(f"Error renaming file {file_number}: {str(e)}")
            logging.error(f"Rename error for file {file_number}: {str(e)}")

    def rename_file_logic(self, old_path, new_name):
        """Core file renaming logic"""
        try:
            old_path = os.path.normpath(old_path)
            
            if not os.path.exists(old_path):
                raise FileNotFoundError(f"File not found: {old_path}")
            
            directory = os.path.dirname(old_path)
            new_path = os.path.join(directory, new_name)
            
            # If the new file already exists, remove it first
            if os.path.exists(new_path) and new_path != old_path:
                os.remove(new_path)
                logging.info(f"Removed existing file: {new_path}")
            
            os.rename(old_path, new_path)
            logging.info(f"Renamed file from '{old_path}' to '{new_path}'")
            return new_path
            
        except Exception as e:
            logging.error(f"Error in rename_file_logic: {str(e)}")
            raise

    def on_root_name_changed(self, file_number, text):
        """Handle root name changes and validate input"""
        try:
            if text:
                logging.info(f"Root name changed for file {file_number}: {text}")
                
                # Check for invalid characters in filename
                invalid_chars = r'<>:"/\|?*'  # Fixed invalid escape sequence
                if any(char in text for char in invalid_chars):
                    self.show_error(f"Invalid characters in filename. Avoid: {invalid_chars}")
                    return
                
                # Update UI to show valid input
                getattr(self, f'new_name_input{file_number}').setStyleSheet("""
                    QLineEdit {
                        padding: 5px;
                        border: 1px solid #2ecc71;
                        border-radius: 3px;
                    }
                """)
        except Exception as e:
            logging.error(f"Error in root name change handler: {str(e)}")

    def reset_root_names(self):
        """Reset all root name fields and clear stored data"""
        try:
            msg_box = QtWidgets.QMessageBox()
            msg_box.setIcon(QtWidgets.QMessageBox.Question)
            msg_box.setText("Are you sure you want to reset all root names?")
            msg_box.setWindowTitle("Confirm Reset")
            msg_box.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            
            if msg_box.exec_() == QtWidgets.QMessageBox.Yes:
                for i in range(1, self.num_files + 1):
                    # Clear input fields
                    getattr(self, f'new_name_input{i}').clear()
                    getattr(self, f'rename_input{i}').clear()
                    
                    # Reset styling
                    getattr(self, f'new_name_input{i}').setStyleSheet("""
                        QLineEdit {
                            padding: 5px;
                            border: 1px solid #bdc3c7;
                            border-radius: 3px;
                        }
                    """)
                
                # Clear stored data
                self.original_filenames.clear()
                self.file_paths.clear()
                
                self.show_success("All root names have been reset")
                logging.info("All fields have been reset")
        except Exception as e:
            self.show_error(f"Error resetting root names: {str(e)}")
            logging.error(f"Reset error: {str(e)}")

    def show_success(self, message):
        """Display success messages"""
        self.status_label.setText(message)
        self.status_label.setStyleSheet("""
            QLabel {
                color: green;
                font-size: 12pt;
                background-color: #ecf9f1;
                padding: 5px;
                border-radius: 3px;
            }
        """)

    def show_error(self, message):
        """Display error messages"""
        self.status_label.setText(message)
        self.status_label.setStyleSheet("""
            QLabel {
                color: red;
                font-size: 12pt;
                background-color: #f9ecec;
                padding: 5px;
                border-radius: 3px;
            }
        """)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())
