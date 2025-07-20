# Fichier : AST_tools/lancer_ast_tool.py
import sys
import os

# SUIVI: Le script externe a démarré.
print("--- Lancement du script 'lancer_ast_tool.py' ---")

try:
    print("="*50)
    print("🚀 L'outil d'analyse AST a été lancé avec succès !")
    print("="*50)

    if len(sys.argv) > 1:
        folder_path = sys.argv[1]
        print(f"Dossier reçu pour analyse : {folder_path}")
        # SUIVI: Vérification si le dossier existe.
        if not os.path.isdir(folder_path):
            print(f"\nERREUR: Le dossier '{folder_path}' est introuvable.")
    else:
        print("Aucun dossier n'a été passé en argument.")

    print("\nC'est ici que vous mettriez votre logique d'analyse de code.")
    # Exemple d'erreur pour tester le suivi :
    # x = 1 / 0

except Exception as e:
    # SUIVI: Une erreur est survenue pendant l'exécution du script.
    print("\n" + "="*50)
    print(f"ERREUR CRITIQUE DANS L'OUTIL AST : {e}")
    print("="*50)
    # Affiche l'erreur sur la sortie d'erreur standard également
    sys.stderr.write(f"Erreur dans lancer_ast_tool.py: {e}\n")

finally:
    # SUIVI: Le script a atteint la fin de son exécution.
    print("\n--- Fin du script. En attente de la fermeture manuelle. ---")
    input("\nAppuyez sur Entrée pour fermer cette fenêtre.")