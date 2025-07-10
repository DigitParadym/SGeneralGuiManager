import os
import sys
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Dict

class SystemManager:
    """
    Complete system manager for launching all interfaces:
    - ConnectorPro
    - Rename Interface
    - Individual Manager
    - Folder Manager
    - Run Interface
    - File Structure Generator
    """
    
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("System Manager")
        self.root.geometry("500x550")
        
        # Track running processes
        self.processes: Dict[str, Optional[subprocess.Popen]] = {
            'individual': None,
            'folder': None,
            'connector': None,
            'rename': None,
            'run': None,
            'structure': None
        }

        # Define paths - Corrected for PyInstaller
        self.base_path = self._get_base_path()
        self.paths = {
            'individual': os.path.join(self.base_path, 'Individual', 'copypaste_individual_manager.py'),
            'folder': os.path.join(self.base_path, 'Folder', 'FolderCopypaste_interface.py'),
            'connector': os.path.join(self.base_path, 'connectorpro', 'main.py'),
            'rename': os.path.join(self.base_path, 'rename', 'main_window.py'),
            'run': os.path.join(self.base_path, 'run', 'gui70_main.py'),
            'structure': os.path.join(self.base_path, 'structure', 'file_structure_generator.py')
        }

        # Initialize GUI elements dictionary
        self.gui_elements = {
            'individual': {'status': None, 'button': None},
            'folder': {'status': None, 'button': None},
            'connector': {'status': None, 'button': None},
            'rename': {'status': None, 'button': None},
            'run': {'status': None, 'button': None},
            'structure': {'status': None, 'button': None}
        }

        # Setup and create GUI
        self._verify_setup()
        self._create_gui()
        
        # Setup periodic process status check
        self.root.after(1000, self._check_process_status)

    def _get_base_path(self) -> str:
        """Get the correct base path for both development and PyInstaller."""
        if getattr(sys, 'frozen', False):
            # Running as PyInstaller executable
            return sys._MEIPASS
        else:
            # Running as Python script
            return os.path.dirname(__file__)

    def _verify_setup(self) -> None:
        """Verify all required files exist and are accessible."""
        missing_files = []
        for manager, path in self.paths.items():
            if not os.path.exists(path):
                missing_files.append(f"{manager} interface: {path}")

        if missing_files:
            error_msg = "Missing required files:\n" + "\n".join(missing_files)
            messagebox.showerror("Setup Error", error_msg)
            # Don't exit, just show warning for PyInstaller compatibility
            print("Warning: Some files are missing but continuing...")

    def _create_gui(self) -> None:
        """Create the main GUI layout with improved styling and organization."""
        # Main container with padding
        container = ttk.Frame(self.root, padding="10")
        container.pack(fill=tk.BOTH, expand=True)

        # Title with improved styling
        title = ttk.Label(
            container, 
            text="System Manager", 
            font=('Segoe UI', 14, 'bold')
        )
        title.pack(pady=(0, 10))

        # Create manager sections
        self._create_sections(container)

        # Status bar with improved styling
        self.status_label = ttk.Label(
            container, 
            text="All systems ready", 
            relief=tk.SUNKEN, 
            anchor='w',
            padding=(5, 2)
        )
        self.status_label.pack(fill=tk.X, pady=(10, 0))

    def _create_sections(self, container: ttk.Frame) -> None:
        """Create organized sections for different types of tools."""
        # Main tools section
        main_tools = ttk.LabelFrame(container, text="Main Tools", padding="5")
        main_tools.pack(fill=tk.X, pady=5)
        
        main_managers = {
            'connector': 'ConnectorPro',
            'run': 'Run Interface'
        }
        for manager_type, display_name in main_managers.items():
            self._create_manager_frame(main_tools, manager_type, display_name)

        # File management tools section
        file_tools = ttk.LabelFrame(container, text="File Management", padding="5")
        file_tools.pack(fill=tk.X, pady=5)
        
        file_managers = {
            'rename': 'Rename Interface',
            'individual': 'Individual Manager',
            'folder': 'Folder Manager'
        }
        for manager_type, display_name in file_managers.items():
            self._create_manager_frame(file_tools, manager_type, display_name)

        # Utilities section
        utilities = ttk.LabelFrame(container, text="Utilities", padding="5")
        utilities.pack(fill=tk.X, pady=5)
        
        utilities_managers = {
            'structure': 'File Structure Generator'
        }
        for manager_type, display_name in utilities_managers.items():
            self._create_manager_frame(utilities, manager_type, display_name)

    def _create_manager_frame(self, container: ttk.Frame, manager_type: str, display_name: str) -> None:
        """Create a frame for a specific manager type."""
        frame = ttk.Frame(container, padding="5")
        frame.pack(fill=tk.X, pady=2)

        # Name label
        name_label = ttk.Label(frame, text=display_name, width=20)
        name_label.pack(side=tk.LEFT, padx=5)

        # Status label with style based on status
        status = ttk.Label(frame, text="Ready", width=15)
        status.pack(side=tk.LEFT, padx=5)
        self.gui_elements[manager_type]['status'] = status

        # Button frame for multiple buttons
        button_frame = ttk.Frame(frame)
        button_frame.pack(side=tk.RIGHT)

        # Launch button
        button = ttk.Button(
            button_frame, 
            text="Launch",
            command=lambda: self.launch_manager(manager_type),
            width=10
        )
        button.pack(side=tk.RIGHT, padx=2)
        self.gui_elements[manager_type]['button'] = button

    def launch_manager(self, manager_type: str) -> None:
        """Launch a specific manager type with improved process handling."""
        if not self._is_manager_running(manager_type):
            try:
                script_path = self.paths[manager_type]
                
                # Check if file exists before launching
                if not os.path.exists(script_path):
                    error_msg = f"Script not found: {script_path}"
                    messagebox.showerror("File Not Found", error_msg)
                    self.status_label.config(text=f"Error: {self._get_display_name(manager_type)} not found")
                    return

                working_dir = os.path.dirname(script_path)
                
                # Special handling for Run interface and Structure generator
                env = os.environ.copy()
                if manager_type in ['run', 'structure']:
                    env['PYTHONPATH'] = working_dir + os.pathsep + env.get('PYTHONPATH', '')
                
                # Use CREATE_NO_WINDOW only on Windows
                creation_flags = 0
                if os.name == 'nt':  # Windows
                    creation_flags = subprocess.CREATE_NO_WINDOW
                
                process = subprocess.Popen(
                    ['python', script_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    creationflags=creation_flags,
                    cwd=working_dir,
                    env=env
                )
                
                self.processes[manager_type] = process
                
                display_name = self._get_display_name(manager_type)
                self._update_status(manager_type, "Running")
                self.status_label.config(text=f"{display_name} launched successfully")
                
            except Exception as e:
                self._handle_error(f"Failed to launch {self._get_display_name(manager_type)}", e)
        else:
            messagebox.showinfo(
                "Info", 
                f"{self._get_display_name(manager_type)} is already running"
            )

    def _get_display_name(self, manager_type: str) -> str:
        """Get the display name for a manager type."""
        display_names = {
            'connector': 'ConnectorPro',
            'rename': 'Rename Interface',
            'individual': 'Individual Manager',
            'folder': 'Folder Manager',
            'run': 'Run Interface',
            'structure': 'File Structure Generator'
        }
        return display_names.get(manager_type, manager_type.title())

    def _is_manager_running(self, manager_type: str) -> bool:
        """Check if a specific manager is currently running."""
        process = self.processes[manager_type]
        return process is not None and process.poll() is None

    def _check_process_status(self) -> None:
        """Periodically check the status of running processes."""
        for manager_type, process in self.processes.items():
            if process is not None:
                if process.poll() is not None:
                    # Process has terminated
                    self.processes[manager_type] = None
                    self._update_status(manager_type, "Ready")
                else:
                    # Process is running
                    self._update_status(manager_type, "Running")

        # Schedule next check
        self.root.after(1000, self._check_process_status)

    def _update_status(self, manager_type: str, status: str) -> None:
        """Update the status display for a specific manager."""
        if self.gui_elements[manager_type]['status']:
            status_colors = {
                'Ready': 'black',
                'Running': 'green',
                'Error': 'red'
            }
            self.gui_elements[manager_type]['status'].config(
                text=status,
                foreground=status_colors.get(status, 'black')
            )

    def _handle_error(self, message: str, error: Exception) -> None:
        """Handle and display errors with improved error information."""
        error_detail = f"{message}: {str(error)}"
        messagebox.showerror("Error", error_detail)
        self.status_label.config(text=f"Error: {message}")
        print(f"Error occurred: {error_detail}")

def main():
    # Import sys here to avoid issues if not available
    import sys
    
    root = tk.Tk()
    root.minsize(500, 550)
    
    # Set window icon if available
    icon_path = os.path.join(os.path.dirname(__file__), 'assets', 'icon.ico')
    if os.path.exists(icon_path):
        try:
            root.iconbitmap(icon_path)
        except:
            pass  # Ignore icon errors
    
    app = SystemManager(root)
    root.mainloop()

if __name__ == "__main__":
    main()