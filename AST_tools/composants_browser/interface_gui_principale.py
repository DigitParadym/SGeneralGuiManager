#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interface GUI Principale - Lanceur pour les modules AST
"""
import sys
import os
from pathlib import Path
import datetime
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# MODIFICATION : Importer les classes nécessaires depuis l'autre module
from composants_browser.file_selector_ui import FileSelectorApp, collect_python_files_from_selection

# Ajouter le répertoire parent au path pour trouver les modules
current_dir = Path(__file__).parent.parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

class InterfaceAST:
    """Interface graphique principale pour les transformations AST."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Interface AST - Transformations Modulaires")
        self.root.geometry("800x600")
        
        self.fichiers_selectionnes = []
        self.transformations_disponibles = []
        self.loader = None
        
        self.creer_interface()
        self.init_transformation_loader()
    
    def creer_interface(self):
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        tk.Label(main_frame, text="Interface AST - Transformations Modulaires", font=('Arial', 14, 'bold')).pack(pady=(0, 20))
        
        files_frame = tk.LabelFrame(main_frame, text="Fichiers", font=('Arial', 12, 'bold'))
        files_frame.pack(fill='x', pady=(0, 10))
        
        buttons_frame = tk.Frame(files_frame)
        buttons_frame.pack(fill='x', padx=10, pady=10)
        
        # MODIFICATION : Ce bouton lance maintenant le sélecteur avancé
        tk.Button(buttons_frame, text="Sélecteur Avancé", command=self.select_files_advanced).pack(side='left', padx=(0, 10))
        tk.Button(buttons_frame, text="Dossier (Simple)", command=self.select_folder_simple).pack(side='left', padx=(0, 10))
        tk.Button(buttons_frame, text="Effacer", command=self.clear_selection).pack(side='left', padx=(0, 10))
        
        self.files_listbox = tk.Listbox(files_frame, height=5)
        self.files_listbox.pack(fill='x', expand=True, padx=10, pady=(0, 10))
        
        # Le reste de l'interface...
        transform_frame = tk.LabelFrame(main_frame, text="Transformations", font=('Arial', 12, 'bold'))
        transform_frame.pack(fill='x', pady=(0, 10))
        self.transformation_var = tk.StringVar()
        self.transformation_combo = ttk.Combobox(transform_frame, textvariable=self.transformation_var, state="readonly")
        self.transformation_combo.pack(fill='x', padx=10, pady=10)
        tk.Button(main_frame, text="Appliquer la Transformation", command=self.apply_transformation, font=('Arial', 12, 'bold'), bg='#27ae60', fg='white').pack(pady=10)
        console_frame = tk.LabelFrame(main_frame, text="Console", font=('Arial', 12, 'bold'))
        console_frame.pack(fill='both', expand=True)
        self.console_text = tk.Text(console_frame, font=('Courier', 9), wrap='word')
        self.console_text.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        self.log_message("=== Interface AST démarrée ===")

    # NOUVELLE MÉTHODE pour lancer la fenêtre enfant
    def select_files_advanced(self):
        self.log_message("Ouverture du sélecteur de fichiers avancé...")
        selector_window = FileSelectorApp(self.root)
        self.root.wait_window(selector_window)
        
        if selector_window.result:
            selected_items, selection_type = selector_window.result
            if selected_items:
                self.fichiers_selectionnes = collect_python_files_from_selection(selected_items, selection_type)
                self.update_files_display()
                self.log_message(f"+ {len(self.fichiers_selectionnes)} fichier(s) prêt(s) pour traitement.")
        else:
            self.log_message("Sélection annulée.")

    def update_files_display(self):
        self.files_listbox.delete(0, tk.END)
        for f_path in self.fichiers_selectionnes:
            self.files_listbox.insert(tk.END, os.path.basename(f_path))

    def clear_selection(self):
        self.fichiers_selectionnes = []
        self.update_files_display()
        self.log_message("Sélection effacée.")

    # Le reste de vos méthodes (init_transformation_loader, apply_transformation, etc.) reste ici...
    # (Par souci de clarté, je ne les répète pas, mais elles doivent être dans votre classe)

    def log_message(self, message):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        full_message = f"[{timestamp}] {message}\n"
        self.console_text.insert(tk.END, full_message)
        self.console_text.see(tk.END)
        self.root.update_idletasks()

    def run(self):
        self.root.mainloop()

if __name__ == '__main__':
    app = InterfaceAST()
    app.run()