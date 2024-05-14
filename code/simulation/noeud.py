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
        """
        Retire un usager du noeud.

        Args:
            voiture: La voiture à retirer du noeud.

        Returns:
            None
        """
        if self.usagers.get(voiture, False):
            self.usagers.pop(voiture)

    def get_poids(self):
        """
        Calcule le poids du noeud.

        Returns:
            float: Le poids du noeud.
        """
        return self.size.x / self.get_vitesse_moyenne()
    
    def get_vitesse_moyenne(self):
        """
        Calcule la vitesse moyenne des usagers du noeud.

        Returns:
            float: La vitesse moyenne des usagers, au minimum 1 pour éviter les erreurs de division.
        """
        if len(self.usagers) != 0:
            moyenne = sum([usager.vitesse for usager in self.usagers.keys()]) / len(self.usagers)
        else:
            moyenne = self.vitesse_max
        return max(moyenne, 1)
    
    def get_usagers(self):
        """
        Renvoie les usagers actuels du noeud.

        Returns:
            dict: Les usagers actuels du noeud.
        """
        return self.usagers
    
    def enregistrer_usager(self, voiture, orientation, intention):
        """
        Enregistre un usager sur le noeud.

        Args:
            voiture: La voiture à enregistrer.
            orientation: L'orientation de la voiture.
            intention: L'intention de déplacement de la voiture.
        """
        self.usagers[voiture] = [orientation, intention]

    def passage_possible(self, voiture):
        """
        Vérifie si le passage est possible pour une voiture donnée selon le code de la route.

        Args:
            voiture: La voiture pour laquelle vérifier le passage.

        Returns:
            bool: True si le passage est possible, False sinon.
        """
        orientation, intention = voiture.direction, voiture.direction_prochain_chemin
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
    
    def est_empruntee(self) -> bool:
        """
        Vérifie si le noeud est emprunté par des usagers.

        Returns:
            bool: True si le noeud est emprunté, False sinon.
        """
        return len(self.usagers) > 0
    
    def est_un_usager(self, voiture) -> bool:
        """
        Vérifie si une voiture est un usager du noeud.

        Args:
            voiture: La voiture à vérifier.

        Returns:
            bool: True si la voiture est un usager, False sinon.
        """
        return voiture in self.usagers

class Virage(Noeud):
    def __init__(self, position, aretes=None):
        super().__init__(position, aretes)
        self.type=self.VIRAGE

    def voie_est_libre(self, voiture):
        """
        La voie est toujours libre pour un virage.

        Args:
            voiture: La voiture à concernée par la demande.

        Returns:
            bool: True
        """
        return True
    
class Intersection_T(Noeud):
    def __init__(self, position, aretes=None):
        super().__init__(position, aretes)
        self.type=self.INTERSECTION_T
    
    def voie_est_libre(self, voiture):
        """
        Vérifie si la voie est libre pour une voiture donnée.

        Args:
            voiture: La voiture à vérifier.

        Returns:
            bool: True si la voie est libre, False sinon.
        """
        return self.passage_possible(voiture)

class Intersection_X(Noeud):

    def __init__(self, position, aretes=None) -> None:
        super().__init__(position, aretes)
        self.type=self.INTERSECTION_X
    
    def voie_est_libre(self, voiture):
        """
        Vérifie si la voie est libre pour une voiture donnée.

        Args:
            voiture: La voiture à vérifier.

        Returns:
            bool: True si la voie est libre, False sinon.
        """
        return self.passage_possible(voiture)

class EntreeSortie(Noeud):

    def __init__(self, position, aretes):
        super().__init__(position, aretes)
        self.type=self.ENTREE_SORTIE

    def voie_est_libre(self):
        """
        Détermine si le noeud est libre pour l'apparition d'une voiture.

        Returns:
            bool: True s'il n'y a plus personne sur le noeud, False sinon.
        """
        if self.usagers:
            return False
        else:
            return True