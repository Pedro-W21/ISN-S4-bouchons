import math
import time
from courbe import Courbe
import numpy as np
import matplotlib.pyplot as plt
import courbe
# NE PAS MODIFIER

if __name__ == "__main__":
    test = "test3"
    a = 2
    b = -1
    c = 2*np.exp(-1)
    d = 1/2

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

        fps = 1/60


        vitesse_initiale = 0
        vitesse_finale = 20/3.6


        
        courbe = Courbe(vitesse_initiale, vitesse_finale, 8)
        print("courbe.t0", "courbe.tf", "courbe.plage_t")
        print(courbe.t0, courbe.tf, courbe.plage_t)

        frames = np.arange(1, 3600, 1)
        
        vitesses = [0]
        positions = [0]
        temps = [time.time()]


        vitesse = vitesse_initiale


        for frame in frames:
            t = time.time()
            try:
                vitesse = courbe.result_e(t)

            except ValueError:
                print("Erreur")
                break
            
            print("vitesse", vitesse)
            print("temps", t)
            temps.append(t)
            vitesses.append(vitesse)

            """if frame == 5:
                break"""
            time.sleep(1/60)

        #print("temps", temps)
        #print("vitesses", vitesses)

        print(temps)
        print(vitesses)
        plt.plot(temps, vitesses, label='Vitesse')
        # plt.plot(temps, positions, label='Position')
        plt.xlabel('Temps')
        plt.ylabel('Vitesse / Position')
        plt.title('Évolution de la vitesse et de la position')
        plt.legend()
        plt.grid(True)
        plt.show()
    
    elif test == "test3":

        t = np.linspace(0, 1, 100)
        position = 1/(2*a*c) * ((a*c*d*t + np.exp(b+a*t)*(-1+b+a*t)) * (1 - np.sign(b + a*t)) + (a*c*d*t - np.exp(-b-a*t)* (1+b+a*t)) * (1 + np.sign(b + a*t))) + 1/2
        vitesse = (a*t+b)*np.exp(-np.abs(a*t+b)) / c + d

        plt.plot(t, position, label='Position')
        plt.plot(t, vitesse, label='Vitesse')
        plt.xlabel('t')
        plt.ylabel('position / vitesse')
        plt.title('Évolution de la position et de la vitesse')
        plt.legend()
        plt.grid(True)
        plt.show()

    elif test == "test4":
        
        courbe = Courbe(0, 10, 0, 10, -1, 0)
        t = 0
        start = t


        positions = []
        vitesses = []
        temps = []
        
        position = 0
        i = 0
        
        while True:
            vitesse, e, test = courbe.result_e_test_temps(t)

            print("vitesse", vitesse)
            position += e
            temps.append(t - start)
            positions.append(position)
            vitesses.append(vitesse)


            if test:
                i+=1
            if i > 6:
                break
            t += 1/60
        
        plt.plot(temps, vitesses, label='Vitesse')
        plt.plot(temps, positions, label='Position')
        plt.xlabel('t')
        plt.ylabel('position / vitesse')
        plt.title('Évolution de la position et de la vitesse')
        plt.legend()
        plt.grid(True)
        plt.show()
    elif test == "test5":

        t = np.linspace(0, 1, 100)
        position = 1/(2*a*c) * ((a*c*d*t + np.exp(b+a*t)*(-1+b+a*t)) * (1 - np.sign(b + a*t)) + (a*c*d*t - np.exp(-b-a*t)* (1+b+a*t)) * (1 + np.sign(b + a*t))) + 1/2
        vitesse = (a*t+b)*np.exp(-np.abs(a*t+b)) / c + d

        plt.plot(t, position, label='Position')
        plt.plot(t, vitesse, label='Vitesse')
        plt.xlabel('t')
        plt.ylabel('position / vitesse')
        plt.title('Évolution de la position et de la vitesse')
        plt.legend()
        plt.grid(True)
        plt.show()

