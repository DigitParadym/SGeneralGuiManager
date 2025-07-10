def is_stdlib_module(name):
    return name in ("os", "sys", "math")

def format_import(name):
    return name.strip()
