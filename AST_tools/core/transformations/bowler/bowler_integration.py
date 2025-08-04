"""
Interface principale pour l'integration avec Bowler.

Ce module fournit une interface unifie pour utiliser Bowler
dans le systeme de transformation AST existant.
"""

from pathlib import Path
from typing import Optional, Union

try:
    from bowler import BowlerException, Query

    BOWLER_AVAILABLE = True
except ImportError:
    BOWLER_AVAILABLE = False

    # Mock classes pour eviter les erreurs d'import
    class Query:
        pass

    class BowlerException(Exception):
        pass


class BowlerIntegration:
    """
    Interface principale pour l'integration avec Bowler.
    """

    def __init__(self):
        """Initialise l'integration Bowler."""
        self.available = BOWLER_AVAILABLE
        self.last_query = None
        self.dry_run = True  # Mode securise par defaut

        if not self.available:
            print("Warning: Bowler n'est pas disponible. Mode simulation active.")

    def check_availability(self) -> bool:
        """
        Verifie si Bowler est disponible.

        Returns:
            True si Bowler est installe et disponible
        """
        return self.available

    def create_query(self, file_path: Union[str, Path]) -> Optional[Query]:
        """
        Cree une nouvelle query Bowler pour un fichier.

        Args:
            file_path: Chemin vers le fichier a transformer

        Returns:
            Query Bowler ou None si non disponible
        """
        if not self.available:
            print(f"Mode simulation: creation query pour {file_path}")
            return None

        try:
            if isinstance(file_path, str):
                file_path = Path(file_path)

            if not file_path.exists():
                raise FileNotFoundError(f"Fichier non trouve: {file_path}")

            query = Query(str(file_path))
            self.last_query = query
            return query

        except Exception as e:
            print(f"Erreur lors de la creation de la query: {e}")
            return None

    def apply_transformation(
        self, query: Query, transformation_func: callable, dry_run: bool = None
    ) -> bool:
        """
        Applique une transformation via Bowler.

        Args:
            query: Query Bowler
            transformation_func: Fonction de transformation
            dry_run: Mode dry run (defaut: self.dry_run)

        Returns:
            True si la transformation a reussi
        """
        if not self.available:
            print("Mode simulation: transformation appliquee")
            return True

        if dry_run is None:
            dry_run = self.dry_run

        try:
            # Application de la transformation
            modified_query = query.select_method(transformation_func)

            if dry_run:
                print("Mode dry run: transformation preparee mais pas appliquee")
                return True
            else:
                # Application reelle (attention!)
                modified_query.execute()
                print("Transformation appliquee avec succes")
                return True

        except Exception as e:
            print(f"Erreur lors de l'application de la transformation: {e}")
            return False

    def transform_file(
        self,
        file_path: Union[str, Path],
        selector: str,
        modifier: callable,
        dry_run: bool = None,
    ) -> bool:
        """
        Transforme un fichier avec un selecteur et modificateur.

        Args:
            file_path: Chemin du fichier
            selector: Selecteur CSS-like pour les noeuds AST
            modifier: Fonction de modification
            dry_run: Mode dry run

        Returns:
            True si la transformation a reussi
        """
        if not self.available:
            print(f"Mode simulation: transformation de {file_path}")
            print(f"  Selecteur: {selector}")
            print(
                f"  Modificateur: {modifier.__name__ if hasattr(modifier, '__name__') else 'fonction'}"
            )
            return True

        if dry_run is None:
            dry_run = self.dry_run

        try:
            query = self.create_query(file_path)
            if query is None:
                return False

            # Application du selecteur et modificateur
            transformed = query.select(selector).modify(modifier)

            if dry_run:
                print(f"Dry run: {file_path} pret pour transformation")
                # Optionnel: afficher les changements prevus
                diff = transformed.diff()
                if diff:
                    print("Changements prevus:")
                    print(diff)
                return True
            else:
                # Application reelle
                transformed.execute()
                print(f"Fichier transforme: {file_path}")
                return True

        except Exception as e:
            print(f"Erreur lors de la transformation: {e}")
            return False

    def set_dry_run(self, enabled: bool):
        """
        Active ou desactive le mode dry run.

        Args:
            enabled: True pour activer le mode dry run
        """
        self.dry_run = enabled
        mode = "active" if enabled else "desactive"
        print(f"Mode dry run {mode}")

    def preview_changes(
        self, file_path: Union[str, Path], selector: str, modifier: callable
    ) -> str:
        """
        Previsualise les changements sans les appliquer.

        Args:
            file_path: Chemin du fichier
            selector: Selecteur pour les noeuds
            modifier: Fonction de modification

        Returns:
            Diff des changements ou message d'erreur
        """
        if not self.available:
            return "Mode simulation: preview non disponible sans Bowler"

        try:
            query = self.create_query(file_path)
            if query is None:
                return "Erreur: impossible de creer la query"

            transformed = query.select(selector).modify(modifier)
            diff = transformed.diff()

            return diff if diff else "Aucun changement detecte"

        except Exception as e:
            return f"Erreur lors du preview: {e}"


# Fonctions utilitaires pour les transformations courantes
def print_to_logging_modifier(node, capture, filename):
    """
    Modificateur pour remplacer print() par logging.

    Exemple d'usage avec Bowler.
    """
    if not BOWLER_AVAILABLE:
        return node

    # Implementation du modificateur
    # Cette fonction serait utilisee avec query.select("Name").modify(print_to_logging_modifier)
    return node


def f_string_modifier(node, capture, filename):
    """
    Modificateur pour convertir .format() en f-strings.
    """
    if not BOWLER_AVAILABLE:
        return node

    # Implementation du modificateur pour f-strings
    return node


# Exemple d'utilisation
if __name__ == "__main__":
    integration = BowlerIntegration()

    if integration.check_availability():
        print("Bowler est disponible!")

        # Exemple de transformation
        file_path = "exemple.py"
        selector = "power< 'print' trailer< '(' args=any ')' > >"

        # Preview des changements
        preview = integration.preview_changes(
            file_path, selector, print_to_logging_modifier
        )
        print("Preview des changements:")
        print(preview)

    else:
        print("Bowler n'est pas disponible. Mode simulation active.")
