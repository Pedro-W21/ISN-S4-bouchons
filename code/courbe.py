import time
import numpy as np

a = 2
b = -1
c = 2*np.exp(-1)
d = 1/2

    
def fonction_position_e(x):
    return (a*x+b)*np.exp(-np.abs(a*x+b)) / c + d

def fonction_position_lineaire(x):
    return x

def fonction_vitesse_e(x):
    lineaire_fonction = a*x+b
    return (a*np.exp(-np.abs(lineaire_fonction)))/()

def fonction_vitesse_lineaire(x):
    return 1

class Courbe:

    def __init__(self, position_initiale: float, position_finale: float, acceleration: float = 8) -> None:
        self.position_initiale = position_initiale
        self.position_finale = position_finale

        self.t0 = time.time()
        self.tf = ((position_finale - position_initiale) / acceleration) + self.t0


        self.plage_t = (self.tf - self.t0)
        self.plage_position = (position_finale - position_initiale)

        self.active = True
    
    def result_e(self, t: float) -> float:
        temps_normalise = (t - self.t0) / self.plage_t
        if temps_normalise > 1:
            raise ValueError("position doit être entre position_depart et position_arrivee")
        position_normalise = fonction_e(temps_normalise)
        position = position_normalise * self.plage_position + self.position_initiale
        return position
    

    def result_lineaire(self, t: float):
        temps_normalise = (t - self.t0) / self.plage_t
        if temps_normalise > 1.2:
            raise ValueError("position doit être entre position_depart et position_arrivee")
        elif temps_normalise > 1:
            return self.position_finale
        position_normalise = fonction_lineaire(temps_normalise)
        position = position_normalise * self.plage_position + self.position_initiale
        return position

    def __eq__(self, courbe) -> bool:
        return self.position_depart == courbe.position_depart and self.position_arrivee == courbe.position_arrivee and self.position_initiale == courbe.position_initiale and self.position_finale == courbe.position_finale

