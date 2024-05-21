import numpy as np

class Vecteur2D:
    def __init__(self, x:float, y:float):
        self.x = x
        self.y = y
    def __str__(self):
        return f"[{self.x},{self.y}]"
    
    def get_x(self):
        """
        Retourne la valeur de l'attribut 'x' de l'instance.

        Returns:
            float: La valeur de l'attribut 'x' de l'instance.
        """
        return self.x
    
    def get_y(self):
        """
        Retourne la valeur de l'attribut 'y' de l'instance.

        Returns:
            float: La valeur de l'attribut 'y' de l'instance.
        """
        return self.y
    
    def valeur_projetee(self):
        """
        Calcule et retourne la valeur projetée en additionnant les attributs 'x' et 'y' de l'instance.

        Returns:
            float: La somme des attributs 'x' et 'y' de l'instance.
        """
        return self.x+self.y
    
    def __add__(self, rhs):
        if type(rhs) == Vecteur2D:
            return Vecteur2D(self.x + rhs.x, self.y + rhs.y)
        elif isinstance(rhs, (float, int, np.float64)):
            return Vecteur2D(self.x + rhs, self.y + rhs)
        else:
            raise TypeError("GROSSE ERREUR DE TYPE ICI AUSSI")
    
    def __sub__(self, rhs):
        return Vecteur2D(self.x - rhs.x, self.y - rhs.y)
    
    def scalaire(self, rhs):
        """
        Calcule le produit scalaire de l'instance courante avec un autre vecteur.

        Args:
            rhs (Vecteur2D): Le vecteur avec lequel effectuer le produit scalaire.

        Returns:
            Vecteur2D: Un nouveau vecteur résultant du produit scalaire des deux vecteurs.
        """
        return Vecteur2D(self.x * rhs.x, self.y * rhs.y)
    
    def norme(self):
        """
        Calcule et retourne la norme du vecteur.

        Returns:
            float: La norme du vecteur, calculée comme la racine carrée de la somme des carrés
                des attributs 'x' et 'y' de l'instance.
        """
        return (self.x**2 + self.y**2)**0.5

    def norme_manathan(self):
        """
        Calcule et retourne la norme de Manhattan (ou distance de Manhattan) du vecteur.

        Returns:
            float: La norme de Manhattan du vecteur, calculée comme la somme des valeurs absolues
                des attributs 'x' et 'y' de l'instance.
        """
        return abs(self.x) + abs(self.y)
    
    def unitaire(self):
        """
        Calcule et retourne le vecteur unitaire (ou normalisé) du vecteur.

        Returns:
            Vecteur2D: Un nouveau vecteur qui est la version normalisée de l'instance actuelle.
                    La normalisation est effectuée en divisant chaque composante par la norme
                    du vecteur original.
        """
        return self/self.norme()

    def abs(self):
        """
        Calcule et retourne un nouveau vecteur dont les composantes sont les valeurs absolues
        des composantes du vecteur original.

        Returns:
            Vecteur2D: Un nouveau vecteur avec les composantes absolues des attributs 'x' et 'y'
                    de l'instance.
        """
        return Vecteur2D(abs(self.x), abs(self.y))
    
    def projection(self, vect):
        """
        Calcule et retourne la projection de l'instance courante sur un autre vecteur.

        Args:
            vect (Vecteur2D): Le vecteur sur lequel projeter l'instance courante.

        Returns:
            Vecteur2D: Un nouveau vecteur résultant de la projection de l'instance courante
                    sur le vecteur spécifié. Si le vecteur spécifié n'est pas une instance
                    de Vecteur2D, la méthode retourne None.
        """
        if isinstance(vect, (Vecteur2D)):
            vect = vect.unitaire()
            return Vecteur2D(vect.x * self.x, vect.y * self.y)

    def __mul__(self, rhs):
        if type(rhs) == Vecteur2D:
            return self.scalaire(rhs)
        elif isinstance(rhs, (float, int, np.float64)):
            return Vecteur2D(self.x * rhs, self.y * rhs)
        
    def __truediv__(self, rhs):
        if isinstance(rhs, (float, int, np.float64)):
            return Vecteur2D(self.x / rhs, self.y / rhs)

    def __eq__(self, rhs):
        if type(rhs) != Vecteur2D:
            return self.x == rhs[0] and self.y == rhs[1]
        return self.x == rhs.x and self.y == rhs.y
    
    def __abs__(self):
        return Vecteur2D(abs(self.x), abs(self.y))
    
    def __gt__(self, number):
        return self.x > number or self.y > number
    
    def __ge__(self, number):
        return self.x >= number or self.y >= number
    
    def __lt__(self, number):
        return self.x < number or self.y < number
    
    def __le__(self, number):
        return self.x <= number or self.y <= number