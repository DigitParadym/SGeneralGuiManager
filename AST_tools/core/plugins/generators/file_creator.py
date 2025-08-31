#!/usr/bin/env python3
"""
File Creator - Generateur de fichiers Python
"""

import sys
from pathlib import Path
from typing import Any, Dict, Optional

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from core.plugins.base.base_transformer import BaseTransformer


class FileCreator(BaseTransformer):
    """Generateur pour creer de nouveaux fichiers Python."""

    def __init__(self):
        super().__init__()
        self.name = "File Creator"
        self.description = "Cree de nouveaux fichiers Python"
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
        """Mode generation."""
        if not code_source:
            return self.generate_new_file()
        else:
            raise ValueError("FileCreator ne modifie pas de fichiers existants")

    def generate_new_file(self, params: Optional[Dict[str, Any]] = None) -> str:
        """Genere un nouveau fichier Python."""
        if params is None:
            params = {}

        template_type = params.get("template", "basic")
        module_name = params.get("module_name", "new_module")
        author = params.get("author", "AST Tools")

        if template_type == "class":
            class_name = params.get("class_name", "MyClass")
            return self._generate_class_code(module_name, class_name, author)
        else:
            return self._generate_basic_code(module_name, author)

    def _generate_basic_code(self, module_name: str, author: str) -> str:
        """Genere code basique."""
        lines = [
            "#!/usr/bin/env python3",
            '"""',
            "Module: " + module_name,
            "Author: " + author,
            '"""',
            "",
            "",
            "def main():",
            '    """Fonction principale."""',
            '    print("Hello from ' + module_name + '")',
            "",
            "",
            'if __name__ == "__main__":',
            "    main()",
        ]
        return "\n".join(lines)

    def _generate_class_code(self, module_name: str, class_name: str, author: str) -> str:
        """Genere code avec classe."""
        lines = [
            "#!/usr/bin/env python3",
            '"""',
            "Module: " + module_name,
            "Author: " + author,
            '"""',
            "",
            "from typing import Any, Dict",
            "",
            "",
            "class " + class_name + ":",
            '    """' + class_name + ' implementation."""',
            "",
            "    def __init__(self):",
            "        self.data = {}",
            "",
            "    def process(self, input_data: Any) -> Dict:",
            '        return {"status": "processed", "data": input_data}',
            "",
            "",
            "def main():",
            "    instance = " + class_name + "()",
            '    result = instance.process("test")',
            '    print(f"Result: {result}")',
            "",
            "",
            'if __name__ == "__main__":',
            "    main()",
        ]
        return "\n".join(lines)
