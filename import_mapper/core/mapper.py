import ast
import json
from pathlib import Path
from datetime import datetime
from collections import Counter
from .visitor import ImportVisitor
from .utils import classify_import

class ImportMapper:
    def __init__(self, project_path, detailed=False):
        self.project_path = Path(project_path).resolve()
        self.detailed = detailed
        self.dependency_map = {}
        self.parsing_errors = []
        self.stats = Counter()

    def run_analysis(self):
        ignore_dirs = {'.git', '__pycache__', 'venv', '.venv', 'build', 'dist'}
        files = [p for p in self.project_path.rglob('*.py') if not any(part in ignore_dirs for part in p.parts)]

        for path in files:
            rel_path = str(path.relative_to(self.project_path)).replace('\\', '/')
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    tree = ast.parse(f.read())
                visitor = ImportVisitor(str(self.project_path), rel_path)
                visitor.visit(tree)
                if visitor.imports:
                    self.dependency_map[rel_path] = self._classify(visitor.imports)
                    self.stats.update(m['module'] for m in visitor.imports)
            except Exception as e:
                self.parsing_errors.append({"file": rel_path, "error": f"{type(e).__name__}: {e}"})

        return self._report(len(files))

    def _classify(self, imports):
        result = {"stdlib": [], "external": [], "internal": []}
        for imp in imports:
            category = classify_import(imp['module'])
            result[category].append(imp['module'])
        return {k: sorted(set(v)) for k, v in result.items() if v}

    def _report(self, file_count):
        top = self.stats.most_common(5)
        top_files = sorted(self.dependency_map.items(), key=lambda x: sum(len(v) for v in x[1].values()), reverse=True)[:5]
        return {
            "metadata": {
                "project_path": str(self.project_path),
                "generation_date": datetime.utcnow().isoformat() + "Z",
                "files_analyzed": file_count,
                "parsing_errors": self.parsing_errors
            },
            "statistics": {
                "most_imported_modules": dict(top),
                "most_dependent_files": [f[0] for f in top_files]
            },
            "dependency_map": self.dependency_map
        }

    def save_to_json(self, data, output_file):
        out_path = self.project_path / output_file
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
