from arrete import Arrete
from vecteur_2d import Vecteur2D

class Noeud:
    size = Vecteur2D(6, 6)

    VIRAGE = "virage"
    INTERSECTION_T = "intersection_t"
    INTERSECTION_X = "rond_point"
    ENTREE_SORTIE = "entree_sortie"

    def __init__(self, position: Vecteur2D, arretes: list[Arrete]):
        #Implémentation données pour affichage
        self.position = Vecteur2D(position.get_x(), position.get_y())

        self.usagers = {}
        # self.usagers: dict[Voiture : list[Vecteur2D, Vecteur2D]] = {}
        #                 {voiture : [orientation, direction_prochaine]}
        self.vitesse_max = 40
        temps_deceleration = abs(0 - 40) / 8
        self.distance_securite = 1/2 * (8 / 3.6) * temps_deceleration**2 + 0.5 * self.size[0]
        self.arretes = arretes

    def update(self):
        #TODO Est-ce que c'est la voiture qui se retire des usagers
        #ou est-ce que c'est le noeud qui retire la voiture de ses usagers
        #(après certaine distance parcourue)

        #if usagers != last_usagers:
            #for i in voiture_attente:
            #   voie_est_libre(voiture)
        pass
    
    def retirer_usager(self, voiture):
        del self.usagers[voiture]
        #Ou alors directement utiliser voiture, mais donc implémenter fonction __eq__ pour vérifier que c'est la même voiture

    def get_poids(self):
        return self.size.x / self.get_vitesse_moyenne()
    
    def get_vitesse_moyenne(self):
        if len(self.usagers) != 0:
            moyenne = sum([usager.vitesse for usager in self.usagers.keys()]) / len(self.usagers)
        else:
            moyenne = self.vitesse_max
        return max(moyenne, 1)
    
    def enregistrer_usager(self, voiture, orientation, intention):
        self.usagers[voiture] = [orientation, intention]

    def voie_est_libre(self, voiture):
        return True
    
    def est_empruntee(self) -> bool:
        return self.usagers > 0

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
        from_right_to_left = [orientation[1],-orientation[0]]
        from_left_to_right = [-orientation[1],orientation[0]]
        from_front_to_me = [-orientation[0],-orientation[1]]
        from_me_to_front = orientation
        # nulle part [0, 0] 
        # selon x [1, 0]
        # selon y [0, 1]
        # selon -x [-1, 0]
        # selon -y [0, -1]
        #vient de ma droite / va à ma gauche
        #vient de ma gauche / va à ma droite
        #vient d'en face / va vers moi
        #vient de ma voix / va en face de moi

        for usager, intentions in self.usagers.items():
            orientation_usager, intention_usager = intentions
            if usager.id != voiture.id:
                if intention == orientation: #Je vais tout droit
                    if orientation_usager == from_right_to_left and intention_usager in [intention, from_front_to_me, from_right_to_left]:
                        #Personne à ma droite ne doit tourner sur ma trajectoire ou la couper   
                        return False
                    if orientation_usager == from_left_to_right and intention_usager in [intention, from_left_to_right]:
                        #Personne à ma gauche ne tourne sur ma trajectoire
                        return False
                    if orientation_usager == from_front_to_me and intention_usager == from_left_to_right:
                        #Personne en face tourne à sa gauche
                        return False 
                elif intention == from_left_to_right:#Je vais sur ma droite
                    if orientation_usager == from_front_to_me and intention_usager == from_left_to_right:
                        #Personne en face tourne à sa gauche
                        return False
                    if orientation_usager == from_left_to_right and intention_usager == from_left_to_right:
                        #Personne à ma gauche tourne à sa gauche
                        return False
                elif intention == from_right_to_left:#Je vais sur ma gauche
                    if orientation_usager == from_right_to_left and intention_usager in [from_front_to_me, intention, from_me_to_front]:
                        #Personne à ma droite tourne
                        return False
                    if orientation_usager == from_left_to_right and intention_usager in [from_left_to_right, from_me_to_front]:
                        #Personne à ma gauche tourne à sa gauche
                        return False
                    if orientation_usager == from_front_to_me and intention_usager in [from_front_to_me, from_right_to_left, from_left_to_right]:
                        #Personne en face va tout droit
                        return False  
        self.enregistrer_usager(voiture, orientation, intention)
        return True

class Intersection_X(Noeud):

    def __init__(self, position, aretes=None) -> None:
        super().__init__(position, aretes)
        self.type=self.INTERSECTION_X
    
    def voie_est_libre(self, voiture):
        orientation, intention = voiture.intention()
        from_right_to_left = [orientation[1],-orientation[0]]
        from_left_to_right = [-orientation[1],orientation[0]]
        from_front_to_me = [-orientation[0],-orientation[1]]
        from_me_to_front = orientation
        # nulle part [0, 0] 
        # selon x [1, 0]
        # selon y [0, 1]
        # selon -x [-1, 0]
        # selon -y [0, -1]
        #vient de ma droite / va à ma gauche
        #vient de ma gauche / va à ma droite
        #vient d'en face / va vers moi
        #vient de ma voix / va en face de moi

        for usager, intentions in self.usagers.items():
            orientation_usager, intention_usager = intentions
            if usager.id != voiture.id:
                if intention == orientation: #Je vais tout droit
                    if orientation_usager == from_right_to_left and intention_usager in [intention, from_front_to_me, from_right_to_left]:
                        #Personne à ma droite ne doit tourner sur ma trajectoire ou la couper   
                        return False
                    if orientation_usager == from_left_to_right and intention_usager in [intention, from_left_to_right]:
                        #Personne à ma gauche ne tourne sur ma trajectoire
                        return False
                    if orientation_usager == from_front_to_me and intention_usager == from_left_to_right:
                        #Personne en face tourne à sa gauche
                        return False 
                elif intention == from_left_to_right:#Je vais sur ma droite
                    if orientation_usager == from_front_to_me and intention_usager == from_left_to_right:
                        #Personne en face tourne à sa gauche
                        return False
                    if orientation_usager == from_left_to_right and intention_usager == from_left_to_right:
                        #Personne à ma gauche tourne à sa gauche
                        return False
                elif intention == from_right_to_left:#Je vais sur ma gauche
                    if orientation_usager == from_right_to_left and intention_usager in [from_front_to_me, intention, from_me_to_front]:
                        #Personne à ma droite tourne
                        return False
                    if orientation_usager == from_left_to_right and intention_usager in [from_left_to_right, from_me_to_front]:
                        #Personne à ma gauche tourne à sa gauche
                        return False
                    if orientation_usager == from_front_to_me and intention_usager in [from_front_to_me, from_right_to_left, from_left_to_right]:
                        #Personne en face va tout droit
                        return False  
        self.enregistrer_usager(voiture, orientation, intention)
        return True

class EntreeSortie(Noeud):

    def __init__(self, position, aretes):
        super().__init__(position, aretes)
        self.type=self.ENTREE_SORTIE
    
    #TODO Implémenter fonction pour vérifier si la voie est libre
    #Si quelqu'un a spawn c'est False 
    #si le dernier qui a spawn est assez loin c'est True
    def voie_est_libre(self, voiture):
        return True
