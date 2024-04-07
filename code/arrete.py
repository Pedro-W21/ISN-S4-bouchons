
from vecteur_2d import Vecteur2D


class Arrete:

    def __init__(self, position_depart: Vecteur2D, position_arrivee: Vecteur2D, longueur) -> None:
        self.voitures = []
        self.longueur = longueur
        self.position_depart = position_depart
        self.position_arrivee = position_arrivee
        self.vitesse_moyenne = 0
        self.vitesse_max = 80

    def get_first_voiture(self):
        return self.voitures[0]
    
    def get_last_voiture(self):
        return self.voitures[-1]
    
    def pop_voiture(self):
        return self.voitures.pop(0)
    
    def push_voiture(self, voiture):
        self.voitures.append(voiture)

    def get_poids(self):
        return self.longueur / self.get_vitesse_moyenne()
    
    def get_vitesse_moyenne(self):
        if len(self.voitures) != 0:
            moyenne = sum([voiture.vitesse for voiture in self.voitures]) / len(self.voitures)
        else:
            moyenne = self.vitesse_max
        return max(moyenne, 1)