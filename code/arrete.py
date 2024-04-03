from noeud import Noeud

class Arrete:

    def __init__(self, noeud_depart: Noeud, noeud_arrivee: Noeud, longueur, poids_par_voiture) -> None:
        self.voitures = []
        self.longueur = 0
        self.noeud_depart = noeud_depart
        self.noeud_arrivee = noeud_arrivee
        self.poids_par_voiture = poids_par_voiture
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