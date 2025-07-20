# ==================================================
# Fichier : copypaste_manager.py (Version 2.14 - Amélioration du Browse)
# ==================================================
import os
import sys
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional, Dict

class SystemManager:
    """
    Gestionnaire de système complet avec détection récursive et affichage intelligent.
    - Découvre automatiquement tous les modules Python dans les sous-dossiers.
    - Permet de définir un dossier cible unique pour tous les outils d'analyse.
    - Mémorise le dernier dossier d'analyse sélectionné.
    """
    
    def __init__(self, root):
        self.root = root
        self.root.title("System Manager - V2.14")
        self.root.geometry("600x600")
        
        self.processes = {}
        self.base_path = self._get_base_path()
        
        # Variable pour le dossier cible de l'analyse
        self.analysis_target_folder = tk.StringVar()
        
        self.discovered_modules = self._discover_modules()
        
        for module_key in self.discovered_modules.keys():
            self.processes[module_key] = None

        self.gui_elements = {}
        for module_key in self.discovered_modules.keys():
            self.gui_elements[module_key] = {'status': None, 'button': None}

        self._create_gui()
        self.root.after(1000, self._check_process_status)

    def _get_base_path(self):
        """Obtient le chemin de base correct pour le développement et pour PyInstaller."""
        if getattr(sys, 'frozen', False):
            return sys._MEIPASS
        else:
            return os.path.dirname(__file__)

    def _discover_modules(self):
        """Découvre récursivement tous les modules Python lançables."""
        modules = {}
        main_files = [
            'main.py', 'gui_main.py', 'interface.py', 'main_window.py', 
            'gui70_main.py', 'run_app.py', 'copypaste_individual_manager.py',
            'FolderCopypaste_interface.py', 'file_structure_generator.py',
            'unzip_utility.py', 'PointerUnzipConnector.py'
        ]
        
        excluded_dirs = {
            '__pycache__', 'build', 'dist', 'node_modules', '.git', '.venv', 'venv', 
            'unicode_backup', 'assets', 'indexNavigator', 'SUnZip', 'pointer'
        }

        for root, dirs, files in os.walk(self.base_path):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in excluded_dirs]
            
            for main_file in main_files:
                if main_file in files:
                    full_path = os.path.join(root, main_file)
                    relative_path = os.path.relpath(root, self.base_path)
                    
                    module_key = f"{relative_path.replace(os.sep, '_')}_{main_file.replace('.py', '')}" if relative_path != '.' else main_file.replace('.py', '')
                    display_name = self._create_display_name(relative_path, main_file)
                    
                    modules[module_key] = {'path': full_path, 'display_name': display_name, 'directory': relative_path, 'file': main_file}
        
        return modules

    def _create_display_name(self, directory, filename):
        """Crée un nom d'affichage convivial pour un module."""
        special_names = {
            'main.py': 'Application Principale', 'gui_main.py': 'GUI Principale', 'interface.py': 'Interface',
            'main_window.py': 'Fenêtre Principale', 'gui70_main.py': 'GUI 70 Principale', 'run_app.py': 'Lancer Application',
            'copypaste_individual_manager.py': 'Gestionnaire Individuel', 'FolderCopypaste_interface.py': 'Gestionnaire de Dossier',
            'file_structure_generator.py': 'Générateur de Structure', 'unzip_utility.py': 'Utilitaire de Décompression',
            'srename_interface.py': 'Interface de Renommage', 'PointerUnzipConnector.py': 'Connecteur Pointeur Décompression'
        }
        
        base_name = special_names.get(filename, filename.replace('.py', '').replace('_', ' ').title())
        
        if directory == '.':
            return base_name
        else:
            dir_name = directory.replace(os.sep, ' > ').replace('_', ' ').title()
            return f"{dir_name} > {base_name}"

    def _create_gui(self) -> None:
        """Crée la disposition principale de l'interface graphique."""
        container = ttk.Frame(self.root, padding="10")
        container.pack(fill=tk.BOTH, expand=True)

        title = ttk.Label(container, text="System Manager", font=('Segoe UI', 14, 'bold'))
        title.pack(pady=(0, 10), fill=tk.X)

        info_label = ttk.Label(container, text=f"{len(self.discovered_modules)} modules découverts", font=('Segoe UI', 10))
        info_label.pack(pady=(0, 10), fill=tk.X)

        self._create_scrollable_modules(container)

        self.status_label = ttk.Label(container, text="Tous les systèmes sont prêts", relief=tk.SUNKEN, anchor='w', padding=(5, 2))
        self.status_label.pack(fill=tk.X, pady=(10, 0), side=tk.BOTTOM)

        refresh_btn = ttk.Button(container, text="Rafraîchir les Modules", command=self._refresh_modules)
        refresh_btn.pack(pady=(5, 0), side=tk.BOTTOM)

    def _create_scrollable_modules(self, container: ttk.Frame) -> None:
        """Crée une zone défilante pour l'affichage des modules."""
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

        grouped_modules = self._group_modules_by_directory()

        for directory_name, modules in grouped_modules.items():
            if len(modules) == 1 and directory_name != 'Répertoire Racine':
                module_key, module_info = list(modules.items())[0]
                simple_display_name = directory_name.replace(' > ', ' ').title()
                self._create_module_frame(scrollable_frame, module_key, simple_display_name)
            else:
                section_frame = ttk.LabelFrame(scrollable_frame, text=directory_name, padding="5")
                section_frame.pack(fill=tk.X, pady=5, padx=5, expand=True)
                for module_key, module_info in modules.items():
                    self._create_module_frame(section_frame, module_key, module_info['display_name'])
        
        analysis_tools_frame = ttk.LabelFrame(scrollable_frame, text="Outils d'Analyse", padding="5")
        analysis_tools_frame.pack(fill=tk.X, pady=5, padx=5, expand=True)
        self._create_analysis_tools(analysis_tools_frame)

    def _group_modules_by_directory(self):
        """Groupe les modules découverts par leur répertoire."""
        grouped = {}
        for module_key, module_info in self.discovered_modules.items():
            directory = module_info['directory']
            if directory == '.': directory = 'Répertoire Racine'
            else: directory = directory.replace(os.sep, ' > ').replace('_', ' ').title()
            if directory not in grouped: grouped[directory] = {}
            grouped[directory][module_key] = module_info
        return grouped

    def _create_module_frame(self, container, module_key, display_name):
        """Crée un cadre pour un module lançable spécifique."""
        frame = ttk.Frame(container)
        frame.pack(fill=tk.X, expand=True, pady=2, padx=5)
        frame.columnconfigure(0, weight=1)
        ttk.Label(frame, text=display_name).grid(row=0, column=0, sticky="w", padx=5)
        status = ttk.Label(frame, text="Prêt", width=10)
        status.grid(row=0, column=1, sticky="e", padx=5)
        self.gui_elements[module_key]['status'] = status
        ttk.Button(frame, text="Lancer", command=lambda: self.launch_module(module_key), width=10).grid(row=0, column=2, sticky="e", padx=5)

    def _create_analysis_tools(self, container):
        """Crée les contrôles pour la section d'analyse."""
        target_frame = ttk.Frame(container, padding="5")
        target_frame.pack(fill=tk.X, expand=True, pady=(5, 10))
        target_frame.columnconfigure(1, weight=1)
        
        ttk.Label(target_frame, text="Dossier Cible :").grid(row=0, column=0, sticky="w", padx=5)
        entry = ttk.Entry(target_frame, textvariable=self.analysis_target_folder, state="readonly")
        entry.grid(row=0, column=1, sticky="ew", padx=5)
        ttk.Button(target_frame, text="Parcourir...", command=self._browse_analysis_folder).grid(row=0, column=2, padx=5)

        dep_frame = ttk.Frame(container)
        dep_frame.pack(fill=tk.X, expand=True, pady=2, padx=5)
        dep_frame.columnconfigure(0, weight=1)
        ttk.Label(dep_frame, text="Analyseur de Dépendances").grid(row=0, column=0, sticky="w", padx=5)
        ttk.Label(dep_frame, text="Prêt", width=10).grid(row=0, column=1, sticky="e", padx=5)
        ttk.Button(dep_frame, text="Analyser", command=self.run_dependency_analysis, width=10).grid(row=0, column=2, sticky="e", padx=5)

    def _browse_analysis_folder(self):
        """Ouvre une boîte de dialogue pour sélectionner le dossier cible de l'analyse."""
        # --- MODIFIÉ : Mémorise le dernier dossier utilisé ---
        initial_dir = self.analysis_target_folder.get()
        if not initial_dir or not os.path.isdir(initial_dir):
            initial_dir = self.base_path
        
        folder = filedialog.askdirectory(
            title="Sélectionnez le dossier du projet à analyser",
            initialdir=initial_dir
        )
        if folder:
            self.analysis_target_folder.set(folder)
            self.status_label.config(text=f"Dossier cible pour l'analyse : {os.path.basename(folder)}")

    def run_dependency_analysis(self):
        """Lance l'analyseur de dépendances sur le dossier sélectionné."""
        target_folder = self.analysis_target_folder.get()
        if not target_folder:
            messagebox.showwarning("Aucun dossier sélectionné", "Veuillez d'abord sélectionner un dossier cible pour l'analyse.")
            return

        self.status_label.config(text=f"Analyse de '{os.path.basename(target_folder)}' en cours...")
        
        messagebox.showinfo("En Développement", 
                            f"L'analyse du dossier suivant serait lancée :\n\n{target_folder}\n\n"
                            "L'intégration complète est prévue pour la Phase 2.")
        
        self.status_label.config(text="Prêt.")
    
    def launch_module(self, module_key):
        if self._is_module_running(module_key): messagebox.showinfo("Info", f"{self.discovered_modules[module_key]['display_name']} est déjà en cours d'exécution"); return
        try:
            module_info = self.discovered_modules[module_key]
            script_path = module_info['path']
            if not os.path.exists(script_path): messagebox.showerror("Fichier non trouvé", f"Script non trouvé : {script_path}"); return
            working_dir = os.path.dirname(script_path)
            env = os.environ.copy()
            env['PYTHONPATH'] = working_dir + os.pathsep + env.get('PYTHONPATH', '')
            creation_flags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            process = subprocess.Popen(['python', script_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=creation_flags, cwd=working_dir, env=env, text=True, errors='ignore')
            self.processes[module_key] = process
            self._update_status(module_key, "En cours")
            self.status_label.config(text=f"{module_info['display_name']} lancé avec succès")
        except Exception as e: self._handle_error(f"Échec du lancement de {module_info['display_name']}", e)
    def _is_module_running(self, module_key):
        process = self.processes.get(module_key)
        return process is not None and process.poll() is None
    def _check_process_status(self):
        for module_key, process in list(self.processes.items()):
            if process is not None and process.poll() is not None:
                self.processes[module_key] = None
                self._update_status(module_key, "Prêt")
        self.root.after(1000, self._check_process_status)
    def _update_status(self, module_key, status):
        if module_key in self.gui_elements and self.gui_elements[module_key].get('status'):
            status_colors = {'Prêt': 'black', 'En cours': 'green', 'Erreur': 'red'}
            self.gui_elements[module_key]['status'].config(text=status, foreground=status_colors.get(status, 'black'))
    def _refresh_modules(self):
        for widget in self.root.winfo_children(): widget.destroy()
        self.__init__(self.root)
    def _handle_error(self, message, error):
        error_detail = f"{message}: {str(error)}"
        messagebox.showerror("Erreur", error_detail)
        self.status_label.config(text=f"Erreur : {message}")
        print(f"Erreur survenue : {error_detail}")

def main():
    root = tk.Tk()
    root.minsize(600, 550)
    app = SystemManager(root)
    root.mainloop()

if __name__ == "__main__":
    main()
