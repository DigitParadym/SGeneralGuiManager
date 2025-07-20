# ==================================================
# FICHIER 2 : rename/rename_interface_tk.py (Nouveau Fichier)
# Créez ce fichier dans le dossier 'rename/'.
# ==================================================
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import re
from pathlib import Path

class RenameInterface(ttk.Frame):
    """
    Une interface Tkinter pour renommer des fichiers en masse dans un dossier.
    """
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        
        self.folder_path = tk.StringVar()
        self.find_pattern = tk.StringVar()
        self.replace_pattern = tk.StringVar()
        self.recursive_rename = tk.BooleanVar(value=True)
        
        self.setup_gui()

    def setup_gui(self):
        mainframe = ttk.Frame(self, padding="10")
        mainframe.pack(fill=tk.BOTH, expand=True)

        # --- Cadre de sélection du dossier ---
        folder_frame = ttk.LabelFrame(mainframe, text="Dossier Cible", padding="10")
        folder_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Entry(folder_frame, textvariable=self.folder_path, width=70).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        ttk.Button(folder_frame, text="Parcourir...", command=self.browse_folder).pack(side=tk.LEFT)

        # --- Cadre des motifs de renommage ---
        pattern_frame = ttk.LabelFrame(mainframe, text="Règles de Renommage", padding="10")
        pattern_frame.pack(fill=tk.X, padx=5, pady=5, expand=True)
        pattern_frame.columnconfigure(1, weight=1)
        
        ttk.Label(pattern_frame, text="Trouver :").grid(row=0, column=0, sticky="w", pady=2)
        ttk.Entry(pattern_frame, textvariable=self.find_pattern).grid(row=0, column=1, sticky="ew", pady=2)
        
        ttk.Label(pattern_frame, text="Remplacer par :").grid(row=1, column=0, sticky="w", pady=2)
        ttk.Entry(pattern_frame, textvariable=self.replace_pattern).grid(row=1, column=1, sticky="ew", pady=2)

        # --- Cadre des options ---
        options_frame = ttk.LabelFrame(mainframe, text="Options", padding="10")
        options_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Checkbutton(options_frame, text="Inclure les sous-dossiers (Récursif)", variable=self.recursive_rename).pack(anchor=tk.W)

        # --- Cadre de l'aperçu ---
        preview_frame = ttk.LabelFrame(mainframe, text="Aperçu des Changements", padding="10")
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.preview_tree = ttk.Treeview(preview_frame, columns=("original", "nouveau"), show="headings")
        self.preview_tree.heading("original", text="Nom Original")
        self.preview_tree.heading("nouveau", text="Nouveau Nom")
        self.preview_tree.pack(fill=tk.BOTH, expand=True)

        # --- Boutons d'action ---
        button_frame = ttk.Frame(mainframe, padding="10 0 0 0")
        button_frame.pack(fill=tk.X, side=tk.BOTTOM)
        ttk.Button(button_frame, text="Prévisualiser", command=self.preview_rename).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="Exécuter le Renommage", command=self.execute_rename).pack(side=tk.RIGHT)

    def browse_folder(self):
        folder = filedialog.askdirectory(title="Sélectionnez le dossier à traiter")
        if folder:
            self.folder_path.set(folder)
            self.preview_rename()

    def preview_rename(self):
        """Affiche un aperçu des changements sans les appliquer."""
        folder = self.folder_path.get()
        find_what = self.find_pattern.get()
        replace_with = self.replace_pattern.get()

        if not folder or not find_what:
            messagebox.showwarning("Information manquante", "Veuillez sélectionner un dossier et spécifier un motif à trouver.")
            return

        self.preview_tree.delete(*self.preview_tree.get_children())
        
        try:
            path_obj = Path(folder)
            file_iterator = path_obj.rglob('*') if self.recursive_rename.get() else path_obj.glob('*')

            for item in file_iterator:
                if item.is_file():
                    new_name = re.sub(find_what, replace_with, item.name)
                    if new_name != item.name:
                        self.preview_tree.insert("", "end", values=(item.name, new_name))
        except re.error as e:
            messagebox.showerror("Erreur d'Expression Régulière", f"Le motif de recherche est invalide : {e}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur est survenue lors de la prévisualisation : {e}")

    def execute_rename(self):
        """Exécute le renommage après confirmation."""
        changes = self.preview_tree.get_children()
        if not changes:
            messagebox.showinfo("Aucun changement", "Aucun fichier ne correspond au motif pour être renommé.")
            return

        msg = f"Vous êtes sur le point de renommer {len(changes)} fichier(s).\nCette action est irréversible.\n\nContinuer ?"
        if not messagebox.askyesno("Confirmation de Renommage", msg):
            return

        folder = self.folder_path.get()
        path_obj = Path(folder)
        
        renamed_count = 0
        for item_id in changes:
            original_name, new_name = self.preview_tree.item(item_id)['values']
            
            # On reconstruit le chemin complet
            original_path = path_obj / original_name
            new_path = path_obj / new_name
            
            try:
                os.rename(original_path, new_path)
                renamed_count += 1
            except Exception as e:
                messagebox.showerror("Erreur de Renommage", f"Impossible de renommer '{original_name}':\n{e}")
                break # Arrêter en cas d'erreur
        
        messagebox.showinfo("Succès", f"{renamed_count} fichier(s) ont été renommés avec succès.")
        self.preview_rename() # Rafraîchir l'aperçu
