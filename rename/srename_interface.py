from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    """Main window UI class for the Smart Rename System"""
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("SmartRenameSystem")
        MainWindow.resize(1200, 800)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        
        # Main layout
        self.main_layout = QtWidgets.QVBoxLayout(self.centralwidget)
        
        # Title Label with reduced space
        self.title_label = QtWidgets.QLabel("Smart Rename System")
        self.title_label.setStyleSheet("""
            font-size: 14pt;
            font-weight: bold;
            margin: 5px;
            padding: 5px;
        """)
        self.title_label.setAlignment(QtCore.Qt.AlignCenter)
        self.main_layout.addWidget(self.title_label)
        
        # Naming Interface
        self.naming_group = QtWidgets.QGroupBox("File Management")
        self.naming_group.setStyleSheet("""
            QGroupBox {
                font-size: 14pt;
                font-weight: bold;
                padding: 15px;
            }
        """)
        self.naming_layout = QtWidgets.QVBoxLayout(self.naming_group)
        
        # Header row
        header_layout = QtWidgets.QHBoxLayout()
        header_style = "font-weight: bold; color: #2c3e50; font-size: 12pt;"
        
        root_name_label = QtWidgets.QLabel("Root Name")
        root_name_label.setStyleSheet(header_style)
        file_path_label = QtWidgets.QLabel("File Path")
        file_path_label.setStyleSheet(header_style)
        actions_label = QtWidgets.QLabel("Actions")
        actions_label.setStyleSheet(header_style)
        
        header_layout.addWidget(root_name_label, 2)
        header_layout.addWidget(file_path_label, 3)
        header_layout.addWidget(actions_label, 1)
        self.naming_layout.addLayout(header_layout)
        
        # Separator line
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.naming_layout.addWidget(line)
        
        # File input rows (8 slots)
        for i in range(1, 9):
            file_layout = QtWidgets.QHBoxLayout()
            
            # Root name input
            new_name_input = QtWidgets.QLineEdit()
            new_name_input.setObjectName(f"new_name_input{i}")
            new_name_input.setPlaceholderText(f"Enter root name for file {i}")
            new_name_input.setStyleSheet("""
                QLineEdit {
                    padding: 5px;
                    border: 1px solid #bdc3c7;
                    border-radius: 3px;
                    font-size: 11pt;
                }
                QLineEdit:focus {
                    border: 1px solid #3498db;
                }
            """)
            file_layout.addWidget(new_name_input, 2)
            setattr(self, f'new_name_input{i}', new_name_input)
            
            # File path input
            rename_input = QtWidgets.QLineEdit()
            rename_input.setObjectName(f"rename_input{i}")
            rename_input.setReadOnly(True)
            rename_input.setPlaceholderText("File path will appear here")
            rename_input.setStyleSheet("""
                QLineEdit {
                    padding: 5px;
                    border: 1px solid #bdc3c7;
                    border-radius: 3px;
                    background-color: #f5f6fa;
                    font-size: 11pt;
                }
            """)
            file_layout.addWidget(rename_input, 3)
            setattr(self, f'rename_input{i}', rename_input)
            
            # Button container
            button_layout = QtWidgets.QHBoxLayout()
            
            # Browse button
            browse_btn = QtWidgets.QPushButton("Browse")
            browse_btn.setObjectName(f"rename_browse{i}")
            browse_btn.setStyleSheet("""
                QPushButton {
                    padding: 5px 15px;
                    background-color: #3498db;
                    color: white;
                    border-radius: 3px;
                    border: none;
                    font-size: 11pt;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            button_layout.addWidget(browse_btn)
            setattr(self, f'rename_browse{i}', browse_btn)
            
            # Rename button
            rename_btn = QtWidgets.QPushButton("Rename")
            rename_btn.setObjectName(f"rename_file{i}")
            rename_btn.setStyleSheet("""
                QPushButton {
                    padding: 5px 15px;
                    background-color: #2ecc71;
                    color: white;
                    border-radius: 3px;
                    border: none;
                    font-size: 11pt;
                }
                QPushButton:hover {
                    background-color: #27ae60;
                }
            """)
            button_layout.addWidget(rename_btn)
            setattr(self, f'rename_file{i}', rename_btn)
            
            file_layout.addLayout(button_layout, 1)
            self.naming_layout.addLayout(file_layout)
        
        # Add spacing before run button
        self.naming_layout.addSpacing(20)
        
        # Run Script button
        self.run_script_button = QtWidgets.QPushButton("Run Script (File 1)")
        self.run_script_button.setMinimumWidth(200)
        self.run_script_button.setStyleSheet("""
            QPushButton {
                padding: 8px 20px;
                background-color: #9b59b6;
                color: white;
                border-radius: 3px;
                border: none;
                font-weight: bold;
                font-size: 12pt;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #95a5a6;
            }
        """)
        self.naming_layout.addWidget(self.run_script_button, alignment=QtCore.Qt.AlignCenter)
        
        # Add spacing between run and reset buttons
        self.naming_layout.addSpacing(10)
        
        # Reset button
        self.reset_button = QtWidgets.QPushButton("Reset Root Names")
        self.reset_button.setMinimumWidth(150)
        self.reset_button.setStyleSheet("""
            QPushButton {
                padding: 8px 20px;
                background-color: #e74c3c;
                color: white;
                border-radius: 3px;
                border: none;
                font-weight: bold;
                font-size: 12pt;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        self.naming_layout.addWidget(self.reset_button, alignment=QtCore.Qt.AlignCenter)
        
        # Status label
        self.status_label = QtWidgets.QLabel()
        self.status_label.setStyleSheet("""
            QLabel {
                padding: 10px;
                margin-top: 10px;
                border-radius: 3px;
                font-size: 12pt;
            }
        """)
        self.status_label.setAlignment(QtCore.Qt.AlignCenter)
        self.naming_layout.addWidget(self.status_label)
        
        # Add the naming group to main layout
        self.main_layout.addWidget(self.naming_group)
        
        # Set central widget
        MainWindow.setCentralWidget(self.centralwidget)
        MainWindow.setWindowTitle("Smart Rename System")
