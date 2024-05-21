from utils.vecteur_2d import Vecteur2D


class Arete:
    
    size = Vecteur2D(6, 6) # m [longueur, largeur]
    
    def __init__(self, position_depart: Vecteur2D, position_arrivee: Vecteur2D) -> None:
        self.voitures = []
        vecteur = position_arrivee - position_depart
        self.longueur = vecteur.norme_manathan()
        self.position_depart = position_depart
        self.position_arrivee = position_arrivee
        self.vitesse_moyenne = 0.0
        self.vitesse_max = 5 # m/s
    
    def __str__(self):
        return f"Arete : {self.position_depart} -> {self.position_arrivee}"
    
    def __eq__(self, other, inverted = False):
        is_the_same = self.position_depart == other.position_depart and self.position_arrivee == other.position_arrivee
        return is_the_same
    
    def is_equal(self, other, inverted = False):
        """
        Détermine si deux arêtes sont identiques.

        Cette méthode compare les attributs `position_depart` et `position_arrivee` de l'objet
        actuel avec ceux de l'objet passé en argument `other`.

        Args:
            self (Arete): L'arête actuelle.
            other (Arete): L'autre arête à comparer.
            inverted (bool, optional): Si `True`, considère aussi les positions dans l'ordre inverse.
                Par défaut, `False`.

        Returns:
            bool: `True` si les objets sont équivalents, sinon `False`.
        """
        is_the_same = self.position_depart == other.position_depart and self.position_arrivee == other.position_arrivee
        is_inverted = self.position_depart == other.position_arrivee and self.position_arrivee == other.position_depart
        return is_the_same or (is_inverted and inverted)
    
    def a_des_voitures(self):
        """
        Vérifie si l'arête possède des voitures.

        Cette méthode vérifie si l'arête contient au moins une voiture dans sa liste de voitures.

        Returns:
            bool: `True` si l'objet possède au moins une voiture, sinon `False`.
        """
        return len(self.voitures) > 0
    
    def push_voiture(self, voiture):
        """
        Ajoute une voiture à la liste des voitures présentes sur l'arête.

        Args:
            voiture (Voiture): L'objet voiture à ajouter.

        Raises:
            ValueError: Si la voiture est déjà présente sur l'arête.

        Returns:
            None
        """
        if voiture not in self.voitures:
            self.voitures.append(voiture)
        else:
            raise ValueError("Erreur : On tente d'ajouter une voiture déjà présente sur l'arête")

    def get_poids(self):
        """
        Calcule le poids de l'arête en divisant sa longueur par sa vitesse moyenne.

        Returns:
            float: Le poids de l'arête.
        """
        return self.longueur / self.get_vitesse_moyenne()
    
    def get_vitesse_moyenne(self):
        """
        Calcule la vitesse moyenne des voitures présentes sur l'arête.

        Returns:
            float: La vitesse moyenne des voitures sur l'arête, au minimum 1 pour éviter les erreurs de division.
        """
        if len(self.voitures) != 0:
            moyenne = sum([voiture.vitesse for voiture in self.voitures]) / len(self.voitures)
        else:
            moyenne = self.vitesse_max
        return max(moyenne, 1)