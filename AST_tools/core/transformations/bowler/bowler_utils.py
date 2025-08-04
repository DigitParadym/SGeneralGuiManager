"""
Utilitaires pour faciliter l'utilisation de Bowler.

Ce module contient des fonctions utilitaires pour simplifier
la creation et l'utilisation des transformations Bowler.
"""

import ast
import re
from pathlib import Path
from typing import Any, Dict, List

try:
    # from bowler import Query  # Unused import

    BOWLER_AVAILABLE = True
except ImportError:
    BOWLER_AVAILABLE = False


class BowlerUtils:
    """
    Classe utilitaire pour faciliter l'usage de Bowler.
    """

    @staticmethod
    def validate_syntax(code: str) -> bool:
        """
        Valide la syntaxe Python d'un code.

        Args:
            code: Code Python a valider

        Returns:
            True si la syntaxe est valide
        """
        try:
            ast.parse(code)
            return True
        except SyntaxError:
            return False

    @staticmethod
    def backup_file(file_path: Path, backup_suffix: str = ".backup") -> Path:
        """
        Cree une sauvegarde d'un fichier.

        Args:
            file_path: Chemin du fichier a sauvegarder
            backup_suffix: Suffixe pour le fichier de sauvegarde

        Returns:
            Chemin du fichier de sauvegarde
        """
        backup_path = file_path.with_suffix(file_path.suffix + backup_suffix)

        if file_path.exists():
            import shutil

            shutil.copy2(file_path, backup_path)
            print(f"Sauvegarde creee: {backup_path}")

        return backup_path

    @staticmethod
    def restore_from_backup(file_path: Path, backup_suffix: str = ".backup") -> bool:
        """
        Restaure un fichier depuis sa sauvegarde.

        Args:
            file_path: Chemin du fichier original
            backup_suffix: Suffixe du fichier de sauvegarde

        Returns:
            True si la restauration a reussi
        """
        backup_path = file_path.with_suffix(file_path.suffix + backup_suffix)

        if backup_path.exists():
            import shutil

            shutil.copy2(backup_path, file_path)
            print(f"Fichier restaure depuis: {backup_path}")
            return True
        else:
            print(f"Fichier de sauvegarde non trouve: {backup_path}")
            return False

    @staticmethod
    def analyze_file_structure(file_path: Path) -> Dict[str, Any]:
        """
        Analyse la structure d'un fichier Python.

        Args:
            file_path: Chemin du fichier a analyser

        Returns:
            Dictionnaire contenant l'analyse de la structure
        """
        if not file_path.exists():
            return {"error": "Fichier non trouve"}

        try:
            with open(file_path, encoding="utf-8") as f:
                source = f.read()

            tree = ast.parse(source)

            analysis = {
                "functions": [],
                "classes": [],
                "imports": [],
                "global_variables": [],
                "decorators": [],
                "docstring": ast.get_docstring(tree),
                "line_count": len(source.split("\n")),
            }

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    analysis["functions"].append(
                        {
                            "name": node.name,
                            "line": node.lineno,
                            "args": [arg.arg for arg in node.args.args],
                            "decorators": [
                                BowlerUtils._get_decorator_name(d)
                                for d in node.decorator_list
                            ],
                            "docstring": ast.get_docstring(node),
                        }
                    )

                elif isinstance(node, ast.ClassDef):
                    analysis["classes"].append(
                        {
                            "name": node.name,
                            "line": node.lineno,
                            "bases": [
                                BowlerUtils._get_node_name(base) for base in node.bases
                            ],
                            "decorators": [
                                BowlerUtils._get_decorator_name(d)
                                for d in node.decorator_list
                            ],
                            "methods": [
                                n.name
                                for n in node.body
                                if isinstance(n, ast.FunctionDef)
                            ],
                        }
                    )

                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            analysis["imports"].append(
                                {
                                    "type": "import",
                                    "module": alias.name,
                                    "alias": alias.asname,
                                    "line": node.lineno,
                                }
                            )
                    else:  # ImportFrom
                        for alias in node.names:
                            analysis["imports"].append(
                                {
                                    "type": "from_import",
                                    "module": node.module,
                                    "name": alias.name,
                                    "alias": alias.asname,
                                    "line": node.lineno,
                                }
                            )

                elif isinstance(node, ast.Assign) and isinstance(
                    node.targets[0], ast.Name
                ):
                    # Variables globales (approximation)
                    if (
                        hasattr(node, "lineno") and node.lineno < 50
                    ):  # Heuristique pour detecter les globales
                        analysis["global_variables"].append(
                            {"name": node.targets[0].id, "line": node.lineno}
                        )

            return analysis

        except Exception as e:
            return {"error": f"Erreur lors de l'analyse: {e}"}

    @staticmethod
    def _get_decorator_name(decorator):
        """Extrait le nom d'un decorateur."""
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Attribute):
            return f"{BowlerUtils._get_node_name(decorator.value)}.{decorator.attr}"
        return str(decorator)

    @staticmethod
    def _get_node_name(node):
        """Extrait le nom d'un noeud AST."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{BowlerUtils._get_node_name(node.value)}.{node.attr}"
        return str(node)

    @staticmethod
    def find_transformation_opportunities(file_path: Path) -> List[Dict[str, Any]]:
        """
        Identifie les opportunites de transformation dans un fichier.

        Args:
            file_path: Chemin du fichier a analyser

        Returns:
            Liste des opportunites de transformation
        """
        opportunities = []

        if not file_path.exists():
            return opportunities

        try:
            with open(file_path, encoding="utf-8") as f:
                source = f.read()

            # Recherche de patterns communs a transformer
            patterns = [
                {
                    "pattern": r"print\s*\(",
                    "description": "Appels print() - peuvent etre convertis en logging",
                    "category": "logging",
                    "transformer": "print_to_logging",
                },
                {
                    "pattern": r"\.format\s*\(",
                    "description": "Formatage .format() - peut etre converti en f-string",
                    "category": "strings",
                    "transformer": "format_to_fstring",
                },
                {
                    "pattern": r"%\s*\(",
                    "description": "Formatage % - peut etre converti en f-string",
                    "category": "strings",
                    "transformer": "percent_to_fstring",
                },
                {
                    "pattern": r"os\.path\.",
                    "description": "Usage os.path - peut etre converti en pathlib",
                    "category": "pathlib",
                    "transformer": "os_path_to_pathlib",
                },
                {
                    "pattern": r"import\s+imp\b",
                    "description": "Module imp deprecie - peut etre mis a jour",
                    "category": "deprecated",
                    "transformer": "update_deprecated_apis",
                },
            ]

            for pattern_info in patterns:
                matches = re.finditer(pattern_info["pattern"], source)
                for match in matches:
                    line_num = source[: match.start()].count("\n") + 1
                    opportunities.append(
                        {
                            "file": str(file_path),
                            "line": line_num,
                            "pattern": pattern_info["pattern"],
                            "description": pattern_info["description"],
                            "category": pattern_info["category"],
                            "transformer": pattern_info["transformer"],
                            "matched_text": match.group(),
                        }
                    )

            return opportunities

        except Exception as e:
            print(f"Erreur lors de l'analyse des opportunites: {e}")
            return opportunities

    @staticmethod
    def generate_transformation_report(opportunities: List[Dict[str, Any]]) -> str:
        """
        Genere un rapport des opportunites de transformation.

        Args:
            opportunities: Liste des opportunites trouvees

        Returns:
            Rapport formate en texte
        """
        if not opportunities:
            return "Aucune opportunite de transformation trouvee."

        report = []
        report.append("RAPPORT D'OPPORTUNITES DE TRANSFORMATION")
        report.append("=" * 50)
        report.append(f"Total d'opportunites trouvees: {len(opportunities)}\n")

        # Grouper par categorie
        by_category = {}
        for opp in opportunities:
            category = opp["category"]
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(opp)

        for category, opps in by_category.items():
            report.append(f"Categorie: {category.upper()}")
            report.append("-" * 30)
            report.append(f"Nombre d'opportunites: {len(opps)}\n")

            for opp in opps:
                report.append(f"  Fichier: {opp['file']}")
                report.append(f"  Ligne: {opp['line']}")
                report.append(f"  Description: {opp['description']}")
                report.append(f"  Transformateur suggere: {opp['transformer']}")
                report.append(f"  Texte: {opp['matched_text']}")
                report.append("")

        return "\n".join(report)

    @staticmethod
    def create_batch_script(
        opportunities: List[Dict[str, Any]], output_path: Path = None
    ) -> str:
        """
        Cree un script pour appliquer les transformations en lot.

        Args:
            opportunities: Liste des opportunites
            output_path: Chemin de sortie pour le script

        Returns:
            Contenu du script genere
        """
        script_lines = [
            "#!/usr/bin/env python3",
            '"""',
            "Script genere automatiquement pour appliquer les transformations Bowler.",
            '"""',
            "",
            "from pathlib import Path",
            "from AST_tools.core.transformations.bowler import BowlerTransformers",
            "",
            "def main():",
            "    transformers = BowlerTransformers()",
            "    ",
            "    # Transformations a appliquer",
            "    transformations = [",
        ]

        # Grouper par fichier et transformateur
        by_file_transformer = {}
        for opp in opportunities:
            key = (opp["file"], opp["transformer"])
            if key not in by_file_transformer:
                by_file_transformer[key] = []
            by_file_transformer[key].append(opp)

        for (file_path, transformer), _opps in by_file_transformer.items():
            script_lines.append(f"        (Path('{file_path}'), '{transformer}'),")

        script_lines.extend(
            [
                "    ]",
                "    ",
                "    print(f'Application de {len(transformations)} transformations...')",
                "    ",
                "    for file_path, transformer_name in transformations:",
                "        print(f'Transformation de {file_path} avec {transformer_name}...')",
                "        success = transformers.apply_transformer(",
                "            transformer_name, file_path, dry_run=True  # Changez en False pour appliquer",
                "        )",
                "        if success:",
                "            print('  Succes')",
                "        else:",
                "            print('  Echec')",
                "    ",
                "    print('Transformations terminees.')",
                "",
                "if __name__ == '__main__':",
                "    main()",
            ]
        )

        script_content = "\n".join(script_lines)

        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(script_content)
            print(f"Script genere: {output_path}")

        return script_content


# Exemple d'utilisation
if __name__ == "__main__":
    utils = BowlerUtils()

    # Test de validation de syntaxe
    print("Test de validation syntaxe:")
    print(f"Code valide: {utils.validate_syntax('def test(): pass')}")
    print(f"Code invalide: {utils.validate_syntax('def test( pass')}")

    # Analyse d'un fichier exemple
    test_file = Path("exemple.py")
    if test_file.exists():
        print(f"\nAnalyse de {test_file}:")
        analysis = utils.analyze_file_structure(test_file)
        print(f"Fonctions: {len(analysis.get('functions', []))}")
        print(f"Classes: {len(analysis.get('classes', []))}")
        print(f"Imports: {len(analysis.get('imports', []))}")
