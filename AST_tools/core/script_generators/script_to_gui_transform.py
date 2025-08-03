"""
Transformateur pour generer des interfaces GUI a partir de scripts.

Ce module permet de generer automatiquement des interfaces graphiques
basees sur l'analyse de scripts Python existants.
"""

import ast
from typing import List, Dict, Any, Optional
from pathlib import Path


class ScriptToGuiTransform:
    """
    Generateur d'interface GUI basee sur l'analyse de scripts Python.
    """
    
    def __init__(self):
        """Initialise le transformateur script vers GUI."""
        self.supported_frameworks = ['tkinter', 'PyQt5', 'wxPython']
        self.default_framework = 'tkinter'
    
    def analyze_script(self, script_path: Path) -> Dict[str, Any]:
        """
        Analyse un script Python pour extraire les elements GUI potentiels.
        
        Args:
            script_path: Chemin vers le script a analyser
            
        Returns:
            Dictionnaire contenant l'analyse du script
        """
        if not script_path.exists():
            raise FileNotFoundError(f"Script non trouve: {script_path}")
        
        with open(script_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        try:
            tree = ast.parse(source_code)
            analysis = {
                'functions': self._extract_functions(tree),
                'variables': self._extract_variables(tree),
                'inputs': self._detect_input_needs(tree),
                'outputs': self._detect_output_needs(tree),
                'gui_elements': self._suggest_gui_elements(tree)
            }
            return analysis
            
        except SyntaxError as e:
            raise ValueError(f"Erreur de syntaxe dans {script_path}: {e}")
    
    def _extract_functions(self, tree: ast.AST) -> List[Dict[str, str]]:
        """Extrait les fonctions du script."""
        functions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append({
                    'name': node.name,
                    'args': [arg.arg for arg in node.args.args],
                    'docstring': ast.get_docstring(node) or "Pas de documentation"
                })
        return functions
    
    def _extract_variables(self, tree: ast.AST) -> List[str]:
        """Extrait les variables globales du script."""
        variables = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        variables.append(target.id)
        return list(set(variables))
    
    def _detect_input_needs(self, tree: ast.AST) -> List[Dict[str, str]]:
        """Detecte les besoins d'entree utilisateur."""
        inputs = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if (isinstance(node.func, ast.Name) and 
                    node.func.id == 'input'):
                    prompt = "Entree utilisateur"
                    if node.args and isinstance(node.args[0], ast.Str):
                        prompt = node.args[0].s
                    inputs.append({
                        'type': 'text_input',
                        'prompt': prompt
                    })
        return inputs
    
    def _detect_output_needs(self, tree: ast.AST) -> List[Dict[str, str]]:
        """Detecte les besoins de sortie."""
        outputs = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if (isinstance(node.func, ast.Name) and 
                    node.func.id == 'print'):
                    outputs.append({
                        'type': 'text_output',
                        'content': 'Sortie console'
                    })
        return outputs
    
    def _suggest_gui_elements(self, tree: ast.AST) -> List[Dict[str, str]]:
        """Suggere des elements GUI bases sur l'analyse."""
        elements = []
        
        # Analyse des patterns communs
        has_input = any(isinstance(node, ast.Call) and 
                       isinstance(node.func, ast.Name) and 
                       node.func.id == 'input' 
                       for node in ast.walk(tree))
        
        has_print = any(isinstance(node, ast.Call) and 
                       isinstance(node.func, ast.Name) and 
                       node.func.id == 'print' 
                       for node in ast.walk(tree))
        
        if has_input:
            elements.append({
                'type': 'Entry',
                'description': 'Zone de saisie de texte'
            })
            elements.append({
                'type': 'Button',
                'description': 'Bouton de validation'
            })
        
        if has_print:
            elements.append({
                'type': 'Text',
                'description': 'Zone d'affichage des resultats'
            })
        
        return elements
    
    def generate_gui_code(self, analysis: Dict[str, Any], 
                         framework: str = None) -> str:
        """
        Genere le code GUI base sur l'analyse.
        
        Args:
            analysis: Resultat de l'analyse du script
            framework: Framework GUI a utiliser
            
        Returns:
            Code GUI genere
        """
        if framework is None:
            framework = self.default_framework
        
        if framework not in self.supported_frameworks:
            raise ValueError(f"Framework non supporte: {framework}")
        
        if framework == 'tkinter':
            return self._generate_tkinter_code(analysis)
        else:
            raise NotImplementedError(f"Generation pour {framework} pas encore implementee")
    
    def _generate_tkinter_code(self, analysis: Dict[str, Any]) -> str:
        """Genere du code Tkinter."""
        code_parts = []
        
        # Import et classe de base
        code_parts.append("""import tkinter as tk
from tkinter import ttk, messagebox


class GeneratedGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Interface Generee")
        self.root.geometry("400x300")
        
        self.create_widgets()
    
    def create_widgets(self):""")
        
        # Generation des widgets bases sur l'analyse
        if analysis.get('inputs'):
            for i, input_info in enumerate(analysis['inputs']):
                code_parts.append(f"""
        # Zone d'entree {i+1}
        self.label_{i} = tk.Label(self.root, text="{input_info['prompt']}")
        self.label_{i}.pack(pady=5)
        
        self.entry_{i} = tk.Entry(self.root, width=30)
        self.entry_{i}.pack(pady=5)""")
        
        # Bouton d'execution
        code_parts.append("""
        # Bouton d'execution
        self.execute_btn = tk.Button(self.root, text="Executer", 
                                   command=self.execute_action)
        self.execute_btn.pack(pady=10)""")
        
        if analysis.get('outputs'):
            code_parts.append("""
        # Zone de resultats
        self.result_text = tk.Text(self.root, height=10, width=50)
        self.result_text.pack(pady=10, padx=10, fill='both', expand=True)""")
        
        # Methode d'execution
        code_parts.append("""
    
    def execute_action(self):
        """Execute l'action principale."""
        try:
            # TODO: Implementer la logique metier ici
            result = "Execution reussie!"
            if hasattr(self, 'result_text'):
                self.result_text.insert(tk.END, result + "\n")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))


def main():
    root = tk.Tk()
    app = GeneratedGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()""")
        
        return "".join(code_parts)
    
    def save_generated_gui(self, gui_code: str, output_path: Path) -> None:
        """
        Sauvegarde le code GUI genere.
        
        Args:
            gui_code: Code GUI a sauvegarder
            output_path: Chemin de sortie
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(gui_code)
        
        print(f"Code GUI sauvegarde dans: {output_path}")


# Exemple d'utilisation
if __name__ == "__main__":
    transformer = ScriptToGuiTransform()
    
    # Exemple d'analyse d'un script simple
    example_analysis = {
        'functions': [{'name': 'main', 'args': [], 'docstring': 'Fonction principale'}],
        'variables': ['name', 'age'],
        'inputs': [
            {'type': 'text_input', 'prompt': 'Entrez votre nom: '},
            {'type': 'text_input', 'prompt': 'Entrez votre age: '}
        ],
        'outputs': [
            {'type': 'text_output', 'content': 'Sortie console'}
        ],
        'gui_elements': [
            {'type': 'Entry', 'description': 'Zone de saisie'},
            {'type': 'Button', 'description': 'Bouton validation'},
            {'type': 'Text', 'description': 'Zone resultats'}
        ]
    }
    
    # Generation du code GUI
    gui_code = transformer.generate_gui_code(example_analysis)
    print("Code GUI genere:")
    print("=" * 50)
    print(gui_code[:500] + "..." if len(gui_code) > 500 else gui_code)
