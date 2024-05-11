import json
from arete import Arete
from voiture import Voiture
from noeud import Intersection_T, Intersection_X, Virage, Noeud, EntreeSortie
from vecteur_2d import Vecteur2D
import numpy as np
from carte import Carte
from random import choice, shuffle, random

from courbe import Courbe

class Simulation:

    VIRAGE = "VIRAGE"
    INTERSECTION_T = "INTERSECTION_T"
    INTERSECTION_X = "INTERSECTION_X"
    ENTREE_SORTIE = "ENTREE_SORTIE"

    def __init__(self, carte: Carte, nombre_voiture: float, agressivite: float) -> None:
        self.iteration = 0
        self.id = 0
        self.noeuds: list[Noeud] = carte.into_aretes_noeuds()
        self.couleurs = ['red', 'blue', 'green', 'yellow', 'orange', 'purple', 'pink', 'brown', 'cyan', 'magenta']
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

        self.temps_simulation = 0

    def activer_voitures(self):
        """
        Active les voitures sur les entrées libres s'il en manque et génère de nouvelles voitures si l'interface en veut davantage.

        Returns:
            None
        """
        entrees_libres = self.trouver_entrees_libres()

        #Si on a besoin de créer de nouvelles voitures
        for i in range(max(0,self.nombre_voiture-len(self.voitures))):
            nouvelle_voiture = Voiture(self.graphe)
            self.voitures.append(nouvelle_voiture)
        
        voitures_non_active = self.recuperer_voitures_non_actives()
        nb_voitures_active = len(self.recuperer_voitures())
        while len(voitures_non_active) > 0 and len(entrees_libres) > 0 and nb_voitures_active < self.nombre_voiture :
            voiture = voitures_non_active.pop()
            entree = choice(entrees_libres)
            entrees_libres.remove(entree)
            sorties = self.entrees_sorties.copy()
            sorties.remove(entree)
            sortie = choice(sorties)
            couleur = self.genere_couleur()
            voiture.demarrage(self.genere_id(), self.genere_agressivite(), entree, sortie, couleur, self.temps_simulation)
            nb_voitures_active+=1

    def genere_id(self) -> int:
        """
        Génère un identifiant unique pour une nouvelle voiture.

        Returns:
            int: L'identifiant unique généré.
        """
        self.id+=1
        return self.id
    
    def genere_couleur(self):
        """
        Sélectionne aléatoirement une couleur pour une nouvelle voiture.

        Returns:
            str: La couleur choisie.
        """
        couleur = choice(self.couleurs)
        return couleur
    
    def trouver_entrees_libres(self) -> list[EntreeSortie]:
        """
        Trouve les entrées libres où les voitures peuvent être activées.

        Returns:
            list[EntreeSortie]: Une liste des entrées libres.
        """
        entrees_libres = [noeud for noeud in self.entrees_sorties if noeud.voie_est_libre()]
        return entrees_libres
    
    def genere_agressivite(self):
        """
        Génère aléatoirement un niveau d'agressivité pour une nouvelle voiture.

        Returns:
            float: Le niveau d'agressivité généré.
        """
        agressivite = np.random.normal(self.moyenne_agressivite, self.ecart_type_agressivite)
        # return min(max(0.0,agressivite),1.0)
        return 0.5

    def import_configuration_carte(self, file_path: str):
        """
        Importe la configuration de la carte à partir d'un fichier JSON.

        Args:
            file_path (str): Le chemin du fichier JSON contenant la configuration de la carte.

        Returns:
            None
        """
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
        """
        Génère le graphe représentant la carte routière avec les noeuds et les arêtes connectés.

        Returns:
            None
        """
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
          
    def update(self, environnement_actif, delta_temps_simulation):
        """
        Met à jour l'environnement : active les voitures si nécessaire et met à jour chaque voiture active.

        Args:
            environnement_actif (bool, optional): Indique si l'environnement est actif. Par défaut, True.

        Returns:
            None
        """
        #Si on veut générer + de voitures
        self.temps_simulation += delta_temps_simulation
        Courbe.delta_temps_simulation = delta_temps_simulation
        self.iteration+=1
        if environnement_actif:
            voitures_actives = self.recuperer_voitures()
            if self.nombre_voiture > len(self.voitures) or len(voitures_actives) < len(self.voitures):
                self.activer_voitures()
            for voiture in voitures_actives:
                entrees_libres = self.trouver_entrees_libres()
                print("\n\n===============================\nTOUR DE ", voiture.couleur, voiture.id, voiture.affiche)
                voiture.update(self.temps_simulation)
        else:
            pass
        # if self.iteration == 25:
            # exit()
    
    def mettre_a_jour_agressivite(self, agressivite: float):
        """
        Met à jour le niveau moyen d'agressivité des voitures dans l'environnement.

        Args:
            agressivite (float): Le nouveau niveau d'agressivité (compris entre 0 et 1).

        Returns:
            None
        """
        # agressivite de 0 à 1
        self.moyenne_agressivite = min(max(0.0,agressivite),1.0)

    def mettre_a_jour_nombre_voiture(self, nombre_voiture: int):
        """
        Met à jour le nombre de voitures dans l'environnement.

        Args:
            nombre_voiture (int): Le nouveau nombre de voitures.

        Returns:
            None
        """
        self.nombre_voiture = nombre_voiture

    def recuperer_voitures(self):
        """
        Récupère la liste des voitures actives dans l'environnement.

        Returns:
            list: La liste des voitures actives.
        """
        liste_voitures = [voiture for voiture in self.voitures if voiture.affiche]
        return liste_voitures
    
    def recuperer_voitures_non_actives(self):
        """
        Récupère la liste des voitures non actives dans l'environnement.

        Returns:
            list: La liste des voitures non actives.
        """
        return [voiture for voiture in self.voitures if not voiture.affiche]