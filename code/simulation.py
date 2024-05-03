import json
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

        self.entrees_sorties: list[EntreeSortie] = [noeud for noeud in self.noeuds if noeud.type == self.ENTREE_SORTIE]

        self.graphe: dict[Noeud: list[Noeud, Arete]] = {}
        #            position_noeud : list[position_noeuds]
        self.genere_graphe()

        self.nombre_voiture = nombre_voiture
        self.voitures: list[Voiture] = []

        self.moyenne_agressivite = agressivite
        self.ecart_type_agressivite = 0.25

    def activer_voitures(self):
        entrees_libres = self.trouver_entrees_libres()

        #Si on a besoin de créer de nouvelles voitures
        for i in range(max(0,self.nombre_voiture-len(self.voitures))):
            nouvelle_voiture = Voiture(self.genere_id(), self.graphe)
            self.voitures.append(nouvelle_voiture)
        
        voitures_non_active = self.recuperer_voitures_non_actives()
        while len(voitures_non_active) > 0 and len(entrees_libres) > 0:
            voiture = voitures_non_active.pop()
            entree = choice(entrees_libres)
            entrees_libres.remove(entree)
            sorties = self.entrees_sorties.copy()
            sorties.remove(entree)
            sortie = choice(sorties)
            voiture.demarrage(self.genere_agressivite(), entree, sortie)

    def genere_id(self) -> int:
        return len(self.voitures)
 
    def trouver_entrees_libres(self) -> list[EntreeSortie]:
        entrees_libres: list[EntreeSortie] = self.entrees_sorties.copy()
        for noeud in entrees_libres:
            if not noeud.voie_est_libre():
                entrees_libres.remove(noeud)      
        return entrees_libres

    def genere_agressivite(self):
        agressivite = np.random.normal(self.moyenne_agressivite, self.ecart_type_agressivite)
        return min(max(0.0,agressivite),1.0)

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
            aretes_connectees = []
            for noeud_arrivee in self.noeuds:
                if noeud_arrivee != noeud_courant:
                    for arete1 in noeud_courant.aretes:
                        for arete2 in noeud_arrivee.aretes:
                            if arete1.is_equal(arete2, inverted=True):
                                aretes_connectees.append((noeud_arrivee, arete1))
            self.graphe[noeud_courant] = aretes_connectees
          
    def update(self, environnement_actif = False):
        #Si on veut générer + de voitures
        if environnement_actif:
            voitures_actives = self.recuperer_voitures()
            if self.nombre_voiture > len(self.voitures) or len(voitures_actives) < len(self.voitures):
                self.activer_voitures()
            for voiture in voitures_actives:
                print("\n\n===============================\nTOUR DE ", voiture.couleur)
                voiture.update()
        else:
            pass
    
    def mettre_a_jour_agressivite(self, agressivite: float):
        # agressivite de 0 à 1
        self.moyenne_agressivite = min(max(0.0,agressivite),1.0)

    def mettre_a_jour_nombre_voiture(self, nombre_voiture: int):
        self.nombre_voiture = nombre_voiture

    def recuperer_voitures(self):
        return [voiture for voiture in self.voitures if voiture.affiche]
    
    def recuperer_voitures_non_actives(self):
        return [voiture for voiture in self.voitures if not voiture.affiche]