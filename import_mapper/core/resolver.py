from pathlib import Path

def resolve_relative_import(file_path, level, module):
    base = Path(file_path).parent
    for _ in range(level - 1):
        base = base.parent
    return f"{str(base).replace('\\', '.')}.{module}" if module else str(base).replace('\\', '.')
