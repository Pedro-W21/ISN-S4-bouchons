import time
import numpy as np
import math

a = 2
b = -1
c = 2*np.exp(-1)
d = 1/2

def fonction_vitesse_e(t):
    """
    Calcule la vitesse normalisée en fonction du temps par une courbe exponentielle de transfert.
    
    Args:
        t (float): Le temps.
        
    Returns:
        float: La vitesse normalisée calculée.
    """
    return (a*t+b)*np.exp(-np.abs(a*t+b)) / c + d

def fonction_vitesse_lineaire(t):
    """
    Fonction qui représente la courbe linéaire de transfert de vitesse normalisée.
    
    Args:
        t (float): Le temps.
    
    Returns:
        float: La vitesse linéaire normalisée.
    """
    return t

def fonction_position_e(t):
    """
    Calcule de position normalisée via une courbe exponentielle.

    Args:
        t (float): Valeur du temps.

    Returns:
        float: Valeur de la courbe exponentielle de position normalisée.
    """
    return (1/(2*a*c) * ((a*c*d*t + np.exp(b+a*t)*(-1+b+a*t)) * (1 - np.sign(b + a*t)) + (a*c*d*t - np.exp(-b-a*t)* (1+b+a*t)) * (1 + np.sign(b + a*t))) +1/2)

def fonction_position_lineaire(t):
    """
    Calcule la position normalisée via une courbe carre.

    Args:
        t (float): Valeur du temps.

    Returns:
        float: Valeur de la courbe exponentielle de position normalisée.
    """
    return (1/2) * (t**2)

class Courbe:
    
    delta_temps_simulation = 0

    def __init__(self, vitesse_initiale, vitesse_finale, duree, temps_simulation) -> None:
        self.vitesse_initiale = vitesse_initiale
        self.vitesse_finale = vitesse_finale
        self.duree = abs(duree)
        self.temps_depart = temps_simulation - self.delta_temps_simulation

        self.last_position = 0
        self.last_deplacement = 0


    def result_negatif(self, temps_simuation):
        """
        Calcule la vitesse et le déplacement pour un differentiel de vitesse négatif 
        à un certain temps de simulation.

        Args:
            temps_simulation (float): Le temps de simulation.

        Returns:
            tuple: Un tuple contenant la vitesse(float) et le déplacement(float).
        """
        if temps_simuation > self.temps_depart + self.duree:
            vitesse = self.vitesse_finale
            position = self.last_deplacement + self.last_position
        else:
            vitesse = fonction_vitesse_e(abs(temps_simuation - self.temps_depart)/self.duree) * (self.vitesse_finale - self.vitesse_initiale) + self.vitesse_initiale
            position = (1-fonction_position_e(abs(temps_simuation - self.temps_depart)/self.duree)) * abs(self.vitesse_finale - self.vitesse_initiale) * abs(temps_simuation - self.temps_depart) + min(self.vitesse_finale, self.vitesse_initiale) * abs(temps_simuation-self.temps_depart)      
        
        deplacement = abs(position) - self.last_position
        self.last_position = abs(position)
        self.last_deplacement = abs(deplacement)
        return vitesse, deplacement
    
    def result_positif(self, temps_simuation):
        """
        Calcule la vitesse et le déplacement pour un differentiel de vitesse positif 
        à un certain temps de simulation.

        Args:
            temps_simulation (float): Le temps de simulation.

        Returns:
            tuple: Un tuple contenant la vitesse(float) et le déplacement(float).
        """
        if temps_simuation > self.temps_depart + self.duree:
            vitesse = self.vitesse_finale
            position = self.last_deplacement + self.last_position
        else:
            vitesse = fonction_vitesse_e(abs(temps_simuation - self.temps_depart)/self.duree) * (self.vitesse_finale - self.vitesse_initiale) + self.vitesse_initiale
            position = fonction_position_e(abs(temps_simuation - self.temps_depart)/self.duree) * abs(self.vitesse_finale - self.vitesse_initiale) * abs(temps_simuation - self.temps_depart) + min(self.vitesse_finale, self.vitesse_initiale) * abs(temps_simuation-self.temps_depart)      
        
        deplacement = abs(position) - self.last_position
        self.last_position = abs(position)
        self.last_deplacement = abs(deplacement)
        return abs(vitesse), abs(deplacement)

    def result(self, temps_simuation):
        """
        Calcule la vitesse et le déplacement à un certain temps de simulation.

        Args:
            temps_simulation (float): Le temps de simulation.

        Returns:
            tuple: Un tuple contenant la vitesse(float) et le déplacement(float).
        """
        if self.vitesse_finale - self.vitesse_initiale < 0:
            return self.result_negatif(temps_simuation)
        else:
            return self.result_positif(temps_simuation)