# -*- coding: utf-8 -*-
# force_build.py
# Ce script automatise la reconstruction d'une application PyInstaller.
# Il force la fermeture des processus existants, nettoie les anciens dossiers de build,
# et lance une nouvelle compilation à partir d'un fichier .spec.

import os
import subprocess
import shutil
import time

# --- CONFIGURATION ---
# Nom de l'exécutable à chercher et à fermer.
TARGET_EXE_NAME = "copypaste_manager.exe"
# Nom du fichier de configuration PyInstaller à utiliser pour la compilation.
SPEC_FILE_NAME = "copypaste_manager.spec"
# --------------------

def kill_process(exe_name):
    """
    Tente de forcer la fermeture d'un processus par son nom d'exécutable.
    Cette fonction est spécifique à Windows et utilise la commande 'taskkill'.
    """
    print(f"[INFO] Tentative de fermeture du processus : {exe_name}")
    # /F force la fermeture.
    # /IM spécifie le nom de l'image (exécutable).
    # stderr=subprocess.DEVNULL ignore les messages d'erreur si le processus n'est pas trouvé.
    try:
        result = subprocess.run(
            ["taskkill", "/F", "/IM", exe_name],
            capture_output=True, text=True, check=False
        )
        if "SUCCESS" in result.stdout:
            print(f"[OK] Processus {exe_name} terminé avec succès.")
            time.sleep(1) # Laisse un court instant au système pour libérer le fichier.
        else:
            print(f"[INFO] Le processus {exe_name} n'était pas en cours d'exécution.")
    except FileNotFoundError:
        print("[AVERTISSEMENT] La commande 'taskkill' n'a pas été trouvée. Impossible de forcer la fermeture du processus.")
    except Exception as e:
        print(f"[ERREUR] Une erreur inattendue est survenue lors de la tentative de fermeture du processus : {e}")

def clean_directories():
    """
    Supprime les anciens dossiers 'build' et 'dist' pour assurer une compilation propre.
    """
    dirs_to_clean = ['build', 'dist']
    print("[INFO] Nettoyage des anciens dossiers de compilation...")
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            try:
                shutil.rmtree(dir_name)
                print(f"[OK] Dossier '{dir_name}' supprimé.")
            except OSError as e:
                print(f"[ERREUR] Impossible de supprimer le dossier '{dir_name}': {e}")
                print("         Veuillez le fermer si un explorateur de fichiers l'utilise.")
                return False
    return True

def build_with_pyinstaller(spec_file):
    """
    Lance la compilation avec PyInstaller en utilisant le fichier .spec fourni.
    """
    if not os.path.exists(spec_file):
        print(f"[ERREUR] Le fichier .spec '{spec_file}' n'a pas été trouvé.")
        return False
        
    print(f"[INFO] Lancement de PyInstaller avec '{spec_file}'...")
    try:
        # 'check=True' lèvera une exception si PyInstaller retourne un code d'erreur.
        subprocess.run(["pyinstaller", spec_file], check=True)
        print("[OK] Compilation terminée avec succès.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERREUR] La compilation avec PyInstaller a échoué : {e}")
        return False
    except FileNotFoundError:
        print("[ERREUR] La commande 'pyinstaller' n'est pas reconnue.")
        print("         Veuillez vérifier que PyInstaller est installé et dans votre PATH système.")
        return False

def main():
    """
    Fonction principale qui orchestre les étapes de nettoyage et de compilation.
    """
    print("==================================================")
    print("=== SCRIPT DE FORCAGE DE COMPILATION PYINSTALLER ===")
    print("==================================================")

    # 1. Tuer le processus existant pour éviter les erreurs de permission.
    kill_process(TARGET_EXE_NAME)
    
    # 2. Nettoyer les dossiers de la compilation précédente.
    if not clean_directories():
        return # Arrêter le script si le nettoyage échoue.
        
    # 3. Reconstruire l'application à partir du fichier .spec.
    if build_with_pyinstaller(SPEC_FILE_NAME):
        print(f"\n[SUCCES] Votre application a été reconstruite dans le dossier 'dist'.")
        print(f"         Vous pouvez trouver l'exécutable ici : dist\\{TARGET_EXE_NAME}")
    else:
        print("\n[ECHEC] La reconstruction a échoué. Veuillez vérifier les messages d'erreur ci-dessus.")

if __name__ == "__main__":
    main()
    input("\nAppuyez sur Entrée pour fermer...")
