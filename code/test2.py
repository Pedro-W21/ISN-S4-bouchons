import math
from courbe import Courbe
import numpy as np
import matplotlib.pyplot as plt

# NE PAS MODIFIER

if __name__ == "__main__":
    test = "test2"
    if test == "test1":
        position_depart = 0
        position_arrivee = 50
        vitesse_initiale = 0
        vitesse_finale = 20
        
        x = np.linspace(position_depart, position_arrivee, 100)
        y = Courbe(position_depart, position_arrivee, vitesse_initiale, vitesse_finale).result(x)

        plt.plot(x, y)
        plt.xlabel('x')
        plt.ylabel('y')
        plt.title('Courbe')
        plt.grid(True)
        plt.show()
    
    elif test == "test2":
        # TODO : 
        # observation courbe trop bombé donc pas de vitessse suffisante pour accelerer
        # augmenter le nombre de fps
        # diminuer le nombre de frame
        # augmenter l'acceleration de depart

        # controller les parametre pour voir si la vitesse finale est atteinte
        # faire une courbe avec une acceleration moyenne de 8m/s²

        fps = 60

        position_depart = 0
        position_arrivee = 50
        vitesse_initiale = 0
        vitesse_finale = 20/3.6
        
        courbe = Courbe(position_depart, position_arrivee, vitesse_initiale, vitesse_finale)
        frames = np.arange(1, 999999999, 1)
        
        vitesses = [0]
        positions = [0]
        temps = [0]



        acceleration_depart = 0.01
        position = position_depart
        vitesse = 0


        for frame in frames:
            temps_courant = frame/fps
            try:
                if vitesse == 0:
                    vitesse = (vitesse + acceleration_depart)
                    position += vitesse/fps
                else:
                    vitesse = courbe.result(position)
                    position += vitesse/fps
            except ValueError:
                print("Erreur")
                break

            temps.append(temps_courant)
            vitesses.append(vitesse)
            positions.append(position)

            """if frame == 5:
                break"""


        #print("temps", temps)
        #print("vitesses", vitesses)
        #print("positions", positions)

        plt.plot(temps, vitesses, label='Vitesse')
        plt.plot(temps, positions, label='Position')
        plt.xlabel('Temps')
        plt.ylabel('Vitesse / Position')
        plt.title('Évolution de la vitesse et de la position')
        plt.legend()
        plt.grid(True)
        plt.show()
            

            
