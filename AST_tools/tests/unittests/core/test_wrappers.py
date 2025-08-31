#!/usr/bin/env python3
"""
Script de test pour les nouveaux wrappers generiques.
"""

import json
import sys
from pathlib import Path

# Ajouter le chemin pour les imports
sys.path.insert(0, str(Path(__file__).parent))
from core.plugins.wrappers.pyupgrade_wrapper import PyupgradeWrapper
from core.plugins.wrappers.ruff_wrapper import RuffWrapper

# Code de test
TEST_CODE = """
import os
import sys
from typing import List, Dict

def hello_world(name: str) -> str:
    # Simple fonction de test
    message = "Hello, %s!" % name
    print message
    return message

class OldStyleClass:
    def __init__(self):
        super(OldStyleClass, self).__init__()
        self.data = dict()
"""


def test_ruff_wrapper():
    """Test du wrapper Ruff avec differents parametres."""
    print("\n" + "=" * 60)
    print("TEST RUFF WRAPPER")
    print("=" * 60)

    wrapper = RuffWrapper()

    # Test 1: Check simple avec fix
    params1 = {"command": "check", "fix": True, "select": ["E", "F"], "ignore": ["E501"]}

    print("\nTest 1 - Check avec fix et selection de regles:")
    print(f"Parametres: {json.dumps(params1, indent=2)}")

    try:
        result1 = wrapper.transform(TEST_CODE, params1)
        print(f"Code transforme (premiers 200 caracteres):\n{result1[:200]}...")
    except Exception as e:
        print(f"Erreur: {e}")

    # Test 2: Format avec options
    params2 = {"command": "format", "line_length": 100}

    print("\nTest 2 - Format avec longueur de ligne:")
    print(f"Parametres: {json.dumps(params2, indent=2)}")

    try:
        result2 = wrapper.transform(TEST_CODE, params2)
        print(f"Code formate (premiers 200 caracteres):\n{result2[:200]}...")
    except Exception as e:
        print(f"Erreur: {e}")


def test_pyupgrade_wrapper():
    """Test du wrapper Pyupgrade."""
    print("\n" + "=" * 60)
    print("TEST PYUPGRADE WRAPPER")
    print("=" * 60)

    wrapper = PyupgradeWrapper()

    # Test avec mise a jour vers Python 3.8+
    params = {"python_version": "38"}

    print("\nTest - Modernisation vers Python 3.8+:")
    print(f"Parametres: {json.dumps(params, indent=2)}")

    try:
        result = wrapper.transform(TEST_CODE, params)
        print(f"Code modernise (premiers 200 caracteres):\n{result[:200]}...")
    except Exception as e:
        print(f"Erreur: {e}")


if __name__ == "__main__":
    print("\n[START] TESTS DES WRAPPERS GENERIQUES\n")

    test_ruff_wrapper()
    test_pyupgrade_wrapper()

    print("\n" + "=" * 60)
    print("[OK] TESTS TERMINES!")
    print("=" * 60)
