#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
System Manager - Version Stable
Gestionnaire d'applications unifie - AST en mode integre simple
"""

import tkinter as tk
from tkinter import ttk
import subprocess
import sys
import os
from pathlib import Path

class SystemManager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("System Manager")
        self.root.geometry("600x500")
        
        # Variables
        self.main_pane = None
        self.active_integrated_frame = None
        
        # Configuration des modules
        self.modules = {
            "ConnectorPro": {
                "name": "ConnectorPro",
                "status": "Ready",
                "launch_mode": "external",
                "script": "connectorpro/main.py"
            },
            "AST - Transformations": {
                "name": "Interface AST - Transformations", 
                "status": "Ready",
                "launch_mode": "integrated",
                "script": "AST_tools/composants_browser/interface_gui_principale.py"
            },
            "Smart Rename System": {
                "name": "Smart Rename System",
                "status": "Ready", 
                "launch_mode": "external",
                "script": "rename/main_window.py"
            },
            "Individual Manager": {
                "name": "Individual Manager",
                "status": "Ready",
                "launch_mode": "external", 
                "script": "Individual/copypaste_individual_manager.py"
            }
        }
        
        self.create_interface()
    
    def create_interface(self):
        """Cree l'interface principale."""
        
        # Titre
        title_label = ttk.Label(self.root, text="System Manager", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Info
        info_label = ttk.Label(self.root, text=str(len(self.modules)) + " modules found")
        info_label.pack(pady=(0, 20))
        
        # Frame principal avec PanedWindow
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # PanedWindow pour interface integree
        self.main_pane = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        self.main_pane.pack(fill=tk.BOTH, expand=True)
        
        # Panel de gauche - Liste des modules
        left_panel = ttk.Frame(self.main_pane)
        self.main_pane.add(left_panel, weight=1)
        
        # Titre section
        modules_label = ttk.Label(left_panel, text="Main Tools", font=("Arial", 12, "bold"))
        modules_label.pack(pady=(0, 10))
        
        # Creer les boutons pour chaque module
        for module_key, module_info in self.modules.items():
            self.create_module_button(left_panel, module_key, module_info)
        
        # Bouton refresh
        ttk.Button(left_panel, text="Refresh Interface", 
                  command=self.refresh_interface).pack(pady=20)
        
        # Message status
        self.status_label = ttk.Label(left_panel, text="All systems are ready")
        self.status_label.pack(side=tk.BOTTOM, pady=10)
    
    def create_module_button(self, parent, module_key, module_info):
        """Cree un bouton pour un module."""
        
        # Frame pour le module
        module_frame = ttk.LabelFrame(parent, text=module_info["name"], padding=10)
        module_frame.pack(fill=tk.X, pady=5)
        
        # Status
        status_label = ttk.Label(module_frame, text="Status: " + module_info["status"])
        status_label.pack(anchor=tk.W)
        
        # Bouton launch
        launch_btn = ttk.Button(module_frame, text="Launch",
                               command=lambda mk=module_key: self.launch_module(mk))
        launch_btn.pack(pady=(5, 0))
    
    def launch_module(self, module_key):
        """Lance un module."""
        
        if module_key not in self.modules:
            print("Module non trouve: " + module_key)
            return
        
        module_info = self.modules[module_key]
        self.status_label.config(text="Launching " + module_info["name"] + "...")
        
        print("Lancement: " + module_info["name"])
        
        # Mode de lancement
        if module_info["launch_mode"] == "integrated":
            self.launch_integrated(module_key, module_info)
        else:
            self.launch_external(module_key, module_info)
    
    def launch_integrated(self, module_key, module_info):
        """Lance un module en mode integre."""
        
        try:
            # Fermer l'interface integree actuelle si elle existe
            if self.active_integrated_frame:
                try:
                    self.active_integrated_frame.destroy()
                except:
                    pass
                self.active_integrated_frame = None
            
            # Import dynamique du module AST
            if "AST" in module_key:
                script_path = Path(module_info["script"])
                
                if not script_path.exists():
                    self.status_label.config(text="Script non trouve: " + str(script_path))
                    return
                
                # Ajouter le chemin au sys.path
                module_dir = script_path.parent
                if str(module_dir) not in sys.path:
                    sys.path.insert(0, str(module_dir))
                
                # Import du module
                import importlib.util
                module_name = script_path.stem
                spec = importlib.util.spec_from_file_location(module_name, script_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Creer l'interface AST simple (sans callback)
                self.active_integrated_frame = module.InterfaceAST(self.main_pane)
                self.main_pane.add(self.active_integrated_frame, weight=2)
                
                self.status_label.config(text="Interface AST active - Version stable")
            
            else:
                # Autres modules (implementation future)
                self.status_label.config(text="Mode integre non implemente pour ce module")
        
        except Exception as e:
            self.status_label.config(text="Erreur: " + str(e))
            print("Erreur lancement integre: " + str(e))
            import traceback
            traceback.print_exc()
    
    def launch_external(self, module_key, module_info):
        """Lance un module en mode externe."""
        
        try:
            script_path = Path(module_info["script"])
            
            if not script_path.exists():
                self.status_label.config(text="Script non trouve: " + str(script_path))
                return
            
            # Lancement externe
            subprocess.Popen([sys.executable, str(script_path)], 
                           cwd=str(script_path.parent))
            
            self.status_label.config(text=module_info["name"] + " lance en mode externe")
        
        except Exception as e:
            self.status_label.config(text="Erreur lancement: " + str(e))
            print("Erreur lancement externe: " + str(e))
    
    def refresh_interface(self):
        """Rafraichit l'interface."""
        if self.active_integrated_frame:
            try:
                self.active_integrated_frame.destroy()
            except:
                pass
            self.active_integrated_frame = None
        
        self.status_label.config(text="Interface rafraichie")
    
    def run(self):
        """Lance l'application."""
        self.root.mainloop()

def main():
    """Point d'entree principal."""
    app = SystemManager()
    app.run()

if __name__ == "__main__":
    main()
