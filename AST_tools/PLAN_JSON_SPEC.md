Cette spécification est excellente et correspond parfaitement à la structure validée par models.py. Voici quelques points supplémentaires utiles :
Paramètres spécifiques par wrapper
Ruff (ruff_wrapper)
json"params": {
  "command": "check" | "format",        // Sous-commande Ruff
  "fix": true/false,                    // Appliquer les corrections
  "select": ["E", "F", "I", ...],      // Règles à activer
  "ignore": ["D", "ANN", ...],         // Règles à ignorer
  "line-length": 100,                  // Longueur de ligne max
  "target-version": "py38",            // Version Python cible
  "unsafe-fixes": false,               // Corrections risquées
  "show-fixes": true,                  // Afficher les corrections
  "exclude": ["*.pyc", "venv"],        // Fichiers à exclure
  "_return_original_on_error": true    // Garder l'original si erreur
}
Pyupgrade (pyupgrade_wrapper)
json"params": {
  "python_version": "38",    // Version Python cible (38, 39, 310, 311, etc.)
  "keep-percent-format": true,
  "keep-fstring-formatting": true
}
Erreurs de validation courantes
ErreurMessageSolutionType invalidetype: Input should be 'appel_plugin'...Utiliser exactement un des 4 types validesPlugin inconnuLe plugin 'RuffWrapper' n'existe pasUtiliser ruff_wrapper (avec underscore, minuscules)Champ manquantdescription: Field requiredAjouter le champ description à chaque transformationChamp non autoriséExtra inputs are not permittedRetirer les champs non reconnus
Cas d'usage spéciaux
Générateur de fichier
json{
  "type": "generator",
  "description": "Créer un nouveau module",
  "plugin_name": "module_generator",
  "params": {
    "type": "service",
    "name": "my_service"
  }
}
Transformation custom (non implémentée)
json{
  "type": "custom",
  "description": "Transformation personnalisée",
  "module": "path.to.module",
  "function": "transform_func"
}
Votre spécification est maintenant complète et prête à être utilisée comme référence !