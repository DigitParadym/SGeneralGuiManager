# ===================================================================
# FICHIER : copypaste_manager.py (Version Originale)
# Orchestrateur qui affiche les modules dans des groupes logiques
# et inclut une interface de selection pour les outils d'analyse.
# ===================================================================
import os
import sys
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import font as tkfont

print("--- TEST: JE LANCE BIEN LA VERSION MODIFIÉE DU FICHIER ---")

# --- Importation des classes d'interface integrables ---
try:
    from Folder.FolderCopypaste_interface import AdvancedCopypasteInterface
    from structure.file_structure_generator import StructureGeneratorInterface
    from Individual.copypaste_individual_manager import IndividualCopypasteInterface
    from run.run_interface_tk import RunInterface
    from import_mapper.analysis_interface import AnalysisToolsInterface
    from AST_tools.composants_browser.interface_gui_principale import InterfaceAST
    INTEGRATED_MODULES_AVAILABLE = True
except ImportError as e:
    print(f"WARNING: One or more interface modules could not be imported. {e}")
    # Classes factices pour eviter que le programme ne plante
    class AdvancedCopypasteInterface: 
        def __init__(self, parent): pass
    class StructureGeneratorInterface: 
        def __init__(self, parent): pass
    class IndividualCopypasteInterface: 
        def __init__(self, parent): pass
    class RunInterface: 
        def __init__(self, parent): pass
    class AnalysisToolsInterface: 
        def __init__(self, parent): pass
    class InterfaceAST: 
        def __init__(self, parent): pass
    INTEGRATED_MODULES_AVAILABLE = False


