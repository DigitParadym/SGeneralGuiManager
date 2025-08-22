#!/usr/bin/env python3
"""
Script de nettoyage du projet AST Tools
1. Sauvegarde Git de l'etat actuel
2. Supprime les fichiers .py non necessaires
3. Prepare le projet pour les nouveaux plugins
"""

import os
import subprocess
import shutil
from pathlib import Path
from datetime import datetime

class NettoyeurProjet:
    def __init__(self):
        self.projet_path = Path(".")
        self.core_path = Path("core")
        
        # Fichiers essentiels a conserver
        self.fichiers_essentiels = {
            # Fichiers principaux
            "AST.py",
            "main.py", 
            "modificateur_interactif.py",
            "execution.py",
            "__init__.py",
            
            # Fichiers core essentiels
            "core/base_transformer.py",
            "core/models.py",
            "core/global_logger.py", 
            "core/transformation_loader.py",
            "core/ast_logger.py",
            "core/__init__.py"
        }
        
        # Patterns de fichiers a supprimer
        self.patterns_a_supprimer = [
            "*_backup_*.py",           # Sauvegardes automatiques
            "fix_*.py",                # Scripts de correction
            "diagnostic_*.py",         # Scripts de diagnostic  
            "creer_*.py",             # Scripts de creation
            "nettoyage_*.py",         # Scripts de nettoyage
            "test_*.py",              # Fichiers de test temporaires
            "temp_*.py",              # Fichiers temporaires
            "*.tmp",                   # Fichiers temporaires
            "*.bak",                   # Sauvegardes
            "__pycache__/*",          # Cache Python
            "*.pyc",                   # Bytecode Python
        ]
        
        self.fichiers_supprimes = []
        self.taille_liberee = 0

    def git_sauvegarde(self):
        """Fait un git add pour sauvegarder l'etat actuel"""
        print("GIT SAUVEGARDE DE L'ETAT ACTUEL")
        print("=" * 40)
        
        try:
            # Verifier si on est dans un repo git
            result = subprocess.run(["git", "status"], 
                                  capture_output=True, text=True)
            
            if result.returncode != 0:
                print("Pas un repository Git - initialisation...")
                subprocess.run(["git", "init"], check=True)
                print("Repository Git initialise")
            
            # Ajouter tous les fichiers
            subprocess.run(["git", "add", "."], check=True)
            print("Tous les fichiers ajoutes au staging")
            
            # Commit avec timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            message = f"Sauvegarde avant nettoyage AST Tools - {timestamp}"
            
            subprocess.run(["git", "commit", "-m", message], 
                         check=True, capture_output=True)
            print(f"Commit cree: {message}")
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"Erreur Git: {e}")
            return False
        except FileNotFoundError:
            print("Git non installe - sauvegarde ignoree")
            return False

    def lister_fichiers_projet(self):
        """Liste tous les fichiers .py du projet"""
        fichiers_py = []
        
        # Fichiers a la racine
        for fichier in self.projet_path.glob("*.py"):
            fichiers_py.append(str(fichier))
            
        # Fichiers dans core/
        if self.core_path.exists():
            for fichier in self.core_path.glob("*.py"):
                fichiers_py.append(str(fichier))
                
        # Fichiers dans sous-dossiers
        for fichier in self.projet_path.rglob("*.py"):
            if str(fichier) not in fichiers_py:
                fichiers_py.append(str(fichier))
                
        return fichiers_py

    def analyser_fichiers(self):
        """Analyse quels fichiers garder/supprimer"""
        print("\nANALYSE DES FICHIERS DU PROJET")
        print("=" * 35)
        
        tous_fichiers = self.lister_fichiers_projet()
        print(f"Fichiers .py trouves: {len(tous_fichiers)}")
        
        fichiers_a_garder = []
        fichiers_a_supprimer = []
        
        for fichier in tous_fichiers:
            fichier_path = Path(fichier)
            fichier_relatif = str(fichier_path.relative_to(self.projet_path))
            
            # Verifier si essentiel
            if fichier_relatif in self.fichiers_essentiels:
                fichiers_a_garder.append(fichier)
                continue
                
            # Verifier patterns a supprimer
            doit_supprimer = False
            for pattern in self.patterns_a_supprimer:
                if fichier_path.match(pattern) or fichier_relatif.endswith(tuple(pattern.split('*')[-1:])):
                    doit_supprimer = True
                    break
                    
            if doit_supprimer:
                fichiers_a_supprimer.append(fichier)
            else:
                # Fichier non reconnu - demander confirmation
                print(f"Fichier non categorise: {fichier_relatif}")
                fichiers_a_garder.append(fichier)  # Par securite
        
        return fichiers_a_garder, fichiers_a_supprimer

    def afficher_plan_nettoyage(self, a_garder, a_supprimer):
        """Affiche le plan de nettoyage"""
        print(f"\nPLAN DE NETTOYAGE")
        print("=" * 20)
        
        print(f"\nFichiers a GARDER ({len(a_garder)}):")
        for fichier in sorted(a_garder):
            taille = Path(fichier).stat().st_size if Path(fichier).exists() else 0
            print(f"  ✅ {Path(fichier).relative_to(self.projet_path)} ({taille} bytes)")
            
        print(f"\nFichiers a SUPPRIMER ({len(a_supprimer)}):")
        taille_totale = 0
        for fichier in sorted(a_supprimer):
            if Path(fichier).exists():
                taille = Path(fichier).stat().st_size
                taille_totale += taille
                print(f"  ❌ {Path(fichier).relative_to(self.projet_path)} ({taille} bytes)")
            else:
                print(f"  ❌ {Path(fichier).relative_to(self.projet_path)} (introuvable)")
                
        print(f"\nEspace a liberer: {taille_totale} bytes ({taille_totale/1024:.1f} KB)")
        return taille_totale

    def executer_nettoyage(self, fichiers_a_supprimer):
        """Execute le nettoyage"""
        print(f"\nEXECUTION DU NETTOYAGE")
        print("=" * 25)
        
        for fichier in fichiers_a_supprimer:
            try:
                fichier_path = Path(fichier)
                if fichier_path.exists():
                    taille = fichier_path.stat().st_size
                    fichier_path.unlink()
                    self.fichiers_supprimes.append(fichier)
                    self.taille_liberee += taille
                    print(f"  Supprime: {fichier_path.relative_to(self.projet_path)}")
                else:
                    print(f"  Deja supprime: {fichier_path.relative_to(self.projet_path)}")
                    
            except Exception as e:
                print(f"  Erreur suppression {fichier}: {e}")

    def nettoyer_dossiers_vides(self):
        """Supprime les dossiers vides"""
        print(f"\nSUPPRESSION DOSSIERS VIDES")
        print("=" * 30)
        
        dossiers_supprimes = 0
        for dossier in self.projet_path.rglob("*"):
            if (dossier.is_dir() and 
                dossier.name != ".git" and
                not any(dossier.iterdir())):  # Dossier vide
                try:
                    dossier.rmdir()
                    print(f"  Dossier vide supprime: {dossier.relative_to(self.projet_path)}")
                    dossiers_supprimes += 1
                except Exception as e:
                    print(f"  Erreur suppression dossier {dossier}: {e}")
                    
        if dossiers_supprimes == 0:
            print("  Aucun dossier vide trouve")

    def afficher_rapport_final(self):
        """Affiche le rapport final"""
        print(f"\n" + "=" * 50)
        print(f"RAPPORT FINAL DE NETTOYAGE")
        print("=" * 50)
        
        print(f"Fichiers supprimes: {len(self.fichiers_supprimes)}")
        print(f"Espace libere: {self.taille_liberee} bytes ({self.taille_liberee/1024:.1f} KB)")
        
        print(f"\nFichiers essentiels conserves:")
        for fichier in sorted(self.fichiers_essentiels):
            if Path(fichier).exists():
                print(f"  ✅ {fichier}")
            else:
                print(f"  ⚠️  {fichier} (manquant)")
                
        print(f"\nProjet nettoye et pret pour les nouveaux plugins !")

    def executer_nettoyage_complet(self):
        """Execute le nettoyage complet"""
        print("NETTOYAGE COMPLET AST TOOLS")
        print("=" * 30)
        
        # 1. Sauvegarde Git
        if not self.git_sauvegarde():
            reponse = input("\nGit echec. Continuer sans sauvegarde ? (y/N): ")
            if reponse.lower() != 'y':
                print("Nettoyage annule")
                return
        
        # 2. Analyse des fichiers
        a_garder, a_supprimer = self.analyser_fichiers()
        
        # 3. Afficher le plan
        taille_a_liberer = self.afficher_plan_nettoyage(a_garder, a_supprimer)
        
        # 4. Confirmation
        if a_supprimer:
            print(f"\n⚠️  ATTENTION: {len(a_supprimer)} fichiers seront supprimes !")
            reponse = input("Continuer le nettoyage ? (y/N): ")
            if reponse.lower() != 'y':
                print("Nettoyage annule")
                return
        else:
            print("\nAucun fichier a supprimer - projet deja propre")
            return
        
        # 5. Execution
        self.executer_nettoyage(a_supprimer)
        self.nettoyer_dossiers_vides()
        
        # 6. Rapport final
        self.afficher_rapport_final()

def main():
    """Fonction principale"""
    nettoyeur = NettoyeurProjet()
    nettoyeur.executer_nettoyage_complet()

if __name__ == "__main__":
    main()