#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interface GUI Principale - Version Stable
Compatible System Manager SANS bouton retour
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import sys
import json
from pathlib import Path
from datetime import datetime

class InterfaceAST:
    """Interface graphique pour AST - Version Stable."""
    
    def __init__(self, parent=None):
        """
        Constructeur compatible avec System Manager.
        
        Args:
            parent: Widget parent (None pour mode autonome, widget pour mode integre)
        """
        self.parent = parent
        self.is_integrated = parent is not None
        
        # Variables
        self.plan_json_path = tk.StringVar()
        self.fichiers_cibles = []
        self.orchestrateur = None
        
        # Creation de l'interface selon le mode
        if self.is_integrated:
            self.setup_integrated_mode()
        else:
            self.setup_standalone_mode()
        
        # Interface commune
        self.create_widgets()
        self.init_moteur_modulaire()
    
    def setup_standalone_mode(self):
        """Configure le mode autonome."""
        self.root = tk.Tk()
        self.root.title("AST Tools - Execution de Plans JSON")
        self.root.geometry("800x700")
        self.container = self.root
    
    def setup_integrated_mode(self):
        """Configure le mode integre."""
        self.root = None
        self.container = self.parent
    
    def create_widgets(self):
        """Cree l'interface utilisateur."""
        
        # Frame principal
        if self.is_integrated:
            main_frame = ttk.Frame(self.container)
            main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        else:
            main_frame = ttk.Frame(self.container)
            main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Titre (seulement en mode autonome)
        if not self.is_integrated:
            title_label = ttk.Label(main_frame, text="AST Tools - Execution de Plans JSON", 
                                   font=("Arial", 16, "bold"))
            title_label.pack(pady=(0, 20))
        
        # Section 1: Selection du plan JSON
        self.create_plan_selection_section(main_frame)
        
        # Section 2: Selection des fichiers cibles
        self.create_file_selection_section(main_frame)
        
        # Section 3: Boutons d'action
        self.create_action_buttons(main_frame)
        
        # Section 4: Zone de logs
        self.create_log_section(main_frame)
    
    def create_plan_selection_section(self, parent):
        """Cree la section de selection du plan JSON."""
        
        # Frame pour le plan JSON
        plan_frame = ttk.LabelFrame(parent, text="1. Selection du Plan JSON", padding=10)
        plan_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Selecteur de fichier JSON
        json_frame = ttk.Frame(plan_frame)
        json_frame.pack(fill=tk.X)
        
        ttk.Label(json_frame, text="Plan JSON:").pack(side=tk.LEFT)
        
        self.plan_entry = ttk.Entry(json_frame, textvariable=self.plan_json_path, width=40)
        self.plan_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5))
        
        ttk.Button(json_frame, text="Parcourir...", 
                  command=self.select_plan_json).pack(side=tk.RIGHT)
        
        # Informations sur le plan
        self.plan_info_frame = ttk.Frame(plan_frame)
        self.plan_info_frame.pack(fill=tk.X, pady=(10, 0))
        
        height = 3 if self.is_integrated else 4
        self.plan_info_text = scrolledtext.ScrolledText(self.plan_info_frame, height=height, width=60)
        self.plan_info_text.pack(fill=tk.X)
    
    def create_file_selection_section(self, parent):
        """Cree la section de selection des fichiers cibles."""
        
        # Frame pour les fichiers cibles
        files_frame = ttk.LabelFrame(parent, text="2. Selection des Fichiers Cibles", padding=10)
        files_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Boutons de selection
        buttons_frame = ttk.Frame(files_frame)
        buttons_frame.pack(fill=tk.X)
        
        ttk.Button(buttons_frame, text="Ajouter Fichier(s)", 
                  command=self.add_files).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="Ajouter Dossier", 
                  command=self.add_folder).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="Vider Liste", 
                  command=self.clear_files).pack(side=tk.LEFT, padx=(0, 5))
        
        # Liste des fichiers
        height = 4 if self.is_integrated else 6
        self.files_listbox = tk.Listbox(files_frame, height=height)
        self.files_listbox.pack(fill=tk.X, pady=(10, 0))
    
    def create_action_buttons(self, parent):
        """Cree les boutons d'action."""
        
        # Frame pour les boutons
        action_frame = ttk.Frame(parent)
        action_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Bouton principal
        self.execute_button = ttk.Button(action_frame, text="EXECUTER LE PLAN", 
                                        command=self.execute_plan)
        self.execute_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Bouton de validation
        ttk.Button(action_frame, text="Valider Plan", 
                  command=self.validate_plan).pack(side=tk.LEFT, padx=(0, 10))
        
        # Bouton d'aide (seulement en mode autonome)
        if not self.is_integrated:
            ttk.Button(action_frame, text="Aide", 
                      command=self.show_help).pack(side=tk.RIGHT)
    
    def create_log_section(self, parent):
        """Cree la section des logs."""
        
        # Frame pour les logs
        log_frame = ttk.LabelFrame(parent, text="Logs d'Execution", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        # Zone de texte pour les logs
        height = 8 if self.is_integrated else 12
        self.log_text = scrolledtext.ScrolledText(log_frame, height=height, width=70)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Bouton pour vider les logs
        ttk.Button(log_frame, text="Vider Logs", 
                  command=self.clear_logs).pack(pady=(5, 0))
    
    def select_plan_json(self):
        """Ouvre le selecteur de fichier JSON."""
        file_path = filedialog.askopenfilename(
            title="Selectionner un plan JSON",
            filetypes=[("Fichiers JSON", "*.json"), ("Tous les fichiers", "*.*")]
        )
        
        if file_path:
            self.plan_json_path.set(file_path)
            self.load_plan_info(file_path)
    
    def load_plan_info(self, plan_path):
        """Charge et affiche les informations du plan JSON."""
        try:
            with open(plan_path, 'r', encoding='utf-8') as f:
                plan_data = json.load(f)
            
            # Extraire les informations
            metadata = plan_data.get('metadata', {})
            transformations = plan_data.get('transformations', [])
            
            # Afficher les informations
            info_text = "Plan: " + str(metadata.get('name', 'Non specifie')) + "\n"
            info_text += "Version: " + str(metadata.get('version', 'N/A')) + "\n"
            info_text += "Description: " + str(metadata.get('description', 'Aucune description')) + "\n"
            info_text += "Transformations: " + str(len(transformations)) + " etape(s)\n"
            
            if transformations:
                info_text += "\nEtapes:\n"
                for i, transform in enumerate(transformations, 1):
                    desc = transform.get('description', 'Sans description')
                    info_text += "  " + str(i) + ". " + str(desc) + "\n"
            
            self.plan_info_text.delete(1.0, tk.END)
            self.plan_info_text.insert(1.0, info_text)
            
            self.log_message("Plan charge: " + os.path.basename(plan_path))
            
        except Exception as e:
            self.log_message("ERREUR lecture plan: " + str(e))
            self.plan_info_text.delete(1.0, tk.END)
            self.plan_info_text.insert(1.0, "Erreur: " + str(e))
    
    def add_files(self):
        """Ajoute des fichiers a la liste des cibles."""
        files = filedialog.askopenfilenames(
            title="Selectionner les fichiers Python",
            filetypes=[("Fichiers Python", "*.py"), ("Tous les fichiers", "*.*")]
        )
        
        for file_path in files:
            if file_path not in self.fichiers_cibles:
                self.fichiers_cibles.append(file_path)
                self.files_listbox.insert(tk.END, os.path.basename(file_path))
        
        self.log_message(str(len(files)) + " fichier(s) ajoute(s)")
    
    def add_folder(self):
        """Ajoute tous les fichiers .py d'un dossier."""
        folder_path = filedialog.askdirectory(title="Selectionner un dossier")
        
        if folder_path:
            python_files = list(Path(folder_path).rglob("*.py"))
            added_count = 0
            
            for file_path in python_files:
                file_str = str(file_path)
                if file_str not in self.fichiers_cibles:
                    self.fichiers_cibles.append(file_str)
                    self.files_listbox.insert(tk.END, file_path.name)
                    added_count += 1
            
            self.log_message(str(added_count) + " fichier(s) Python ajoute(s) depuis " + os.path.basename(folder_path))
    
    def clear_files(self):
        """Vide la liste des fichiers cibles."""
        self.fichiers_cibles.clear()
        self.files_listbox.delete(0, tk.END)
        self.log_message("Liste des fichiers videe")
    
    def validate_plan(self):
        """Valide le plan JSON selectionne."""
        if not self.plan_json_path.get():
            messagebox.showwarning("Attention", "Aucun plan JSON selectionne")
            return
        
        try:
            with open(self.plan_json_path.get(), 'r', encoding='utf-8') as f:
                plan_data = json.load(f)
            
            # Validations basiques
            if 'transformations' not in plan_data:
                raise ValueError("Le plan doit contenir une section 'transformations'")
            
            transformations = plan_data['transformations']
            if not transformations:
                raise ValueError("Le plan doit contenir au moins une transformation")
            
            # Valider chaque transformation
            for i, transform in enumerate(transformations):
                if 'type' not in transform:
                    raise ValueError("Transformation " + str(i+1) + ": 'type' manquant")
            
            messagebox.showinfo("Validation", "Plan JSON valide!\n" + str(len(transformations)) + " transformation(s) detectee(s)")
            self.log_message("Plan JSON valide")
            
        except Exception as e:
            messagebox.showerror("Erreur Validation", "Plan JSON invalide:\n" + str(e))
            self.log_message("ERREUR validation: " + str(e))
    
    def execute_plan(self):
        """Execute le plan JSON sur les fichiers cibles."""
        
        # Verifications
        if not self.plan_json_path.get():
            messagebox.showwarning("Attention", "Aucun plan JSON selectionne")
            return
        
        if not self.fichiers_cibles:
            messagebox.showwarning("Attention", "Aucun fichier cible selectionne")
            return
        
        if not self.orchestrateur:
            messagebox.showerror("Erreur", "Moteur AST non initialise")
            return
        
        # Confirmation
        nb_files = len(self.fichiers_cibles)
        plan_name = os.path.basename(self.plan_json_path.get())
        
        result = messagebox.askyesno("Confirmation", 
                                   "Executer le plan '" + plan_name + "' sur " + str(nb_files) + " fichier(s)?")
        if not result:
            return
        
        # Execution
        try:
            self.log_message("=" * 50)
            self.log_message("DEBUT EXECUTION: " + plan_name)
            self.log_message("Fichiers cibles: " + str(nb_files))
            self.log_message("=" * 50)
            
            # Appel de la methode executer_plan
            self.orchestrateur.executer_plan(self.plan_json_path.get(), self.fichiers_cibles)
            
            self.log_message("=" * 50)
            self.log_message("EXECUTION TERMINEE AVEC SUCCES!")
            self.log_message("=" * 50)
            
            messagebox.showinfo("Succes", "Plan execute avec succes sur " + str(nb_files) + " fichier(s)")
            
        except Exception as e:
            error_msg = "ERREUR execution: " + str(e)
            self.log_message(error_msg)
            messagebox.showerror("Erreur", error_msg)
    
    def show_help(self):
        """Affiche l'aide (seulement en mode autonome)."""
        if self.is_integrated:
            return
            
        help_text = """
AIDE - AST Tools Plans JSON

1. SELECTION DU PLAN:
   - Cliquez sur 'Parcourir...' pour selectionner un fichier .json
   - Le plan contient la liste des transformations a appliquer

2. SELECTION DES FICHIERS:
   - 'Ajouter Fichier(s)': Selectionnez des fichiers .py individuels
   - 'Ajouter Dossier': Ajoute tous les .py d'un dossier

3. EXECUTION:
   - 'Valider Plan': Verifie la validite du plan
   - 'EXECUTER LE PLAN': Lance toutes les transformations
        """
        
        help_window = tk.Toplevel(self.container)
        help_window.title("Aide")
        help_window.geometry("500x300")
        
        help_display = scrolledtext.ScrolledText(help_window, wrap=tk.WORD)
        help_display.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        help_display.insert(1.0, help_text)
        help_display.configure(state='disabled')
    
    def init_moteur_modulaire(self):
        """Initialise le moteur AST."""
        try:
            # Ajouter le chemin AST_tools
            import sys
            from pathlib import Path
            ast_tools_path = Path(__file__).parent.parent
            sys.path.insert(0, str(ast_tools_path))
            
            # Import de l'orchestrateur
            from modificateur_interactif import OrchestrateurAST
            
            # Creer l'instance
            self.orchestrateur = OrchestrateurAST()
            
            self.log_message("+ Moteur AST connecte avec succes!")
            if self.is_integrated:
                self.log_message("+ Mode integre actif - Version stable")
            else:
                self.log_message("+ Mode autonome actif")
            
        except Exception as e:
            self.log_message("ERREUR connexion moteur: " + str(e))
            self.orchestrateur = None
    
    def log_message(self, message):
        """Ajoute un message aux logs."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = "[" + timestamp + "] " + str(message) + "\n"
        
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        
        # Imprimer aussi dans la console
        print(message)
    
    def clear_logs(self):
        """Vide la zone de logs."""
        self.log_text.delete(1.0, tk.END)
    
    def run(self):
        """Lance l'interface (seulement en mode autonome)."""
        if not self.is_integrated and self.root:
            self.root.mainloop()
    
    def destroy(self):
        """Detruit l'interface."""
        if self.root:
            self.root.destroy()

def main():
    """Point d'entree principal."""
    app = InterfaceAST()
    app.run()

if __name__ == "__main__":
    main()
