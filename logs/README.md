# AST_tools Logs

Ce dossier contient tous les logs du systeme AST_tools.

## Structure des logs:
- `ast_tools_debug.log` - Logs de debug detailles
- `ast_tools_errors.log` - Logs d'erreurs uniquement  
- `transformations.log` - Logs des transformations
- `transformations_detailed.jsonl` - Details JSON des transformations
- `sessions/` - Logs de sessions avec timestamp
- `bowler/` - Logs specifiques a Bowler
- `analysis/` - Logs d'analyse de code

## Utilisation:
```python
from AST_tools.core.ast_logger import get_ast_logger

logger = get_ast_logger()
logger.log_transformation_start("fichier.py", "plan_transformation")
```

## Analyse des logs:
```python
analysis = logger.analyze_logs()
print(analysis)
```
