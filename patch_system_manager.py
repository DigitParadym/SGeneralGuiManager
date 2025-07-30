#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Patch pour System Manager - Support bouton retour AST
Ajoute le callback de retour pour l'interface AST
"""

def patch_system_manager():
    """Modifie copypaste_manager.py pour supporter le bouton retour."""
    
    import os
    from pathlib import Path
    
    manager_file = Path("copypaste_manager.py")
    
    if not manager_file.exists():
        print("ERREUR: copypaste_manager.py non trouve")
        return False
    
    # Lire le contenu actuel
    with open(manager_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Chercher la methode _open_integrated_view
    if "_open_integrated_view" not in content:
        print("ERREUR: Methode _open_integrated_view non trouvee")
        return False
    
    # Modifier l'appel a InterfaceAST pour inclure le callback
    old_call = "self.active_integrated_frame = InterfaceClass(self.main_pane)"
    
    new_call = """# Callback pour retourner au menu
            def return_to_main_menu():
                self._close_integrated_view()
                self._show_main_interface()
            
            # Creer l'interface avec callback de retour
            if "AST" in module_key:
                self.active_integrated_frame = InterfaceClass(self.main_pane, return_to_main_menu)
            else:
                self.active_integrated_frame = InterfaceClass(self.main_pane)"""
    
    if old_call in content:
        content = content.replace(old_call, new_call)
        
        # Sauvegarder le fichier modifie
        with open(manager_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("+ System Manager patche avec succes")
        print("+ Callback de retour ajoute pour AST")
        return True
    else:
        print("! Ligne a modifier non trouvee - modification manuelle necessaire")
        print("! Cherchez cette ligne dans copypaste_manager.py:")
        print("! " + old_call)
        print("! Et remplacez-la par le code du callback")
        return False

if __name__ == "__main__":
    patch_system_manager()
