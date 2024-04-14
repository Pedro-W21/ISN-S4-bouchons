import random
import math
from arrete import Arrete
from vecteur_2d import Vecteur2D
from noeud import Noeud
from courbe import Courbe

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
        # TODO: A FAIRE
        # Renvoie True si on a dépassé le noeud
        # Renvoie False si on est toujours sur le noeud

        # ne pas tenir compte des virages
        # simple calcul d'orientation et de direction de la voiture par rapport au point
        # renvoie NONE ou le noeud qui vient d'être dépassé
        pass



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
    def follow_curve(self, newcurve=None):
        if newcurve:
            self.curve = True
            vitesse_origine = self.vitesse
            point_origine = self.position
            point_objectif = newcurve[0]
            vitesse_objectif = newcurve[1]
        
        new_vitesse = vitesse_origine+(self.position-point_origine)(vitesse_objectif-vitesse_origine)/(point_objectif-point_origine)
        if vitesse_origine < vitesse_objectif:
            #croissant
            new_vitesse = min(new_vitesse, vitesse_objectif)
        else:
            #décroissant
            new_vitesse = max(new_vitesse, vitesse_objectif)
        self.vitesse = new_vitesse

        #TODO MANAGE DEPASSEMENT DE POINT (TOUS LES SENS)
        self.position[0] += self.vitesse * math.cos(self.orientation)
        self.position[1] += self.vitesse * math.sin(self.orientation)

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

    ##TODO A SUPPRIMER SI PLUS BESOIN
    def contrainte_plus_proche(self):
        # On obtient tous les points pouvant constituer des arêtes contenant des voitures sous la distance de sécurité
        distance_totale = 0
        noeuds_a_traiter = [(self,0)]
        prochain_noeuds = iter(self.chemin.items())
        premier_noeud = next(prochain_noeuds)
        for noeud in prochain_noeuds.key():
            distance_to_point = noeud.position - noeuds_a_traiter[-1][0].position
            if distance_totale < self.distance_securite_point and self.noeuds[noeud]=="stop":
                noeuds_a_traiter.append([noeud,distance_to_point])
            distance_totale+=distance_to_point
        noeuds_a_traiter[0] = (premier_noeud[0],0)
        # On obtient toutes les voitures sous la distance de sécurité 
        # (on pourrait aussi s'arrêter à la première voiture)
        distance_totale = 0
        voitures_a_traiter = [(self,0)]
        #TODO
        #trouver la voiture la plus proche (pas avant nous), qui peut être sur notre arête ou une suivante
        for i in range(len(noeuds_a_traiter)-1):
            arrete = self.trouver_arrete(noeuds_a_traiter[i][0], noeuds_a_traiter[i+1][0])
            for voiture in arrete.voitures:
                distance_to_voiture = voiture.position-voitures_a_traiter[-1][1]
                distance_totale+=distance_to_voiture
                if distance_totale < self.distance_securite_voiture:
                    voitures_a_traiter.append((voiture,distance_totale))
                    break
            distance_totale+=noeuds_a_traiter[i][1]
            if len(voitures_a_traiter)>1:
                break
        voitures_a_traiter.pop(0)
        for noeud in noeuds_a_traiter:
            # {Noeud:"stop",Noeud:"pass",Noeud:"slow"}
            reponse = noeud[0].voie_est_libre(self)
            if reponse:
                if self.direction_prochain_chemin == self.orientation:
                    self.noeuds[noeud[0]] = "go"
                else:
                    self.noeuds[noeud[0]] = "slow"
            else:
                self.noeuds[noeud[0]] = "stop"
        contraintes = None#TODO
        #tant que les points disent go ou slow et qu'il n'y a pas de voiture entre
        #distance prochain obstacle = prochain point
        #dès qu'on a une voiture, distance prochain obstacle c'est lui
            #regulate pour obtenir v voiture à distance_modulation_voiture
        #si un point a dit slow, alors on ralentit à distance_arret_point
        ##NON REPRENDRE DEFINITION

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
                if arrete.voitures[0].id != self.id and len(arrete.voitures) > 1:
                    voiture_obstacle = arrete.voitures[arrete.voitures.index(self)-1]
                else:
                    None
        return None

    def trouver_noeud_sur_mon_chemin(self):
        # renvoie ou pas un noeud qui est dans ma distance de securite et sur mon chemin
        for i in range(len(self.chemin)):
            if i != 0:
                noeud_devant = self.chemin[i]
                if self.est_dans_zone_securite(noeud_devant.position):
                    if noeud_devant.est_emprsuntee():
                        return noeud_devant
                else:
                    return None
        return None


