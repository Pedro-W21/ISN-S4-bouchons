class Vecteur2D:
    def __init__(self, x:float, y:float):
        self.x = x
        self.y = y
    
    def get_x(self):
        return self.x
    
    def get_y(self):
        return self.y
    
    def __add__(self, rhs):
        return Vecteur2D(self.x + rhs.x, self.y + rhs.y)
    
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

    def projection(self, vect):
        # projection uniquement sur +-x ou +-y je crois
        if type(vect) == Vecteur2D:
            vect = vect.unitaire()
            return Vecteur2D(vect.x * self.x, vect.y * self.y)
        else:
            raise TypeError("GROSSE ERREUR DE TYPE ICI AUSSI")


    def __mul__(self, rhs):
        if type(rhs) == Vecteur2D:
            return self.scalaire(rhs)
        elif type(rhs) == float or type(rhs) == int:
            return Vecteur2D(self.x * rhs, self.y * rhs)
        else:
            raise TypeError("GROSSE ERREUR DE TYPE ICI AUSSI")
        
    def __div__(self, rhs):
        if type(rhs) == float or type(rhs) == int:
            return Vecteur2D(self.x / rhs, self.y / rhs)
        else:
            raise TypeError("GROSSE ERREUR DE TYPE ICI AUSSI")


    def __str__(self):
        return f"x : {self.x}, y : {self.y}"
    
    def __eq__(self, rhs):
        return self.x == rhs.x and self.y == rhs.y
    
    def __abs__(self):
        return Vecteur2D(abs(self.x), abs(self.y))