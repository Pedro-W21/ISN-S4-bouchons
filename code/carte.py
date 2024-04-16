from arete import Arete
from noeud import Noeud, Intersection_T, Intersection_X, EntreeSortie, Virage
from vecteur_2d import Vecteur2D
from random import randint, choice
import numpy as np

class Carte:
    def __init__(self, largeur:int, hauteur:int, grille_interface=None):
        if type(grille_interface) == type(None):
            self.grille = np.zeros((largeur, hauteur))
        else:
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
                    aretes.append(Arete(Vecteur2D(xc * sx, yc * sy), Vecteur2D(fxc * sx, fyc * sy), abs(fxc - xc)  * sx + abs(fyc - yc) * sy ))
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

    def directions_posables_a(self, xc:int, yc:int) -> list[tuple[int,int]]:
        posables = []
        directions = [(-1, 0), (1, 0), (0, 1), (0, -1)]
        for dx, dy in directions:
            if self.position_posable_et_vide(xc + dx, yc + dy):
                posables.append((dx, dy))
        return posables

    def sur_le_bord(self, xc:int, yc:int) -> bool:
        return xc <= 0 or xc >= self.largeur - 1 or yc <= 0 or yc >= self.hauteur - 1
    def dans_un_coin(self, xc:int, yc:int) -> bool:
        return (xc == 0 and yc == 0) or (xc == 0 and yc == self.hauteur - 1) or (xc == self.largeur - 1 and yc == 0) or (xc == self.largeur - 1 and yc == self.hauteur - 1)

    def position_posable_et_vide(self, xc:int, yc:int) -> bool:
        ret = True
        if self.get_at_or_0(xc, yc) == 1 or self.dans_un_coin(xc, yc):
            ret = False
        else:
            positions_a_check_coins = [[(-1, -1), (-1, 0), (0, -1)], [(-1, 1), (-1, 0), (0, 1)], [(1,1), (0,1), (1,0)], [(1, -1), (0, -1), (1,0)]] # triplets de positions de coins
            for triplet in positions_a_check_coins:
                compte = 0
                for (dx, dy) in triplet:
                    compte += self.get_at_or_0(xc + dx, yc + dy)
                if compte == 3:
                    ret = False
            if self.sur_le_bord(xc, yc) and not self.case_bord_valide(xc, yc):
                ret = False
        return ret
    
    def case_bord_valide(self, xc, yc):
        checks = [-1, 1]
        bads = 0
        goods = 0
        ret = True
        if xc == 0 or xc == self.largeur - 1:
            for dy in checks:
                bads += self.get_at_or_0(xc, yc + dy)
            for dx in checks:
                goods += self.get_at_or_0(xc + dx, yc)
        if yc == 0 or yc == self.hauteur - 1:
            for dx in checks:
                bads += self.get_at_or_0(xc + dx, yc)
            for dy in checks:
                goods += self.get_at_or_0(xc, yc + dy)
        if bads > 0 and goods == 0:
            ret = False
        elif goods == 0:
            ret = False
        return ret

    def pos_utilisable_comme_start(self, xc:int, yc:int) -> tuple[int, int]:
        rx, ry = xc, yc
        if xc == 0 and yc == 0:
            rx += 1
        elif xc == self.largeur - 1 and yc == 0:
            rx -= 1
        elif xc == 0 and yc == self.hauteur - 1:
            rx += 1
        elif xc == self.largeur - 1 and yc == self.hauteur - 1:
            rx -= 1
        return (rx, ry)

    def genere_aleatoirement(largeur:int, hauteur:int):
        carte = Carte(largeur=largeur, hauteur=hauteur)
        sx, sy = carte.pos_utilisable_comme_start(randint(0, largeur - 1), randint(0, hauteur - 1))
        fini = False
        cases_posees = {(sx, sy)}
        directions = [(-1, 0), (1, 0), (0, 1), (0, -1)]
        while not fini:
            a_poser = []
            a_enlever = []
            for (xc, yc) in cases_posees:
                if len(cases_posees) > 5 and randint(0, 10) <= 3:
                    a_enlever.append((xc, yc))
                else:
                    for (dx, dy) in directions:
                        i = 1
                        while carte.position_posable_et_vide(xc + i * dx, yc + i * dy) and randint(0, 10) >= 4:
                            a_poser.append((xc + i * dx, yc + i * dy))
                            carte.grille[xc + i * dx, yc + i * dy] = 1
                            i += 1
                    a_enlever.append((xc, yc))
            for (xc, yc) in a_poser:
                cases_posees.add((xc, yc))
            for (xc, yc) in a_enlever:
                cases_posees.remove((xc, yc))
    
            if len(a_poser) == 0:
                fini = True
        return carte
            


