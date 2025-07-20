# Fichier: import_mapper/analysis_interface.py
import tkinter as tk
from tkinter import ttk, filedialog

class AnalysisToolsInterface(ttk.Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        
        self.target_folder = tk.StringVar(value="Aucun dossier selectionne")
        
        # --- Widgets ---
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Label et bouton sur la meme ligne
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(top_frame, text="Dossier Cible :").pack(side=tk.LEFT, padx=(0, 10))
        
        browse_button = ttk.Button(top_frame, text="Parcourir...", command=self.select_folder)
        browse_button.pack(side=tk.RIGHT)

        # Label pour afficher le chemin selectionne
        path_label = ttk.Label(main_frame, textvariable=self.target_folder, foreground="gray", wraplength=400)
        path_label.pack(fill=tk.X)

    def select_folder(self):
        """Ouvre une boite de dialogue pour selectionner un dossier."""
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.target_folder.set(folder_selected)
            print(f"Dossier cible pour l'analyse selectionne : {folder_selected}")