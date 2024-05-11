import numpy as np

class Vecteur2D:
    def __init__(self, x:float, y:float):
        self.x = x
        self.y = y
    def __str__(self):
        return f"[{self.x},{self.y}]"
    
    def get_x(self):
        return self.x
    
    def get_y(self):
        return self.y
    
    def valeur_projetee(self):
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
        return Vecteur2D(self.x * rhs.x, self.y * rhs.y)
    
    def norme(self):
        return (self.x**2 + self.y**2)**0.5

    def norme_manathan(self):
        return abs(self.x) + abs(self.y)
    
    def unitaire(self):
        return self/self.norme()

    def abs(self):
        return Vecteur2D(abs(self.x), abs(self.y))
    
    def projection(self, vect):
        # projection uniquement sur +-x ou +-y je crois
        if isinstance(vect, (Vecteur2D)):
            vect = vect.unitaire()
            return Vecteur2D(vect.x * self.x, vect.y * self.y)
        else:
            raise TypeError("GROSSE ERREUR DE TYPE ICI AUSSI")


    def __mul__(self, rhs):
        if type(rhs) == Vecteur2D:
            return self.scalaire(rhs)
        elif isinstance(rhs, (float, int, np.float64)):
            return Vecteur2D(self.x * rhs, self.y * rhs)
        else:
            raise TypeError("GROSSE ERREUR DE TYPE ICI AUSSI")
        
    def __truediv__(self, rhs):
        if isinstance(rhs, (float, int, np.float64)):
            return Vecteur2D(self.x / rhs, self.y / rhs)
        else:
            raise TypeError("GROSSE ERREUR DE TYPE ICI AUSSI")

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