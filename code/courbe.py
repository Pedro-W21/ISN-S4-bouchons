import time
import numpy as np
import math



a = 2
b = -1
c = 2*np.exp(-1)
d = 1/2

    
def fonction_vitesse_e(t):
    return (a*t+b)*np.exp(-np.abs(a*t+b)) / c + d

def fonction_vitesse_lineaire(t):
    return t

def fonction_position_e(t):
    return 1/(2*a*c) * ((a*c*d*t + np.exp(b+a*t)*(-1+b+a*t)) * (1 - np.sign(b + a*t)) + (a*c*d*t - np.exp(-b-a*t)* (1+b+a*t)) * (1 + np.sign(b + a*t))) + 1/2


def fonction_position_lineaire(t):
    return (1/2) * t^2

class Courbe:

    def __init__(self, vitesse_initiale: float, vitesse_finale: float, position_initiale: float, position_finale: float, acceleration: float = 8) -> None:
        self.vitesse_initiale = vitesse_initiale
        self.vitesse_finale = vitesse_finale

        self.position_initiale = position_initiale
        self.position_finale = position_finale

        self.t0 = time.time()
        self.tf = ((vitesse_finale - vitesse_initiale) / acceleration) + self.t0


        self.plage_t = (self.tf - self.t0)
        self.plage_vitesse = (vitesse_finale - vitesse_initiale)

        self.active = True
    
    def result_e(self, t: float) -> tuple[float, float]:
        temps_normalise = (t - self.t0) / self.plage_t
        if temps_normalise > 1:
            raise ValueError("vitesse doit être entre vitesse_depart et vitesse_arrivee")
        vitesse_normalise = fonction_vitesse_e(temps_normalise)
        position_normalise = fonction_position_e(temps_normalise)

        vitesse = vitesse_normalise * self.plage_vitesse + self.vitesse_initiale
        position = position_normalise * self.plage_vitesse + self.position_initiale
        return vitesse, position
    
    def result_lineaire(self, t: float):
        temps_normalise = (t - self.t0) / self.plage_t
        if temps_normalise > 1.2:
            raise ValueError("vitesse doit être entre vitesse_depart et vitesse_arrivee")
        elif temps_normalise > 1:
            return self.vitesse_finale
        vitesse_normalise = fonction_vitesse_lineaire(temps_normalise)
        position_normalise = fonction_position_lineaire(temps_normalise)
        vitesse = vitesse_normalise * self.plage_vitesse + self.vitesse_initiale
        position = position_normalise * self.plage_vitesse + self.position_initiale
        return vitesse, position

    def __eq__(self, courbe) -> bool:
        return (self.vitesse_initiale, self.vitesse_finale, self.acceleration) == (courbe.vitesse_initiale, courbe.vitesse_finale, courbe.acceleration)
