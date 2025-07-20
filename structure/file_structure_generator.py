# ==================================================
# Fichier : structure/file_structure_generator.py (Version 2.1 - avec Copie)
# ==================================================
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from pathlib import Path
import pyperclip # Ajout pour la fonctionnalité de copie

class StructureGeneratorInterface(ttk.Frame):
    """
    Un outil de génération de structure de projet, conçu comme un composant réutilisable,
    avec une fonctionnalité de copie dans le presse-papiers.
    """
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        
        self.folder_path = tk.StringVar()
        self.setup_gui()

    def setup_gui(self):
        mainframe = ttk.Frame(self, padding="10")
        mainframe.pack(fill=tk.BOTH, expand=True)

        # --- Section de sélection du dossier ---
        folder_frame = ttk.LabelFrame(mainframe, text="Target Project Folder", padding="10")
        folder_frame.pack(fill=tk.X, padx=5, pady=5)
        
        folder_entry = ttk.Entry(folder_frame, textvariable=self.folder_path, width=80, state="readonly")
        folder_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        browse_btn = ttk.Button(folder_frame, text="Browse...", command=self.browse_folder)
        browse_btn.pack(side=tk.RIGHT)

        # --- Section de prévisualisation ---
        preview_frame = ttk.LabelFrame(mainframe, text="Generated Structure", padding="10")
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        preview_scroll = ttk.Scrollbar(preview_frame)
        preview_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.preview = tk.Text(preview_frame, wrap=tk.WORD, yscrollcommand=preview_scroll.set, font=("Courier New", 9))
        self.preview.pack(fill=tk.BOTH, expand=True)
        preview_scroll.config(command=self.preview.yview)
        
        # --- NOUVEAU : Section des boutons ---
        button_frame = ttk.Frame(mainframe, padding="5 5 0 0")
        button_frame.pack(fill=tk.X)
        
        copy_btn = ttk.Button(button_frame, text="Copier la Structure", command=self.copy_to_clipboard)
        copy_btn.pack(side=tk.RIGHT)

    def browse_folder(self):
        folder = filedialog.askdirectory(title="Select Project Root Folder")
        if folder:
            self.folder_path.set(folder)
            self.generate_structure(folder)

    def generate_structure(self, folder):
        self.preview.delete(1.0, tk.END)
        try:
            path_obj = Path(folder)
            structure = f"{path_obj.name}/\n"
            
            for line in self._tree(path_obj):
                structure += line + "\n"
                
            self.preview.insert(tk.END, structure)
            messagebox.showinfo("Success", "Project structure generated successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate structure: {e}")

    def _tree(self, dir_path: Path, prefix: str = ""):
        """Un générateur récursif qui produit la structure du répertoire."""
        excluded = {'.git', '__pycache__', 'venv', '.venv', 'build', 'dist', 'node_modules'}
        contents = sorted([p for p in dir_path.iterdir() if p.name not in excluded], key=lambda p: (p.is_file(), p.name.lower()))
        
        pointers = [("├── ") for _ in range(len(contents) - 1)] + [("└── ")]
        for pointer, path in zip(pointers, contents):
            yield prefix + pointer + path.name
            if path.is_dir():
                extension = "│   " if pointer == "├── " else "    "
                yield from self._tree(path, prefix=prefix + extension)

    # --- NOUVEAU : Fonction de copie ---
    def copy_to_clipboard(self):
        """Copie la structure générée dans le presse-papiers."""
        content = self.preview.get(1.0, tk.END).strip()
        if content:
            try:
                pyperclip.copy(content)
                messagebox.showinfo("Success", "Structure copied to clipboard!")
            except Exception as e:
                messagebox.showerror("Error", f"Could not copy to clipboard: {str(e)}")
        else:
            messagebox.showwarning("Warning", "No structure to copy.")

# Pour permettre de tester ce module seul si nécessaire
if __name__ == '__main__':
    root = tk.Tk()
    root.title("Structure Generator Test")
    root.geometry("700x500")
    
    app = StructureGeneratorInterface(root)
    app.pack(fill="both", expand=True)
    
    root.mainloop()
