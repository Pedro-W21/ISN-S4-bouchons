import json

from arrete import Arrete
from noeud import Intersection_T, Intersection_X, Virage, Noeud
from vecteur_2d import Vecteur2D

class Simulation:
    
    ROND_POINT = 'rond_point'
    VIRAGE = 'virage'
    INTERSECTION_T = 'intersection_t'
    ARRETE = 'arrete'

    def __init__(self) -> None:
        self.arretes: list[Arrete] = []
        self.noeuds: list[Noeud] = []

        self.graphe: dict[list[int, int]: list[list[int, int]]] = {}
        #            position_noeud : list[position_noeuds]

    def import_configuration_carte(self, file_path: str):
        with open(file_path, 'r') as file:
            json_file = json.load(file)

            rond_points = json_file[self.ROND_POINT]
            intersections_t = json_file[self.INTERSECTION_T]
            virages = json_file[self.VIRAGE]
            arretes = json_file[self.ARRETE]

            for arrete in arretes:
                point1, point2 = arrete
                point1 = Vecteur2D(point1[0], point1[1])
                point2 = Vecteur2D(point2[0], point2[1])
                longueur = (point1 - point2).norme()
                
                #TODO: ajout de l'aller-retour ?
                self.arretes.append(Arrete(longueur, point1, point2))
                self.arretes.append(Arrete(longueur, point2, point1))
            
            for rond_point in rond_points:
                arretes_reliee = []
                for arrete in self.arretes:
                    if list(arrete.position_depart) == rond_point:
                        arretes_reliee.append(arrete)
                self.noeuds.append(Intersection_X(Vecteur2D(rond_point[0], rond_point[1]), arretes_reliee))
            
            for virage in virages:
                arretes_reliee = []
                for arrete in self.arretes:
                    if list(arrete.position_depart) == virage:
                        arretes_reliee.append(arrete)
                self.noeuds.append(Virage(Vecteur2D(virage[0], virage[1]), arretes_reliee))
                
            for intersection in intersections_t:
                arretes_reliee = []
                for arrete in self.arretes:
                    if list(arrete.position_depart) == intersection:
                        arretes_reliee.append(arrete)
                self.noeuds.append(Intersection_T(Vecteur2D(intersection[0], intersection[1]), arretes_reliee))
                
    def create_graphe(self):
        for noeud_courant in self.noeuds:
            self.graphe[noeud_courant.position] = []
            for noeud_arrivee in self.noeuds:
                if noeud_arrivee.position != noeud_courant.position:
                    # verifie que les noeuds sont bien reliés
                    if any(arrete in noeud_courant.arretes for arrete in noeud_arrivee.arretes):
                        self.graphe[noeud_courant.position].append(noeud_arrivee.position)
                
    def update(self):
        # TODO: update la simulation
        for arrete in self.arretes:
            for voiture in arrete.voitures:
                voiture.update()
                 
    

Simulation().import_configuration_carte('routes.json')