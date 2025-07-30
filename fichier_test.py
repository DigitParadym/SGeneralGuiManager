#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Fichier de test pour valider les transformations JSON.
"""

import os
import sys

# TODO: Ajouter plus de fonctionnalités

def test_function():
    print("Debut du test")
    print("Execution en cours...")
    return True

def calculate_sum(a, b):
    result = a + b
    print(f"Resultat: {result}")
    return result

def process_data(items):
    print("Traitement des donnees")
    processed = []
    for item in items:
        if item > 0:
            processed.append(item * 2)
            print(f"Item traite: {item}")
    return processed

class TestClass:
    def __init__(self, name):
        self.name = name
        print(f"Instance creee: {name}")
    
    def display_info(self):
        print(f"Nom: {self.name}")

def main():
    print("=== PROGRAMME DE TEST ===")
    
    # TODO: Implémenter plus de tests
    result = test_function()
    print(f"Test result: {result}")
    
    calculator_result = calculate_sum(10, 20)
    print(f"Calcul: {calculator_result}")
    
    data = [1, -2, 3, -4, 5]
    processed_data = process_data(data)
    print(f"Donnees traitees: {processed_data}")
    
    test_obj = TestClass("MonTest")
    test_obj.display_info()
    
    print("=== FIN DU TEST ===")

if __name__ == "__main__":
    main()
