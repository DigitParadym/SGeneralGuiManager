"""
Bibliotheque de queries Bowler pre-definies.

Ce module contient des queries Bowler couramment utilisees
pour les transformations AST.
"""

from typing import Any, Dict, List, Optional

try:
    # from bowler import Query  # Unused import

    BOWLER_AVAILABLE = True
except ImportError:
    BOWLER_AVAILABLE = False


class BowlerQueries:
    """
    Bibliotheque de queries Bowler pre-definies.
    """

    def __init__(self):
        """Initialise la bibliotheque de queries."""
        self.queries = self._load_predefined_queries()

    def _load_predefined_queries(self) -> Dict[str, Dict[str, Any]]:
        """
        Charge les queries pre-definies.

        Returns:
            Dictionnaire des queries avec leurs metadonnees
        """
        return {
            # Queries pour les fonctions
            "all_functions": {
                "selector": "funcdef< 'def' name=any parameters=any ':' suite=any >",
                "description": "Selectionne toutes les definitions de fonctions",
                "category": "functions",
            },
            "functions_with_name": {
                "selector": "funcdef< 'def' name='{function_name}' parameters=any ':' suite=any >",
                "description": "Selectionne les fonctions avec un nom specifique",
                "category": "functions",
                "parameters": ["function_name"],
            },
            # Queries pour les imports
            "all_imports": {
                "selector": "import_name< 'import' dotted_as_names< any* > >",
                "description": "Selectionne tous les imports simples",
                "category": "imports",
            },
            "from_imports": {
                "selector": "import_from< 'from' module_name=any 'import' import_as_names< any* > >",
                "description": "Selectionne tous les from imports",
                "category": "imports",
            },
            "specific_import": {
                "selector": "import_name< 'import' dotted_as_names< '{module_name}' > >",
                "description": "Selectionne un import specifique",
                "category": "imports",
                "parameters": ["module_name"],
            },
            # Queries pour les appels de fonctions
            "function_calls": {
                "selector": "power< '{function_name}' trailer< '(' args=any ')' > >",
                "description": "Selectionne les appels a une fonction specifique",
                "category": "calls",
                "parameters": ["function_name"],
            },
            "print_calls": {
                "selector": "power< 'print' trailer< '(' args=any ')' > >",
                "description": "Selectionne tous les appels a print()",
                "category": "calls",
            },
            "method_calls": {
                "selector": "power< any trailer< '.' '{method_name}' > trailer< '(' args=any ')' > >",
                "description": "Selectionne les appels a une methode specifique",
                "category": "calls",
                "parameters": ["method_name"],
            },
            # Queries pour les strings
            "format_strings": {
                "selector": "power< string trailer< '.' 'format' trailer< '(' args=any ')' > > >",
                "description": "Selectionne les appels .format() sur les strings",
                "category": "strings",
            },
            "percent_formatting": {
                "selector": "comparison< string '%' any >",
                "description": "Selectionne le formatage % des strings",
                "category": "strings",
            },
            # Queries pour les classes
            "all_classes": {
                "selector": "classdef< 'class' name=any ['(' [bases=any] ')'] ':' suite=any >",
                "description": "Selectionne toutes les definitions de classes",
                "category": "classes",
            },
            "class_methods": {
                "selector": "classdef< 'class' any [any] ':' suite< any* funcdef< 'def' name=any parameters< '(' ['self' any*] ')' > ':' any > any* > >",
                "description": "Selectionne les methodes de classe",
                "category": "classes",
            },
            # Queries pour les variables
            "assignments": {
                "selector": "expr_stmt< name=any '=' value=any >",
                "description": "Selectionne les assignations simples",
                "category": "variables",
            },
            "global_variables": {
                "selector": "simple_stmt< expr_stmt< name=any '=' value=any > >",
                "description": "Selectionne les variables globales",
                "category": "variables",
            },
            # Queries pour les exceptions
            "try_except": {
                "selector": "try_stmt< 'try' ':' suite=any except_clause< 'except' [test=any] ':' suite=any >* ['else' ':' suite=any] ['finally' ':' suite=any] >",
                "description": "Selectionne les blocs try/except",
                "category": "exceptions",
            },
            "raise_statements": {
                "selector": "raise_stmt< 'raise' [test=any ['from' test=any]] >",
                "description": "Selectionne les statements raise",
                "category": "exceptions",
            },
            # Queries pour les decorateurs
            "decorated_functions": {
                "selector": "decorated< decorators< decorator< '@' dotted_name< any* > any* >* > funcdef< any* > >",
                "description": "Selectionne les fonctions decorees",
                "category": "decorators",
            },
            "specific_decorator": {
                "selector": "decorated< decorators< decorator< '@' '{decorator_name}' any* >* > funcdef< any* > >",
                "description": "Selectionne les fonctions avec un decorateur specifique",
                "category": "decorators",
                "parameters": ["decorator_name"],
            },
        }

    def get_query(self, query_name: str, **parameters) -> str:
        """
        Retourne une query formatee avec les parametres.

        Args:
            query_name: Nom de la query
            **parameters: Parametres pour formatter la query

        Returns:
            Query formatee ou string vide si non trouvee
        """
        if query_name not in self.queries:
            print(f"Query inconnue: {query_name}")
            return ""

        query_info = self.queries[query_name]
        selector = query_info["selector"]

        # Verification des parametres requis
        required_params = query_info.get("parameters", [])
        for param in required_params:
            if param not in parameters:
                print(f"Parametre manquant pour {query_name}: {param}")
                return ""

        # Formatage de la query
        try:
            formatted_selector = selector.format(**parameters)
            return formatted_selector
        except KeyError as e:
            print(f"Erreur de formatage pour {query_name}: {e}")
            return ""

    def list_queries(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Liste les queries disponibles.

        Args:
            category: Filtre par categorie (optionnel)

        Returns:
            Liste des queries avec leurs informations
        """
        result = []

        for name, info in self.queries.items():
            if category is None or info.get("category") == category:
                result.append(
                    {
                        "name": name,
                        "description": info["description"],
                        "category": info.get("category", "general"),
                        "parameters": info.get("parameters", []),
                        "selector": info["selector"],
                    }
                )

        return result

    def get_categories(self) -> List[str]:
        """
        Retourne la liste des categories de queries.

        Returns:
            Liste des categories uniques
        """
        categories = set()
        for info in self.queries.values():
            categories.add(info.get("category", "general"))

        return sorted(categories)

    def search_queries(self, keyword: str) -> List[Dict[str, Any]]:
        """
        Recherche des queries par mot-cle.

        Args:
            keyword: Mot-cle a rechercher

        Returns:
            Liste des queries correspondantes
        """
        result = []
        keyword_lower = keyword.lower()

        for name, info in self.queries.items():
            # Recherche dans le nom, description ou selecteur
            if (
                keyword_lower in name.lower()
                or keyword_lower in info["description"].lower()
                or keyword_lower in info["selector"].lower()
            ):
                result.append(
                    {
                        "name": name,
                        "description": info["description"],
                        "category": info.get("category", "general"),
                        "parameters": info.get("parameters", []),
                        "selector": info["selector"],
                    }
                )

        return result

    def create_custom_query(
        self,
        name: str,
        selector: str,
        description: str,
        category: str = "custom",
        parameters: Optional[List[str]] = None,
    ) -> bool:
        """
        Cree une query personnalisee.

        Args:
            name: Nom de la query
            selector: Selecteur Bowler
            description: Description de la query
            category: Categorie
            parameters: Parametres requis

        Returns:
            True si la query a ete creee
        """
        if name in self.queries:
            print(f"Query {name} existe deja")
            return False

        self.queries[name] = {
            "selector": selector,
            "description": description,
            "category": category,
            "parameters": parameters or [],
        }

        print(f"Query personnalisee creee: {name}")
        return True


# Exemple d'utilisation
if __name__ == "__main__":
    queries = BowlerQueries()

    print("Categories disponibles:")
    for category in queries.get_categories():
        print(f"  - {category}")

    print("\nQueries pour les imports:")
    import_queries = queries.list_queries("imports")
    for query in import_queries:
        print(f"  - {query['name']}: {query['description']}")

    # Exemple de query formatee
    print("\nExemple de query formatee:")
    specific_import = queries.get_query("specific_import", module_name="os")
    print(f"Query: {specific_import}")
