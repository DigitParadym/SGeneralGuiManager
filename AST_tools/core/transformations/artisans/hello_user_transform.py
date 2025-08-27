#!/usr/bin/env python3
"""
Plugin Hello User Transform pour AST_tools
Ajoute une interaction utilisateur au debut du programme
"""

import sys
from pathlib import Path

# Import correct pour la nouvelle structure
parent_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(parent_dir))

from core.transformations.base.base_transformer import BaseTransformer


class HelloUserTransform(BaseTransformer):
    """Transformateur qui ajoute une interaction Hello User"""
    
    def __init__(self):
        super().__init__()
        self.name = "Hello User Transform"
        self.description = "Ajoute une demande de nom et affiche Hello + nom"
        self.version = "1.0.0"
        self.author = "AST_tools"
    
    def get_metadata(self):
        """Retourne les metadonnees du transformateur"""
        return {
            'name': self.name,
            'description': self.description,
            'version': self.version,
            'author': self.author
        }
    
    def transform(self, code_source):
        """
        Transforme le code pour ajouter l'interaction utilisateur
        
        Args:
            code_source (str): Code source original
            
        Returns:
            str: Code source transforme avec interaction utilisateur
        """
        try:
            print("Application Hello User Transform...")
            
            # Separer le code en lignes
            lignes = code_source.split('\n')
            nouvelles_lignes = []
            
            # Variables pour tracker ou on est dans le code
            imports_done = False
            interaction_added = False
            
            for i, ligne in enumerate(lignes):
                # Garder tous les imports et commentaires du debut
                if not imports_done:
                    if ligne.strip().startswith('#') or 'import' in ligne or ligne.strip() == '':
                        nouvelles_lignes.append(ligne)
                    else:
                        # On a fini les imports, ajouter l'interaction
                        imports_done = True
                        
                        if not interaction_added:
                            # Ajouter l'interaction utilisateur
                            nouvelles_lignes.append('')
                            nouvelles_lignes.append('# === Interaction utilisateur ajoutee par AST_tools ===')
                            nouvelles_lignes.append('nom_utilisateur = input("Quel est votre nom ? ")')
                            nouvelles_lignes.append('print(f"Hello {nom_utilisateur}!")')
                            nouvelles_lignes.append('print("-" * 50)')
                            nouvelles_lignes.append('')
                            interaction_added = True
                        
                        # Ajouter la ligne courante
                        nouvelles_lignes.append(ligne)
                else:
                    # Modifier les print existants pour inclure le nom
                    if 'print(' in ligne:
                        # Si c'est un print simple, le personnaliser
                        if 'Script starting' in ligne:
                            ligne = ligne.replace(
                                'Script starting...', 
                                'Script starting for {nom_utilisateur}...'
                            )
                            # Corriger le formatage
                            ligne = ligne.replace('print("', 'print(f"')
                        elif 'Fin du programme' in ligne:
                            ligne = ligne.replace(
                                'Fin du programme',
                                'Au revoir {nom_utilisateur}!'
                            )
                            ligne = ligne.replace('print("', 'print(f"')
                    
                    nouvelles_lignes.append(ligne)
            
            # Si on n'a jamais ajoute l'interaction (fichier vide ou que des imports)
            if not interaction_added:
                nouvelles_lignes.append('')
                nouvelles_lignes.append('# === Interaction utilisateur ajoutee par AST_tools ===')
                nouvelles_lignes.append('nom_utilisateur = input("Quel est votre nom ? ")')
                nouvelles_lignes.append('print(f"Hello {nom_utilisateur}!")')
                nouvelles_lignes.append('')
            
            # Ajouter un message de fin si on a un bloc __main__
            code_transforme = '\n'.join(nouvelles_lignes)
            
            if '__name__ == "__main__"' in code_transforme:
                # Ajouter un au revoir a la fin du main
                lignes_finales = code_transforme.split('\n')
                resultat = []
                in_main = False
                
                for ligne in lignes_finales:
                    resultat.append(ligne)
                    if '__name__ == "__main__"' in ligne:
                        in_main = True
                
                # Ajouter le message de fin avant la derniere ligne si on est dans main
                if in_main:
                    message_fin = '    print(f"Merci {nom_utilisateur} pour avoir utilise ce programme!")'
                    resultat.insert(-1, message_fin)
                
                code_transforme = '\n'.join(resultat)
            
            print("  [OK] Interaction utilisateur ajoutee")
            print("  [OK] Messages personnalises avec le nom")
            
            return code_transforme
            
        except Exception as e:
            print(f"Erreur Hello User Transform: {e}")
            return code_source
    
    def can_transform(self, code_source):
        """Verifie si la transformation peut s'appliquer"""
        # On peut toujours ajouter une interaction utilisateur
        # Sauf si elle existe deja
        return 'nom_utilisateur = input(' not in code_source
