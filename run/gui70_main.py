# gui70_main.py
from PyQt5 import QtWidgets, QtCore, QtGui
import sys
import os
import json
import datetime
from gui70_interface import Ui_MainWindow
from run70_functions import RunManager

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
        # Initialize the RunManager
        self.run_manager = RunManager(os.path.dirname(__file__))
        
        # Initialize history file if needed
        self._initialize_history()
        
        # Connect all signals to slots
        self._connect_signals()
        
        # Set initial status
        self.status_label.setText("Ready")
        
        # Update history file display
        self._update_history_display()

    def _initialize_history(self):
        '''Initialize history file if it doesn't exist'''
        try:
            if not os.path.exists(self.run_manager.history_file):
                init_message = {
                    "initialized": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "version": "1.0",
                    "entries": []
                }
                with open(self.run_manager.history_file, 'w', encoding='utf-8') as f:
                    json.dump(init_message, f, indent=2)
                return True
            return False
        except Exception as e:
            self.status_label.setText(f"Error initializing history: {str(e)}")
            self.status_label.setStyleSheet("color: red;")
            return False

    def _connect_signals(self):
        '''Connect all signals to their slots'''
        self.browse_script.clicked.connect(self.browse_script_file)
        self.run_script.clicked.connect(self.execute_script)
        self.copy_history.clicked.connect(self.copy_history_to_clipboard)
        self.troubleshoot_button.clicked.connect(self.show_troubleshooting_dialog)
        self.select_history.clicked.connect(self.select_history_file)
        self.clear_discussion.clicked.connect(self.clear_discussions)
        self.add_files_btn.clicked.connect(self.add_files_to_modular)  # Corrected method
        self.reset_modular.clicked.connect(self.reset_modular_files)
        self.script_path.textChanged.connect(self._validate_script_path)
        self.history_file_name.editingFinished.connect(
            lambda: self._on_history_name_changed(self.history_file_name.text())
        )

    def _validate_script_path(self):
        '''Enable or disable the run button based on the script path validity'''
        path = self.script_path.text()
        self.run_script.setEnabled(bool(path and os.path.exists(path) and path.endswith('.py')))

    def _update_history_display(self):
        '''Update the display of current history file'''
        history_path = self.run_manager.history_file
        display_path = os.path.relpath(history_path, self.run_manager.base_dir)
        self.current_history_label.setText(f"Current: {display_path}")
        self.current_history_label.setStyleSheet("color: gray; font-size: 10px;")

    def _on_history_name_changed(self, text):
        '''Handle changes to the history file name field'''
        if text:
            new_path = os.path.join(self.run_manager.srun_dir, text)
            success, message = self.run_manager.set_history_file(new_path)
            if success:
                self._update_history_display()
                self.status_label.setText(message)
                self.status_label.setStyleSheet("color: green;")
            else:
                self.status_label.setText(message)
                self.status_label.setStyleSheet("color: red;")

    def browse_script_file(self):
        '''Open file dialog to select a Python script'''
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Select Python Script",
            "",
            "Python Files (*.py)"
        )
        if file_path:
            self.script_path.setText(file_path)

    def execute_script(self):
        '''Execute the selected script and handle modular files'''
        script_path = self.script_path.text()
        if not script_path:
            self.status_label.setText("Please select a script to run")
            return

        try:
            history_file_name = self.history_file_name.text() or "run_history.log"
            if not history_file_name.endswith('.log'):
                history_file_name += '.log'

            modular_files = [self.modular_files.item(i).text() for i in range(self.modular_files.count())] if self.modular_section.isChecked() else None
            discussions = self.discussion_text.toPlainText()

            result = self.run_manager.run_script(
                script_path,
                self.script_args.text(),
                self.use_venv.isChecked(),
                history_file_name,
                self.include_content.isChecked(),
                modular_files,
                discussions
            )

            # Display results
            self.run_output.clear()
            if result.stdout:
                self.run_output.append(result.stdout)
            if result.stderr:
                self.run_output.append("\nErrors:\n" + result.stderr)

            # Update status
            script_dir = os.path.dirname(script_path)
            modular_count = len(modular_files) if modular_files else 0

            if result.returncode == 0:
                reply = QtWidgets.QMessageBox.question(
                    self,
                    'Execution Complete',
                    'Script executed successfully. What would you like to clear?',
                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Cancel
                )

                if reply == QtWidgets.QMessageBox.Yes:  # "Clear Both"
                    self.discussion_text.clear()
                    if self.modular_section.isChecked():
                        self.modular_files.clear()
                    self.status_label.setText("Execution complete. Discussions and modular files cleared.")
                    self.status_label.setStyleSheet("color: green;")
                elif reply == QtWidgets.QMessageBox.No:  # "Clear Discussions Only"
                    self.discussion_text.clear()
                    self.status_label.setText("Execution complete. Discussions cleared.")
                    self.status_label.setStyleSheet("color: green;")
                else:  # "Don't Clear"
                    self.status_label.setText("Execution complete.")
                    self.status_label.setStyleSheet("color: green;")

            else:
                status_parts = [f"Script failed. Executed from {script_dir}"]
                if modular_files:
                    status_parts.append(f"Including {modular_count} modular files")
                if discussions:
                    status_parts.append("Discussions saved")
                status_parts.append(f"History saved to {history_file_name}")
                
                self.status_label.setText(". ".join(status_parts))
                self.status_label.setStyleSheet("color: red;")

        except Exception as e:
            self.status_label.setText(f"Error: {str(e)}")
            self.run_output.append(f"Error occurred: {str(e)}")
            self.status_label.setStyleSheet("color: red;")

    def add_files_to_modular(self):
        '''Open file dialog to add multiple files to the modular list'''
        file_paths, _ = QtWidgets.QFileDialog.getOpenFileNames(
            self,
            "Select Modular Files",
            "",
            "All Files (*.*)"
        )
        for file_path in file_paths:
            self.modular_files.addItem(file_path)

    def copy_history_to_clipboard(self):
        '''Copy the run history to the clipboard'''
        try:
            history_content = self.run_manager.get_history()
            
            if not history_content:
                self.status_label.setText("History file is empty or cannot be read")
                self.status_label.setStyleSheet("color: red;")
                return
                
            clipboard = QtWidgets.QApplication.clipboard()
            clipboard.setText(history_content)
            
            current_file = os.path.basename(self.run_manager.history_file)
            self.status_label.setText(f"Run history from {current_file} copied to clipboard")
            self.run_output.append(f"Run history from {current_file} copied to clipboard")
            self.status_label.setStyleSheet("color: green;")

        except Exception as e:
            self.status_label.setText(f"Error copying history: {str(e)}")
            self.run_output.append(f"Error occurred: {str(e)}")
            self.status_label.setStyleSheet("color: red;")

    def reset_modular_files(self):
        """Reset modular files with confirmation"""
        if self.modular_files.count() > 0:
            reply = QtWidgets.QMessageBox.question(
                self, 'Reset Modular Files',
                'Are you sure you want to clear all modular files?',
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                QtWidgets.QMessageBox.No
            )
            if reply == QtWidgets.QMessageBox.Yes:
                self.modular_files.clear()
                self.status_label.setText("Modular files cleared")
                self.status_label.setStyleSheet("color: blue;")

    def clear_discussions(self):
        """Clear discussions with confirmation if not empty"""
        if self.discussion_text.toPlainText():
            reply = QtWidgets.QMessageBox.question(
                self, 'Clear Discussions',
                'Are you sure you want to clear the discussions?',
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                QtWidgets.QMessageBox.No
            )
            if reply == QtWidgets.QMessageBox.Yes:
                self.discussion_text.clear()
                self.status_label.setText("Discussions cleared")
                self.status_label.setStyleSheet("color: blue;")

    def select_history_file(self):
        '''Allow user to select an existing history file or create new one'''
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Select or Create History File",
            self.run_manager.srun_dir,
            "Log Files (*.log);;All Files (*.*)"
        )
        
        if file_path:
            success, message = self.run_manager.set_history_file(file_path)
            
            if success:
                self._update_history_display()
                self.status_label.setText(message)
                self.status_label.setStyleSheet("color: green;")
                self.history_file_name.setText(os.path.basename(file_path))
            else:
                self.status_label.setText(message)
                self.status_label.setStyleSheet("color: red;")

    def show_troubleshooting_dialog(self):
        '''Show a dialog with basic troubleshooting and environment information'''
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Troubleshooting")
        dialog.setModal(True)
        dialog.resize(600, 400)
        
        layout = QtWidgets.QVBoxLayout(dialog)
        tabs = QtWidgets.QTabWidget()
        
        # Basic troubleshooting tab
        basic_tab = QtWidgets.QWidget()
        basic_layout = QtWidgets.QVBoxLayout(basic_tab)
        troubleshooting_text = (
            "Basic Troubleshooting Steps:\n\n"
            "1. Check if the script exists in the selected path\n"
            "2. Verify the virtual environment if enabled\n"
            "3. Check script permissions\n"
            "4. Review the output for error messages\n"
            "5. Check the run history for previous executions\n"
            "6. Verify script can access required dependencies\n"
            "7. Check modular files if enabled\n"
            "8. Ensure discussions are saved per run\n"
            "9. Verify Python version compatibility\n"
            "10. Check available disk space for history"
        )
        basic_info = QtWidgets.QLabel(troubleshooting_text)
        basic_info.setWordWrap(True)
        basic_layout.addWidget(basic_info)
        tabs.addTab(basic_tab, "Basic Steps")
        
        # Environment information tab
        env_tab = QtWidgets.QWidget()
        env_layout = QtWidgets.QVBoxLayout(env_tab)
        
        modular_count = len(self.modular_files.selectedItems()) if self.modular_section.isChecked() else 0
        env_text = (
            "Environment Information:\n\n"
            f" History Directory: {self.run_manager.srun_dir}\n"
            f" History File: {self.run_manager.history_file}\n"
            f" Python Version: {sys.version.split()[0]}\n"
            f" Working Directory: {os.getcwd()}\n"
            f" Script Directory: {os.path.dirname(self.script_path.text()) if self.script_path.text() else 'Not selected'}\n"
            f" Modular Files: {modular_count} selected\n"
            " Virtual Environment Status: " + 
            ("Found" if os.path.exists(os.path.join(self.run_manager.srun_dir, 'venv')) 
             else "Not Found")
        )
        env_info = QtWidgets.QLabel(env_text)
        env_info.setWordWrap(True)
        env_layout.addWidget(env_info)
        tabs.addTab(env_tab, "Environment")
        
        layout.addWidget(tabs)
        
        # View history button
        view_history = QtWidgets.QPushButton("View Run History")
        view_history.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_FileDialogDetailedView))
        view_history.clicked.connect(self._show_history_dialog)
        layout.addWidget(view_history)
        
        # Close button
        close_button = QtWidgets.QPushButton("Close")
        close_button.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_DialogCloseButton))
        close_button.clicked.connect(dialog.close)
        layout.addWidget(close_button)
        
        dialog.setLayout(layout)
        dialog.exec_()

    def _show_history_dialog(self):
        '''Show the run history in a separate dialog'''
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Run History")
        dialog.setModal(True)
        dialog.resize(800, 600)
        
        layout = QtWidgets.QVBoxLayout(dialog)
        splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        
        # Upper section - Run details
        history_text = QtWidgets.QTextEdit()
        history_text.setReadOnly(True)
        history_text.setFont(QtGui.QFont("Consolas", 10))
        
        # Lower section - Discussions
        discussions_text = QtWidgets.QTextEdit()
        discussions_text.setReadOnly(True)
        discussions_text.setFont(QtGui.QFont("Segoe UI", 10))
        discussions_text.setStyleSheet("background-color: #f8f8f8;")
        
        try:
            history_entries = self.run_manager.get_history_entries()
            
            # Format and display run history entries
            for entry in history_entries:
                formatted_entry = f"Timestamp: {entry['timestamp']}\nScript: {entry['script_path']}\n"
                if "discussions" in entry:
                    formatted_entry += f"Discussions:\n{entry['discussions']}\n"
                history_text.append(formatted_entry)
            
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
        
        splitter.addWidget(history_text)
        splitter.addWidget(discussions_text)
        
        layout.addWidget(splitter)
        
        close_button = QtWidgets.QPushButton("Close")
        close_button.clicked.connect(dialog.close)
        layout.addWidget(close_button)
        
        dialog.setLayout(layout)
        dialog.exec_()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
