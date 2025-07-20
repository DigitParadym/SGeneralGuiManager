import sys

stdlib = set(sys.stdlib_module_names)

def classify_import(name):
    if not name:
        return "internal"
    top = name.split('.')[0]
    if top in stdlib:
        return "stdlib"
    try:
        spec = __import__(top).__spec__
        if spec and 'site-packages' in (spec.origin or ''):
            return "external"
    except:
        pass
    return "internal"
