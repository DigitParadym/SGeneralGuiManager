#!/usr/bin/env python3
"""
SGeneralGuiManager - Global Test Runner - V3.1 (Finale, Sans Emojis)
Ce script robuste teste l'intégralité des modules Python d'un projet.
Il rapporte les succès et les échecs avec précision, fournit un résumé clair
et copie automatiquement le rapport final dans le presse-papiers.
Cette version n'utilise aucun caractère spécial pour une compatibilité maximale.
"""

import ast
import importlib.util
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path


# --- FONCTION UTILITAIRE: COPIE PRESSE-PAPIERS (MULTI-PLATEFORME) ---
def copy_to_clipboard(text: str):
    """Copie le texte donné dans le presse-papiers."""
    try:
        if sys.platform == "win32":
            subprocess.run(
                ["clip"],
                input=text.encode("utf-8"),
                check=True,
                stderr=subprocess.DEVNULL,
            )
        elif sys.platform == "darwin":
            subprocess.run(
                ["pbcopy"],
                input=text.encode("utf-8"),
                check=True,
                stderr=subprocess.DEVNULL,
            )
        else:
            subprocess.run(
                ["xclip", "-selection", "clipboard"],
                input=text.encode("utf-8"),
                check=True,
                stderr=subprocess.DEVNULL,
            )
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False
    except Exception:
        return False


# --- FONCTION UTILITAIRE: AFFICHAGE D'EN-TÊTES ---
def print_header(title):
    """Affiche un en-tête stylisé pour séparer les sections."""
    print(f"\n{'=' * 60}")
    print(f" {title.upper()} ")
    print(f"{'=' * 60}")


# --- FONCTION CŒUR: TEST D'UN MODULE INDIVIDUEL ---
def test_single_module(module_path: Path, base_path: Path):
    """
    Teste un seul module pour l'existence, la syntaxe et l'importation.
    Retourne un dictionnaire détaillé avec le statut ('PASS' ou 'FAIL').
    """
    relative_path = module_path.relative_to(base_path)
    result = {"name": str(relative_path), "status": "PASS", "details": []}

    if not module_path.exists():
        result["status"] = "FAIL"
        result["details"].append("Fichier non trouvé")
        return result
    result["details"].append("Fichier existe")

    try:
        with open(module_path, encoding="utf-8") as f:
            ast.parse(f.read(), filename=str(module_path))
        result["details"].append("Syntaxe valide")
    except Exception as e:
        result["status"] = "FAIL"
        result["details"].append(f"Erreur de syntaxe: {e}")
        return result

    try:
        module_name = str(relative_path).replace(os.sep, ".").replace(".py", "")
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        if not spec or not spec.loader:
            raise ImportError("Impossible de créer les spécifications du module.")

        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        result["details"].append("Import réussi")
    except Exception as e:
        result["status"] = "FAIL"
        result["details"].append(f"Échec de l'import: {e}")

    return result


# --- FONCTION UTILITAIRE: GÉNÉRATION DU RAPPORT FINAL ---
def generate_text_report(summary: dict, results: list) -> str:
    """Génère un rapport textuel formaté à partir des résultats."""
    report_lines = []
    report_lines.append("RAPPORT DE TEST - SGENERALGUIMANAGER")
    report_lines.append("=" * 60)
    report_lines.append(f"Tests totaux : {summary['total']}")
    report_lines.append(f"Succès : {summary['passed']}")
    report_lines.append(f"Échecs : {summary['failed']}")
    report_lines.append(f"Taux de réussite : {summary['success_rate']:.1f}%")

    if summary["failed"] > 0:
        report_lines.append("\n" + "--- DÉTAILS DES ÉCHECS ---")
        for res in results:
            if res["status"] == "FAIL":
                # MODIFICATION: Remplacement de l'émoji '❌' par du texte
                report_lines.append(f"[ECHEC] {res['name']}")
                report_lines.append(f"   |-- Raison: {res['details'][-1]}")

    return "\n".join(report_lines)


# --- FONCTION PRINCIPALE: ORCHESTRATEUR DE LA SUITE DE TESTS ---
def run_suite():
    """Exécute la suite de tests complète de manière orchestrée."""
    base_path = Path(__file__).parent.parent
    sys.path.insert(0, str(base_path))

    print_header("SGENERALGUIMANAGER - LANCEUR DE TEST GLOBAL V3.1")

    modules_to_test = [
        p for p in base_path.rglob("*.py") if "__init__" not in p.name and "run_tests" not in p.name
    ]
    all_results = []

    print_header("ANALYSE DES MODULES PYTHON")
    for module_path in sorted(modules_to_test):
        result = test_single_module(module_path, base_path)
        all_results.append(result)

        print(f"\nAnalyse de: {result['name']}")
        print("-" * 40)
        for detail in result["details"][:-1]:
            print(f"+ {detail}")

        last_detail = result["details"][-1]
        if result["status"] == "PASS":
            print(f"+ {last_detail}")
        else:
            print(f"X {last_detail}")

    passed_count = sum(1 for r in all_results if r["status"] == "PASS")
    failed_count = len(all_results) - passed_count
    summary = {
        "total": len(all_results),
        "passed": passed_count,
        "failed": failed_count,
        "success_rate": (passed_count / len(all_results) * 100) if all_results else 0,
    }

    print_header("RAPPORT SOMMAIRE DES TESTS")
    report_string = generate_text_report(summary, all_results)
    print(report_string)

    if copy_to_clipboard(report_string):
        print("\n" + "=" * 50)
        # MODIFICATION: Remplacement des émojis
        print(">> Rapport complet copié dans le presse-papiers !")
        print("=" * 50)
    else:
        print("\n" + "=" * 50)
        print(">> Impossible de copier le rapport automatiquement.")
        print("=" * 50)

    report_path = base_path / "tests" / f"test_results_{datetime.now():%Y%m%d_%H%M%S}.json"
    report_path.parent.mkdir(exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump({"summary": summary, "results": all_results}, f, indent=4)
    print(f"\nRapport JSON détaillé sauvegardé dans : {report_path}")

    # MODIFICATION: Remplacement des émojis
    if summary["failed"] == 0:
        print("\n>> TOUS LES TESTS ONT RÉUSSI !")
    else:
        print(f"\n>> {summary['failed']} TEST(S) ONT ÉCHOUÉ.")


if __name__ == "__main__":
    run_suite()
