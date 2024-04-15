import json
import random

from arete import Arete
from voiture import Voiture
from noeud import Intersection_T, Intersection_X, Virage, Noeud, EntreeSortie
from vecteur_2d import Vecteur2D
import numpy as np
from carte import Carte
from random import choice, shuffle

class Simulation:

    VIRAGE = "VIRAGE"
    INTERSECTION_T = "INTERSECTION_T"
    INTERSECTION_X = "INTERSECTION_X"
    ENTREE_SORTIE = "ENTREE_SORTIE"

    def __init__(self, carte: Carte, nombre_voiture: float, agressivite: float) -> None:
        
        self.noeuds: list[Noeud] = carte.into_aretes_noeuds() 
        self.aretes: list[Arete] = []
        for noeud in self.noeuds:
            for arete in noeud.aretes:
                if arete not in self.aretes:
                    self.aretes.append(arete)
        self.entrees_sorties: list[EntreeSortie] = [noeud for noeud in self.noeuds if noeud.type == self.entrees_sorties]


        self.graphe: dict[Noeud: list[Noeud, Arete]] = {}
        #            position_noeud : list[position_noeuds]
        self.genere_graphe()

        self.nombre_voiture = nombre_voiture
        self.voitures_generees: list[Voiture] = []
        self.voitures_non_affichees: list[Voiture] = []

        self.moyenne_agressivite = agressivite
        self.ecart_type_agressivite = 0.25
        
        self.compteur_id = 0

    def genere_voitures(self):
        entrees_libres = self.trouver_entrees_libres()
        shuffle(entrees_libres)

        for entree in entrees_libres:
            if len(self.voitures_generees) < self.nombre_voiture:
                sorties = self.entrees_sorties.copy()
                sorties.remove(entree)
                sortie = choice(sorties)

                self.voitures_generees.append(Voiture(self.genere_id(), self.genere_agressivite(), entree, sortie, self.graphe))
            else:
                break
        
    def reasign_voitures(self):
        entrees_libres = self.trouver_entrees_libres()
        for voiture in self.voitures_non_affichees:
            sorties = self.entrees_sorties.copy()
            entree = choice(entrees_libres)
            
            entrees_libres.remove(entrees_libres)
            sorties.remove(entree)
            
            sortie = choice(sorties)
            
            voiture.reassign(self.genere_agressivite, entree, sortie)

    def genere_id(self) -> int:
        self.compteur_id += 1
        return self.compteur_id - 1
 
    def trouver_entrees_libres(self) -> list[EntreeSortie]:
        entrees_libres: list[EntreeSortie] = self.entrees_sorties.copy()

        for voiture in self.voitures_generees:
            if entrees_libres:
                # verifie si il n'y pas des voitures deja générées sur le point
                if voiture.noeud_depart in entrees_libres:
                    entrees_libres.remove(voiture.noeud_depart)
            else:
                break
        
        entrees_restantes: list[EntreeSortie] = entrees_libres.copy()
        for entree in entrees_restantes:
            # TODO: problème si les aretes sont plus petites que la distance de sécurité ?
            # vérifie que il n'y a pas de voiture proche
            if entree.aretes[0].voitures and entree.aretes[0].voitures[-1].distance_a_entite(entree.position) < Voiture.distance_marge_securite:
                entrees_libres.remove(entree)
        return entrees_libres

    def genere_agressivite(self):
        agressivite = np.random.normal(self.moyenne_agressivite, self.ecart_type_agressivite)
        if agressivite < 0:
            agressivite = 0
        elif agressivite > 1:
            agressivite = 1
        return agressivite

    def import_configuration_carte(self, file_path: str):
        with open(file_path, 'r') as file:
            json_file = json.load(file)

            rond_points = json_file[self.INTERSECTION_X]
            intersections_t = json_file[self.INTERSECTION_T]
            virages = json_file[self.VIRAGE]
            # erreur incoming selon le format de fichier
            aretes = json_file[self.ARETE]

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

    def genere_graphe(self):
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
        if not self.voitures_non_affichees:
            self.genere_voitures()
        else:
            self.reasign_voitures()

        for arete in self.aretes:
            for voiture in arete.voitures:
                voiture.update()
                if voiture.affiche == False:
                    self.voitures_non_affichees.append(voiture)

    def recuperer_voitures(self):
        return [voiture for voiture in self.voitures_generees if voiture not in self.voitures_non_affichees]

    def mettre_a_jour_agressivite(self, agressivite: float):
        # agressivite de 0 à 1
        self.moyenne_agressivite = agressivite

    def mettre_a_jour_nombre_voiture(self, nombre_voiture: float):
        self.nombre_voiture = nombre_voiture