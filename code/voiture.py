import random
import math
from arete import Arete
from vecteur_2d import Vecteur2D
from noeud import Noeud
from gestionnaire_vitesse import GestionnaireVitesse



class Voiture:

    size = Vecteur2D(4.5, 2.5) # m [longueur, largeur]
    distance_marge_securite = size.x + size.y

    def __init__(self, id: int, agressivite: float, noeud_depart: Noeud, noeud_arrivee: Noeud, graphe: dict):
        self.id = id

        self.position = noeud_depart.position
        self.direction = Vecteur2D(0, 0)
        self.direction_prochain_chemin = Vecteur2D(0, 0)

        self.affiche = False

        self.noeud_depart: Noeud = noeud_depart
        self.noeud_arrivee: Noeud = noeud_arrivee
        self.graphe = graphe
        
        self.vitesse = 0
        self.gestionnaire_vitesse = GestionnaireVitesse(self)

        self.agressivite = agressivite # compris entre 0 et 1
        
        self.modulation_acceleration = 3 * agressivite

        self.acceleration = (5 + self.modulation_acceleration) / 3.6
        self.deceleration = (5 + self.modulation_acceleration)  / 3.6

        self.deceleration_demarage = 0.6 #m/s^2 -> acceleration pour passer de 0 à 0.01 m/s en 1/60s
        self.acceleration_demarage = 0.6 #m/s^2 -> acceleration pour passer de 0 à 0.01 m/s en 1/60s

        #Variables primaires (ne changeront plus)
        self.couleur = self.genere_couleur()
        self.distance_securite()

        self.chemin: list[Noeud] = [None]+self.recherche_chemin(noeud_depart)

        self.arete_actuelle: Arete = self.trouver_arete(self.chemin[1], self.chemin[2])

        if self.chemin[2] != Noeud.ENTREE_SORTIE:
            self.prochaine_arete: Arete = self.trouver_arete(self.chemin[2], self.chemin[3])
        else:
            self.prochaine_arete = None
        self.ancienne_arete: Arete = None
        self.update_orientation()
        self.update_orientation_prochain_chemin()

        self.arete_actuelle.push_voiture(self)

        self.ancient_usagers = {}

        self.etat = GestionnaireVitesse.ACCELERATION

    def reassign(self, agressivite: float, noeud_depart: Noeud, noeud_arrivee: Noeud):

        self.position = noeud_depart.position        
        self.affiche = False
        
        self.noeud_depart: Noeud = noeud_depart
        self.noeud_arrivee: Noeud = noeud_arrivee
        
        self.vitesse = 0

        self.agressivite = agressivite # compris entre 0 et 1
        
        self.modulation_acceleration = 3 * agressivite

        self.acceleration = (5 + self.modulation_acceleration) / 3.6
        self.deceleration = (5 + self.modulation_acceleration)  / 3.6

        #Variables primaires (ne changeront plus)
        self.genere_couleur()
        self.distance_securite()

        self.chemin: list[Noeud] = [None]+self.recherche_chemin(noeud_depart)

        self.arete_actuelle: Arete = self.trouver_arete(self.chemin[1], self.chemin[2])
        self.prochaine_arete: Arete = self.trouver_arete(self.chemin[2], self.chemin[3])
        self.ancienne_arete: Arete = None
        self.update_orientation()
        self.update_orientation_prochain_chemin()

        self.arete_actuelle.push_voiture(self)

        self.distance_marge_securite = self.size.x + self.size.y

        self.ancient_usagers = {}

        self.etat = GestionnaireVitesse.ACCELERATION

    def update(self, fps: int):
        if fps == 0:
            return
        self.update_position(1/fps)
        self.update_position_graphe()
        self.update_vitesse()

    def update_vitesse(self):
        # identification des obstacles dans ma zone de sécurité
        voiture_obstacle: Voiture = self.trouver_voiture_sur_mon_chemin()
        noeuds_obstacles: list[Noeud] = self.trouver_noeuds_sur_mon_chemin()
        
        # Si il n'y pas d'obstacle
        if voiture_obstacle is None and (not noeuds_obstacles):
             
            #Je desactive toutes les autres courbes
            desactiver_courbes = [GestionnaireVitesse.FREINAGE,
                                    GestionnaireVitesse.SUIVRE_VOITURE,
                                    GestionnaireVitesse.ARRET]
            self.gestionnaire_vitesse.desactiver_courbes(desactiver_courbes)
            
            # si on est pas à la vitesse max
            if self.vitesse < self.arete_actuelle.vitesse_max:
                if not self.gestionnaire_vitesse.courbe_est_active(GestionnaireVitesse.ACCELERATION):
                    self.gestionnaire_vitesse.genere_courbe_acceleration_arete()   
            elif not self.gestionnaire_vitesse.courbe_est_active(GestionnaireVitesse.ROULE):
                self.gestionnaire_vitesse.genere_courbe_par_defaut()
        
        else:
            desactiver_courbes = [GestionnaireVitesse.ROULE,
                                    GestionnaireVitesse.ACCELERATION]
            self.gestionnaire_vitesse.desactiver_courbes(desactiver_courbes)


            if voiture_obstacle is not None:
                if not self.gestionnaire_vitesse.courbe_est_active(GestionnaireVitesse.SUIVRE_VOITURE):
                    self.gestionnaire_vitesse.genere_courbe_suivre_voiture(voiture_obstacle)
            else:
                self.gestionnaire_vitesse.desactiver_courbes([GestionnaireVitesse.SUIVRE_VOITURE])

            # TODO: revoir courbes de freinage/distance de ping adaptative
            
            for i in range(len(noeuds_obstacles)):
                # si c'est le premier noeud et que c'est une intersection
                if i == 0 and noeuds_obstacles[0].type in (Noeud.INTERSECTION_T, Noeud.INTERSECTION_X):
                    if not noeuds_obstacles[0].est_un_usager(self):
                        # si je suis dans la zone de ping
                        if self.distance_a_entite(noeuds_obstacles[0].position) < noeuds_obstacles[0].distance_securite:
                            
                            # je demande si je peux passer
                            # ceci est optimise pour ne pas faire de calcul inutile
                            est_empruntee = noeuds_obstacles[0].est_empruntee()
                            usagers_differents = self.ancient_usagers != noeuds_obstacles[0].get_usagers()
                            voie_est_libre = usagers_differents and noeuds_obstacles[0].voie_est_libre(self)
                            
                            #voie pas empruntée ou voie libre
                            if (not est_empruntee) or (voie_est_libre):
                               
                                # TODO : de quel courbe d'arret on parle il y en a plusieurs
                                self.gestionnaire_vitesse.desactiver_courbes([GestionnaireVitesse.ARRET], position_finale=noeuds_obstacles[0].position)
                                self.ancient_usagers = {}
                            else:
                                #voie empruntée et voie pas libre
                                self.gestionnaire_vitesse.genere_courbe_arret()
                            
                            # voie pas libre
                            if not voie_est_libre:
                                self.ancient_usagers = noeuds_obstacles[0].get_usagers().copy()
                else:
                    # si je suis dans la zone de ping
                    if self.distance_a_entite(noeuds_obstacles[i].position) < noeuds_obstacles[i].distance_securite:
                        self.gestionnaire_vitesse.genere_courbe_freinage()
            else:
                desactiver_courbes = [GestionnaireVitesse.FREINAGE,
                                    GestionnaireVitesse.ARRET]
                self.gestionnaire_vitesse.desactiver_courbes(desactiver_courbes)
    
    def update_position_graphe(self):
        noeud_depasse: Noeud = self.depasse_noeud()
        # si on depasse un noeud
        if noeud_depasse:
            
            if noeud_depasse == self.noeud_depart:
                    self.noeud_depasse.retirer_usager(self)
            elif noeud_depasse == self.noeud_arrivee:
                # desactive la voiture
                self.affiche = False
                self.arete_actuelle.voitures.remove(self)
                # TODO: faire dispawn la voiture
                # TODO: Réponse : Devrait suffir car simulation prend le relai lorsque affiche = False
                ## Par contre il faut fixe, prochaine_arete = None, voir TODO plus haut

            else:
                # si le noeud est une intersection
                if noeud_depasse.type in (Noeud.INTERSECTION_T, Noeud.INTERSECTION_X):
                # si le noeud est une intersection
                    noeud_depasse.retirer_usager(self)
                # recherche le chemin depuis le noeud depasse
                self.recherche_chemin(noeud_depasse)
                # update les variables de position sur le graphes
                self.ancienne_arete = self.arete_actuelle
                self.arete_actuelle = self.trouver_arete(self.chemin[0], self.chemin[1])
                self.update_orientation()
                # si le prochain noeud n'est pas une entré-sortie
                if self.chemin[1].type != Noeud.ENTREE_SORTIE:
                    self.prochaine_arete = self.trouver_arete(self.chemin[1], self.chemin[2])
                    self.update_orientation_prochain_chemin()
                else:
                    self.prochaine_arete = None
                
                # update les variables de position sur le graphes
                self.arete_actuelle.push_voiture(self)
                self.ancienne_arete.voitures.remove(self)

    def depasse_noeud(self):
        # selon de la voiture renvoie si elle a dépassé le prochain point sur le chemin
        prochain_noeud = self.chemin[1]
        if self.direction == (1, 0):
            if self.position.x > prochain_noeud.position.x + prochain_noeud.size.x:
                return True
        elif self.direction == (-1, 0):
            if self.position.x < prochain_noeud.position.x - prochain_noeud.size.x:
                return True
        elif self.direction == (0, 1):
            if self.position.y > prochain_noeud.position.y + prochain_noeud.size.y:
                return True
        elif self.direction == (0, -1):
            if self.position.y < prochain_noeud.position.y - prochain_noeud.size.y:
                return True

        return False

    def recherche_chemin(self, noeud_depart: Noeud):
        # Recherche chemin à partir de dernier point passé

        chemin = {noeud: float('inf') for noeud in self.graphe}
        chemin[noeud_depart] = 0

        queue = [(0, noeud_depart)]

        while queue:
            dist, noeud = queue.pop(0)
            if chemin[noeud] < dist:
                continue
            for (noeud_arrivee, arete) in self.graphe[noeud].values():
                new_distance = chemin[noeud] + arete.get_poids()
                if new_distance < chemin[noeud_arrivee]:
                    chemin[noeud_arrivee] = new_distance
                    queue.append((new_distance, noeud_arrivee))
        self.chemin = chemin

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
        return self.direction, self.direction_prochain_chemin
    
    def trouver_arete(self, noeud_depart: Noeud, noeud_arrivee: Noeud):
        for arete in noeud_depart.aretes:
            if arete == [noeud_depart, noeud_arrivee]:
                return arete
        return None
            
    def update_orientation(self):
        self.direction = (self.arete_actuelle.position_arrivee - self.arete_actuelle.position_depart) / (self.arete_actuelle.position_arrivee - self.arete_actuelle.position_depart).norme()

    def genere_couleur(self):
        couleurs = ['red', 'blue', 'green', 'yellow', 'orange', 'purple', 'pink', 'brown', 'cyan', 'magenta']
        return random.choice(couleurs)

    def update_position(self, time_elapsed):
        # TODO: utiliser le gestionnaire de vitesse pour recuperer la vitesse et mettre à jour la position
        # suivre la courbe sauf si :
        # - la vitesse est nulle
        # - la position est celle de depart (coup de pouce recursif)

        self.position.x += self.vitesse * math.cos(self.direction) * time_elapsed
        self.position.y += self.vitesse * math.sin(self.direction) * time_elapsed

    def update_orientation_prochain_chemin(self):
        if self.prochaine_arete is not None:
            self.direction_prochain_chemin = (self.prochaine_arete.position_arrivee - self.prochaine_arete.position_depart) / (self.prochaine_arete.position_arrivee - self.prochaine_arete.position_depart).norme()
        else:
            self.direction_prochain_chemin = None

    def trouver_arete_entre_noeuds(self, noeud_depart: Noeud, noeud_arrivee: Noeud) -> Arete:
        for arete in noeud_depart.aretes:
            if arete in noeud_arrivee.aretes:
                return arete

    def distance_a_entite(self, position_entite: Vecteur2D):
        return (position_entite - self.position).norme_manathan()

    def est_dans_zone_securite(self, position_entite: Vecteur2D) -> bool:
        return self.distance_a_entite(position_entite) < self.distance_securite()

    def trouver_voiture_sur_mon_chemin(self):
        # renvoie ou pas une voiture qui est dans ma distance de securite et sur mon chemin
        for i in range(len(self.chemin)-1):
            noeud_depart = self.chemin[i]
            noeud_arrivee = self.chemin[i+1]
            arete = self.trouver_arete_entre_noeuds(noeud_depart, noeud_arrivee)
            if i != 0:
                if self.est_dans_zone_securite(noeud_depart.position):
                    if arete.a_des_voitures():
                        voiture_obstacle = arete.voitures[-1]
                        if self.est_dans_zone_securite(voiture_obstacle.position):
                            return voiture_obstacle
                        else:
                            return None
                else:
                    return None
            else:
                if arete.voitures[0] != self and len(arete.voitures) > 1:
                   return arete.voitures[arete.voitures.index(self)-1]
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
