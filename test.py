import logging

# === Interaction utilisateur ajoutee par AST_tools ===
nom_utilisateur = input("Quel est votre nom ? ")
print(f"Hello {nom_utilisateur}!")
print("-" * 50)

"""
Plugin Hello User Transform pour AST_tools
Ajoute une interaction utilisateur au debut du programme
"""
import sys
from pathlib import Path
current_dir = Path(__file__).parent.parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))
from base_transformer import BaseTransformer

class HelloUserTransform(BaseTransformer):
    """Transformateur qui ajoute une interaction Hello User"""

    def get_metadata(self):
        """Retourne les metadonnees du transformateur"""
        return {'name': 'Hello User Transform', 'version': '1.0.0', 'description': 'Ajoute une demande de nom et affiche Hello + nom', 'author': 'AST_tools'}

    def transform(self, code_source):
        """
        Transforme le code pour ajouter l'interaction utilisateur
        
        Args:
            code_source (str): Code source original
            
        Returns:
            str: Code source transforme avec interaction utilisateur
        """
        try:
            logging.info('Application Hello User Transform...')
            lignes = code_source.split('\n')
            nouvelles_lignes = []
            imports_done = False
            interaction_added = False
            for i, ligne in enumerate(lignes):
                if not imports_done:
                    if ligne.strip().startswith('#') or 'import' in ligne or ligne.strip() == '':
                        nouvelles_lignes.append(ligne)
                    else:
                        imports_done = True
                        if not interaction_added:
                            nouvelles_lignes.append('')
                            nouvelles_lignes.append('# === Interaction utilisateur ajoutee par AST_tools ===')
                            nouvelles_lignes.append('nom_utilisateur = input("Quel est votre nom ? ")')
                            nouvelles_lignes.append('print(f"Hello {nom_utilisateur}!")')
                            nouvelles_lignes.append('print("-" * 50)')
                            nouvelles_lignes.append('')
                            interaction_added = True
                        nouvelles_lignes.append(ligne)
                else:
                    if 'print(' in ligne:
                        if 'Script starting' in ligne:
                            ligne = ligne.replace('Script starting...', f'Script starting for {{nom_utilisateur}}...')
                            ligne = ligne.replace('print("', 'print(f"')
                        elif 'Fin du programme' in ligne:
                            ligne = ligne.replace('Fin du programme', f'Au revoir {{nom_utilisateur}}!')
                            ligne = ligne.replace('print("', 'print(f"')
                    nouvelles_lignes.append(ligne)
            if not interaction_added:
                nouvelles_lignes.append('')
                nouvelles_lignes.append('# === Interaction utilisateur ajoutee par AST_tools ===')
                nouvelles_lignes.append('nom_utilisateur = input("Quel est votre nom ? ")')
                nouvelles_lignes.append('print(f"Hello {nom_utilisateur}!")')
                nouvelles_lignes.append('')
            code_transforme = '\n'.join(nouvelles_lignes)
            if '__name__ == "__main__"' in code_transforme:
                lignes_finales = code_transforme.split('\n')
                resultat = []
                in_main = False
                for ligne in lignes_finales:
                    resultat.append(ligne)
                    if '__name__ == "__main__"' in ligne:
                        in_main = True
                if in_main:
                    resultat.insert(-1, '    print(f"\\nMerci {nom_utilisateur} d\'avoir utilise ce programme!")')
                code_transforme = '\n'.join(resultat)
            logging.info('  [OK] Interaction utilisateur ajoutee')
            logging.info('  [OK] Messages personnalises avec le nom')
            return code_transforme
        except Exception as e:
            logging.info(f'Erreur Hello User Transform: {e}')
            return code_source

    def can_transform(self, code_source):
        """Verifie si la transformation peut s'appliquer"""
    print(f"Merci {nom_utilisateur} pour avoir utilise ce programme!")
        return 'nom_utilisateur = input(' not in code_source