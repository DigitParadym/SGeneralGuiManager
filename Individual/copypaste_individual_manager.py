# Fichier: Individual/copypaste_individual_manager.py (Version Corrigee)
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import pyperclip

class IndividualCopypasteInterface(ttk.Frame):
    """
    Un outil pour agreger et copier le contenu de plusieurs fichiers individuels.
    Concu comme un composant reutilisable.
    """
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        
        self.file_paths = [tk.StringVar() for _ in range(5)] # 5 slots de fichiers
        self.setup_gui()

    def setup_gui(self):
        mainframe = ttk.Frame(self, padding="10")
        mainframe.pack(fill=tk.BOTH, expand=True)

        # Cadre pour les selections de fichiers
        files_frame = ttk.LabelFrame(mainframe, text="Select Files", padding="10")
        files_frame.pack(fill=tk.X, padx=5, pady=5)

        for i in range(len(self.file_paths)):
            file_row = ttk.Frame(files_frame)
            file_row.pack(fill=tk.X, pady=2)
            
            entry = ttk.Entry(file_row, textvariable=self.file_paths[i], width=70)
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
            
            browse_btn = ttk.Button(file_row, text="Browse...", command=lambda i=i: self.browse_file(i))
            browse_btn.pack(side=tk.LEFT)

        # Cadre pour l'apercu du contenu
        preview_frame = ttk.LabelFrame(mainframe, text="Aggregated Content", padding="10")
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        preview_scroll = ttk.Scrollbar(preview_frame)
        preview_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.preview = tk.Text(preview_frame, wrap=tk.WORD, yscrollcommand=preview_scroll.set, font=("Courier New", 9))
        self.preview.pack(fill=tk.BOTH, expand=True)
        preview_scroll.config(command=self.preview.yview)

        # Cadre pour les boutons d'action
        button_frame = ttk.Frame(mainframe, padding="10 0 0 0")
        button_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        copy_btn = ttk.Button(button_frame, text="Copy to Clipboard", command=self.copy_to_clipboard)
        copy_btn.pack(side=tk.RIGHT, padx=5)
        
        clear_btn = ttk.Button(button_frame, text="Clear All", command=self.clear_all)
        clear_btn.pack(side=tk.RIGHT)

    def browse_file(self, index):
        """Ouvre une boite de dialogue pour selectionner un fichier."""
        filepath = filedialog.askopenfilename(title=f"Select File {index + 1}")
        if filepath:
            self.file_paths[index].set(filepath)
            self.aggregate_content()

    def aggregate_content(self):
        """Lit tous les fichiers selectionnes et les affiche dans l'apercu."""
        self.preview.delete(1.0, tk.END)
        
        full_content = []
        for i, file_var in enumerate(self.file_paths):
            filepath = file_var.get()
            if filepath:
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        file_content = f.read()
                    
                    full_content.append(f"\\n{'='*60}")
                    full_content.append(f"\\nFile {i+1}: {os.path.basename(filepath)}")
                    full_content.append(f"\\n{'='*60}\\n")
                    full_content.append(file_content)
                    full_content.append("\\n")
                except Exception as e:
                    full_content.append(f"\\nError reading {os.path.basename(filepath)}: {str(e)}\\n")
        
        self.preview.insert(tk.END, "".join(full_content))

    def copy_to_clipboard(self):
        """Copie le contenu agrege dans le presse-papiers."""
        content = self.preview.get(1.0, tk.END).strip()
        if content:
            pyperclip.copy(content)
            messagebox.showinfo("Success", "Content copied to clipboard!")
        else:
            messagebox.showwarning("Warning", "No content to copy.")

    def clear_all(self):
        """Efface tous les champs et l'apercu."""
        self.preview.delete(1.0, tk.END)
        for file_var in self.file_paths:
            file_var.set("")