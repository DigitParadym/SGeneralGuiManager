__test__ = False  # Empêche Pytest de collecter ce module comme test
#!/usr/bin/env python3
"""
Test Generator - Genere des tests unitaires
"""

import sys
from pathlib import Path
from typing import Any, Dict, Optional

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from core.plugins.base.base_transformer import BaseTransformer


class TestFileGenerator(BaseTransformer):
    """Generateur de fichiers de test."""

    def __init__(self):
        super().__init__()
        self.name = "Test Generator"
        self.description = "Genere des fichiers de test unitaire"
        self.version = "1.0.0"
        self.author = "AST Tools"

    def get_metadata(self):
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "author": self.author,
            "type": "generator",
        }

    def transform(self, code_source: str = "") -> str:
        """Generation de tests."""
        if code_source:
            raise ValueError("TestFileGenerator cree de nouveaux fichiers uniquement")
        return self.generate_test()

    def generate_test(self, params: Optional[Dict[str, Any]] = None) -> str:
        """Genere un fichier de test."""
        if params is None:
            params = {}

        module_name = params.get("module_name", "my_module")
        class_name = params.get("class_name", "MyClass")

        return self._generate_unittest(module_name, class_name)

    def _generate_unittest(self, module_name: str, class_name: str) -> str:
        """Genere un test unittest."""
        test_class = "Test" + class_name

        template = "#!/usr/bin/env python3\n"
        template += '"""\n'
        template += f"Unit tests for {module_name}\n"
        template += '"""\n\n'
        template += "import unittest\n"
        template += "import sys\n"
        template += "from pathlib import Path\n\n"
        template += "sys.path.insert(0, str(Path(__file__).parent.parent))\n\n"
        template += "try:\n"
        template += f"    from {module_name} import {class_name}\n"
        template += "except ImportError:\n"
        template += f"    {class_name} = None\n\n\n"
        template += f"class {test_class}(unittest.TestCase):\n"
        template += f'    """Test cases for {class_name}."""\n\n'
        template += "    def setUp(self):\n"
        template += f"        self.instance = {class_name}() if {class_name} else None\n\n"
        template += "    def test_initialization(self):\n"
        template += f'        """Test {class_name} initialization."""\n'
        template += f"        if not {class_name}:\n"
        template += '            self.skipTest("Module not available")\n'
        template += "        self.assertIsNotNone(self.instance)\n\n\n"
        template += 'if __name__ == "__main__":\n'
        template += "    unittest.main()\n"

        return template
