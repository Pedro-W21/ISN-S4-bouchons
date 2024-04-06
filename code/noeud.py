from car import Voiture
from vecteur_2d import Vecteur2D

class Noeud:
    def __init__(self, position: Vecteur2D, arretes, rayon=40):
        #Implémentation données pour affichage
        self.position = Vecteur2D(position[0], position[1])

        self.aretes = [] #Les arêtes partant de ce point
        self.usagers: list[list[Voiture, Vecteur2D, Vecteur2D]] = []
        #                    [[voiture, orientation, intention]]
        self.rayon = rayon
        self.vitesse_max = 40
        self.distance_securite = 8*rayon
        self.arrete = arretes

    def definir_aretes(self, aretes):
        self.aretes = aretes

    def retirer_usager(self, voiture):
        self.usagers = [element for element in self.usagers if element[0].id != voiture.id]
        #Ou alors directement utiliser voiture, mais donc implémenter fonction __eq__ pour vérifier que c'est la même voiture

    def get_poids(self):
        return self.rayon / self.get_vitesse_moyenne()
    
    def est_proche(self, voiture):
        vecteur: Vecteur2D = self.position - voiture.position
        return vecteur.norme_manathan() < self.distance_securite

    def get_vitesse_moyenne(self):
        if len(self.usagers) != 0:
            moyenne = sum([usager[0].vitesse for usager in self.usagers]) / len(self.usagers)
        else:
            moyenne = self.vitesse_max
        return max(moyenne, 1)


class Virage(Noeud):
    def __init__(self, position, aretes=None):
        super().__init__(position, aretes)
        self.type="Virage"
    
    def voie_est_libre(self, voiture):
        return True
    
class Intersection_T(Noeud):
    def __init__(self, position, aretes=None):
        super().__init__(position, aretes)
        self.type="Intersection"
    
    def voie_est_libre(self, voiture):
        orientation, intention = voiture.intention()
        from_right_to_left = [orientation[1],-orientation[0]]
        from_left_to_right = [-orientation[1],orientation[0]]
        from_front_to_me = [-orientation[0],-orientation[1]]
        # nulle part [0, 0] 
        # selon x [1, 0]
        # selon y [0, 1]
        # selon -x [-1, 0]
        # selon -y [0, -1]
        #vient de ma droite / va à ma gauche
        #vient de ma gauche / va à ma droite
        #vient d'en face / va vers moi
        #vient de ma voix / va en face de moi

        for usager, orientation_usager, intention_usager in self.usagers:
            if intention == orientation: #Je vais tout droit
                if orientation_usager == from_right_to_left and intention_usager in [orientation, from_front_to_me]:
                    #Personne à ma droite ne doit tourner sur ma trajectoire ou la couper
                    return False
                if orientation_usager == from_left_to_right and intention_usager == orientation:
                    #Personne à ma gauche ne tourne sur ma trajectoire
                    return False
                if orientation_usager == from_front_to_me and intention_usager == from_left_to_right:
                    #Personne en face tourne à sa gauche
                    return False
            elif intention == from_left_to_right:#Je vais sur ma droite
                if orientation_usager == from_front_to_me and intention_usager == from_left_to_right:
                    #Personne en face tourne à sa gauche
                    return False
                if orientation_usager == from_left_to_right and intention_usager == orientation:
                    #Personne à ma gauche tourne à sa gauche
                    return False
            elif intention == from_right_to_left:#Je vais sur ma gauche
                if orientation_usager == from_right_to_left and intention_usager in [orientation,from_front_to_me]:
                    #Personne à ma droite tourne
                    return False
                if orientation_usager == from_left_to_right and intention_usager == orientation:
                    #Personne à ma gauche tourne à sa gauche
                    return False
                if orientation_usager == from_front_to_me and intention_usager == from_front_to_me:
                    #Personne en face va tout droit
                    return False
        self.usagers.append([voiture, orientation, intention])
        return True

    def passe(self, voiture):
        pass
    
    #if un usager fait la même chose devant toi


class RondPoint(Noeud):

    def __init__(self, position, aretes=None) -> None:
        super().__init__(position, aretes)
        self.type="Rond Point"