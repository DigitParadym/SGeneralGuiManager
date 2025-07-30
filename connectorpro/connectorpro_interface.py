#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
INTERFACE CONNECTORPRO INTEGREE
Wrapper pour integrer ConnectorPro dans le SystemManager
Compatible compilation .exe
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
from pathlib import Path

class ConnectorProInterface(ttk.Frame):
    """Interface integree pour ConnectorPro"""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        # Configuration du frame
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        
        # Variables
        self.connectorpro_app = None
        
        # Interface utilisateur
        self.create_ui()
        self.init_connectorpro()
    
    def create_ui(self):
        """Cree l'interface utilisateur"""
        
        # En-tete
        header_frame = ttk.Frame(self)
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        ttk.Label(
            header_frame,
            text="ConnectorPro - Interface Integree",
            font=("Segoe UI", 14, "bold")
        ).pack(side=tk.LEFT)
        
        self.status_label = ttk.Label(
            header_frame,
            text="Initialisation...",
            foreground="orange"
        )
        self.status_label.pack(side=tk.RIGHT)
        
        # Zone principale - Conteneur pour ConnectorPro
        self.main_container = ttk.Frame(self)
        self.main_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.main_container.columnconfigure(0, weight=1)
        self.main_container.rowconfigure(0, weight=1)
        
        # Message temporaire
        self.temp_label = ttk.Label(
            self.main_container,
            text="Chargement de ConnectorPro...\nVeuillez patienter...",
            justify=tk.CENTER
        )
        self.temp_label.grid(row=0, column=0)
    
    def init_connectorpro(self):
        """Initialise ConnectorPro"""
        try:
            # Ajouter le chemin du projet
            project_root = Path(__file__).parent.parent
            if str(project_root) not in sys.path:
                sys.path.insert(0, str(project_root))
            
            # Import conditionnel de ConnectorPro
            try:
                from connectorpro.gui_component import create_main_interface
                
                # Supprimer le message temporaire
                self.temp_label.destroy()
                
                # Creer l'interface ConnectorPro dans notre conteneur
                self.connectorpro_app = create_main_interface(self.main_container)
                
                if self.connectorpro_app:
                    # Configurer l'interface ConnectorPro pour qu'elle remplisse l'espace
                    self.connectorpro_app.pack(fill="both", expand=True)
                    self.status_label.config(text="Pret", foreground="green")
                    self.log_message("ConnectorPro initialise avec succes")
                else:
                    self.show_fallback_interface("Interface ConnectorPro non creee")
                    
            except ImportError as e:
                self.show_fallback_interface(f"Import ConnectorPro echoue: {e}")
            except Exception as e:
                self.show_fallback_interface(f"Erreur ConnectorPro: {e}")
                
        except Exception as e:
            self.show_fallback_interface(f"Erreur generale: {e}")
    
    def show_fallback_interface(self, error_msg):
        """Affiche une interface de remplacement en cas d'erreur"""
        
        # Supprimer le message temporaire
        try:
            self.temp_label.destroy()
        except:
            pass
        
        # Interface de remplacement
        fallback_frame = ttk.LabelFrame(self.main_container, text="ConnectorPro - Non Disponible")
        fallback_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        ttk.Label(
            fallback_frame,
            text="ConnectorPro n'est pas disponible",
            font=("Segoe UI", 12, "bold"),
            foreground="red"
        ).pack(pady=10)
        
        ttk.Label(
            fallback_frame,
            text=f"Erreur: {error_msg}",
            wraplength=400,
            justify=tk.CENTER
        ).pack(pady=5)
        
        ttk.Label(
            fallback_frame,
            text="Solutions possibles:\n1. Verifier que connectorpro/gui_component.py existe\n2. Verifier les dependances ConnectorPro\n3. Redemarrer l'application",
            justify=tk.LEFT
        ).pack(pady=10)
        
        ttk.Button(
            fallback_frame,
            text="Reessayer",
            command=self.retry_init
        ).pack(pady=10)
        
        self.status_label.config(text="Erreur", foreground="red")
        self.log_message(f"Erreur ConnectorPro: {error_msg}")
    
    def retry_init(self):
        """Retente l'initialisation"""
        # Nettoyer le conteneur
        for widget in self.main_container.winfo_children():
            widget.destroy()
        
        # Recreer le message temporaire
        self.temp_label = ttk.Label(
            self.main_container,
            text="Nouvelle tentative...\nChargement ConnectorPro...",
            justify=tk.CENTER
        )
        self.temp_label.grid(row=0, column=0)
        
        # Retenter l'initialisation
        self.after(1000, self.init_connectorpro)
    
    def log_message(self, message):
        """Log les messages (pour debug)"""
        print(f"[ConnectorProInterface] {message}")

# Test autonome
if __name__ == "__main__":
    root = tk.Tk()
    root.title("ConnectorPro Interface - Test")
    root.geometry("800x600")
    
    app = ConnectorProInterface(root)
    app.pack(fill="both", expand=True, padx=10, pady=10)
    
    root.mainloop()
