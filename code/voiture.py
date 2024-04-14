import random
import math
from arrete import Arrete
from vecteur_2d import Vecteur2D
from noeud import Noeud
from gestionnaire_vitesse import GestionnaireVitesse

"""
On fait 
voiture = Voiture(...1)
voiture.__init__(...2)
ou 
voiture = Voiture(...1)
voiture.reassign(...2)

"""

class Voiture:
    size = Vecteur2D(4.5, 2.5) # m [longueur, largeur]

    def __init__(self, id: int, agressivite: float, noeud_depart: Noeud, noeud_arrivee: Noeud, graphe: dict):
        self.id = id

        self.position = noeud_depart.position
        self.affiche = True

        self.noeud_depart: Noeud = noeud_depart
        self.noeud_arrivee: Noeud = noeud_arrivee
        self.graphe = graphe
        
        self.vitesse = 0
        self.gestionnaire_vitesse = GestionnaireVitesse(self)

        self.agressivite = agressivite # compris entre 0 et 1
        
        self.modulation_acceleration = 3 * agressivite
        self.affiche = True
        self.acceleration = (5 + self.modulation_acceleration) / 3.6
        self.deceleration = (5 + self.modulation_acceleration)  / 3.6

        self.deceleration_demarage = 0.6 #m/s^2 -> acceleration pour passer de 0 à 0.01 m/s en 1/60s
        self.acceleration_demarage = 0.6 #m/s^2 -> acceleration pour passer de 0 à 0.01 m/s en 1/60s

        #Variables primaires (ne changeront plus)
        self.couleur = self.generate_color()
        self.distance_securite()

        self.chemin: list[Noeud] = self.recherche_chemin(noeud_depart)

        self.arrete_actuelle: Arrete = self.trouver_arrete(self.chemin[0], self.chemin[1])
        self.prochaine_arrete: Arrete = self.trouver_arrete(self.chemin[1], self.chemin[2])
        self.ancienne_arrete: Arrete = None

        self.distance_marge_securite = self.size.x + self.size.y

    def reassign(self, agressivite: float, noeud_depart: Noeud, noeud_arrivee: Noeud):

        self.position = noeud_depart.position
        self.affiche = True
        
        self.noeud_depart: Noeud = noeud_depart
        self.noeud_arrivee: Noeud = noeud_arrivee
        
        self.vitesse = 0

        self.agressivite = agressivite # compris entre 0 et 1
        
        self.modulation_acceleration = 3 * agressivite

        self.acceleration = (5 + self.modulation_acceleration) / 3.6
        self.deceleration = (5 + self.modulation_acceleration)  / 3.6

        #Variables primaires (ne changeront plus)
        self.generate_color()
        self.distance_securite()

        self.chemin: list[Noeud] = self.recherche_chemin(noeud_depart)

        self.arrete_actuelle: Arrete = self.trouver_arrete(self.chemin[0], self.chemin[1])
        self.prochaine_arrete: Arrete = self.trouver_arrete(self.chemin[1], self.chemin[2])
        self.ancienne_arrete: Arrete = None

        self.distance_marge_securite = self.size.x + self.size.y
    
    def update(self, fps: int):
        if fps == 0:
            return
        self.update_position(1/fps)
        self.update_position_graphe()
    

    def update_vitesse(self):
        # identification des obstacles dans ma zone de sécurité
        voiture_obstacle: list[Voiture] = self.trouver_voiture_sur_mon_chemin()
        noeuds_obstacles: list[Noeud] = self.trouver_noeuds_sur_mon_chemin()
        
        """

        Si il n'y pas d'obstacle
            Je desactive toutes les autres courbes
            Si je n'ai pas déjà une courbe d'acceleration active : 
                Je genere une courbe  d'acceleration et je l'active
        Sinon
            Je desactive la courbe

        """
        # Si il n'y pas d'obstacle
        if voiture_obstacle is None and not noeuds_obstacles == 0:
            #Je desactive toutes les autres courbes
            #Si je n'ai pas déjà une courbe d'acceleration active
                #Je genere une courbe  d'acceleration et je l'active
            pass
        else:
            # je desactive la courbe d'acceleration
            if voiture_obstacle is not None:
                #Je prends sa courbe
                #Si j'ai pas une courbe active
                    #Je l'enregistre
                    #Je l'active
                pass
            else:
                #Je désactive la courbe de suivie des voitures
                pass

            for i in range(len(noeuds_obstacles)):
                if i == 0 and noeuds_obstacles[0].type in (Noeud.INTERSECTION_T, Noeud.INTERSECTION_X):
                    # si je suis dans la zone de ping
                    if self.distance_a_entite(noeuds_obstacles[0].position) < noeuds_obstacles[0].distance_securite:
                        # je demande si je peux passer
                        if noeuds_obstacles[0].voie_est_libre(self):
                            # Je désactive la courbe d'arret de ce point
                            pass
                        else:
                            # Je genere une courbe d'arret
                            # Je l'active
                            pass
                else:
                    # si je suis dans la zone de ping
                    if self.distance_a_entite(noeuds_obstacles[i].position) < noeuds_obstacles[i].distance_securite:
                        # Je genere une courbe d'arret si elle n'exsite pas
                            # Je l'active
                        pass
                    #Je prends sa courbe
                    #Si j'ai pas une courbe active
                        #Je la cré et l'enregistre
                        #Je l'active
                    pass
            else:
                # Je desactive les courbes
                pass



            

        
    
    def update_position_graphe(self):
        noeud_depasse = self.depasse_noeud()
        # si on depasse un noeud
        if noeud_depasse:
            # si c'est une entree sortie
            if self.prochaine_arrete is None:
                # desactive la voiture
                self.affiche = False
                self.arrete_actuelle.voitures.remove(self)
                # TODO: faire dispawn la voiture

            else:
                # recherche le chemin depuis le noeud depasse
                self.recherche_chemin(noeud_depasse)
                # update les variables de position sur le graphes
                self.ancienne_arrete = self.arrete_actuelle
                self.arrete_actuelle = self.trouver_arrete(self.chemin[0], self.chemin[1])

                # si le prochain noeud n'est pas une entré-sortie
                if len(self.chemin) > 2:
                    self.prochaine_arrete = self.trouver_arrete(self.chemin[1], self.chemin[2])
                else:
                    self.prochaine_arrete = None
                
                # update les variables de position sur le graphes
                self.arrete_actuelle.push_voiture(self)
                self.ancienne_arrete.voitures.remove(self)

    def depasse_noeud(self):
        # selon de la voiture renvoie si elle a dépassé le prochain point sur le chemin
        prochain_noeud = self.chemin[1]
        if self.orientation() == (1, 0):
            if self.position.x > prochain_noeud.position.x:
                return True
        elif self.orientation() == (-1, 0):
            if self.position.x < prochain_noeud.position.x:
                return True
        elif self.orientation() == (0, 1):
            if self.position.y > prochain_noeud.position.y:
                return True
        elif self.orientation() == (0, -1):
            if self.position.y < prochain_noeud.position.y:
                return True

        return False

    def recherche_chemin(self, noeud_depart: Noeud) -> list[Noeud]:
        # Recherche chemin à partir de dernier point passé

        chemin = {noeud: float('inf') for noeud in self.graphe}
        chemin[noeud_depart] = 0

        queue = [(0, noeud_depart)]

        while queue:
            dist, noeud = queue.pop(0)
            if chemin[noeud] < dist:
                continue
            for (noeud_arrivee, arrete) in self.graphe[noeud].values():
                new_distance = chemin[noeud] + arrete.get_poids()
                if new_distance < chemin[noeud_arrivee]:
                    chemin[noeud_arrivee] = new_distance
                    queue.append((new_distance, noeud_arrivee))
        return chemin

    def distance_securite(self, vitesse: float) -> float:
        return self.distance_deceleration(vitesse, 0) + self.distance_marge_securite

    def distance_deceleration(self, vitesse_initiale, vitesse_finale) -> float:
        temps_deceleration = abs(vitesse_initiale/3.6 - vitesse_finale/3.6) / self.deceleration
        distance = 1/2 * self.deceleration * temps_deceleration**2
        return distance
    
    def distance_freinage_complet(self):
        return self.distance_deceleration(self.vitesse, 0)
        
    def distance_acceleration(self, vitesse_initiale, vitesse_finale) -> float:
        temps_acceleration = abs(vitesse_finale/3.6 - vitesse_initiale/3.6) / self.acceleration
        distance = 1/2 * self.acceleration * temps_acceleration**2
        return distance

    def intention(self):
        return self.orientation(), self.direction_prochain_chemin()
    
    def trouver_arrete(self, noeud_depart: Noeud, noeud_arrivee: Noeud):
        for arrete in noeud_depart.arretes:
            if arrete == [noeud_depart, noeud_arrivee]:
                return arrete
            
    def orientation(self):
        dir_x = self.arrete_actuelle.position_depart.x - self.arrete_actuelle.position_arrivee.x / abs(self.arrete_actuelle.position_depart.x - self.arrete_actuelle.position_arrivee.x)
        dir_y = self.arrete_actuelle.position_depart.y - self.arrete_actuelle.position_arrivee.y / abs(self.arrete_actuelle.position_depart.y - self.arrete_actuelle.position_arrivee.y)
        return dir_x, dir_y

    def generate_color(self):
        colors = ['red', 'blue', 'green', 'yellow', 'orange', 'purple', 'pink', 'brown', 'cyan', 'magenta']
        randomIndex = math.floor(random.random() * colors.length)
        return colors[randomIndex]

    ##TODO A SUPPRIMER SI PLUS BESOIN
    def update_position(self, time_elapsed):
        # suivre la courbe sauf si :
        # - la vitesse est nulle
        # - la position est celle de depart (coup de pouce recursif)

        self.position.x += self.vitesse * math.cos(self.orientation()) * time_elapsed
        self.position.y += self.vitesse * math.sin(self.orientation()) * time_elapsed

    def direction_prochain_chemin(self):
        dir_x = self.prochaine_arrete.position_depart.x - self.prochaine_arrete.position_arrivee.x / abs(self.prochaine_arrete.position_depart.x - self.prochaine_arrete.position_arrivee.x)
        dir_y = self.prochaine_arrete.position_depart.y - self.prochaine_arrete.position_arrivee.y / abs(self.prochaine_arrete.position_depart.y - self.prochaine_arrete.position_arrivee.y)
        return dir_x, dir_y

    def trouver_arrete_entre_noeuds(self, noeud_depart: Noeud, noeud_arrivee: Noeud) -> Arrete:
        for arrete in noeud_depart.arretes:
            if arrete in noeud_arrivee.arretes:
                return arrete

    def distance_a_entite(self, position_entite: Vecteur2D):
        return (position_entite - self.position).norme_manathan()

    def est_dans_zone_securite(self, position_entite: Vecteur2D) -> bool:
        return self.distance_a_entite(position_entite) < self.distance_securite()

    def trouver_voiture_sur_mon_chemin(self):
        # renvoie ou pas une voiture qui est dans ma distance de securite et sur mon chemin
        for i in range(len(self.chemin)-1):
            noeud_depart = self.chemin[i]
            noeud_arrivee = self.chemin[i+1]
            arrete = self.trouver_arrete_entre_noeuds(noeud_depart, noeud_arrivee)
            if i != 0:
                if self.est_dans_zone_securite(noeud_depart.position):
                    if arrete.a_des_voitures():
                        voiture_obstacle = arrete.voitures[-1]
                        if self.est_dans_zone_securite(voiture_obstacle.position):
                            return voiture_obstacle
                        else:
                            return None
                else:
                    return None
            else:
                if arrete.voitures[0] != self and len(arrete.voitures) > 1:
                   return arrete.voitures[arrete.voitures.index(self)-1]
        return None

    def trouver_noeuds_sur_mon_chemin(self):
        # renvoie ou pas tous les noeuds qui sont dans ma distance de securite et sur mon chemin
        noeuds: Noeud = []
        for i in range(len(self.chemin)):
            if i != 0:
                noeud_devant = self.chemin[i]
                if self.est_dans_zone_securite(noeud_devant.position):
                    if noeud_devant.est_emprsuntee():
                        noeuds.append(noeud_devant)
                else:
                    return noeuds
        return noeuds

    def __eq__(self, voiture) -> bool:
        return self.id == voiture.id
