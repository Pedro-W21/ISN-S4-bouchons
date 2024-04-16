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
        return self.get_at_or_0(xc, yc) == 0 and self.position_posable(xc, yc)
    def position_posable(self, xc:int, yc:int) -> bool:
        ret = True
        if self.dans_un_coin(xc, yc):
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
    def set_dirs_depuis(self, xc, yc):
        dirs = self.directions_posables_a(xc, yc)
        ens = set()
        while len(dirs) > 0:
            choix = choice(dirs)
            dirs.remove(choix)
            ens.add(choix)
        return ens

    def genere_aleatoirement_2(largeur:int, hauteur:int):
        carte = Carte(largeur=largeur, hauteur=hauteur)
        sx, sy = carte.pos_utilisable_comme_start(randint(0, largeur - 1), randint(0, hauteur - 1))
        dirs_depuis = {(sx, sy):carte.set_dirs_depuis(sx, sy)}
        cases_avec_dirs = {(sx, sy)}
        while len(cases_avec_dirs) > 0:
            a_rajouter = []
            a_enlever = []
            avec_dirs = choice(list(cases_avec_dirs))
            xc, yc = avec_dirs
            for dx, dy in dirs_depuis[avec_dirs]:
                i = 1
                while carte.position_posable_et_vide(xc + i * dx, yc + i * dy):
                    a_rajouter.append((xc + i * dx, yc + i * dy))
                    carte.grille[xc + i * dx, yc + i * dy] = 1
                    i += 1
            for (xc, yc) in cases_avec_dirs:
                ens = carte.set_dirs_depuis(xc, yc)
                if len(ens) == 0:
                    a_enlever.append((xc, yc))
                else:
                    dirs_depuis[(xc, yc)] = ens
            for (xc, yc) in a_rajouter:
                ens = carte.set_dirs_depuis(xc, yc)
                if len(ens) > 1:
                    cases_avec_dirs.add((xc, yc))
                    dirs_depuis[(xc, yc)] = ens
            for enlev in a_enlever:
                cases_avec_dirs.remove(enlev)
            nb = randint(3, 10)
            while len(cases_avec_dirs) > nb and randint(0, 10) > 1:
                cases_avec_dirs.remove(choice(list(cases_avec_dirs)))
        carte.filtre_correction_carte()
        return carte
    def applique_changements(self, changements):
        for xc, yc in changements:
            if self.grille[xc, yc] != 0:
                self.grille[xc, yc] = 0

    def trouve_composantes_connexes(self):
        explores = {}
        composantes = []
        decalages_possibles = [(-1,0), (1,0), (0, 1), (0, -1)]
        for yc in range(0, self.hauteur):
            for xc in range(0, self.largeur):
                if self.get_at_or_0(xc, yc) == 1 and explores.get((xc,yc), None) == None:
                    queue = [(xc, yc)]
                    id_composante = len(composantes)
                    composantes.append([(xc, yc)])
                    explores[(xc, yc)] = id_composante
                    set_local = {(xc, yc)}
                    while len(queue) > 0:
                        axc, ayc = queue.pop()
                        for (dx, dy) in decalages_possibles:
                            nxc, nyc = axc + dx, ayc + dy
                            if self.get_at_or_0(nxc, nyc) == 1 and (nxc, nyc) not in set_local:
                                explores[(nxc, nyc)] = id_composante
                                queue.append((nxc, nyc))
                                set_local.add((nxc, nyc))
                                composantes[id_composante].append((nxc, nyc))
        return composantes

    def case_dedans_valide(self, xc, yc):
        checks = [(-1,0), (1,0), (0, 1), (0, -1)]
        ret = True
        if self.get_at_or_0(xc, yc) == 1:
            total = 0
            for (dx, dy) in checks:
                total += self.get_at_or_0(xc + dx, yc + dy)
            if total <= 1:
                ret = False
        return ret

    def filtre_correction_carte(self):
        bon = False
        coins = [(0, 0), (0, self.hauteur - 1), (self.largeur - 1, 0), (self.largeur - 1, self.hauteur - 1)]
        while bon == False:
            changements = []
            for yc in range(0, self.hauteur):
                for xc in range(0, self.largeur):
                    if self.grille[xc, yc] == 1:
                        bord = (xc == 0 or xc == self.largeur - 1 or yc == 0 or yc == self.hauteur - 1)
                        coin = (xc, yc) in coins
                        if bord and ((coin and self.get_at_or_0(xc, yc) == 1) or not self.case_bord_valide(xc, yc)):
                            changements.append((xc, yc))
                        elif not bord and not self.case_dedans_valide(xc, yc):
                            changements.append((xc, yc))
            self.applique_changements(changements)
            if len(changements) == 0:
                bon = True
        
        changements = []
        composantes = self.trouve_composantes_connexes()
        if len(composantes) > 1:
            id_plus_petite = 0
            for i in range(len(composantes)):
                if len(composantes[i]) < len(composantes[id_plus_petite]):
                    id_plus_petite = i
            for xc, yc in composantes[id_plus_petite]:
                changements.append((xc, yc))
        self.applique_changements(changements)

    def entree_sortie_possible(self):
        total = 0
        for xc in range(self.largeur):
            for yc in range(self.hauteur):
                if self.sur_le_bord(xc, yc) and self.grille[xc, yc] == 1:
                    total += 1
        return total >= 2

        


