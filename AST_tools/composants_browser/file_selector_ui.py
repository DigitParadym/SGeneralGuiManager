#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sélecteur de Fichiers/Dossiers Python - Refactorisé en Toplevel
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import datetime

# MODIFICATION CLÉ : La classe hérite de tk.Toplevel
class FileSelectorApp(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master) # Initialise la fenêtre Toplevel
        
        self.master = master
        self.result = None  # Pour stocker le résultat
        self.selected_files = []
        self.selected_folders = []
        self.current_directory = os.getcwd()
        self.selection_mode = "file"

        # Configuration de la fenêtre (self, pas master)
        self.title("Sélecteur Avancé")
        self.geometry("1100x700")
        self.transient(master)  # S'affiche au-dessus du parent
        self.grab_set()         # Bloque les interactions avec le parent

        # ... le reste de votre code de création de l'interface
        self.create_widgets()
        self.populate_tree()
        self.protocol("WM_DELETE_WINDOW", self.cancel_selection)

    def confirm_selection(self):
        """Confirme la sélection et ferme la fenêtre."""
        if self.selection_mode == "file" and self.selected_files:
            self.result = (self.selected_files, "file")
            self.destroy() # Ferme cette fenêtre
        elif self.selection_mode == "folders" and self.selected_folders:
            self.result = (self.selected_folders, "folders")
            self.destroy() # Ferme cette fenêtre
        else:
            messagebox.showwarning("Aucune sélection", "Veuillez sélectionner un élément.", parent=self)

    def cancel_selection(self):
        """Annule et ferme la fenêtre."""
        self.result = ([], None) # Résultat vide
        self.destroy()

    # ... (Copiez ici le reste de vos méthodes de file_selector_ui.py SANS les modifier) ...
    # create_widgets, on_item_select, populate_tree, etc.

# --- Logique de collecte, à conserver dans ce fichier ---
def collect_python_files_from_selection(selected_items, selection_type):
    python_files = []
    if selection_type == "file" and selected_items:
        file_path = selected_items[0]
        if os.path.exists(file_path) and file_path.endswith('.py'):
            python_files.append(file_path)
    elif selection_type == "folders" and selected_items:
        for folder_path in selected_items:
            if os.path.isdir(folder_path):
                for root, dirs, files in os.walk(folder_path):
                    dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
                    for file in files:
                        if file.endswith('.py'):
                            python_files.append(os.path.join(root, file))
    return python_files

# Bloc de test pour ce module seul
if __name__ == '__main__':
    root = tk.Tk()
    root.withdraw() # On cache la fenêtre parente de test
    
    # Simule l'appel depuis une application principale
    selector = FileSelectorApp(root)
    root.wait_window(selector)
    
    if selector.result:
        print("Sélection reçue:", selector.result)
        files = collect_python_files_from_selection(selector.result[0], selector.result[1])
        print(f"Fichiers collectés : {len(files)}")
    else:
        print("Sélection annulée.")
    
    root.destroy()