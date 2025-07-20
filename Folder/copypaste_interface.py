import os
import sys
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Dict, List, Tuple

class SystemManager:
    """
    Complete system manager for launching all interfaces with recursive module detection:
    - Automatically discovers all Python modules in subdirectories
    - Launches interfaces dynamically
    - Monitors process status
    """
    
    def __init__(self, root):
        self.root = root
        self.root.title("System Manager - Recursive")
        self.root.geometry("600x700")
        
        # Track running processes
        self.processes = {}
        
        # Define paths - Corrected for PyInstaller
        self.base_path = self._get_base_path()
        
        # Discover all available modules recursively
        self.discovered_modules = self._discover_modules()
        
        # Initialize processes dict for discovered modules
        for module_key in self.discovered_modules.keys():
            self.processes[module_key] = None

        # Initialize GUI elements dictionary
        self.gui_elements = {}
        for module_key in self.discovered_modules.keys():
            self.gui_elements[module_key] = {'status': None, 'button': None}

        # Setup and create GUI
        self._create_gui()
        
        # Setup periodic process status check
        self.root.after(1000, self._check_process_status)

    def _get_base_path(self):
        """Get the correct base path for both development and PyInstaller."""
        if getattr(sys, 'frozen', False):
            # Running as PyInstaller executable
            return sys._MEIPASS
        else:
            # Running as Python script
            return os.path.dirname(__file__)

    def _discover_modules(self):
        """Recursively discover all launchable Python modules."""
        modules = {}
        
        # Known main files to look for in each directory
        main_files = [
            'main.py',
            'gui_main.py', 
            'interface.py',
            'main_window.py',
            'gui70_main.py',
            'run_app.py',
            'copypaste_individual_manager.py',
            'FolderCopypaste_interface.py',
            'file_structure_generator.py',
            'unzip_utility.py',
            'srename_interface.py',
            'PointerUnzipConnector.py'
        ]
        
        # Walk through all subdirectories
        for root, dirs, files in os.walk(self.base_path):
            # Skip hidden directories and build directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'build', 'dist', 'node_modules']]
            
            # Look for main files
            for main_file in main_files:
                if main_file in files:
                    full_path = os.path.join(root, main_file)
                    relative_path = os.path.relpath(root, self.base_path)
                    
                    # Create a unique key for this module
                    if relative_path == '.':
                        module_key = main_file.replace('.py', '')
                    else:
                        module_key = f"{relative_path.replace(os.sep, '_')}_{main_file.replace('.py', '')}"
                    
                    # Create display name
                    display_name = self._create_display_name(relative_path, main_file)
                    
                    modules[module_key] = {
                        'path': full_path,
                        'display_name': display_name,
                        'directory': relative_path,
                        'file': main_file
                    }
        
        return modules

    def _create_display_name(self, directory, filename):
        """Create a user-friendly display name for a module."""
        # Special cases for known modules
        special_names = {
            'main.py': 'Main Application',
            'gui_main.py': 'GUI Main',
            'interface.py': 'Interface',
            'main_window.py': 'Main Window',
            'gui70_main.py': 'GUI 70 Main',
            'run_app.py': 'Run Application',
            'copypaste_individual_manager.py': 'Individual Manager',
            'FolderCopypaste_interface.py': 'Folder Manager',
            'file_structure_generator.py': 'Structure Generator',
            'unzip_utility.py': 'Unzip Utility',
            'srename_interface.py': 'Rename Interface',
            'PointerUnzipConnector.py': 'Pointer Unzip Connector'
        }
        
        base_name = special_names.get(filename, filename.replace('.py', '').replace('_', ' ').title())
        
        if directory == '.':
            return base_name
        else:
            dir_name = directory.replace(os.sep, ' > ').replace('_', ' ').title()
            return f"{dir_name} > {base_name}"

    def _create_gui(self) -> None:
        """Create the main GUI layout with improved styling and organization."""
        # Main container with padding
        container = ttk.Frame(self.root, padding="10")
        container.pack(fill=tk.BOTH, expand=True)

        # Title with improved styling
        title = ttk.Label(
            container, 
            text="System Manager - Recursive Discovery", 
            font=('Segoe UI', 14, 'bold')
        )
        title.pack(pady=(0, 10))

        # Module count info
        info_label = ttk.Label(
            container,
            text=f"Discovered {len(self.discovered_modules)} modules",
            font=('Segoe UI', 10)
        )
        info_label.pack(pady=(0, 10))

        # Create scrollable frame for modules
        self._create_scrollable_modules(container)

        # Status bar with improved styling
        self.status_label = ttk.Label(
            container, 
            text="All systems ready", 
            relief=tk.SUNKEN, 
            anchor='w',
            padding=(5, 2)
        )
        self.status_label.pack(fill=tk.X, pady=(10, 0))

        # Refresh button
        refresh_btn = ttk.Button(
            container,
            text="Refresh Modules",
            command=self._refresh_modules
        )
        refresh_btn.pack(pady=(5, 0))

    def _create_scrollable_modules(self, container: ttk.Frame) -> None:
        """Create a scrollable area for module display."""
        # Create canvas and scrollbar
        canvas = tk.Canvas(container, height=400)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Group modules by directory
        grouped_modules = self._group_modules_by_directory()

        # Create sections for each directory
        for directory, modules in grouped_modules.items():
            section_frame = ttk.LabelFrame(scrollable_frame, text=directory, padding="5")
            section_frame.pack(fill=tk.X, pady=5, padx=5)

            for module_key, module_info in modules.items():
                self._create_module_frame(section_frame, module_key, module_info['display_name'])

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _group_modules_by_directory(self):
        """Group discovered modules by their directory."""
        grouped = {}
        
        for module_key, module_info in self.discovered_modules.items():
            directory = module_info['directory']
            if directory == '.':
                directory = 'Root Directory'
            else:
                directory = directory.replace(os.sep, ' > ').replace('_', ' ').title()
            
            if directory not in grouped:
                grouped[directory] = {}
            
            grouped[directory][module_key] = module_info
        
        return grouped

    def _create_module_frame(self, container, module_key, display_name):
        """Create a frame for a specific module."""
        frame = ttk.Frame(container, padding="5")
        frame.pack(fill=tk.X, pady=2)

        # Name label
        name_label = ttk.Label(frame, text=display_name, width=40)
        name_label.pack(side=tk.LEFT, padx=5)

        # Status label
        status = ttk.Label(frame, text="Ready", width=15)
        status.pack(side=tk.LEFT, padx=5)
        self.gui_elements[module_key]['status'] = status

        # Button frame
        button_frame = ttk.Frame(frame)
        button_frame.pack(side=tk.RIGHT)

        # Launch button
        button = ttk.Button(
            button_frame, 
            text="Launch",
            command=lambda: self.launch_module(module_key),
            width=10
        )
        button.pack(side=tk.RIGHT, padx=2)
        self.gui_elements[module_key]['button'] = button

    def launch_module(self, module_key):
        """Launch a specific module with improved process handling."""
        if not self._is_module_running(module_key):
            try:
                module_info = self.discovered_modules[module_key]
                script_path = module_info['path']
                
                # Check if file exists before launching
                if not os.path.exists(script_path):
                    error_msg = f"Script not found: {script_path}"
                    messagebox.showerror("File Not Found", error_msg)
                    self.status_label.config(text=f"Error: {module_info['display_name']} not found")
                    return

                working_dir = os.path.dirname(script_path)
                
                # Set up environment
                env = os.environ.copy()
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
                
                self.processes[module_key] = process
                
                self._update_status(module_key, "Running")
                self.status_label.config(text=f"{module_info['display_name']} launched successfully")
                
            except Exception as e:
                self._handle_error(f"Failed to launch {module_info['display_name']}", e)
        else:
            messagebox.showinfo(
                "Info", 
                f"{self.discovered_modules[module_key]['display_name']} is already running"
            )

    def _is_module_running(self, module_key):
        """Check if a specific module is currently running."""
        process = self.processes.get(module_key)
        return process is not None and process.poll() is None

    def _check_process_status(self):
        """Periodically check the status of running processes."""
        for module_key, process in self.processes.items():
            if process is not None:
                if process.poll() is not None:
                    # Process has terminated
                    self.processes[module_key] = None
                    self._update_status(module_key, "Ready")
                else:
                    # Process is running
                    self._update_status(module_key, "Running")

        # Schedule next check
        self.root.after(1000, self._check_process_status)

    def _update_status(self, module_key, status):
        """Update the status display for a specific module."""
        if module_key in self.gui_elements and self.gui_elements[module_key]['status']:
            status_colors = {
                'Ready': 'black',
                'Running': 'green',
                'Error': 'red'
            }
            self.gui_elements[module_key]['status'].config(
                text=status,
                foreground=status_colors.get(status, 'black')
            )

    def _refresh_modules(self):
        """Refresh the module discovery and update GUI."""
        # Clear existing GUI elements
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Rediscover modules
        self.discovered_modules = self._discover_modules()
        
        # Reset processes and GUI elements
        self.processes = {}
        self.gui_elements = {}
        for module_key in self.discovered_modules.keys():
            self.processes[module_key] = None
            self.gui_elements[module_key] = {'status': None, 'button': None}
        
        # Recreate GUI
        self._create_gui()
        
        self.status_label.config(text=f"Refreshed - Found {len(self.discovered_modules)} modules")

    def _handle_error(self, message, error):
        """Handle and display errors with improved error information."""
        error_detail = f"{message}: {str(error)}"
        messagebox.showerror("Error", error_detail)
        self.status_label.config(text=f"Error: {message}")
        print(f"Error occurred: {error_detail}")

def main():
    root = tk.Tk()
    root.minsize(600, 700)
    
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