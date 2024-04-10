from vecteur_2d import Vecteur2D


class Arrete:
    
    size = Vecteur2D(6, 6) # m [longueur, largeur]
    
    def __init__(self, position_depart: Vecteur2D, position_arrivee: Vecteur2D, longueur) -> None:
        self.voitures = []
        vecteur = position_arrivee - position_depart
        self.longueur = vecteur.norme_manathan()
        self.position_depart = position_depart
        self.position_arrivee = position_arrivee
        self.vitesse_moyenne = 0
        self.vitesse_max = 80

    def __eq__(self, noeuds):
        if [self.position_depart, self.position_arrivee] == [noeuds[0].position_depart, noeuds[1].position_depart]:
            return True
        return False
    
    def a_des_voitures(self):
        return len(self.voitures) > 0
    
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