# ==================================================
# File: Folder/FolderCopypaste_interface.py (Version 3.1 - Amélioration du Browse)
# ==================================================
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import pyperclip
from pathlib import Path
import json
from datetime import datetime

class AdvancedCopypasteInterface(ttk.Frame):
    """
    Un outil de copie de contenu réutilisable, conçu pour être intégré dans d'autres fenêtres.
    Il mémorise les derniers paramètres utilisés.
    """
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        
        self.settings_file = Path(__file__).parent / 'folder_settings.json'
        
        # Variables pour les options
        self.file_type_mode = tk.StringVar(value="python")
        self.recursive_scan = tk.BooleanVar(value=True)
        self.folder_path = tk.StringVar()
        self.last_folder_path = ""

        # Ensembles d'extensions pour chaque mode
        self.extension_sets = {
            "python": ('.py',),
            "web": ('.py', '.html', '.css', '.js'),
            "docs": ('.py', '.md', '.txt', '.rst'),
            "full": ('.py', '.html', '.css', '.js', '.md', '.txt', '.rst', '.log', '.csv')
        }
        
        self.load_settings()
        self.setup_gui()
        self.restore_last_folder()

        # Le parent (SystemManager) gérera la sauvegarde à la fermeture
        
    def load_settings(self):
        """Charge les paramètres depuis le fichier JSON au démarrage."""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    self.last_folder_path = settings.get('last_folder_path', '')
                    self.file_type_mode.set(settings.get('file_type_mode', 'python'))
                    self.recursive_scan.set(settings.get('recursive_scan', True))
        except Exception as e:
            print(f"Erreur lors du chargement des paramètres : {e}")
            self.last_folder_path = ''

    def save_settings(self):
        """Sauvegarde les paramètres actuels dans le fichier JSON."""
        try:
            settings = {
                'last_folder_path': self.folder_path.get(),
                'file_type_mode': self.file_type_mode.get(),
                'recursive_scan': self.recursive_scan.get(),
                'last_updated': datetime.now().isoformat()
            }
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde des paramètres : {e}")

    def setup_gui(self):
        mainframe = ttk.Frame(self, padding="10")
        mainframe.pack(fill=tk.BOTH, expand=True)
        
        folder_frame = ttk.LabelFrame(mainframe, text="Target Folder", padding="10")
        folder_frame.pack(fill=tk.X, padx=5, pady=5)
        folder_entry = ttk.Entry(folder_frame, textvariable=self.folder_path, width=80)
        folder_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        browse_btn = ttk.Button(folder_frame, text="Browse...", command=self.browse_folder)
        browse_btn.pack(side=tk.RIGHT)
        
        mode_frame = ttk.LabelFrame(mainframe, text="File Type Mode", padding="10")
        mode_frame.pack(fill=tk.X, padx=5, pady=5)
        modes = [("Python only (.py)", "python"), ("Web development", "web"), ("Documentation", "docs"), ("Full scan", "full")]
        for text, mode in modes:
            ttk.Radiobutton(mode_frame, text=text, variable=self.file_type_mode, value=mode, command=self.refresh_preview).pack(anchor=tk.W)
        
        options_frame = ttk.LabelFrame(mainframe, text="Options", padding="10")
        options_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Checkbutton(options_frame, text="Recursive scan", variable=self.recursive_scan, command=self.refresh_preview).pack(side=tk.LEFT)
        
        preview_frame = ttk.LabelFrame(mainframe, text="Content Preview", padding="10")
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        preview_scroll = ttk.Scrollbar(preview_frame)
        preview_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.preview = tk.Text(preview_frame, wrap=tk.WORD, yscrollcommand=preview_scroll.set, font=("Courier New", 9))
        self.preview.pack(fill=tk.BOTH, expand=True)
        preview_scroll.config(command=self.preview.yview)
        
        bottom_frame = ttk.Frame(mainframe, padding="10 0 0 0")
        bottom_frame.pack(fill=tk.X, side=tk.BOTTOM)
        self.status_label = ttk.Label(bottom_frame, text="Ready", foreground="green")
        self.status_label.pack(side=tk.LEFT)
        ttk.Button(bottom_frame, text="Copy to Clipboard", command=self.copy_to_clipboard).pack(side=tk.RIGHT, padx=5)
        ttk.Button(bottom_frame, text="Save to File...", command=self.save_to_file).pack(side=tk.RIGHT)

    def restore_last_folder(self):
        """Restaure le chemin du dernier dossier utilisé et charge son contenu."""
        if self.last_folder_path and Path(self.last_folder_path).exists():
            self.folder_path.set(self.last_folder_path)
            self.status_label.config(text=f"Restored: {Path(self.last_folder_path).name}", foreground="blue")
            self.load_content(self.last_folder_path)

    def browse_folder(self):
        """Ouvre la boîte de dialogue pour sélectionner un dossier, en commençant par le dossier utilisateur."""
        # --- MODIFIÉ : Le dialogue commence maintenant dans le dossier de l'utilisateur ou le dernier dossier utilisé ---
        initial_dir = self.folder_path.get() if self.folder_path.get() and Path(self.folder_path.get()).exists() else Path.home()
        
        folder = filedialog.askdirectory(
            title="Select Target Folder",
            initialdir=str(initial_dir)
        )
        if folder: 
            self.folder_path.set(folder)
            self.load_content(folder)
            self.save_settings() # Sauvegarde le nouveau dossier

    def load_content(self, folder):
        try:
            self.preview.delete(1.0, tk.END); self.status_label.config(text="Loading...", foreground="orange"); self.update_idletasks()
            content, files_found_count = [], 0
            folder_path = Path(folder)
            extensions = self.extension_sets[self.file_type_mode.get()]
            file_iterator = folder_path.rglob('*') if self.recursive_scan.get() else folder_path.glob('*')
            for item_path in file_iterator:
                if item_path.is_dir() or not item_path.name.endswith(extensions): continue
                files_found_count += 1
                try:
                    with open(item_path, 'r', encoding='utf-8', errors='ignore') as f: file_content = f.read()
                    relative_path = item_path.relative_to(folder_path)
                    content.append(f"\n{'='*60}\nFile: {relative_path.as_posix()}\n{'='*60}\n{file_content}\n")
                except Exception as e: content.append(f"\nError reading {item_path.name}: {str(e)}\n")
            self.preview.insert(tk.END, "".join(content))
            if files_found_count > 0: self.status_label.config(text=f"Loaded {files_found_count} files.", foreground="green")
            else: self.status_label.config(text="No eligible files found.", foreground="red")
        except Exception as e: messagebox.showerror("Error", f"An error occurred: {str(e)}"); self.status_label.config(text="Error.", foreground="red")
    
    def refresh_preview(self):
        """Rafraîchit l'aperçu si un dossier est déjà sélectionné."""
        if self.folder_path.get():
            self.load_content(self.folder_path.get())
            
    def copy_to_clipboard(self):
        """Copie le contenu de l'aperçu dans le presse-papiers."""
        content = self.preview.get(1.0, tk.END).strip()
        if content: pyperclip.copy(content); messagebox.showinfo("Success", "Content copied to clipboard!")
        else: messagebox.showwarning("Warning", "No content to copy.")

    def save_to_file(self):
        """Sauvegarde le contenu de l'aperçu dans un fichier."""
        content = self.preview.get(1.0, tk.END).strip()
        if not content: messagebox.showwarning("Warning", "No content to save."); return
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f: f.write(content)
            messagebox.showinfo("Success", "Content saved successfully!")
