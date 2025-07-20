import tkinter as tk
from tkinter import ttk

class InterfaceAST(ttk.Frame):
    """
    L'interface graphique principale pour l'outil de transformation AST.
    Cette classe est conçue pour être intégrée dans une fenêtre parente.
    """
    def __init__(self, parent):
        """
        Initialise le cadre (Frame) de l'interface.
        
        La correction clé est ici :
        - On accepte 'parent' comme argument.
        - On passe 'parent' à la méthode super().__init__().
        """
        super().__init__(parent)

        # Configuration de la grille pour ce Frame
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # --- Widgets de l'interface ---

        # Titre
        titre_label = ttk.Label(self, text="Interface de Transformation AST", font=("Segoe UI", 12, "bold"))
        titre_label.grid(row=0, column=0, pady=(10, 20), padx=20, sticky="w")

        # Zone principale (pour l'instant un simple message)
        placeholder_text = ("C'est ici que vous construirez votre interface.\n\n"
                            "Par exemple, des zones de texte pour le code source, "
                            "des listes pour les transformations, et des boutons "
                            "pour appliquer les changements.")
        
        placeholder_label = ttk.Label(self, text=placeholder_text, justify="center", wraplength=400)
        placeholder_label.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)