def bad_function(x, y):  # Espaces manquants
    very_long_line = (
        x
        + y
        + "cette ligne est trop longue et devrait etre coupee pour respecter les conventions"
    )
    if x == True:  # Comparaison avec True
        print("Hello")
    return very_long_line
