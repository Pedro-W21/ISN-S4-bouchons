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

        self.active = True
    
    def result(self, position: float) -> float:
        position_normalise = (position - self.position_depart) / self.plage_position
        if position_normalise > 1:
            raise ValueError("position doit être entre position_depart et position_arrivee")
        vitesse_position_normalise = fonction(position_normalise)
        vitesse = vitesse_position_normalise * self.plage_vitesse + self.vitesse_initiale
        return vitesse

    def __eq__(self, courbe) -> bool:
        return self.position_depart == courbe.position_depart and self.position_arrivee == courbe.position_arrivee and self.vitesse_initiale == courbe.vitesse_initiale and self.vitesse_finale == courbe.vitesse_finale

