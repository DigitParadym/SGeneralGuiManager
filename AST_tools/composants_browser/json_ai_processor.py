"""
Module JSON AI Processor - Version minimale de secours
Cree automatiquement pour reparer les erreurs de syntaxe
"""

import json
import os
from pathlib import Path


class AnalyseurJSONAI:
    """Analyseur et validateur pour les fichiers JSON de transformations AI."""

    def __init__(self):
        self.schema_version = "1.0"
        self.transformations_supportees = {
            "ajout",
            "substitution",
            "suppression",
            "remplacement_bloc",
        }

    def charger_json_ai(self, chemin_json):
        """Charge et valide un fichier JSON de transformations AI."""
        try:
            with open(chemin_json, encoding="utf-8") as f:
                data = json.load(f)

            if not self.valider_structure(data):
                return None

            print(f"+ JSON AI charge: {len(data.get('transformations', []))} transformations")
            return data

        except json.JSONDecodeError as e:
            print(f"X Erreur format JSON: {e}")
            return None
        except FileNotFoundError:
            print(f"X Fichier JSON non trouve: {chemin_json}")
            return None
        except Exception as e:
            print(f"X Erreur chargement JSON: {e}")
            return None

    def valider_structure(self, data):
        """Valide la structure du JSON AI."""
        champs_requis = ["version", "transformations"]
        for champ in champs_requis:
            if champ not in data:
                print(f"X Champ obligatoire manquant: {champ}")
                return False

        transformations = data.get("transformations", [])
        for i, transform in enumerate(transformations):
            if not self.valider_transformation(transform, i):
                return False

        print(f"+ Structure JSON validee: {len(transformations)} transformations")
        return True

    def valider_transformation(self, transform, index):
        """Valide une transformation individuelle."""
        champs_requis = ["type", "instruction"]
        for champ in champs_requis:
            if champ not in transform:
                print(f"X Transformation {index}: champ '{champ}' manquant")
                return False

        instruction = transform["instruction"]
        if "type" not in instruction:
            print(f"X Transformation {index}: type d'instruction manquant")
            return False

        type_instruction = instruction["type"]
        if type_instruction not in self.transformations_supportees:
            print(f"X Transformation {index}: type '{type_instruction}' non supporte")
            return False

        return True


# Fonctions utilitaires
def format_taille(size_bytes):
    """Formate la taille en bytes de maniere lisible."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024**2:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024**2):.1f} MB"


def creer_structure_sortie(fichiers_source, nom_dossier):
    """Cree la structure de sortie pour les transformations."""
    dossier_sortie = Path(nom_dossier)
    dossier_sortie.mkdir(exist_ok=True)

    mapping_fichiers = {}
    for fichier_source in fichiers_source:
        nom_base = Path(fichier_source).name
        fichier_sortie = dossier_sortie / nom_base
        mapping_fichiers[fichier_source] = fichier_sortie

    return dossier_sortie, mapping_fichiers


def launch_file_selector_with_fallback():
    """Fonction de selection de fichiers de fallback."""
    print("Selection de fichiers (entrez les chemins separes par des espaces):")
    try:
        paths = input("Fichiers: ").strip().split()
        return [p for p in paths if Path(p).exists()]
    except (KeyboardInterrupt, EOFError):
        return []


def gerer_sortie_environnement(sortie, mode):
    """Gestionnaire de sortie d'environnement."""
    print(f"Sortie {mode} geree: {sortie}")


def selectionner_json_ai():
    """Interface pour selectionner le fichier JSON AI."""
    print("*** SELECTION JSON AI ***")
    print("=" * 25)

    fichiers_json = []
    try:
        for fichier in os.listdir("."):
            if fichier.endswith(".json") and (
                "transform" in fichier.lower() or "ai" in fichier.lower()
            ):
                fichiers_json.append(fichier)
    except Exception:
        pass

    if fichiers_json:
        print("Fichiers JSON AI detectes:")
        for i, fichier in enumerate(fichiers_json, 1):
            try:
                taille = format_taille(os.path.getsize(fichier))
                print(f"  {i}. {fichier} ({taille})")
            except Exception:
                print(f"  {i}. {fichier}")

    return input("Chemin du fichier JSON AI: ").strip()


# Test si execution directe
if __name__ == "__main__":
    print("Module JSON AI Processor - Version minimale fonctionnelle")
    analyseur = AnalyseurJSONAI()
    print("+ Analyseur JSON AI initialise avec succes")
