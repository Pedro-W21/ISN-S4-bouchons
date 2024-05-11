from simulation.arete import Arete
from simulation.noeud import Noeud, Intersection_T, Intersection_X, EntreeSortie, Virage
from vecteur_2d import Vecteur2D
from random import randint, choice
import numpy as np
import json

class Carte:
    def __init__(self, largeur:int, hauteur:int, grille_interface=None):
        if type(grille_interface) == type(None):
            self.grille = np.zeros((largeur, hauteur))
        else:
            self.grille = grille_interface
        self.largeur = largeur
        self.hauteur = hauteur

    def into_aretes_noeuds(self) -> list[Noeud]:
        """
        renvoie les noeuds avec arêtes associés à la carte sur laquelle la méthode est appelée

        input : rien
        return : liste de noeuds valide
        """
        noeuds_dict = {}
        for xc in range(self.largeur):
            for yc in range(self.hauteur):
                if self.est_noeud(xc, yc):
                    noeuds_dict[(xc, yc)] = []
        directions = [(-1,0), (1,0), (0,1), (0,-1)]
        sx = Noeud.size.get_x()
        sy = Noeud.size.get_y()
        #print("starting test")
        for ((xc, yc), aretes) in noeuds_dict.items():
            for (dx, dy) in directions:
                fxc, fyc = xc + dx, yc + dy
                while self.get_at_or_0(fxc, fyc) == 1 and not self.est_noeud(fxc, fyc):
                    fxc += dx
                    fyc += dy
                if self.get_at_or_0(fxc, fyc) == 1:
                    #print(xc, yc, fxc, fyc)
                    aretes.append(Arete(Vecteur2D(xc * sx, yc * sy), Vecteur2D(fxc * sx, fyc * sy)))
        return [self.cree_noeud(xc, yc, aretes) for ((xc, yc), aretes) in noeuds_dict.items()]

    def cree_noeud(self, xc:int, yc:int, aretes:list[Arete]) -> Noeud:
        """
        renvoie le noeud associé au point (xc, yc) rempli des arêtes données

        input : 
            - xc : entier de coordonnée horizontale valide dans la carte
            - yc : entier de coordonnée verticale valide dans la carte
            - aretes : liste d'Arete partant de (xc, yc)
        return : type de Noeud valide pour la configuration autour de (xc, yc)
        """
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
    
    def est_noeud(self, xc:int, yc:int) -> bool:
        """
        Renvoie True si la position de la carte en (xc, yc) est un noeud, False sinon

        input : 
            - xc : entier de coordonnée horizontale valide dans la carte
            - yc : entier de coordonnée verticale valide dans la carte
        return : booléen indiquant si la position (xc, yc) est un noeud
        """
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

    def est_dedans(self, xc:int, yc:int) -> bool:
        """
        renvoie un booléen indiquant si (xc, yc) est dans la grille

        input :
            - xc : entier de coordonnée horizontale
            - yc : entier de coordonnée verticale
        return : booléen, True si dedans, False sinon
        """
        return 0 <= xc < self.largeur and 0 <= yc < self.hauteur

    def get_at_or_0(self, xc:int, yc:int) -> int:
        """
        renvoie la valeur de la grille de route en (xc, yc) si elle est dans la carte ou 0 sinon

        input : 
            - xc : entier de coordonnée horizontale
            - yc : entier de coordonnée verticale
        return : entier, 0 ou 1 (pas un booléen car la plupart des fonctions qui appellent celle-ci le font pour compter des voisins)
        """
        ret = 0
        if self.est_dedans(xc, yc):
            ret = self.grille[xc,yc]
        return ret

    def directions_posables_a(self, xc:int, yc:int) -> list[tuple[int,int]]:
        """
        renvoie les directions dans lesquelles on peut poser une route à partir de la coordonnée (xc, yc) dans la carte

        input :
            - xc : entier de coordonnée horizontale valide dans la carte
            - yc : entier de coordonnée verticale valide dans la carte
        return : liste de directions (dx, dy), tuples d'entiers signés
        """
        posables = []
        directions = [(-1, 0), (1, 0), (0, 1), (0, -1)]
        for dx, dy in directions:
            if self.position_posable_et_vide(xc + dx, yc + dy):
                posables.append((dx, dy))
        return posables

    def sur_le_bord(self, xc:int, yc:int) -> bool:
        """
        renvoie True si (xc, yc) est sur le bord ou en dehors de la carte, False sinon

        input :
            - xc : entier de coordonnée horizontale
            - yc : entier de coordonnée verticale
        return : booléen indiquant si (xc, yc) est sur le bord ou en dehors de la carte
        """
        return xc <= 0 or xc >= self.largeur - 1 or yc <= 0 or yc >= self.hauteur - 1
    def dans_un_coin(self, xc:int, yc:int) -> bool:
        """
        renvoie True si (xc, yc) est dans un coin de la carte, False sinon

        input :
            - xc : entier de coordonnée horizontale valide dans la carte
            - yc : entier de coordonnée verticale valide dans la carte
        return : booléen indiquant si (xc, yc) est dans un coin de la carte
        """
        return (xc == 0 and yc == 0) or (xc == 0 and yc == self.hauteur - 1) or (xc == self.largeur - 1 and yc == 0) or (xc == self.largeur - 1 and yc == self.hauteur - 1)

    def position_posable_et_vide(self, xc:int, yc:int) -> bool:
        """
        renvoie True si (xc, yc) est une position vide où l'on peut poser une route, False sinon

        input :
            - xc : entier de coordonnée horizontale valide dans la carte
            - yc : entier de coordonnée verticale valide dans la carte
        return : booléen
        """
        return self.get_at_or_0(xc, yc) == 0 and self.position_posable(xc, yc)
    
    def position_posable(self, xc:int, yc:int) -> bool:
        """
        renvoie True si (xc, yc) est une position où l'on peut poser une route, False sinon

        input :
            - xc : entier de coordonnée horizontale valide dans la carte
            - yc : entier de coordonnée verticale valide dans la carte
        return : booléen
        """
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
    def case_bord_valide(self, xc:int, yc:int) -> bool:
        """
        Envoie True si la case (xc, yc) serait une case de bord valide si elle était pleine, False sinon

        définition case de bord valide : pas de voisin sur le même bord, et 1 lien vers l'intérieur de la carte

        input : 
            - xc : entier de coordonnée horizontale valide dans la carte
            - yc : entier de coordonnée verticale valide dans la carte
        return : booléen
        """
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
        """
        renvoie une position corrigée de (xc, yc) de façon à ce qu'elle ne soit pas dans un coin

        input:
            - xc : entier de coordonnée horizontale valide dans la carte
            - yc : entier de coordonnée verticale valide dans la carte
        return : tuple d'entier (rx, ry) contenus dans la carte, possiblement sur un bord mais pas dans un coin
        """
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
    
    def set_dirs_depuis(self, xc:int, yc:int) -> set[(int, int)]:
        """
        package les directions posables depuis (xc, yc) dans un set généré aléatoirement pour changer l'ordre des explorations de direction

        input :
            - xc : entier de coordonnée horizontale valide dans la carte
            - yc : entier de coordonnée verticale valide dans la carte
        return : set de tuples (dx, dy) indiquant des directions explorables dans la carte au moment où cette fonction est exécutée 
        """
        dirs = self.directions_posables_a(xc, yc)
        ens = set()
        while len(dirs) > 0:
            choix = choice(dirs)
            dirs.remove(choix)
            ens.add(choix)
        return ens

    def noeud_avant_distance(self, xc:int, yc:int, distance:int) -> bool:
        """
        renvoie un booléen indiquant si il y a un noeud autour du point (xc, yc) AVANT (<) la distance donnée

        input :
            - xc : entier de coordonnée horizontale valide dans la carte
            - yc : entier de coordonnée verticale valide dans la carte
            - distance : entier de nombre de cases 
        return : booléen, True si il y a un noeud, false sinon
        """
        cotes_par_dir = {(-1, 0) : [(0, 1), (0, -1)], (1, 0) : [(0, 1), (0, -1)], (0, 1) : [(-1, 0), (1, 0)], (0, -1) : [(-1, 0), (1, 0)]}
        trouve = False
        dirs = list(cotes_par_dir.keys())
        j = 0
        px, py = xc, yc
        branches_trouvees = {}
        while not trouve and j < len(dirs):
            dx, dy = dirs[j]
            i = 1
            px, py = xc + dx, yc + dy
            route_debut = self.get_at_or_0(px, py) == 1
            if route_debut:
                while self.get_at_or_0(px, py) == 1 and not self.est_noeud(px, py):
                    i += 1
                    px, py = xc + i * dx, yc + i * dy
                
            else:
                while self.get_at_or_0(px, py) == 0 and self.est_dedans(px, py):
                    i += 1
                    px, py = xc + i * dx, yc + i * dy
                if self.est_dedans(px, py):
                    branches_trouvees[(px, py)] = (dx, dy)
            trouve = self.get_at_or_0(px, py) == 1 and i < distance
            j += 1
        if not trouve:
            branches = list(branches_trouvees.keys())
            i = 0
            while not trouve and i < len(branches):
                (xc, yc) = branches[i]
                for (dx, dy) in cotes_par_dir[branches_trouvees[(xc, yc)]]:
                    px, py = xc + dx, yc + dy
                    j = 1
                    while j < distance and self.get_at_or_0(px, py) == 1 and not self.est_noeud(px, py):
                        j += 1
                        px, py = xc + j * dx, yc + j * dy
                    if not trouve:
                        trouve = self.est_noeud(px, py)
                i += 1
        # start_x = xc - distance
        # stop_x = xc + distance
        # y = yc - distance
        # stop_y = yc + distance
        # while not trouve and y <= stop_y:
        #     x = start_x
        #     while not trouve and x <= stop_x:
        #         if self.est_noeud(x, y):
        #             trouve = True
        #         x += 1
        #     y += 1
        return trouve

    def genere_aleatoirement(largeur:int, hauteur:int, nombre_de_noeuds:int = 100, distance_minimale_entre_noeuds:int = 1):
        """
        génère aléatoirement une carte de largeur et hauteur données en respectant toutes les règles de construction

        input :
            - largeur : entier >= 3
            - hauteur : entier >= 3
            - nombre_de_noeuds : entier >= 1
        return : Carte respectant toutes les règles de construction imposées par la simulation
        """
        carte = Carte(largeur=largeur, hauteur=hauteur)
        sx, sy = carte.pos_utilisable_comme_start(randint(0, largeur - 1), randint(0, hauteur - 1))
        carte.grille[sx, sy] = 1
        dirs_depuis = {(sx, sy):carte.set_dirs_depuis(sx, sy)}
        cases_avec_dirs = {(sx, sy)}
        noeuds_poses = 0
        noeuds = [(sx, sy)]
        while len(cases_avec_dirs) > 0 and noeuds_poses < nombre_de_noeuds:
            a_rajouter = []
            a_enlever = []
            avec_dirs = choice(list(cases_avec_dirs))
            xc, yc = avec_dirs
            for dx, dy in dirs_depuis[avec_dirs]:
                i = 1
                while carte.position_posable_et_vide(xc + i * dx, yc + i * dy):
                    if i > distance_minimale_entre_noeuds:
                        a_rajouter.append((xc + i * dx, yc + i * dy))
                    carte.grille[xc + i * dx, yc + i * dy] = 1
                    i += 1
            for (xc, yc) in cases_avec_dirs:
                ens = carte.set_dirs_depuis(xc, yc)
                if len(ens) == 0 or carte.noeud_avant_distance(xc, yc, distance_minimale_entre_noeuds):
                    a_enlever.append((xc, yc))
                else:
                    dirs_depuis[(xc, yc)] = ens
            for (xc, yc) in a_rajouter:
                ens = carte.set_dirs_depuis(xc, yc)
                if len(ens) > 1 and not carte.noeud_avant_distance(xc, yc, distance_minimale_entre_noeuds):
                    cases_avec_dirs.add((xc, yc))
                    dirs_depuis[(xc, yc)] = ens
            for enlev in a_enlever:
                cases_avec_dirs.remove(enlev)
            nb = randint(8, 10)
            while len(cases_avec_dirs) > nb and randint(1, 10) > 1:
                cases_avec_dirs.remove(choice(list(cases_avec_dirs)))
            noeuds_poses += 1
        #carte.filtre_correction_carte()
        return carte
    def applique_changements(self, changements:list[tuple[int, int]]):
        """
        mets les coordonnées dans la liste de changements à 0

        input : liste de coordonnées (xc, yc) valides dans la carte
        return : rien
        
        effets secondaires : modifie self.grille à toutes les coordonnées données
        """
        for xc, yc in changements:
            self.grille[xc, yc] = 0

    def trouve_composantes_connexes(self):
        """
        trouve et renvoie une liste des composantes connexes du graphe de routes total

        input : rien
        return : liste de liste de points (xc, yc) entiers et valides dans la carte. Chaque sous liste est une composante connexe
        """
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

    def case_dedans_valide(self, xc:int, yc:int) -> bool:
        """
        renvoie True si (xc, yc) est une case intérieur utilisable pour une route (au moins 2 voisins directs remplis)

        input :
            - xc : entier de coordonnée horizontale valide dans la carte
            - yc : entier de coordonnée verticale valide dans la carte
        return : booléen, True si la case peut faire parti d'une route, False sinon
        """
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
        """
        applique sur la carte actuelle un filtre de correction de carte enlevant les cul-de-sac, et toutes les composantes connexes sauf la plus grande

        input : rien
        return : rien

        effets secondaires : change la carte actuelle, et la rend valide pour la simulation si elle a déjà 1 entrée/sortie

        note : le calcul de composantes connexes ne sert à rien pour les cartes générées procéduralement, car la procédure renvoie une carte connexe de façon garantie
        """
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
        
        
        composantes = self.trouve_composantes_connexes()
        while len(composantes) > 1:
            changements = []
            id_plus_petite = 0
            for i in range(len(composantes)):
                if len(composantes[i]) < len(composantes[id_plus_petite]) or not self.composante_connexe_valide(composantes[i]):
                    id_plus_petite = i
            for xc, yc in composantes[id_plus_petite]:
                changements.append((xc, yc))
            self.applique_changements(changements)
            composantes = self.trouve_composantes_connexes()
        if len(composantes) == 1 and not self.composante_connexe_valide(composantes[0]):
            changements = []
            for xc, yc in composantes[0]:
                changements.append((xc, yc))
            self.applique_changements(changements)
            
    def composante_connexe_valide(self, composante:list[(int, int)]) -> bool:
        """
        renvoie un booléen indiquant si la composante connexe (supposée faite de routes) est valide

        input : composante, liste de tuples de coordonnée
        return : booléen, True si valide, False sinon
        """
        return any(self.case_bord_valide(xc, yc) for (xc, yc) in composante)

    def entree_sortie_possible(self) -> bool:
        """
        renvoie True si la carte a au moins 2 entrées/sortie séparées, False sinon

        input : rien
        return : booléen
        """
        total = 0
        for xc in range(self.largeur):
            for yc in range(self.hauteur):
                if self.sur_le_bord(xc, yc) and self.grille[xc, yc] == 1:
                    total += 1
        return total >= 2

    def charger_carte(nom_fichier:str):
        """
        charge la carte contenue dans le fichier du nom nom_fichier dans le dossier routes

        input : nom_fichier, str du nom complet d'un fichier dans le dossier routes
        return : Carte correspondante si le ficheir est valide et existe, None sinon
        """
        carte = None
        try:
            with open("../routes/" + nom_fichier, "r") as file:
                dico:dict[str:list] = json.load(file)
                grille = dico.get("grille", None)
                if grille != None:
                    largeur = grille["largeur"]
                    hauteur = grille["hauteur"]
                    data = np.array(grille["donnees"])
                    carte = Carte(largeur, hauteur, data)
                else:
                    aretes_decodees:list[Arete] = []
                    # erreur incoming selon le format de fichier
                    aretes = dico["ARETE"]

                    max_x = 0
                    max_y = 0
                    for arete in aretes:
                        
                        point1, point2 = arete
                        point1 = Vecteur2D(point1[0], point1[1])
                        point2 = Vecteur2D(point2[0], point2[1])
                        
                        aretes_decodees.append(Arete(point1, point2))
                        aretes_decodees.append(Arete(point2, point1))

                        max_x = max(max_x, point1.get_x(), point2.get_x())
                        max_y = max(max_y, point1.get_y(), point2.get_y())

                    largeur = int(max_x / Noeud.size.get_x())
                    hauteur = int(max_y / Noeud.size.get_y())
                    grille_route = np.zeros((largeur, hauteur))
                    for arete in aretes_decodees:
                        direction:Vecteur2D = (arete.position_arrivee - arete.position_depart) / Noeud.size.get_x()
                        start:Vecteur2D = Vecteur2D(arete.position_depart.get_x(), arete.position_depart.get_y()) / Noeud.size.get_x()
                        dir_normalisee = direction / direction.norme_manathan()
                        for i in range(int(direction.norme_manathan())):
                            grille_route[int(start.get_x()), int(start.get_y())] = 1
                            start += dir_normalisee
                    carte = Carte(largeur, hauteur, grille_route)
                    
        except FileNotFoundError:
            print("Le fichier n'existe pas !!!! petit malin.................")
        
        except KeyError:
            print("LE FICHIER EST MAL FORMATE, C'EST LA FIN DU MONDE !!!!!!")

        except TypeError:
            print("vraiment, quelqu'un a mis le mauvais type dans ce fichier ? bizarre bizarre....")

        except Exception:
            print("là c'est quoi cte merde par contre")

        return carte
    
    def sauvegarder_carte(self, nom_fichier:str):
        """
        sauvegarde la carte actuelle dans le fichier de nom nom_fichier dans le dossier routes

        input: nom_fichier, str représentant le nom du fichier COMPLET (avec extension)
        return : rien

        effets secondaires : sauvegarde dans le système de fichier
        """
        try:
            with open("../routes/" + nom_fichier, "w") as file:
                dico = {
                    "grille":{
                        "largeur":self.largeur,
                        "hauteur":self.hauteur,
                        "donnees":[[self.grille[x,y] for y in range(self.hauteur)] for x in range(self.largeur)]
                    }
                }
                json.dump(dico, file)
        except Exception:
            print("gros problème !!!!!")


