#!/usr/bin/env python3
"""
Transformateur JSON avec logging integre pour AST_tools.
"""

import json
import ast
import traceback
from pathlib import Path
from typing import Dict, List, Any, Optional

# Import du systeme de logging
try:
    from ..ast_logger import get_ast_logger, log_info, log_error, log_debug
    LOGGING_AVAILABLE = True
except:
    LOGGING_AVAILABLE = False
    def log_info(msg, cat="general"): print(f"INFO: {msg}")
    def log_error(msg, cat="general"): print(f"ERROR: {msg}")
    def log_debug(msg, cat="general"): print(f"DEBUG: {msg}")

class JsonAiTransformerWithLogging:
    """Transformateur JSON avec logging complet."""
    
    def __init__(self):
        """Initialise le transformateur."""
        self.logger = None
        if LOGGING_AVAILABLE:
            self.logger = get_ast_logger()
        
        log_info("JsonAiTransformerWithLogging initialise")
        
    def load_transformation_plan(self, plan_path: Path) -> Dict[str, Any]:
        """Charge un plan de transformation avec logging."""
        log_info(f"Chargement plan: {plan_path}")
        
        if not plan_path.exists():
            log_error(f"Plan non trouve: {plan_path}")
            return {}
        
        try:
            with open(plan_path, 'r', encoding='utf-8') as f:
                plan = json.load(f)
            
            log_info(f"Plan charge: {len(plan.get('transformations', []))} transformations")
            log_debug(f"Contenu plan: {list(plan.keys())}")
            
            return plan
            
        except json.JSONDecodeError as e:
            log_error(f"Erreur JSON dans {plan_path}: {e}")
            return {}
        except Exception as e:
            log_error(f"Erreur chargement plan {plan_path}: {e}")
            return {}
    
    def apply_transformation_to_file(self, plan_path: Path, target_file: Path) -> bool:
        """Applique une transformation avec logging detaille."""
        if self.logger:
            self.logger.log_transformation_start(target_file, plan_path.name)
        
        log_info(f"DEBUT transformation: {target_file} avec {plan_path}")
        
        try:
            # Verification fichier cible
            if not target_file.exists():
                error_msg = f"Fichier cible non trouve: {target_file}"
                log_error(error_msg)
                if self.logger:
                    self.logger.log_transformation_error(target_file, plan_path.name, error_msg)
                return False
            
            # Chargement du plan
            plan = self.load_transformation_plan(plan_path)
            if not plan:
                error_msg = "Plan de transformation vide ou invalide"
                log_error(error_msg)
                if self.logger:
                    self.logger.log_transformation_error(target_file, plan_path.name, error_msg)
                return False
            
            # Lecture du fichier original
            log_debug(f"Lecture fichier original: {target_file}")
            with open(target_file, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            log_debug(f"Contenu original: {len(original_content)} caracteres")
            
            # Creation sauvegarde
            backup_path = target_file.with_suffix(target_file.suffix + '.backup')
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(original_content)
            log_info(f"Sauvegarde creee: {backup_path}")
            
            # Application des transformations
            modified_content = original_content
            transformations = plan.get('transformations', [])
            
            log_info(f"Application de {len(transformations)} transformations")
            
            changes_made = []
            for i, transform in enumerate(transformations, 1):
                log_debug(f"Transformation {i}: {transform.get('description', 'Sans description')}")
                
                try:
                    before_size = len(modified_content)
                    modified_content = self.apply_single_transformation(modified_content, transform)
                    after_size = len(modified_content)
                    
                    change_desc = f"Etape {i}: {after_size - before_size:+d} caracteres"
                    changes_made.append(change_desc)
                    log_debug(f"Transformation {i} reussie: {change_desc}")
                    
                except Exception as e:
                    error_msg = f"Echec transformation {i}: {e}"
                    log_error(error_msg)
                    if self.logger:
                        self.logger.log_transformation_error(target_file, plan_path.name, error_msg)
                    return False
            
            # Verification mode dry run
            is_dry_run = plan.get('transformation_plan', {}).get('dry_run', True)
            
            if is_dry_run:
                log_info("MODE DRY RUN - Changements non appliques")
                log_info(f"Changements prevus: {changes_made}")
                
                # Log du contenu transforme
                log_debug("Apercu contenu transforme:")
                lines = modified_content.split('\n')
                for i, line in enumerate(lines[:10], 1):
                    log_debug(f"  {i}: {line}")
                if len(lines) > 10:
                    log_debug(f"  ... et {len(lines) - 10} lignes de plus")
                
            else:
                # Application reelle
                log_info("Application reelle des changements")
                with open(target_file, 'w', encoding='utf-8') as f:
                    f.write(modified_content)
                log_info(f"Fichier modifie: {target_file}")
            
            # Log de succes
            if self.logger:
                self.logger.log_transformation_success(target_file, plan_path.name, changes_made)
            
            log_info("SUCCES transformation complete")
            return True
            
        except Exception as e:
            error_msg = f"Erreur generale transformation: {e}"
            log_error(error_msg)
            log_error(f"Traceback: {traceback.format_exc()}")
            
            if self.logger:
                self.logger.log_transformation_error(target_file, plan_path.name, error_msg)
            
            return False
    
    def apply_single_transformation(self, content: str, transform: Dict[str, Any]) -> str:
        """Applique une transformation unique."""
        transform_type = transform.get('type', '')
        target_pattern = transform.get('target_pattern', '')
        insert_after = transform.get('insert_after', True)
        code_lines = transform.get('code_lines', [])
        
        log_debug(f"Transformation: type={transform_type}, pattern='{target_pattern}'")
        
        if not target_pattern:
            raise ValueError("target_pattern manquant")
        
        if not code_lines:
            raise ValueError("code_lines manquant")
        
        lines = content.split('\n')
        modified_lines = []
        pattern_found = False
        
        for line_num, line in enumerate(lines, 1):
            modified_lines.append(line)
            
            # Recherche du pattern
            if target_pattern in line:
                pattern_found = True
                log_debug(f"Pattern trouve ligne {line_num}: {line.strip()}")
                
                if insert_after:
                    # Ajouter les nouvelles lignes apres
                    for code_line in code_lines:
                        modified_lines.append(code_line)
                        log_debug(f"  Ligne ajoutee: {code_line}")
        
        if not pattern_found:
            log_error(f"Pattern non trouve: '{target_pattern}'")
            raise ValueError(f"Pattern non trouve: '{target_pattern}'")
        
        result = '\n'.join(modified_lines)
        log_debug(f"Transformation terminee: {len(lines)} -> {len(modified_lines)} lignes")
        
        return result


# Fonction de test
def test_enhanced_transformer():
    """Test du transformateur ameliore."""
    print("\nTest du transformateur avec logging:")
    
    transformer = JsonAiTransformerWithLogging()
    
    # Fichiers de test
    plan_path = Path("AST_tools/test_interface/instructions_json/hello_user_transformation_plan.json")
    target_file = Path("hello_world.py")
    
    if not plan_path.exists():
        print("Plan JSON non trouve: " + str(plan_path))
        return False
    
    if not target_file.exists():
        print("Fichier cible non trouve: " + str(target_file))
        return False
    
    print("Execution transformation avec logs detailles...")
    success = transformer.apply_transformation_to_file(plan_path, target_file)
    
    result = "SUCCES" if success else "ECHEC"
    print(f"Resultat: {result}")
    
    return success

if __name__ == "__main__":
    test_enhanced_transformer()