class RangeError(Exception):
    
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class GestionnaireVitesse:


    # sert à savoir l'etat d'une voiture notamment pour les voitures de derrière
    ACCELERATION = "ACCELERATION"
    FREINAGE = "FREINAGE"
    SUIVRE_VOITURE = "SUIVRE_VOITURE"
    ARRET = "ARRET"
    ROULE = "ROULE"




    def __init__(self, voiture):

        self.voiture: Voiture = voiture

        self.etat = self.ACCELERATION

        self.courbe_par_defaut = Courbe(voiture.position, voiture.position + voiture.arrete_actuelle.longueur, voiture.vitesse, voiture.vitesse)
        self.position_depart_par_defaut: Vecteur2D = voiture.position
        
        self.courbe_obstacle_voiture = self.courbe_par_defaut
        self.position_depart_obstacle_voiture: Vecteur2D = voiture.position

        self.courbe_obstacle_noeud = self.courbe_par_defaut
        self.position_depart_obstacle_noeud: Vecteur2D = voiture.position

        self.courbe_arret = self.courbe_par_defaut
        self.position_depart_arret: Vecteur2D = voiture.position

        self.courbe_acceleration = self.courbe_par_defaut
        self.position_depart_acceleration: Vecteur2D = voiture.position

        self.courbe_courante = self.courbe_par_defaut
        self.position_depart_courante: Vecteur2D = voiture.position
        

        #TODO: gerer les x et y position de la voiture avec les positions de depart
        #TODO: faire une courbe d'arret
        #TODO: verifier que tout est bon
        #TODO: faire les courbes de ralentissement voitures v1 et v2 variables d  = distance de securite variable

    def genere_courbe_obstacle_voiture(self, voiture_obstacle: Voiture) -> tuple[float, str]:
        
        self.position_depart_obstacle_voiture: Vecteur2D = self.voiture.position

        courbe_voiture_obstacle = voiture_obstacle.gestionnaire_vitesse.courbe_courante
        distance_securite_finale = self.voiture.distance_securite(courbe_voiture_obstacle.vitesse_finale)
        self.courbe_obstacle_voiture = Courbe(self.voiture.position, courbe_voiture_obstacle.position_arrivee - distance_securite_finale, self.voiture.vitesse, courbe_voiture_obstacle.vitesse_finale)

    def genere_courbe_obstacle_noeud(self, noeud_obstacle: Noeud):

        self.position_depart_obstacle_noeud: Vecteur2D = self.voiture.position
        self.courbe_obstacle_noeud = Courbe(self.voiture.position, noeud_obstacle.position - noeud_obstacle.distance_securite, self.voiture.vitesse, noeud_obstacle.vitesse_max)

    def genere_courbe_acceleration_arrete(self, arrete: Arrete):
        self.position_depart_acceleration: Vecteur2D = self.voiture.position
        self.courbe_acceleration = Courbe(self.voiture.position, self.voiture.distance_acceleration(self.voiture.vitesse, arrete.vitesse_max), self.voiture.vitesse, arrete.vitesse_max)

    def genere_courbe_par_defaut(self):
        self.position_depart_par_defaut: Vecteur2D = self.voiture.position
        self.courbe_par_defaut = Courbe(self.voiture.position, self.voiture.position + self.voiture.arrete_actuelle.longueur, self.voiture.vitesse, self.voiture.vitesse)
    
    def genere_courbe_arret(self, position_finale):
        self.position_depart_arret: Vecteur2D = self.voiture.position
        self.courbe_arret = Courbe(self.voiture.position, position_finale, self.voiture.vitesse, 0)

    def update_courbe_courante(self):
        if self.etat == self.ACCELERATION:
            self.courbe_courante = self.courbe_acceleration
            self.position_depart_courante = self.position_depart_acceleration
        elif self.etat == self.ROULE:
            self.courbe_courante = self.courbe_par_defaut
            self.position_depart_courante = self.position_depart_par_defaut
        elif self.etat == self.FREINAGE:
            self.courbe_courante = self.courbe_obstacle_noeud
            self.position_depart_courante = self.position_depart_obstacle_noeud
        elif self.etat == self.ARRET:
            self.courbe_courante = self.courbe_arret
            self.position_depart_courante = self.position_depart_arret
        elif self.etat == self.SUIVRE_VOITURE:
            self.courbe_courante = self.courbe_obstacle_voiture
            self.position_depart_courante = self.position_depart_obstacle_voiture

    def recuperer_vitesse(self, default: bool, acceleration: bool, obstacle_voiture: bool, obstacle_noeud: bool, arret: bool):
        etat = []
        vitesses = []
        if default and (self.voiture.position - self.position_depart_par_defaut).norme_manathan() < self.courbe_par_defaut.position_arrivee:
            vitesses.append(self.courbe_par_defaut.result(self.voiture.position - self.position_depart_par_defaut).norme_manathan())
            etat.append(self.ROULE)
        else:
            raise RangeError("La voiture est hors de la courbe")

        if acceleration and (self.voiture.position - self.position_depart_acceleration).norme_manathan() < self.courbe_acceleration.position_arrivee:
            vitesses.append(self.courbe_acceleration.result(self.voiture.position - self.position_depart_acceleration).norme_manathan())
            etat.append(self.ACCELERATION)
        else:
            raise RangeError("La voiture est hors de la courbe")

        if obstacle_voiture and (self.voiture.position - self.position_depart_obstacle_voiture).norme_manathan() < self.courbe_obstacle_voiture.position_arrivee:
            vitesses.append(self.courbe_obstacle_voiture.result(self.voiture.position - self.position_depart_obstacle_voiture).norme_manathan())
            etat.append(self.SUIVRE_VOITURE)
        else:
            raise RangeError("La voiture est hors de la courbe")
        if obstacle_noeud and (self.voiture.position - self.position_depart_obstacle_noeud).norme_manathan() < self.courbe_obstacle_noeud.position_arrivee:
            vitesses.append(self.courbe_obstacle_noeud.result(self.voiture.position - self.position_depart_obstacle_noeud).norme_manathan())
            etat.append(self.FREINAGE)
        else:
            raise RangeError("La voiture est hors de la courbe")
        
        if arret and (self.voiture.position - self.position_depart_arret).norme_manathan() < self.courbe_arret.position_arrivee:
            vitesses.append(self.courbe_arret.result(self.voiture.position - self.position_depart_arret).norme_manathan())
            etat.append(self.ARRET)
        else:
            raise RangeError("La voiture est hors de la courbe")
        vitesse = min(vitesses)
        self.etat = etat[vitesses.index(vitesse)]
        self.update_courbe_courante() 
        return vitesse, self.etat
