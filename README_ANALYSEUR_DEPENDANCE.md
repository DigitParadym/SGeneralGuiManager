Analyseur de Dependances de Projet (import_mapper.py)
import_mapper.py est un outil d'analyse statique en ligne de commande qui parcourt un projet Python pour cartographier toutes les dependances d'importation entre les modules. Il genere un rapport detaille au format JSON, enrichi de metadonnees et de statistiques, pour fournir une vue d'ensemble claire de l'architecture du projet.

Table des Matieres
Objectif de l'Outil

Principes de Conception

Feuille de Route Strategique

Phase 1 : Produit Minimum Viable (MVP)

Phase 2 : Evolution vers un "Mission Control" de Projet

Architecture Suggeree (Phase 1)

Utilisation (Ligne de Commande)

Structure du Rapport JSON

Objectif de l'Outil
Cet analyseur est concu pour aider les developpeurs a :

Visualiser l'Architecture : Comprendre rapidement comment les differentes parties d'un projet sont connectees.

Detecter les Dependances Complexes : Identifier facilement les dependances inattendues, les couplages forts ou les potentiels imports circulaires.

Faciliter la Refactorisation : Avant de modifier un fichier, il est possible de voir immediatement quels autres modules seront impactes, reduisant ainsi les risques de regression.

Principes de Conception
API-First : La logique principale est encapsulee dans une classe ImportMapper pour etre facilement integrable dans d'autres outils (comme le SGeneralGuiManager). Le script en ligne de commande est un simple "wrapper" autour de cette API.

Robustesse : L'analyse continue meme si des fichiers contiennent des erreurs de syntaxe. Les erreurs sont documentees dans le rapport final.

Performance et UX : L'experience utilisateur est prise en compte pour les grands projets, avec une barre de progression et des timeouts pour eviter les blocages.

Feuille de Route Strategique
Phase 1 : Produit Minimum Viable (MVP)
L'objectif de cette phase est de creer un outil en ligne de commande fonctionnel et robuste.

Analyse Recursive : Scanne tous les fichiers .py dans le dossier cible, en ignorant les repertoires specifies dans la configuration (ex: venv, .git, *_test.py).

Categorisation des Dependances : Separe intelligemment les imports en trois categories : stdlib, external, et internal.

Gestion des Imports Relatifs : Resout les imports relatifs en chemins absolus.

Rapport JSON Structure : Genere un rapport complet avec metadata, statistics, et dependency_map.

Granularite des Imports : Offre un mode --detailed pour decomposer les imports.

Options de Sortie : Permet de specifier un dossier de sortie avec --output-dir.

Phase 2 : Evolution vers un "Mission Control" de Projet
Cette phase transforme l'outil en une plateforme d'analyse avancee, integree a l'interface SGeneralGuiManager.

Detection de "Code Smells" : Met en place un systeme d'alertes automatiques base sur des seuils definis dans un fichier config.yaml.

Suivi Temporel et Historique : Conserve des "snapshots" des analyses dans une base de donnees SQLite pour suivre l'evolution de l'architecture.

Visualisation Graphique : Genere des graphiques de dependances interactifs avec des options de clustering et de filtrage.

Integration GUI "Mission Control" : Integre toutes ces fonctionnalites dans le SGeneralGuiManager pour en faire un veritable tableau de bord de sante de projet.

Architecture Suggeree (Phase 1)
import_mapper/
 __init__.py
 import_mapper.py          # Wrapper CLI (utilise argparse)
 core/
    __init__.py
    mapper.py             # Classe principale ImportMapper (API)
    visitor.py            # Classe ImportVisitor (logique AST)
    resolver.py           # Logique de resolution des imports relatifs
    utils.py              # Fonctions generiques (filtrage, formatage)
 config/
     default_config.yaml   # Configuration des seuils et exclusions

Utilisation (Ligne de Commande)
# Analyser le dossier courant
python import_mapper.py

# Analyser un dossier specifique et sauvegarder le rapport
python import_mapper.py /chemin/vers/projet --output rapport.json

# Lancer une analyse detaillee
python import_mapper.py /chemin/vers/projet --detailed

Structure du Rapport JSON
{
  "metadata": {
    "project_path": "C:/Projets/SGeneralGuiManager",
    "generation_date": "2025-07-10T12:00:00Z",
    "files_analyzed": 59,
    "parsing_errors": [
        {"file": "broken.py", "error": "SyntaxError: invalid syntax"}
    ]
  },
  "statistics": {
    "most_imported_modules": { "os": 50, "tkinter": 35 },
    "most_dependent_files": { "copypaste_manager.py": 15 }
  },
  "dependency_map": {
    "Folder/FolderCopypaste_interface.py": {
      "stdlib": ["os", "datetime"],
      "external": ["tkinter", "pyperclip"],
      "internal": []
    }
  }
}
