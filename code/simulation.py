import json
import random

from arete import Arete
from voiture import Voiture
from noeud import Intersection_T, Intersection_X, Virage, Noeud
from vecteur_2d import Vecteur2D
import numpy as np
from carte import Carte
from random import choice

class Simulation:

    VIRAGE = "VIRAGE"
    INTERSECTION_T = "INTERSECTION_T"
    INTERSECTION_X = "INTERSECTION_X"
    ENTREE_SORTIE = "ENTREE_SORTIE"

    def __init__(self, carte: Carte, nombre_voiture) -> None:
        self.noeuds: list[Noeud] = carte.into_aretes_noeuds()

    

        self.aretes: list[Arete] = [] # TODO: generer la liste


        self.graphe: dict[list[int, int]: list[list[int, int]]] = {}
        #            position_noeud : list[position_noeuds]
        self.create_graphe()
        self.moyenne_agressivite = 0.5
        self.ecart_type_agressivite = 0.25
        self.nombre_voiture = nombre_voiture
        self.voiture_generee = [self.create_voiture() for _ in range(nombre_voiture)]
        self.entree_sortie_libre: list[Noeud] = [noeud for noeud in self.noeuds if noeud.type == self.ENTREE_SORTIE]

    def create_voiture(self):
        liste_entree_sortie = self.entree_sortie_libre.copy()
        noeud_depart, noeud_arrivee = random.choices(liste_entree_sortie, k=2)
        return Voiture(self.generer_agressivite(), noeud_depart, noeud_arrivee)
    
    def generer_agressivite(self):
        agressivite = np.random.normal(self.moyenne_agressivite, self.ecart_type_agressivite)
        if agressivite < 0:
            agressivite = 0
        elif agressivite > 1:
            agressivite = 1
        return agressivite

    def import_configuration_carte(self, file_path: str):
        with open(file_path, 'r') as file:
            json_file = json.load(file)

            rond_points = json_file[self.ROND_POINT]
            intersections_t = json_file[self.INTERSECTION_T]
            virages = json_file[self.VIRAGE]
            aretes = json_file[self.arete]

            for arete in aretes:
                point1, point2 = arete
                point1 = Vecteur2D(point1[0], point1[1])
                point2 = Vecteur2D(point2[0], point2[1])
                longueur = (point1 - point2).norme()
                
                #TODO: ajout de l'aller-retour ?
                self.aretes.append(arete(longueur, point1, point2))
                self.aretes.append(arete(longueur, point2, point1))
            
            for rond_point in rond_points:
                aretes_reliee = []
                for arete in self.aretes:
                    if list(arete.position_depart) == rond_point:
                        aretes_reliee.append(arete)
                self.noeuds.append(Intersection_X(Vecteur2D(rond_point[0], rond_point[1]), aretes_reliee))
            
            for virage in virages:
                aretes_reliee = []
                for arete in self.aretes:
                    if list(arete.position_depart) == virage:
                        aretes_reliee.append(arete)
                self.noeuds.append(Virage(Vecteur2D(virage[0], virage[1]), aretes_reliee))
                
            for intersection in intersections_t:
                aretes_reliee = []
                for arete in self.aretes:
                    if list(arete.position_depart) == intersection:
                        aretes_reliee.append(arete)
                self.noeuds.append(Intersection_T(Vecteur2D(intersection[0], intersection[1]), aretes_reliee))
                
    def create_graphe(self):
        for noeud_courant in self.noeuds:
            self.graphe[noeud_courant] = []
            for noeud_arrivee in self.noeuds:
                if noeud_arrivee.position != noeud_courant.position:
                    # trouve l'arete commune entre les deux noeuds
                    arete = next((arete for arete in noeud_arrivee.aretes if arete in noeud_courant.aretes), None)
                    # Si une arête commune est trouvée, l'ajouter au graphe
                    if arete:
                        self.graphe[noeud_courant].append((noeud_arrivee, arete))
          
    def update(self):
        # TODO: update la simulation

        # 1. spawn les voitures
        self.entree_sortie_libre = [noeud for noeud in self.noeuds if noeud.type == self.ENTREE_SORTIE]

        for i in range(min(len(self.voiture_generee), len(self.entree_sortie_libre))):
            noeud_spawn = choice(self.entree_sortie_libre)
            voiture_spawn = choice(self.voiture_generee)
            #voiture_spawn.reassign(TODO)
            self.voiture_generee.remove(voiture)
            self.entree_sortie_libre.remove(noeud_spawn)

        # 2. update les voitures
        for arete in self.aretes:
            for voiture in arete.voitures:
                voiture.update()
                if voiture.affiche == False:
                    self.voiture_generee.append(voiture)
        
        # 3. update les noeuds (intersection, rond-point uniquement)
        for noeud in self.noeuds:
            if noeud.type != self.VIRAGE:
                noeud.update()

    # sert pour l'affichage
    def recuperer_voitures(self):
        voitures = []
        for arete in self.aretes:
            voitures += arete.voitures
        return voitures

    