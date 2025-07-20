# ==================================================
# Fichier : run/run_interface_tk.py (Version 2.4 - Correction de l'affichage)
# ==================================================
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import os
import sys
import subprocess
import threading
import json
from datetime import datetime

class RunInterface(ttk.Frame):
    """
    Une interface Tkinter complète pour lancer des scripts, gérer l'historique,
    les arguments, les fichiers modulaires et les discussions.
    """
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        
        # --- Variables d'état ---
        self.script_path = tk.StringVar()
        self.script_args = tk.StringVar()
        self.use_venv = tk.BooleanVar(value=False)
        self.include_content = tk.BooleanVar(value=True)
        self.process = None
        
        self.history_file_path = tk.StringVar()
        self._initialize_history_path()

        self.setup_gui()

    def _initialize_history_path(self):
        """Définit le chemin par défaut pour le fichier d'historique."""
        default_dir = os.path.join(os.path.dirname(__file__), '.srun')
        os.makedirs(default_dir, exist_ok=True)
        self.history_file_path.set(os.path.join(default_dir, 'run_history.log'))

    def setup_gui(self):
        mainframe = ttk.Frame(self, padding="10")
        mainframe.pack(fill=tk.BOTH, expand=True)

        # --- Cadre principal pour les options (défilable) ---
        canvas = tk.Canvas(mainframe)
        scrollbar = ttk.Scrollbar(mainframe, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        def configure_scrollable_frame(event):
            canvas.itemconfig(canvas_window, width=event.width)
        
        canvas.bind("<Configure>", configure_scrollable_frame)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # --- Section 1: Script et Arguments ---
        script_frame = ttk.LabelFrame(scrollable_frame, text="Script Selection", padding="10")
        script_frame.pack(fill=tk.X, padx=5, pady=5, expand=True)
        
        # --- MODIFIÉ : Utilisation de .grid pour un meilleur contrôle ---
        script_frame.columnconfigure(0, weight=1) # Permet à la colonne 0 (Entry) de s'étendre

        entry = ttk.Entry(script_frame, textvariable=self.script_path)
        entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        browse_btn = ttk.Button(script_frame, text="Browse...", command=self.browse_script)
        browse_btn.grid(row=0, column=1, sticky="e")
        # --- FIN DE LA MODIFICATION ---

        args_frame = ttk.LabelFrame(scrollable_frame, text="Script Arguments", padding="10")
        args_frame.pack(fill=tk.X, padx=5, pady=5, expand=True)
        ttk.Entry(args_frame, textvariable=self.script_args).pack(fill=tk.X, expand=True)

        # --- Section 2: Options ---
        options_frame = ttk.LabelFrame(scrollable_frame, text="Options", padding="10")
        options_frame.pack(fill=tk.X, padx=5, pady=5, expand=True)
        ttk.Checkbutton(options_frame, text="Use Virtual Environment", variable=self.use_venv).pack(anchor=tk.W)
        ttk.Checkbutton(options_frame, text="Include Script Content in History", variable=self.include_content).pack(anchor=tk.W)
        
        history_frame = ttk.Frame(options_frame)
        history_frame.pack(fill=tk.X, pady=5)
        ttk.Label(history_frame, text="History File:").pack(side=tk.LEFT, padx=(0, 5))
        history_entry = ttk.Entry(history_frame, textvariable=self.history_file_path, width=50)
        history_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(history_frame, text="Select History File", command=self.select_history_file).pack(side=tk.LEFT, padx=5)


        # --- Section 3: Fichiers Modulaires ---
        modular_frame = ttk.LabelFrame(scrollable_frame, text="Modular Files", padding="10")
        modular_frame.pack(fill=tk.X, padx=5, pady=5, expand=True)
        
        modular_controls = ttk.Frame(modular_frame)
        modular_controls.pack(fill=tk.X)
        ttk.Button(modular_controls, text="Add Files", command=self.add_modular_files).pack(side=tk.LEFT)
        ttk.Button(modular_controls, text="Reset Files", command=self.reset_modular_files).pack(side=tk.LEFT, padx=5)
        
        self.modular_listbox = tk.Listbox(modular_frame, height=4)
        self.modular_listbox.pack(fill=tk.X, expand=True, pady=5)

        # --- Section 4: Discussions ---
        discussion_frame = ttk.LabelFrame(scrollable_frame, text="Discussions & Plans", padding="10")
        discussion_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.discussion_text = scrolledtext.ScrolledText(discussion_frame, height=5, wrap=tk.WORD, font=("Segoe UI", 9))
        self.discussion_text.pack(fill=tk.BOTH, expand=True)

        # --- Section 5: Sortie ---
        output_frame = ttk.LabelFrame(mainframe, text="Script Output", padding="10")
        output_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5, side=tk.BOTTOM)
        
        self.output_text = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD, font=("Courier New", 9), height=10)
        self.output_text.pack(fill=tk.BOTH, expand=True)
        self.output_text.config(state='disabled')

        # --- Section 6: Boutons d'action ---
        button_frame = ttk.Frame(mainframe, padding="10 0 0 0")
        button_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.run_button = ttk.Button(button_frame, text="Run Script", command=self.run_script)
        self.run_button.pack(side=tk.LEFT)
        
        self.stop_button = ttk.Button(button_frame, text="Stop Script", command=self.stop_script, state='disabled')
        self.stop_button.pack(side=tk.LEFT, padx=10)

    def browse_script(self):
        filepath = filedialog.askopenfilename(title="Select Python Script", filetypes=[("Python Files", "*.py"), ("All Files", "*.*")])
        if filepath:
            self.script_path.set(filepath)

    def select_history_file(self):
        """Permet à l'utilisateur de sélectionner ou de créer un fichier d'historique."""
        filepath = filedialog.asksaveasfilename(
            title="Select or Create History File",
            initialdir=os.path.dirname(self.history_file_path.get()),
            initialfile="run_history.log",
            defaultextension=".log",
            filetypes=[("Log Files", "*.log"), ("All Files", "*.*")]
        )
        if filepath:
            self.history_file_path.set(filepath)

    def add_modular_files(self):
        filepaths = filedialog.askopenfilenames(title="Select Modular Files")
        for fp in filepaths:
            self.modular_listbox.insert(tk.END, fp)

    def reset_modular_files(self):
        self.modular_listbox.delete(0, tk.END)

    def run_script(self):
        script = self.script_path.get()
        if not script or not os.path.exists(script):
            messagebox.showerror("Error", "Please select a valid script to run.")
            return

        self.output_text.config(state='normal')
        self.output_text.delete(1.0, tk.END)
        self.run_button.config(state='disabled')
        self.stop_button.config(state='normal')

        thread = threading.Thread(target=self._execute_in_thread, args=(script,), daemon=True)
        thread.start()

    def _execute_in_thread(self, script):
        """Méthode exécutée dans un thread pour gérer le sous-processus."""
        try:
            command = [sys.executable, script] + self.script_args.get().split()
            
            working_directory = os.path.dirname(script)
            
            self.process = subprocess.Popen(
                command, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT,
                text=True, 
                encoding='utf-8', 
                errors='replace', 
                bufsize=1,
                cwd=working_directory,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            for line in iter(self.process.stdout.readline, ''):
                self.output_text.insert(tk.END, line)
                self.output_text.see(tk.END)
            
            self.process.wait()
            self._save_to_history(script, self.process.returncode)

        except Exception as e:
            self.output_text.insert(tk.END, f"\n--- ERROR LAUNCHING SCRIPT ---\n{e}\n")
        finally:
            self.process = None
            self.run_button.config(state='normal')
            self.stop_button.config(state='disabled')
            self.output_text.config(state='disabled')

    def stop_script(self):
        if self.process:
            self.process.terminate()
            self.output_text.insert(tk.END, "\n--- SCRIPT TERMINATED BY USER ---\n")

    def _save_to_history(self, script, returncode):
        """Sauvegarde une entrée dans le fichier d'historique, en incluant le contenu du script si demandé."""
        history_file = self.history_file_path.get()
        if not history_file:
            print("History file path is not set. Cannot save history.")
            return
            
        try:
            entry = {
                "timestamp": datetime.now().isoformat(),
                "script_path": script,
                "returncode": returncode,
                "discussions": self.discussion_text.get(1.0, tk.END).strip()
            }
            
            if self.include_content.get():
                try:
                    with open(script, 'r', encoding='utf-8', errors='ignore') as f:
                        entry["script_content"] = f.read()
                except Exception as e:
                    entry["script_content_error"] = f"Error reading script: {str(e)}"
            
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                data = {"entries": []}
            
            data["entries"].append(entry)
            
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            print(f"Failed to save to history: {e}")

# Pour permettre de tester ce module seul si nécessaire
if __name__ == '__main__':
    root = tk.Tk()
    root.title("Run Interface Test")
    root.geometry("800x800")
    
    app = RunInterface(root)
    app.pack(fill="both", expand=True)
    
    root.mainloop()
