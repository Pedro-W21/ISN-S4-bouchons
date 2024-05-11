from simulation.arete import Arete
from utils.vecteur_2d import Vecteur2D

class Noeud:
    size = Vecteur2D(6, 6)

    VIRAGE = "VIRAGE"
    INTERSECTION_T = "INTERSECTION_T"
    INTERSECTION_X = "INTERSECTION_X"
    ENTREE_SORTIE = "ENTREE_SORTIE"

    def __init__(self, position: Vecteur2D, aretes: list[Arete]):
        self.position = position
        self.usagers = {} #: dict[Voiture : list[direction: Vecteur2D, direction_prochain_chemin: Vecteur2D]]
        self.nom = f"{position.get_x()},{position.get_y()}"
        self.vitesse_max = 3.5 # m/s
        self.aretes = aretes
    
    def retirer_usager(self, voiture):
        if self.usagers.get(voiture, False):
            self.usagers.pop(voiture)

    def get_poids(self):
        return self.size.x / self.get_vitesse_moyenne()
    
    def get_vitesse_moyenne(self):
        if len(self.usagers) != 0:
            moyenne = sum([usager.vitesse for usager in self.usagers.keys()]) / len(self.usagers)
        else:
            moyenne = self.vitesse_max
        return max(moyenne, 1)
    
    def get_usagers(self):
        return self.usagers
    
    def enregistrer_usager(self, voiture, orientation, intention):
        self.usagers[voiture] = [orientation, intention]

    def voie_est_libre(self):
        return True
    
    def est_empruntee(self) -> bool:
        return len(self.usagers) > 0
    
    def est_un_usager(self, voiture) -> bool:
        return voiture in self.usagers

class Virage(Noeud):
    def __init__(self, position, aretes=None):
        super().__init__(position, aretes)
        self.type=self.VIRAGE

    def voie_est_libre(self, voiture):
        return True
    
class Intersection_T(Noeud):
    def __init__(self, position, aretes=None):
        super().__init__(position, aretes)
        self.type=self.INTERSECTION_T
    
    def voie_est_libre(self, voiture):
        orientation, intention = voiture.intention()
        from_right_to_left = Vecteur2D(orientation.y,-orientation.x) #vient de ma droite / va à ma gauche
        from_left_to_right = Vecteur2D(-orientation.y,orientation.x) #vient de ma gauche / va à ma droite
        from_front_to_me = Vecteur2D(-orientation.x,-orientation.y) #vient d'en face et va tout droit
        from_me_to_front = orientation #va ou vient de la même direction que moi
        # selon x [1, 0]
        # selon y [0, 1]
        # selon -x [-1, 0]
        # selon -y [0, -1]
        libre = True
        for usager, intentions in self.usagers.items():
            orientation_usager, intention_usager = intentions
            if usager.id != voiture.id:
                if intention == orientation: 
                    #Je vais tout droit
                    if orientation_usager == from_right_to_left and intention_usager in [intention, from_front_to_me, from_right_to_left]:
                        #Si la personne à ma droite tourne sur ma trajectoire ou la coupe  
                        libre = False
                    if orientation_usager == from_left_to_right and intention_usager in [intention, from_left_to_right]:
                        #Si la personne à ma gauche tourne sur ma trajectoire ou la coupe
                        libre = False
                    if orientation_usager == from_front_to_me and intention_usager == from_left_to_right:
                        #Si la personne en face de moi tourne à sa gauche
                        libre = False 
                elif intention == from_left_to_right:
                    #Je vais sur ma droite
                    if orientation_usager == from_front_to_me and intention_usager == from_left_to_right:
                        #Si la personne en face de moi tourne à sa gauche
                        libre = False
                    if orientation_usager == from_left_to_right and intention_usager == from_left_to_right:
                        #Si la personne à ma gauche tourne à sa gauche
                        libre = False
                elif intention == from_right_to_left:
                    #Je vais sur ma gauche
                    if orientation_usager == from_right_to_left and intention_usager in [from_front_to_me, intention, from_me_to_front]:
                        #Si la personne à ma droite tourne quelque part
                        libre = False
                    if orientation_usager == from_left_to_right and intention_usager in [from_left_to_right, from_me_to_front]:
                        #Si la personne à ma gauche tourne à sa gauche
                        libre = False
                    if orientation_usager == from_front_to_me and intention_usager in [from_front_to_me, from_right_to_left, from_left_to_right]:
                        #Si la personne en face tourne quelque part
                        libre = False  
        if libre:
            self.enregistrer_usager(voiture, orientation, intention)
        return libre

class Intersection_X(Noeud):

    def __init__(self, position, aretes=None) -> None:
        super().__init__(position, aretes)
        self.type=self.INTERSECTION_X
    
    def voie_est_libre(self, voiture):
        orientation, intention = voiture.intention()
        from_right_to_left = Vecteur2D(orientation.y,-orientation.x) #vient de ma droite / va à ma gauche
        from_left_to_right = Vecteur2D(-orientation.y,orientation.x) #vient de ma gauche / va à ma droite
        from_front_to_me = Vecteur2D(-orientation.x,-orientation.y) #vient d'en face et va tout droit
        from_me_to_front = orientation #va ou vient de la même direction que moi
        # selon x [1, 0]
        # selon y [0, 1]
        # selon -x [-1, 0]
        # selon -y [0, -1]
        libre = True
        for usager, intentions in self.usagers.items():
            orientation_usager, intention_usager = intentions
            if usager.id != voiture.id:
                if intention == orientation: 
                    #Je vais tout droit
                    if orientation_usager == from_right_to_left and intention_usager in [intention, from_front_to_me, from_right_to_left]:
                        #Si la personne à ma droite tourne sur ma trajectoire ou la coupe  
                        libre = False
                    if orientation_usager == from_left_to_right and intention_usager in [intention, from_left_to_right]:
                        #Si la personne à ma gauche tourne sur ma trajectoire ou la coupe
                        libre = False
                    if orientation_usager == from_front_to_me and intention_usager == from_left_to_right:
                        #Si la personne en face de moi tourne à sa gauche
                        libre = False 
                elif intention == from_left_to_right:
                    #Je vais sur ma droite
                    if orientation_usager == from_front_to_me and intention_usager == from_left_to_right:
                        #Si la personne en face de moi tourne à sa gauche
                        libre = False
                    if orientation_usager == from_left_to_right and intention_usager == from_left_to_right:
                        #Si la personne à ma gauche tourne à sa gauche
                        libre = False
                elif intention == from_right_to_left:
                    #Je vais sur ma gauche
                    if orientation_usager == from_right_to_left and intention_usager in [from_front_to_me, intention, from_me_to_front]:
                        #Si la personne à ma droite tourne quelque part
                        libre = False
                    if orientation_usager == from_left_to_right and intention_usager in [from_left_to_right, from_me_to_front]:
                        #Si la personne à ma gauche tourne à sa gauche
                        libre = False
                    if orientation_usager == from_front_to_me and intention_usager in [from_front_to_me, from_right_to_left, from_left_to_right]:
                        #Si la personne en face tourne quelque part
                        libre = False  
        if libre:
            self.enregistrer_usager(voiture, orientation, intention)
        return libre

class EntreeSortie(Noeud):

    def __init__(self, position, aretes):
        super().__init__(position, aretes)
        self.type=self.ENTREE_SORTIE

    def voie_est_libre(self):
        if self.usagers:
            return False
        else:
            return True