import sys
import os
import subprocess
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QSettings
from srename_interface import Ui_MainWindow
import logging
from datetime import datetime

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, obj=None, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.num_files = 8
        self.setup_logging()
        
        # Initialize QSettings
        self.settings = QSettings("SmartRenameSystem", "RenameManager")
        
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

        # Connect reset and run buttons
        self.reset_button.clicked.connect(self.reset_root_names)
        self.run_script_button.clicked.connect(self.run_script)
        
        # Initially disable run button
        self.run_script_button.setEnabled(False)
        
        # Load saved settings
        self.load_settings()

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

    def save_settings(self):
        """Save current state to QSettings"""
        try:
            # Save input fields
            for i in range(1, self.num_files + 1):
                new_name = getattr(self, f'new_name_input{i}').text()
                file_path = getattr(self, f'rename_input{i}').text()
                
                self.settings.setValue(f"new_name_{i}", new_name)
                self.settings.setValue(f"file_path_{i}", file_path)
            
            # Save original filenames and paths
            self.settings.setValue("original_filenames", self.original_filenames)
            self.settings.setValue("file_paths", self.file_paths)
            
            logging.info("Settings saved successfully")
        except Exception as e:
            logging.error(f"Error saving settings: {str(e)}")

    def load_settings(self):
        """Load saved state from QSettings"""
        try:
            # Load input fields
            for i in range(1, self.num_files + 1):
                new_name = self.settings.value(f"new_name_{i}", "")
                file_path = self.settings.value(f"file_path_{i}", "")
                
                if new_name:
                    getattr(self, f'new_name_input{i}').setText(new_name)
                if file_path:
                    getattr(self, f'rename_input{i}').setText(file_path)
            
            # Load original filenames and paths
            self.original_filenames = self.settings.value("original_filenames", {})
            self.file_paths = self.settings.value("file_paths", {})
            
            # Enable run button if file 1 exists
            if self.file_paths.get(1):
                self.run_script_button.setEnabled(True)
            
            logging.info("Settings loaded successfully")
        except Exception as e:
            logging.error(f"Error loading settings: {str(e)}")
            self.show_error("Failed to load saved settings")

    def closeEvent(self, event):
        """Override close event to save settings before closing"""
        try:
            self.save_settings()
            logging.info("Application closed - settings saved")
            event.accept()
        except Exception as e:
            logging.error(f"Error during application close: {str(e)}")
            event.accept()

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
                
                # Enable run button if this is file 1
                if file_number == 1:
                    self.run_script_button.setEnabled(True)
                    self.show_success("File 1 loaded. You can now run the script after renaming.")
                
                # Save settings after file selection
                self.save_settings()
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
            
            # Update run button state if file 1 was renamed
            if file_number == 1:
                self.run_script_button.setEnabled(True)
            
            # Save settings after successful rename
            self.save_settings()
            
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

    def run_script(self):
        """Execute the first selected file"""
        try:
            # Check if file 1 exists and has been renamed
            file_path = self.file_paths.get(1)
            if not file_path or not os.path.exists(file_path):
                self.show_error("File 1 not found. Please select and rename File 1 first.")
                return

            # Check if it's a Python script
            if not file_path.lower().endswith('.py'):
                self.show_error("File 1 must be a Python script (.py file)")
                return

            # Execute the script
            try:
                working_dir = os.path.dirname(file_path)
                
                # Setup environment
                env = os.environ.copy()
                env['PYTHONPATH'] = working_dir + os.pathsep + env.get('PYTHONPATH', '')
                
                # Run the script
                process = subprocess.Popen(
                    ['python', file_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    creationflags=subprocess.CREATE_NO_WINDOW,
                    cwd=working_dir,
                    env=env
                )
                
                # Monitor the process
                stdout, stderr = process.communicate()
                
                if process.returncode == 0:
                    self.show_success("Script executed successfully!")
                    logging.info(f"Script executed successfully: {file_path}")
                else:
                    error_msg = stderr.decode() if stderr else "Unknown error occurred"
                    raise Exception(f"Script execution failed: {error_msg}")
                    
            except Exception as e:
                raise Exception(f"Error executing script: {str(e)}")
                
        except Exception as e:
            self.show_error(str(e))
            logging.error(f"Run script error: {str(e)}")

    def on_root_name_changed(self, file_number, text):
        """Handle root name changes and validate input"""
        try:
            if text:
                logging.info(f"Root name changed for file {file_number}: {text}")
                
                # Check for invalid characters in filename
                invalid_chars = r'<>:"/\|?*'
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
            msg_box.setText("Are you sure you want to reset all root names?\nThis will also clear saved settings.")
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
                
                # Clear settings
                self.settings.clear()
                
                # Disable run button
                self.run_script_button.setEnabled(False)
                
                self.show_success("All root names and settings have been reset")
                logging.info("All fields and settings have been reset")
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

def main():
    app = QtWidgets.QApplication(sys.argv)
    
    # Set application information for QSettings
    app.setOrganizationName("SmartRenameSystem")
    app.setApplicationName("RenameManager")
    
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