class SystemManager:
    """
    Gestionnaire de systeme qui integre dynamiquement des sous-applications
    base sur une configuration de groupes personnalises.
    """
    
    def __init__(self, root):
        self.root = root
        self.root.title("System Manager")
        
        self.processes = {}
        self.base_path = self._get_base_path()
        
        self.active_integrated_frame = None
        self.active_integrated_key = None
        
        self.original_geometry = "600x800"
        self.extended_geometry = "1400x750"

        # Configuration statique des groupes et des modules
        self.module_groups = {
            "Main Tools": [
                {'file': 'main.py', 'path': 'connectorpro', 'display': 'ConnectorPro'},
                {'file': 'run_interface_tk.py', 'path': 'run', 'display': 'Run Interface'}
            ],
            "File Management": [
                {'file': 'main_window.py', 'path': 'rename', 'display': 'Smart Rename System'},
                {'file': 'copypaste_individual_manager.py', 'path': 'Individual', 'display': 'Individual Manager'},
                {'file': 'FolderCopypaste_interface.py', 'path': 'Folder', 'display': 'Folder Manager'},
                {'file': 'file_structure_generator.py', 'path': 'structure', 'display': 'File Structure Generator'}
            ],
            "Outils D'analyse": [
                {'file': 'import_mapper.py', 'path': 'import_mapper', 'display': 'Analyseur de Dependances'},
                {'file': 'interface_gui_principale.py', 'path': 'AST_tools', 'display': 'Interface AST - Transformations'}
            ]
        }

        # On peuple 'discovered_modules' a partir de notre configuration statique
        self.discovered_modules = {}
        for group, modules in self.module_groups.items():
            for module_config in modules:
                module_key = os.path.join(module_config['path'], module_config['file'])
                
                is_integrated_file = any(module_config['file'].endswith(suffix) for suffix in ['_interface.py', '_manager.py', '_generator.py', '_interface_tk.py'])

                self.discovered_modules[module_key] = {
                    'path': os.path.join(self.base_path, module_key),
                    'display_name': module_config['display'],
                    'directory': module_config['path'],
                    'file': module_config['file'],
                    'is_integrated': is_integrated_file,
                    'class': self._get_class_for_file(module_config['file']) 
                }
        
        self.gui_elements = {}
        for module_key in self.discovered_modules.keys():
            self.gui_elements[module_key] = {'status': None, 'button': None}

        self.root.geometry(self.original_geometry)
        self._create_gui()
        self.root.after(1000, self._check_process_status)

    def _get_base_path(self):
        if getattr(sys, 'frozen', False):
            return sys._MEIPASS
        else:
            return os.path.dirname(os.path.abspath(__file__))

    def _get_class_for_file(self, filename):
        if not INTEGRATED_MODULES_AVAILABLE:
            return None
            
        mapping = {
            'run_interface_tk.py': RunInterface,
            'copypaste_individual_manager.py': IndividualCopypasteInterface,
            'FolderCopypaste_interface.py': AdvancedCopypasteInterface,
            'file_structure_generator.py': StructureGeneratorInterface,
            'interface_gui_principale.py': InterfaceAST
        }
        return mapping.get(filename)

    def _create_gui(self) -> None:
        self.main_pane = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_pane.pack(fill=tk.BOTH, expand=True)

        self.left_frame = ttk.Frame(self.main_pane, padding="10")
        self.main_pane.add(self.left_frame, weight=1)
        
        title = ttk.Label(self.left_frame, text="System Manager", font=('Segoe UI', 14, 'bold'))
        title.pack(pady=(0, 10), fill=tk.X)
        
        info_label = ttk.Label(self.left_frame, text=f"{len(self.discovered_modules)} modules found", font=('Segoe UI', 10))
        info_label.pack(pady=(0, 10), fill=tk.X)
        
        self._create_scrollable_modules(self.left_frame)
        
        self.status_label = ttk.Label(self.left_frame, text="All systems are ready", relief=tk.SUNKEN, anchor='w', padding=(5, 2))
        self.status_label.pack(fill=tk.X, pady=(10, 0), side=tk.BOTTOM)
        
        refresh_btn = ttk.Button(self.left_frame, text="Refresh Interface", command=self._refresh_modules)
        refresh_btn.pack(pady=(5, 0), side=tk.BOTTOM)

    def _create_scrollable_modules(self, container: ttk.Frame) -> None:
        canvas_container = ttk.Frame(container)
        canvas_container.pack(fill=tk.BOTH, expand=True)
        canvas = tk.Canvas(canvas_container)
        scrollbar = ttk.Scrollbar(canvas_container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        def configure_scrollable_frame(event):
            canvas.itemconfig(canvas_window, width=event.width)
        def configure_canvas(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        scrollable_frame.bind("<Configure>", configure_canvas)
        canvas.bind("<Configure>", configure_scrollable_frame)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        for group_name, modules_in_group in self.module_groups.items():
            section_frame = ttk.LabelFrame(scrollable_frame, text=group_name, padding="5")
            section_frame.pack(fill=tk.X, pady=5, padx=5, expand=True)

            if group_name == "Outils D'analyse":
                try:
                    analysis_interface = AnalysisToolsInterface(section_frame)
                    analysis_interface.pack(fill=tk.X, pady=(0, 10))
                    
                    ttk.Separator(section_frame, orient='horizontal').pack(fill='x', pady=5)
                except Exception as e:
                    print(f"Warning: Could not create AnalysisToolsInterface: {e}")

            for module_config in modules_in_group:
                module_key = os.path.join(module_config['path'], module_config['file'])
                self._create_module_frame(section_frame, module_key)

    def _create_module_frame(self, container, module_key):
        module_info = self.discovered_modules.get(module_key, {})
        display_name = module_info.get('display_name', 'Unknown')
        
        frame = ttk.Frame(container)
        frame.pack(fill=tk.X, expand=True, pady=4, padx=5)
        frame.columnconfigure(0, weight=1)

        text_frame = ttk.Frame(frame)
        text_frame.grid(row=0, column=0, sticky="w", padx=5)

        name_font = tkfont.Font(family="Segoe UI", size=10, weight="bold")
        name_label = ttk.Label(text_frame, text=display_name, font=name_font)
        name_label.pack(anchor="w")

        path_font = tkfont.Font(family="Segoe UI", size=8)
        path_label = ttk.Label(text_frame, text=module_key, font=path_font, foreground="gray")
        path_label.pack(anchor="w")

        status = ttk.Label(frame, text="Ready", width=10)
        status.grid(row=0, column=1, sticky="e", padx=5)
        self.gui_elements[module_key] = {'status': status}
        
        command = lambda mk=module_key: self._handle_launch(mk)
        button = ttk.Button(frame, text="Launch", command=command, width=10)
        button.grid(row=0, column=2, sticky="e", padx=5)
        self.gui_elements[module_key]['button'] = button

    def _handle_launch(self, module_key):
        if self.discovered_modules[module_key].get('is_integrated'):
            self._handle_integrated_launch(module_key)
        else:
            self.launch_external_module(module_key)

    def _handle_integrated_launch(self, module_key):
        is_already_open = self.active_integrated_frame is not None
        is_same_module = self.active_integrated_key == module_key

        if is_already_open:
            self._close_current_integrated_view()
            if is_same_module: return
        
        self._open_integrated_view(module_key)

    def _open_integrated_view(self, module_key):
        module_info = self.discovered_modules[module_key]
        InterfaceClass = module_info.get('class')
        
        if not InterfaceClass or not INTEGRATED_MODULES_AVAILABLE:
            messagebox.showerror("Error", "Interface class not found for this module.")
            return
            
        self.root.geometry(self.extended_geometry)
        self.active_integrated_frame = InterfaceClass(self.main_pane)
        self.main_pane.add(self.active_integrated_frame, weight=2)
        self.active_integrated_key = module_key
        self._update_status(module_key, "Running")
        self.gui_elements[module_key]['button'].config(text="Close")

    def _close_current_integrated_view(self):
        if self.active_integrated_frame:
            self.main_pane.forget(self.active_integrated_frame)
            self.active_integrated_frame.destroy()
            old_key = self.active_integrated_key
            
            if old_key and old_key in self.gui_elements:
                self._update_status(old_key, "Ready")
                self.gui_elements[old_key]['button'].config(text="Launch")
            
            self.active_integrated_frame = None
            self.active_integrated_key = None
            self.root.geometry(self.original_geometry)

    def launch_external_module(self, module_key):
        if self._is_module_running(module_key):
            messagebox.showinfo("Info", f"{self.discovered_modules[module_key]['display_name']} is already running")
            return
            
        try:
            module_info = self.discovered_modules[module_key]
            script_path = module_info['path']
            if not os.path.exists(script_path):
                messagebox.showerror("File Not Found", f"Script not found: {script_path}")
                return
            
            working_dir = os.path.dirname(script_path)
            env = os.environ.copy()
            env['PYTHONPATH'] = working_dir + os.pathsep + env.get('PYTHONPATH', '')
            
            creation_flags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            process = subprocess.Popen([sys.executable, script_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=creation_flags, cwd=working_dir, env=env, text=True, errors='ignore')
            
            self.processes[module_key] = process
            self._update_status(module_key, "Running")
            self.status_label.config(text=f"{module_info['display_name']} launched successfully")
        except Exception as e:
            self._handle_error(f"Failed to launch {module_info['display_name']}", e)

    def _is_module_running(self, module_key):
        if self.discovered_modules[module_key].get('is_integrated'):
            return self.active_integrated_frame is not None
        process = self.processes.get(module_key)
        return process is not None and process.poll() is None

    def _check_process_status(self):
        for module_key, process in list(self.processes.items()):
            if not self.discovered_modules[module_key].get('is_integrated'):
                if process is not None and process.poll() is not None:
                    self.processes[module_key] = None
                    self._update_status(module_key, "Ready")
        self.root.after(1000, self._check_process_status)

    def _update_status(self, module_key, status):
        if module_key in self.gui_elements and self.gui_elements[module_key].get('status'):
            status_colors = {'Ready': 'black', 'Running': 'green', 'Error': 'red'}
            self.gui_elements[module_key]['status'].config(text=status, foreground=status_colors.get(status, 'black'))
            
    def _refresh_modules(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.__init__(self.root)

    def _handle_error(self, message, error):
        error_detail = f"{message}: {str(error)}"
        messagebox.showerror("Error", error_detail)
        self.status_label.config(text=f"Error: {message}")
        print(f"ERROR: {error_detail}")

def main():
    root = tk.Tk()
    app = SystemManager(root)
    root.mainloop()

if __name__ == "__main__":
    main()