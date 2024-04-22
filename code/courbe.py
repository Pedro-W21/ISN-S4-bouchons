import time
import numpy as np



a = 2
b = -1
c = 2*np.exp(-1)
d = 1/2

    
def fonction_e(x):
    return (a*x+b)*np.exp(-np.abs(a*x+b)) / c + d

def fonction_lineaire(x):
    return x

class Courbe:

    def __init__(self,vitesse_initiale: float, vitesse_finale: float, acceleration: float = 8) -> None:
        self.vitesse_initiale = vitesse_initiale
        self.vitesse_finale = vitesse_finale

        self.t0 = time.time()
        self.tf = ((vitesse_finale - vitesse_initiale) / acceleration) + self.t0


        self.plage_t = (self.tf - self.t0)
        self.plage_vitesse = (vitesse_finale - vitesse_initiale)

        self.active = True
    
    def result_e(self, t: float) -> float:
        temps_normalise = (t - self.t0) / self.plage_t
        if temps_normalise > 1:
            raise ValueError("position doit être entre position_depart et position_arrivee")
        vitesse_normalise = fonction_e(temps_normalise)
        vitesse = vitesse_normalise * self.plage_vitesse + self.vitesse_initiale
        return vitesse
    

    def result_lineaire(self, t: float):
        temps_normalise = (t - self.t0) / self.plage_t
        if temps_normalise > 1.2:
            raise ValueError("position doit être entre position_depart et position_arrivee")
        elif temps_normalise > 1:
            return self.vitesse_finale
        vitesse_normalise = fonction_lineaire(temps_normalise)
        vitesse = vitesse_normalise * self.plage_vitesse + self.vitesse_initiale
        return vitesse

    def __eq__(self, courbe) -> bool:
        return self.position_depart == courbe.position_depart and self.position_arrivee == courbe.position_arrivee and self.vitesse_initiale == courbe.vitesse_initiale and self.vitesse_finale == courbe.vitesse_finale

