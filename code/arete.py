from vecteur_2d import Vecteur2D


class Arete:
    
    size = Vecteur2D(6, 6) # m [longueur, largeur]
    
    def __init__(self, position_depart: Vecteur2D, position_arrivee: Vecteur2D) -> None:
        self.voitures = []
        vecteur = position_arrivee - position_depart
        self.longueur = vecteur.norme_manathan()
        self.position_depart = position_depart
        self.position_arrivee = position_arrivee
        self.vitesse_moyenne = 0.0
        self.vitesse_max = 10.0 # m/s
    
    def __str__(self):
        return f"Arete : {self.position_depart} -> {self.position_arrivee}"
    
    def __eq__(self, other, inverted = False):
        is_the_same = self.position_depart == other.position_depart and self.position_arrivee == other.position_arrivee
        is_inverted = self.position_depart == other.position_arrivee and self.position_arrivee == other.position_depart
        return is_the_same or (is_inverted and inverted)
    
    def is_equal(self, other, inverted = False):
        is_the_same = self.position_depart == other.position_depart and self.position_arrivee == other.position_arrivee
        is_inverted = self.position_depart == other.position_arrivee and self.position_arrivee == other.position_depart
        return is_the_same or (is_inverted and inverted)
    
    def a_des_voitures(self):
        return len(self.voitures) > 0
    
    def get_first_voiture(self):
        return self.voitures[0]
    
    def get_last_voiture(self):
        return self.voitures[-1]
    
    def pop_voiture(self):
        return self.voitures.pop(0)
    
    def push_voiture(self, voiture):
        if voiture not in self.voitures:
            self.voitures.append(voiture)
        else:
            raise ValueError("tente d'ajouter une voiture deja sur l'arete bug ?")

    def get_poids(self):
        return self.longueur / self.get_vitesse_moyenne()
    
    def get_vitesse_moyenne(self):
        if len(self.voitures) != 0:
            moyenne = sum([voiture.vitesse for voiture in self.voitures]) / len(self.voitures)
        else:
            moyenne = self.vitesse_max
        return max(moyenne, 1)