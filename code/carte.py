from arrete import Arrete
from noeud import Noeud, Intersection_T, Intersection_X, EntreeSortie, Virage
from vecteur_2d import Vecteur2D

class Carte:
    def __init__(self, largeur:int, hauteur:int, grille_interface=None):
        self.grille = grille_interface
        self.largeur = largeur
        self.hauteur = hauteur

    def into_aretes_noeuds(self) -> list[Noeud]:
        noeuds_dict = {}
        for xc in range(self.largeur):
            for yc in range(self.hauteur):
                if self.est_noeud(xc, yc):
                    noeuds_dict[(xc, yc)] = []
        directions = [(-1,0), (1,0), (0,1), (0,-1)]
        sx = Noeud.size.get_x()
        sy = Noeud.size.get_y()
        for ((xc, yc), aretes) in noeuds_dict.items():
            for (dx, dy) in directions:
                fxc, fyc = xc, yc
                while self.get_at_or_0(fxc + dx, fyc + dy) == 1:
                    fxc += dx
                    fyc += dy
                if not (fxc == xc and fyc == yc):
                    aretes.append(Arrete(Vecteur2D(xc * sx, yc * sy), Vecteur2D(fxc * sx, fyc * sy), abs(fxc - xc)  * sx + abs(fyc - yc) * sy ))
        return [self.cree_noeud(xc, yc, aretes) for ((xc, yc), aretes) in noeuds_dict.items()]

    def cree_noeud(self, xc, yc, aretes) -> Noeud:
        compteur_h = 0
        compteur_v = 0
        ret = None
        decalages = [-1, 1]
        sx = Noeud.size.get_x()
        sy = Noeud.size.get_y()
        pos = Vecteur2D(xc * sx, yc * sy)
        
        for dx in decalages:
            compteur_h += self.get_at_or_0(xc + dx, yc)
        for dy in decalages:
            compteur_v += self.get_at_or_0(xc, yc + dy)
        if compteur_v == 1 and compteur_h == 1:
            ret = Virage(pos, aretes)
        elif (compteur_h == 1 and compteur_v == 0) or (compteur_h == 0 and compteur_v == 1):
            ret = EntreeSortie(pos, aretes)
        elif (compteur_h == 1 and compteur_v == 2) or (compteur_h == 2 and compteur_v == 1):
            ret = Intersection_T(pos, aretes)
        else:
            ret = Intersection_X(pos, aretes)
        return ret
    
    def est_noeud(self, xc, yc) -> bool:
        compteur_h = 0
        compteur_v = 0
        ret = False
        if self.get_at_or_0(xc, yc) == 1:
            decalages = [-1, 1]
            for dx in decalages:
                compteur_h += self.get_at_or_0(xc + dx, yc)
            for dy in decalages:
                compteur_v += self.get_at_or_0(xc, yc + dy)
            if (compteur_v >= 1 and compteur_h >= 1) or (xc == 0 or xc == self.largeur - 1 or yc == 0 or yc == self.hauteur - 1):
                ret = True
        return ret

    def get_at_or_0(self, xc:int, yc:int) -> int:
        ret = 0
        if 0 <= xc < self.largeur and 0 <= yc < self.hauteur:
            ret = self.grille[xc,yc]
        return ret
    
