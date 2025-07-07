
from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        
        # Create main layout
        self.main_layout = QtWidgets.QVBoxLayout(self.centralwidget)
        
        # Create scroll area
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QtWidgets.QWidget()
        scroll_layout = QtWidgets.QVBoxLayout(scroll_content)
        
        # Script selection group
        self.script_group = QtWidgets.QGroupBox("Script Selection")
        script_layout = QtWidgets.QHBoxLayout()
        
        self.script_path = QtWidgets.QLineEdit()
        self.script_path.setPlaceholderText("Select Python script to run...")
        script_layout.addWidget(self.script_path)
        
        self.browse_script = QtWidgets.QPushButton("Browse")
        script_layout.addWidget(self.browse_script)
        
        self.script_group.setLayout(script_layout)
        scroll_layout.addWidget(self.script_group)
        
        # Script arguments
        self.args_group = QtWidgets.QGroupBox("Script Arguments")
        args_layout = QtWidgets.QVBoxLayout()
        self.script_args = QtWidgets.QLineEdit()
        self.script_args.setPlaceholderText("Enter script arguments (optional)...")
        args_layout.addWidget(self.script_args)
        self.args_group.setLayout(args_layout)
        scroll_layout.addWidget(self.args_group)
        
        # Options group
        self.options_group = QtWidgets.QGroupBox("Options")
        options_layout = QtWidgets.QVBoxLayout()
        
        # Virtual environment checkbox
        self.use_venv = QtWidgets.QCheckBox("Use Virtual Environment")
        options_layout.addWidget(self.use_venv)
        
        # Include content checkbox
        self.include_content = QtWidgets.QCheckBox("Include Script Content in History")
        self.include_content.setChecked(True)
        options_layout.addWidget(self.include_content)
        
        # History file section
        history_layout = QtWidgets.QGridLayout()
        
        self.history_label = QtWidgets.QLabel("History File:")
        self.history_file_name = QtWidgets.QLineEdit()
        self.history_file_name.setPlaceholderText("Enter history file name and press Enter")
        self.history_file_name.setClearButtonEnabled(True)
        self.history_file_name.setToolTip("Enter file name and press Enter to create/switch history file")
        
        self.select_history = QtWidgets.QPushButton("Select History File")
        self.current_history_label = QtWidgets.QLabel()
        self.current_history_label.setStyleSheet("color: gray; font-size: 10px; padding: 2px; font-style: italic;")
        
        history_layout.addWidget(self.history_label, 0, 0)
        history_layout.addWidget(self.history_file_name, 0, 1)
        history_layout.addWidget(self.select_history, 0, 2)
        history_layout.addWidget(self.current_history_label, 1, 0, 1, 3)
        
        options_layout.addLayout(history_layout)
        self.options_group.setLayout(options_layout)
        scroll_layout.addWidget(self.options_group)
        
        # Modular files section with reset
        self.modular_section = QtWidgets.QGroupBox("Modular Files")
        self.modular_section.setCheckable(True)
        self.modular_section.setChecked(False)
        modular_layout = QtWidgets.QVBoxLayout()
        
        # Add control buttons layout
        modular_controls = QtWidgets.QHBoxLayout()
        
        # Add files button
        self.add_files_btn = QtWidgets.QPushButton("Add Files")
        modular_controls.addWidget(self.add_files_btn)
        
        # Reset button for modular files
        self.reset_modular = QtWidgets.QPushButton("Reset Files")
        modular_controls.addWidget(self.reset_modular)
        
        modular_layout.addLayout(modular_controls)
        
        # File list
        self.modular_files = QtWidgets.QListWidget()
        modular_layout.addWidget(self.modular_files)
        
        self.modular_section.setLayout(modular_layout)
        scroll_layout.addWidget(self.modular_section)
        
        # Discussion section with reset
        self.discussion_group = QtWidgets.QGroupBox("Discussions & Plans")
        discussion_layout = QtWidgets.QVBoxLayout()
        
        description_label = QtWidgets.QLabel("Document your plans, discussions, and notes for THIS run:")
        description_label.setWordWrap(True)
        discussion_layout.addWidget(description_label)
        
        self.discussion_text = QtWidgets.QTextEdit()
        self.discussion_text.setPlaceholderText("Enter discussions and plans for the current run...")
        self.discussion_text.setMinimumHeight(100)
        discussion_layout.addWidget(self.discussion_text)
        
        discussion_controls = QtWidgets.QHBoxLayout()
        
        run_info = QtWidgets.QLabel("Notes will be saved with this run only")
        run_info.setStyleSheet("color: gray; font-style: italic;")
        discussion_controls.addWidget(run_info)
        
        discussion_controls.addStretch()
        
        # Clear button for discussions
        self.clear_discussion = QtWidgets.QPushButton("Clear")
        discussion_controls.addWidget(self.clear_discussion)
        
        discussion_layout.addLayout(discussion_controls)
        self.discussion_group.setLayout(discussion_layout)
        scroll_layout.addWidget(self.discussion_group)
        
        # Action buttons
        buttons_layout = QtWidgets.QHBoxLayout()
        
        self.run_script = QtWidgets.QPushButton("Run Script")
        self.run_script.setEnabled(False)
        buttons_layout.addWidget(self.run_script)
        
        self.copy_history = QtWidgets.QPushButton("Copy History")
        buttons_layout.addWidget(self.copy_history)
        
        self.troubleshoot_button = QtWidgets.QPushButton("Troubleshoot")
        buttons_layout.addWidget(self.troubleshoot_button)
        
        scroll_layout.addLayout(buttons_layout)
        
        # Output area
        self.output_group = QtWidgets.QGroupBox("Output")
        output_layout = QtWidgets.QVBoxLayout()
        
        self.run_output = QtWidgets.QTextEdit()
        self.run_output.setReadOnly(True)
        output_layout.addWidget(self.run_output)
        
        self.status_label = QtWidgets.QLabel("Ready")
        output_layout.addWidget(self.status_label)
        
        self.output_group.setLayout(output_layout)
        scroll_layout.addWidget(self.output_group)
        
        scroll.setWidget(scroll_content)
        self.main_layout.addWidget(scroll)
        MainWindow.setCentralWidget(self.centralwidget)
        MainWindow.setWindowTitle("Script Runner")
        
        MainWindow.setMinimumSize(600, 400)
