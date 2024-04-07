import random
import numpy as np
import os
import matplotlib.pyplot as plt


class Carte:

    NOEUD = 1
    ARRETE = 2    

    def __init__(self, taille: list[int, int] = [10, 10], distance_entre_noeuds = 5) -> None:
        width, height = taille

        self.width = width
        self.height = height

        # genere une grille de 0
        self.grille = [[0 for _ in range(width)] for _ in range(height)]

        self.distance_entre_noeud = distance_entre_noeuds
        
        nombre_noeud_max = (self.width * self.height) // (self.distance_entre_noeud*2+1)**2 + 1
        self.nombre_noeud = nombre_noeud_max - random.randint(0, 2)
        self.nombre_noeud = max(1, self.nombre_noeud)


        self.porbabilite_noeud = 1/self.nombre_noeud

        self.porbabilite_entree_sortie = 1/10
        self.nombre_entree_sortie = int((2*width + 2*height) * self.porbabilite_noeud) + 2

    def return_max_grille(self, grille) -> int:
        return max([max(ligne) for ligne in grille])

    def return_positions_de(self, element: int, grille) -> list[list[int, int]]:
        return [[i, j] for i in range(self.height) for j in range(self.width) if grille[i][j] == element]
    
    def return_positions_de_non(self, element: int, grille) -> list[list[int, int]]:
        return [[i, j] for i in range(self.height) for j in range(self.width) if grille[i][j] != element]

    def affiche_grille_terminal(self, grille: list[list[int]]):
        for ligne in grille:
            for case in ligne:
                if case != -1:
                    print(" ", end='')
                print(f"{case:5.3f}", end=' ')
            print()

    def affiche_grille(self, grille: list[list[int]]):
        # Convert the grid values to a numpy array
        grid_array = np.array(grille)

        # Mask -1 values
        masked_array = np.ma.masked_where(grid_array == -1, grid_array)

        # Create a figure and axis
        fig, ax = plt.subplots()

        # Create a colormap with a gradient from blue to red
        cmap = plt.cm.get_cmap('coolwarm')

        # Set the color for masked values to black
        cmap.set_bad(color='black')

        # Plot the grid as an image with the colormap
        im = ax.imshow(masked_array, cmap=cmap, vmin=0, vmax=1)

        # Add grid lines
        ax.grid(True, which='both', color='black', linewidth=1)
        ax.set_xticks(np.arange(0, self.width, 1))
        ax.set_yticks(np.arange(0, self.height, 1))

        # Show the plot
        plt.show()

    def generer_noeud(self):
        grille_probas = [[self.porbabilite_noeud for _ in range(self.width)] for _ in range(self.height)]
        
        # met tous les points de la grille à 0 du bord ou à 1 du bord à 0 de probabilité et les autres à 1
        def initialise_grille_probas():
            for i in range(self.height):
                for j in range(self.width):
                    point_au_bord = i == 0 or i == self.height - 1 or j == 0 or j == self.width - 1
                    point_juste_avant_le_bord = i == 1 or i == self.height - 2 or j == 1 or j == self.width - 2
                    if point_au_bord or point_juste_avant_le_bord:
                        grille_probas[i][j] = 0

        def nombre_point_autour(i: int, j: int, distance_mananthan: int, taille) -> int:
            res = 0
            for x in range(i - distance_mananthan, i + distance_mananthan + 1):
                for y in range(j - distance_mananthan, j + distance_mananthan + 1):
                        res += 1

        def test_genere_noeud():
            return True
        
        def actualise_grille_probas():

            distance_mananthan = self.distance_entre_noeud
            positions_noeuds = self.return_positions_de(self.NOEUD, self.grille)

            # met des 0 ou il est impossible que les intersections apparaissent
            for i, j in positions_noeuds:
                for x in range(i - distance_mananthan, i + distance_mananthan + 1):
                    for y in range(j - distance_mananthan, j + distance_mananthan +1):
                        if 0 <= x < self.height and 0 <= y < self.width:
                            
                            grille_probas[x][y] = 0
            

            # recalcule les probabilités de chaque case non defenie
            positions_noeuds = self.return_positions_de(-1, grille_probas)

            # copie de la grille
            grille_probas_actualisee = [[0 for _ in range(self.width)] for _ in range(self.height)]
            for i in range(self.height):
                for j in range(self.width):
                    grille_probas_actualisee[i][j] = grille_probas[i][j]


            for i, j in positions_noeuds:
                list_valeur_points = []

                for x in range(i - distance_mananthan, i + distance_mananthan + 1):
                    for y in range(j - distance_mananthan, j + distance_mananthan + 1):
                        # pas sur que il n'y est pas des points egal
                        if grille_probas[x][y] != -1 and not (i == x and j == y):
                            list_valeur_points.append(grille_probas[x][y])
                

                # calcul de la probabilité different

                grille_probas_actualisee[i][j] = (1 - sum(list_valeur_points)) / (25 - len(list_valeur_points))

               
            for i in range(self.height):
                for j in range(self.width):
                    grille_probas[i][j] = grille_probas_actualisee[i][j]
        

        initialise_grille_probas()
        """self.affiche_grille_terminal(grille_probas)
        self.affiche_grille(grille_probas)"""


        positions_noeuds_ = []

        for i in range(self.nombre_noeud):
            positions_noeuds = self.return_positions_de_non(-1, grille_probas)
            dict_proba = {}
            for x, y, in positions_noeuds:
                dict_proba[str((x, y))] = grille_probas[x][y]

            sum_proba = sum(dict_proba.values())

            if sum_proba == 0:
                break


            for key in dict_proba.keys():
                dict_proba[key] /= sum_proba
            
            # Tirer aléatoirement une position en fonction des pondérations
            position = np.random.choice(a=list(dict_proba.keys()), p=list(dict_proba.values()))
            
            del dict_proba[position]

            position = [int(i) for i in position[1:-1].split(",")]
            # Mettre à jour la grille avec le nouveau nœud
            self.grille[position[0]][position[1]] = self.NOEUD

            positions_noeuds_.append(position)

            actualise_grille_probas()

            os.system('cls' if os.name == 'nt' else 'clear')
            """self.affiche_grille_terminal(self.grille)
            self.affiche_grille(self.grille)"""

        os.system('cls' if os.name == 'nt' else 'clear')

        """self.affiche_grille_terminal(grille_probas)
        self.affiche_grille(grille_probas)"""

        """print(self.return_positions_de(self.NOEUD, self.grille))
        print(positions_noeuds_)
        print(self.nombre_noeud)"""

        
        

carte = Carte([20, 20], 5)
carte.generer_noeud()
carte.affiche_grille_terminal(carte.grille)
carte.affiche_grille(carte.grille)