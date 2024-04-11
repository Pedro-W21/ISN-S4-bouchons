from vecteur_2d import Vecteur2D
import numpy as np



a = 2
b = -1
c = 2*np.exp(-1)
d = 1/2

    
def fonction(x):
    return (a*x+b)*np.exp(-np.abs(a*x+b)) / c + d

class Courbe:

    def __init__(self, position_depart: float, position_arrivee: float, vitesse_initiale: float, vitesse_finale: float) -> None:
        self.position_depart = position_depart
        self.position_arrivee = position_arrivee
        self.vitesse_initiale = vitesse_initiale
        self.vitesse_finale = vitesse_finale

        self.plage_position = (position_arrivee - position_depart)
        self.plage_vitesse = (vitesse_finale - vitesse_initiale)
    
    def result(self, x_y: float):
        x_y_normalise = (x_y - self.position_depart) / self.plage_position
        vitesse_x_y_normalise = fonction(x_y_normalise)
        vitesse = vitesse_x_y_normalise * self.plage_vitesse + self.vitesse_initiale
        return vitesse
    
    def __eq__(self, courbe) -> bool:
        return self.position_depart == courbe.position_depart and self.position_arrivee == courbe.position_arrivee and self.vitesse_initiale == courbe.vitesse_initiale and self.vitesse_finale == courbe.vitesse_finale

if __name__ == "__main__":
    import matplotlib.pyplot as plt

    position_depart = 40
    position_arrivee = 70
    vitesse_initiale = 80
    vitesse_finale = 50

    x = np.linspace(position_depart, position_arrivee, 100)
    y = Courbe(position_depart, position_arrivee, vitesse_initiale, vitesse_finale).result(x)


    plt.plot(x, y)
    plt.xlabel('x')
    plt.ylabel('y')
    plt.title('Courbe')
    plt.grid(True)
    plt.show()