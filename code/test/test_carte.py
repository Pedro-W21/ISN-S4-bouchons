import os
from os.path import dirname, abspath
import sys
from random import randint

# Ce fichier teste la génération aléatoire de nb_tests cartes et vérifie qu'elles obéissent à toutes les règles de construction des cartes imposées.

if __name__ == "__main__":
    os.chdir(dirname(abspath(__file__)))
    sys.path.append("../")
    from generation.carte import Carte

    nb_tests = 1000
    palier_tests = nb_tests//100
    print(f"Commencement de {nb_tests} tests de génération de cartes aléatoires")
    for i in range(nb_tests):
        distance = randint(4, 10)
        # La génération de carte n'est testée que sur une partie de la range possible maximale de chaque paramètre, précisés dans le readme
        carte = Carte.genere_aleatoirement(randint(4, 20), randint(4,20), randint(10, 100), distance)
        if not carte.teste_carte(distance):
            print(f"Problème en test {i}")
        if i % palier_tests == 0:
            print(f"{i//palier_tests} % des cartes validées")
    print("100 % des cartes validées")
    print(f"Fin des {nb_tests} tests. Toutes les cartes sont conformes.")
