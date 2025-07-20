import ast
from .resolver import resolve_relative_import

class ImportVisitor(ast.NodeVisitor):
    def __init__(self, project_root, file_path):
        self.imports = []
        self.project_root = project_root
        self.file_path = file_path

    def visit_Import(self, node):
        for alias in node.names:
            self.imports.append({'module': alias.name, 'level': 0})
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        mod = node.module or ""
        if node.level > 0:
            resolved = resolve_relative_import(self.file_path, node.level, mod)
            for alias in node.names:
                self.imports.append({'module': f"{resolved}.{alias.name}", 'level': node.level})
        else:
            for alias in node.names:
                self.imports.append({'module': f"{mod}.{alias.name}", 'level': 0})
        self.generic_visit(node)
