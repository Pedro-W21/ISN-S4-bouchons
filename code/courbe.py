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
    return 2*(1/(2*a*c) * ((a*c*d*t + np.exp(b+a*t)*(-1+b+a*t)) * (1 - np.sign(b + a*t)) + (a*c*d*t - np.exp(-b-a*t)* (1+b+a*t)) * (1 + np.sign(b + a*t))) + 1/2)


def fonction_position_lineaire(t):
    return (1/2) * (t**2)

class Courbe:

    def __init__(self, vitesse_initiale: float, vitesse_finale: float, position_initiale: float, position_finale: float, acceleration: float, temps_simulation: float) -> None:
        self.acceleration = acceleration
        
        self.vitesse_initiale = vitesse_initiale
        self.vitesse_finale = vitesse_finale

        self.position_initiale = position_initiale
        self.position_finale = position_finale

        self.t0 = temps_simulation
        # self.tf = ((vitesse_finale - vitesse_initiale) / acceleration) + self.t0
        if vitesse_finale == vitesse_initiale:
            self.tf = ((self.position_finale - self.position_initiale) / ((vitesse_finale + vitesse_initiale) / 2)) + self.t0
        else:
            self.tf = -(self.vitesse_initiale - vitesse_finale) / self.acceleration + self.t0
        self.plage_t = (self.tf - self.t0)
        self.plage_vitesse = (vitesse_finale - vitesse_initiale)
        self.plage_position = (position_finale - position_initiale)

        self.active = True

        self.last_position = position_initiale
        self.last_time = self.t0
        
    
    def result_e(self, t: float) -> tuple[float, float]:

        temps_normalise = (t - self.t0) / self.plage_t
        
        if temps_normalise > 1:
            return self.vitesse_finale, self.position_finale - self.last_position, True
        
        vitesse_normalise = fonction_vitesse_e(temps_normalise)
        position_normalise = fonction_position_e(temps_normalise)
        vitesse = vitesse_normalise * self.plage_vitesse + self.vitesse_initiale
        position = position_normalise * self.plage_position - self.last_position
        self.last_position += position

        return vitesse, position, False
    
    def result_e_test(self, t: float) -> tuple[float, float]:
        temps_normalise = (t - self.t0) / self.plage_t
        
        if temps_normalise > 1:
            res =  self.vitesse_finale, (t - self.last_time)*self.vitesse_finale, True
            self.last_position += (t - self.last_time)*self.vitesse_finale
            return res
        
        vitesse_normalise = fonction_vitesse_e(temps_normalise)
        position_normalise = fonction_position_e(temps_normalise)

        if True:
            vitesse = vitesse_normalise * self.plage_vitesse + self.vitesse_initiale
            position = (t - self.last_time)*vitesse

        self.last_position += position
        self.last_time = t
        return vitesse, position, False
    
    def result_e_test_temps(self, t: float) -> tuple[float, float]:
        temps_normalise = (t - self.t0) / self.plage_t
        
        if temps_normalise > 1:
            res = self.vitesse_finale, (t - self.last_time)*self.vitesse_finale, True
            self.last_position += (t - self.last_time)*self.vitesse_finale
            return res
        
        vitesse_normalise = fonction_vitesse_e(temps_normalise)
        position_normalise = fonction_position_e(temps_normalise)

        if True:
            vitesse = vitesse_normalise * self.plage_vitesse + self.vitesse_initiale
            position = position_normalise * self.plage_position * 2 - self.last_position

        self.last_position += position
        self.last_time = t
        return vitesse, position, False
    
    def result_lineaire(self, t: float):
        temps_normalise = (t - self.t0) / self.plage_t
        if temps_normalise > 1.2:
            raise ValueError("vitesse doit être entre vitesse_depart et vitesse_arrivee")
        elif temps_normalise > 1:
            return self.vitesse_finale
        vitesse_normalise = fonction_vitesse_lineaire(temps_normalise)
        position_normalise = fonction_position_lineaire(temps_normalise)
        vitesse = vitesse_normalise * self.plage_vitesse + self.vitesse_initiale
        position = position_normalise * self.plage_vitesse - self.last_position

        self.last_position += position

        return vitesse, position

    def __eq__(self, courbe) -> bool:
        return (self.vitesse_initiale, self.vitesse_finale, self.position_initiale, self.position_finale) == (courbe.vitesse_initiale, courbe.vitesse_finale, courbe.acceleration, courbe.position_initiale, courbe.position_finale)


if __name__ == "__main__":

    pass