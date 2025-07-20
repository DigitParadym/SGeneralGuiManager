Analyseur de Dépendances de Projet (import_mapper.py)
import_mapper.py est un outil d'analyse statique en ligne de commande qui parcourt un projet Python pour cartographier toutes les dépendances d'importation entre les modules. Il génère un rapport détaillé au format JSON, enrichi de métadonnées et de statistiques, pour fournir une vue d'ensemble claire de l'architecture du projet.

Table des Matières
Objectif de l'Outil

Principes de Conception

Feuille de Route Stratégique

Phase 1 : Produit Minimum Viable (MVP)

Phase 2 : Évolution vers un "Mission Control" de Projet

Architecture Suggérée (Phase 1)

Utilisation (Ligne de Commande)

Structure du Rapport JSON

Objectif de l'Outil
Cet analyseur est conçu pour aider les développeurs à :

Visualiser l'Architecture : Comprendre rapidement comment les différentes parties d'un projet sont connectées.

Détecter les Dépendances Complexes : Identifier facilement les dépendances inattendues, les couplages forts ou les potentiels imports circulaires.

Faciliter la Refactorisation : Avant de modifier un fichier, il est possible de voir immédiatement quels autres modules seront impactés, réduisant ainsi les risques de régression.

Principes de Conception
API-First : La logique principale est encapsulée dans une classe ImportMapper pour être facilement intégrable dans d'autres outils (comme le SGeneralGuiManager). Le script en ligne de commande est un simple "wrapper" autour de cette API.

Robustesse : L'analyse continue même si des fichiers contiennent des erreurs de syntaxe. Les erreurs sont documentées dans le rapport final.

Performance et UX : L'expérience utilisateur est prise en compte pour les grands projets, avec une barre de progression et des timeouts pour éviter les blocages.

Feuille de Route Stratégique
Phase 1 : Produit Minimum Viable (MVP)
L'objectif de cette phase est de créer un outil en ligne de commande fonctionnel et robuste.

Analyse Récursive : Scanne tous les fichiers .py dans le dossier cible, en ignorant les répertoires spécifiés dans la configuration (ex: venv, .git, *_test.py).

Catégorisation des Dépendances : Sépare intelligemment les imports en trois catégories : stdlib, external, et internal.

Gestion des Imports Relatifs : Résout les imports relatifs en chemins absolus.

Rapport JSON Structuré : Génère un rapport complet avec metadata, statistics, et dependency_map.

Granularité des Imports : Offre un mode --detailed pour décomposer les imports.

Options de Sortie : Permet de spécifier un dossier de sortie avec --output-dir.

Phase 2 : Évolution vers un "Mission Control" de Projet
Cette phase transforme l'outil en une plateforme d'analyse avancée, intégrée à l'interface SGeneralGuiManager.

Détection de "Code Smells" : Met en place un système d'alertes automatiques basé sur des seuils définis dans un fichier config.yaml.

Suivi Temporel et Historique : Conserve des "snapshots" des analyses dans une base de données SQLite pour suivre l'évolution de l'architecture.

Visualisation Graphique : Génère des graphiques de dépendances interactifs avec des options de clustering et de filtrage.

Intégration GUI "Mission Control" : Intègre toutes ces fonctionnalités dans le SGeneralGuiManager pour en faire un véritable tableau de bord de santé de projet.

Architecture Suggérée (Phase 1)
import_mapper/
├── __init__.py
├── import_mapper.py          # Wrapper CLI (utilise argparse)
├── core/
│   ├── __init__.py
│   ├── mapper.py             # Classe principale ImportMapper (API)
│   ├── visitor.py            # Classe ImportVisitor (logique AST)
│   ├── resolver.py           # Logique de résolution des imports relatifs
│   └── utils.py              # Fonctions génériques (filtrage, formatage)
└── config/
    └── default_config.yaml   # Configuration des seuils et exclusions

Utilisation (Ligne de Commande)
# Analyser le dossier courant
python import_mapper.py

# Analyser un dossier spécifique et sauvegarder le rapport
python import_mapper.py /chemin/vers/projet --output rapport.json

# Lancer une analyse détaillée
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
