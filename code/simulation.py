

from arrete import Arrete
from noeud import Noeud


class Simulation:

    def __init__(self) -> None:
        self.arretes: list[Arrete] = []
        self.noeuds: list[Noeud] = []

    
    def update(self):
        for arrete in self.arretes:
            for voiture in arrete.voitures:
                voiture.update()
            last_voiture = arrete.get_last_voiture()
            if arrete.noeud_arrivee.est_proche(last_voiture):
                arrete.noeud_arrivee.voie_est_libre(last_voiture)
                pass
                