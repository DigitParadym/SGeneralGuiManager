"""
Transformation d'exemple fonctionnelle
Ajoute des commentaires simples
"""


class ExempleWorkingTransform:
    """Transformation exemple qui marche."""

    def get_metadata(self):
        return {
            "name": "Exemple Fonctionnel",
            "version": "1.0.0",
            "description": "Ajoute des commentaires de test",
            "author": "AST System",
        }

    def can_transform(self, code: str) -> bool:
        """Verifie si transformable."""
        return "def " in code

    def transform(self, code: str) -> str:
        """Ajoute des commentaires aux fonctions."""
        lines = code.split("\n")
        result = []

        for line in lines:
            result.append(line)
            if line.strip().startswith("def ") and ":" in line:
                indent = len(line) - len(line.lstrip())
                comment = " " * (indent + 4) + "# Transforme par AST"
                result.append(comment)

        return "\n".join(result)
