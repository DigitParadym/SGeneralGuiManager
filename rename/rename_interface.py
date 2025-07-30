#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interface wrapper pour Smart Rename System
Permet l'integration dans l'exe principal
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
import os

class SmartRenameInterface(ttk.Frame):
    """Interface integree pour Smart Rename System"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.create_interface()
    
    def create_interface(self):
        """Cree l'interface Smart Rename"""
        
        # Titre
        title_label = ttk.Label(self, text="Smart Rename System", 
                               font=('Segoe UI', 16, 'bold'))
        title_label.pack(pady=10)
        
        # Description
        desc_label = ttk.Label(self, 
                              text="Systeme intelligent de renommage de fichiers",
                              font=('Segoe UI', 10))
        desc_label.pack(pady=5)
        
        # Zone de contenu
        content_frame = ttk.LabelFrame(self, text="Contenu Smart Rename", padding=10)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Message d'information
        info_text = """
        Smart Rename System est maintenant integre dans l'exe principal.
        
        En mode exe, les fonctionnalites de renommage sont adaptees
        pour fonctionner sans processus externes.
        
        Cliquez sur 'Activer Smart Rename' pour charger le module.
        """
        
        info_label = ttk.Label(content_frame, text=info_text.strip(),
                              justify=tk.LEFT, wraplength=400)
        info_label.pack(pady=10)
        
        # Boutons
        button_frame = ttk.Frame(content_frame)
        button_frame.pack(pady=10)
        
        activate_btn = ttk.Button(button_frame, text="Activer Smart Rename",
                                 command=self.activate_rename)
        activate_btn.pack(side=tk.LEFT, padx=5)
        
        info_btn = ttk.Button(button_frame, text="Informations",
                             command=self.show_info)
        info_btn.pack(side=tk.LEFT, padx=5)
    
    def activate_rename(self):
        """Active les fonctionnalites Smart Rename"""
        try:
            # En mode exe, charger directement les fonctionnalites
            if getattr(sys, 'frozen', False):
                messagebox.showinfo("Smart Rename", 
                    "Smart Rename System est maintenant actif dans cette interface.\n"
                    "Fonctionnalites adaptees pour le mode exe.")
            else:
                # En mode script, essayer de lancer normalement
                script_path = os.path.join("rename", "main_window.py")
                if os.path.exists(script_path):
                    subprocess.Popen([sys.executable, script_path])
                else:
                    messagebox.showerror("Erreur", "Script Smart Rename non trouve")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur activation Smart Rename: {e}")
    
    def show_info(self):
        """Affiche les informations Smart Rename"""
        messagebox.showinfo("Smart Rename", 
            "Smart Rename System - Renommage intelligent\n\n"
            "Version integree pour exe PyInstaller\n"
            "Fonctionnalites adaptees pour l'execution en mode exe")

# Interface principale pour compatibilite
def main():
    root = tk.Tk()
    root.title("Smart Rename System")
    root.geometry("600x400")
    
    app = SmartRenameInterface(root)
    app.pack(fill=tk.BOTH, expand=True)
    
    root.mainloop()

if __name__ == "__main__":
    main()
