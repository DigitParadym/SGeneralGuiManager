#!/usr/bin/env python3
"""
Tests Unitaires pour PathLib Converter Transformer
=================================================

Test du transformateur qui modernise le code en remplacant
os.path par pathlib.Path dans le code Python.
"""

import unittest
import sys
import os
from pathlib import Path

# Ajouter le chemin vers le module core
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from core.transformation_loader import TransformationLoader

class TestPathLibConverterTransformer(unittest.TestCase):
    """Tests pour le transformateur PathLib Converter."""
    
    def setUp(self):
        """Configuration des tests."""
        self.loader = TransformationLoader()
        self.transformer = self.loader.get_transformation("pathlib_converter_transformer")
        
        if not self.transformer:
            self.skipTest("Transformateur pathlib_converter_transformer non disponible")
    
    def test_transformer_metadata(self):
        """Test 1: Verifier les metadonnees du transformateur."""
        metadata = self.transformer.get_metadata()
        
        self.assertIn("pathlib", metadata["name"].lower())
        self.assertIn("path", metadata["name"].lower())
        self.assertEqual(metadata["version"], "1.0")
        self.assertIn("os.path", metadata["description"])
        self.assertIn("pathlib", metadata["description"])
    
    def test_can_transform_os_path_join(self):
        """Test 2: Detecter os.path.join."""
        code_with_os_path = ("import os\n"
                             "file_path = os.path.join(\"dossier\", \"fichier.txt\")\n")
        self.assertTrue(self.transformer.can_transform(code_with_os_path))
    
    def test_can_transform_os_path_exists(self):
        """Test 3: Detecter os.path.exists."""
        code_with_exists = ("import os.path\n"
                            "if os.path.exists(\"fichier.txt\"):\n"
                            "    print(\"Fichier existe\")\n")
        self.assertTrue(self.transformer.can_transform(code_with_exists))
    
    def test_cannot_transform_no_os_path(self):
        """Test 4: Ne pas transformer du code sans os.path."""
        code_without_os_path = ("\n"
                                "def calculate(x, y):\n"
                                "    return x + y\n"
                                "\n"
                                "result = calculate(1, 2)\n")
        self.assertFalse(self.transformer.can_transform(code_without_os_path))
    
    def test_transform_os_path_join_simple(self):
        """Test 5: Transformer os.path.join simple."""
        input_code = ("import os\n"
                     "file_path = os.path.join(\"dossier\", \"fichier.txt\")\n")
        
        result = self.transformer.transform(input_code)
        
        # Verifier import pathlib
        self.assertIn("from pathlib import Path", result)
        
        # Verifier transformation (accepter les deux types de guillemets)
        path_transform_found = ("Path(\"dossier\") / \"fichier.txt\"" in result or 
                               "Path('dossier') / 'fichier.txt'" in result)
        self.assertTrue(path_transform_found, f"Transformation Path non trouvee dans: {result}")
        
        # Verifier que os.path.join a disparu
        self.assertNotIn("os.path.join", result)
    
    def test_syntax_correctness(self):
        """Test 6: Verifier la correction syntaxique du code transforme."""
        input_code = ("import os\n"
                     "import os.path\n"
                     "\n"
                     "def process_files():\n"
                     "    base_dir = \"/home/user\"\n"
                     "    filename = \"data.txt\"\n"
                     "    \n"
                     "    full_path = os.path.join(base_dir, filename)\n"
                     "    \n"
                     "    if os.path.exists(full_path):\n"
                     "        if os.path.isfile(full_path):\n"
                     "            name = os.path.basename(full_path)\n"
                     "            directory = os.path.dirname(full_path)\n"
                     "            absolute = os.path.abspath(full_path)\n"
                     "            return True\n"
                     "    \n"
                     "    return False\n")
        
        result = self.transformer.transform(input_code)
        
        # Le code transforme doit etre syntaxiquement correct
        try:
            compile(result, "<string>", "exec")
            syntax_valid = True
        except SyntaxError as e:
            syntax_valid = False
            print(f"Erreur syntaxe: {e}")
            print(f"Code transforme: {result}")
        
        self.assertTrue(syntax_valid, "Le code transforme doit etre syntaxiquement correct")

if __name__ == "__main__":
    # Lancer les tests et capturer le resultat
    import io
    import sys
    from datetime import datetime
    
    # Capturer la sortie
    test_output = io.StringIO()
    runner = unittest.TextTestRunner(stream=test_output, verbosity=2)
    
    # Charger et lancer les tests
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestPathLibConverterTransformer)
    result = runner.run(suite)
    
    # Recuperer la sortie
    output_text = test_output.getvalue()
    
    # Afficher le resultat
    print("=== RESULTATS TESTS PATHLIB CONVERTER ===")
    print(output_text)
    
    # Creer un rapport pour copie
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    rapport = f"""RAPPORT TESTS PATHLIB CONVERTER - {timestamp}
==================================================

CONTEXTE:
- Tests du transformateur PathLib Converter
- Objectif: Remplacer os.path par pathlib.Path
- Tests principaux pour valider les fonctionnalites

RESULTATS:
{output_text}

STATISTIQUES:
- Tests executes: {result.testsRun}
- Succes: {result.testsRun - len(result.failures) - len(result.errors)}
- Echecs: {len(result.failures)}
- Erreurs: {len(result.errors)}
- Taux de reussite: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%

PROBLEMES DETECTES:
"""
    
    # Ajouter les details des echecs
    if result.failures:
        rapport += "\nECHECS:\n"
        for test, traceback in result.failures:
            rapport += f"- {test}: {traceback}\n"
    
    if result.errors:
        rapport += "\nERREURS:\n"
        for test, traceback in result.errors:
            rapport += f"- {test}: {traceback}\n"
    
    rapport += """
FICHIER TRANSFORMATEUR: core/transformations/pathlib_converter_transformer.py

ACTIONS RECOMMANDEES:
1. Corriger les erreurs de transformation detectees
2. Implementer get_imports_required() qui retourne ["pathlib"]
3. S'assurer que tous les appels os.path sont detectes et transformes
4. Gerer les expressions imbriquees correctement
5. Ajouter l'import pathlib automatiquement

Ce rapport peut etre copie dans une IA pour analyse et recommandations.
"""
    
    # Essayer de copier dans le presse-papiers
    try:
        if sys.platform == "win32":
            import subprocess
            process = subprocess.Popen(["clip"], stdin=subprocess.PIPE, text=True)
            process.communicate(input=rapport)
            print("\n+ RAPPORT COPIE DANS LE PRESSE-PAPIERS!")
            print("+ Collez avec Ctrl+V dans une IA pour analyse")
    except:
        print("\n! Impossible de copier automatiquement")
        print("! Copiez manuellement le rapport ci-dessus")
    
    print("\n" + "="*50)
    print("RAPPORT GENERE - PRET POUR ANALYSE IA")
    print("="*50)
