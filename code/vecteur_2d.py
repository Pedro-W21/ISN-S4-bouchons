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

    def __mul__(self, rhs):
        if type(rhs) == Vecteur2D:
            return self.scalaire(rhs)
        elif type(rhs) == float or type(rhs) == int:
            return Vecteur2D(self.x * rhs, self.y * rhs)
        else:
            print("GROSSE ERREUR DE TYPE ICI AUSSI")
        
    def __div__(self, rhs):
        if type(rhs) == float or type(rhs) == int:
            return Vecteur2D(self.x / rhs, self.y / rhs)
        else:
            print("GROSSE ERREUR DE TYPE ICI")

    def __str__(self):
        return f"x : {self.x}, y : {self.y}"