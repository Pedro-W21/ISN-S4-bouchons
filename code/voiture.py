import math
import random
import time
from arete import Arete
from vecteur_2d import Vecteur2D
from noeud import Noeud, Virage, Intersection_T, Intersection_X, EntreeSortie
from gestionnaire_vitesse import GestionnaireVitesse



class Voiture:

    size = Vecteur2D(3.86, 2.14) # m [longueur, largeur]
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

        self.agressivite = agressivite # compris entre 0 et 1
        
        self.modulation_acceleration = 3 * agressivite

        self.acceleration = (5 + self.modulation_acceleration) / 3.6
        self.deceleration = (5 + self.modulation_acceleration)  / 3.6

        self.deceleration_demarage = 0.6 #m/s^2 -> acceleration pour passer de 0 à 0.01 m/s en 1/60s
        self.acceleration_demarage = 0.6 #m/s^2 -> acceleration pour passer de 0 à 0.01 m/s en 1/60s

        #Variables primaires (ne changeront plus)
        self.couleur = self.genere_couleur()
        chemin, distances = self.recherche_chemin(noeud_depart)
        self.chemin: list[Noeud] = [None] + chemin
        self.distances = distances

        self.arete_actuelle: Arete = self.trouver_arete_entre_noeuds(self.chemin[1], self.chemin[2])

        if not type(self.chemin[2]) == EntreeSortie:
            self.prochaine_arete: Arete = self.trouver_arete_entre_noeuds(self.chemin[2], self.chemin[3])
        else:
            self.prochaine_arete = None
        self.ancienne_arete: Arete = None

        self.gestionnaire_vitesse = GestionnaireVitesse(self)

        self.update_orientation()
        self.update_orientation_prochain_chemin()

        self.arete_actuelle.push_voiture(self)

        self.ancient_usagers = {}

        self.etat = GestionnaireVitesse.ACCELERATION

        self.time = time.time()

    def reassign(self, agressivite: float, noeud_depart: Noeud, noeud_arrivee: Noeud):

        # TODO : revoir les differences avec init pour voir si on a pas oublier des choses
        """
        Initialise de nouveau un objet Voiture.

        Cette méthode est utilisée pour remettre en fonctionnement une voiture qui a terminé un trajet.

        Inputs:
            agressivite (float): Le niveau d'agressivité de la voiture, compris entre 0 et 1.
            noeud_depart (Noeud): Le nouveau noeud de départ de la voiture.
            noeud_arrivee (Noeud): Le nouveau noeud d'arrivée de la voiture.

        Returns:
            None

        Effets secondaires:
            Cette méthode initialise plusieurs attributs de la voiture, notamment son identifiant, sa position, sa direction,
            sa vitesse, son agressivité, etc. Elle génère également une couleur pour la voiture et calcule la distance de sécurité.
            La méthode détermine le chemin à suivre par la voiture, ainsi que les arêtes actuelle, prochaine et ancienne sur lesquelles elle se trouve.
            Enfin, elle met à jour l'orientation de la voiture et initialise son état de vitesse.
        """
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
        self.genere_couleur()

        chemin, distances = self.recherche_chemin(noeud_depart)
        self.chemin: list[Noeud] = [None] + chemin
        self.distances = distances

        self.arete_actuelle: Arete = self.trouver_arete_entre_noeuds(self.chemin[1], self.chemin[2])
        self.prochaine_arete: Arete = self.trouver_arete_entre_noeuds(self.chemin[2], self.chemin[3])
        self.ancienne_arete: Arete = None
        self.update_orientation()
        self.update_orientation_prochain_chemin()

        self.arete_actuelle.push_voiture(self)

        self.distance_marge_securite = self.size.x + self.size.y

        self.ancient_usagers = {}

        self.etat = GestionnaireVitesse.ACCELERATION

        self.time = time.time()

    def update(self):
        self.update_vitesse()
        self.update_position()
        self.update_position_graphe()
        

    def update_vitesse(self):
        # identification des obstacles dans ma zone de sécurité
        voiture_obstacle: Voiture
        distance_voiture_obstacle: float
        voiture_obstacle, distance_voiture_obstacle = self.trouver_voiture_sur_mon_chemin()
        noeuds_obstacles_longueur: list[tuple[Noeud, float]] = self.trouver_noeuds_sur_mon_chemin()

        

        # Si il n'y pas d'obstacles
        if not voiture_obstacle and (not noeuds_obstacles_longueur):
             
            #Je desactive toutes les autres courbes
            desactiver_courbes = [GestionnaireVitesse.FREINAGE,
                                    GestionnaireVitesse.SUIVRE_VOITURE,
                                    GestionnaireVitesse.ARRET]
            self.gestionnaire_vitesse.desactiver_courbes(desactiver_courbes)
            
            # si on est pas à la vitesse max
            if self.vitesse < self.arete_actuelle.vitesse_max:
                if not self.gestionnaire_vitesse.courbe_est_active(self.gestionnaire_vitesse.ACCELERATION):
                    self.gestionnaire_vitesse.genere_courbe_acceleration_arete(self.arete_actuelle)
            elif self.vitesse == self.arete_actuelle.vitesse_max:
                if not self.gestionnaire_vitesse.courbe_est_active(self.gestionnaire_vitesse.ROULE):
                    self.gestionnaire_vitesse.genere_courbe_roule_arete(self.arete_actuelle)
            else:
                if not self.gestionnaire_vitesse.courbe_est_active(self.gestionnaire_vitesse.FREINAGE):
                    self.gestionnaire_vitesse.genere_courbe_freinage_arete(self.arete_actuelle)

        
        else:
            # si il y a des obstacles
            desactiver_courbes = [GestionnaireVitesse.ROULE,
                                    GestionnaireVitesse.ACCELERATION]
            self.gestionnaire_vitesse.desactiver_courbes(desactiver_courbes)


            if voiture_obstacle:
                # TODO : implementer un meilleur check vérifier l'id de la voiture (pour plus tard non essentiel)
                if not self.gestionnaire_vitesse.courbe_est_active(GestionnaireVitesse.SUIVRE_VOITURE):
                    self.gestionnaire_vitesse.genere_courbe_suivie_voiture(voiture_obstacle)
            else:
                self.gestionnaire_vitesse.desactiver_courbes([GestionnaireVitesse.SUIVRE_VOITURE])

            
            for i in range(len(noeuds_obstacles_longueur)):
                # si c'est le premier noeud et que c'est une intersection
                noeud_obstacle = noeuds_obstacles_longueur[i][0]
                distance_noeud_obstacle = noeuds_obstacles_longueur[i][1]
                
                if i == 0 and type(noeud_obstacle) in (Intersection_X, Intersection_T):
                    # si je suis dans la zone de ping
                    if self.distance_entite(noeud_obstacle.position) < noeud_obstacle.distance_securite and not noeud_obstacle.est_un_usager(self):
                        
                        # je demande si je peux passer
                        # ceci est optimise pour ne pas faire de calcul inutile
                        est_empruntee = noeud_obstacle.est_empruntee()
                        usagers_differents = self.ancient_usagers != noeud_obstacle.get_usagers()
                        voie_est_libre = usagers_differents and noeud_obstacle.voie_est_libre(self)
                        
                        #voie pas empruntée ou voie libre
                        if (not est_empruntee) or (voie_est_libre):
                        
                            self.gestionnaire_vitesse.desactiver_courbes([GestionnaireVitesse.ARRET])

                            self.ancient_usagers = {}

                            if self.vitesse < noeud_obstacle.vitesse_max:
                                if not self.gestionnaire_vitesse.courbe_est_active(self.gestionnaire_vitesse.ACCELERATION+self.id_noeud(noeud_obstacle)):
                                    self.gestionnaire_vitesse.genere_courbe_acceleration_noeud(noeud_obstacle)
                            elif self.vitesse == noeud_obstacle.vitesse_max:
                                if not self.gestionnaire_vitesse.courbe_est_active(self.gestionnaire_vitesse.ROULE+self.id_noeud(noeud_obstacle)):
                                    self.gestionnaire_vitesse.genere_courbe_roule_noeud(noeud_obstacle)
                            else:
                                if not self.gestionnaire_vitesse.courbe_est_active(self.gestionnaire_vitesse.FREINAGE+self.id_noeud(noeud_obstacle)):
                                    self.gestionnaire_vitesse.genere_courbe_freinage_noeud(noeud_obstacle)

                        else:
                            #voie empruntée et/ou voie pas libre
                            if not self.gestionnaire_vitesse.courbe_est_active(self.gestionnaire_vitesse.ARRET+self.id_noeud(noeud_obstacle)):
                                self.gestionnaire_vitesse.genere_courbe_arret_noeud(distance_noeud_obstacle, noeud_obstacle.nom)
                            self.ancient_usagers = noeuds_obstacles_longueur[0].get_usagers().copy()
                    
                    else:
                        if self.vitesse < noeud_obstacle.vitesse_max:
                            if not self.gestionnaire_vitesse.courbe_est_active(self.gestionnaire_vitesse.ACCELERATION+self.id_noeud(noeud_obstacle)):
                                self.gestionnaire_vitesse.genere_courbe_acceleration_noeud(noeud_obstacle)
                        elif self.vitesse == noeud_obstacle.vitesse_max:
                            if not self.gestionnaire_vitesse.courbe_est_active(self.gestionnaire_vitesse.ROULE+self.id_noeud(noeud_obstacle)):
                                self.gestionnaire_vitesse.genere_courbe_roule_noeud(noeud_obstacle)
                        else:
                            if not self.gestionnaire_vitesse.courbe_est_active(self.gestionnaire_vitesse.FREINAGE+self.id_noeud(noeud_obstacle)):
                                self.gestionnaire_vitesse.genere_courbe_freinage_noeud(noeud_obstacle)


                # ce n'est pas le premier noeud
                else:
                    
                    # si je suis dans la zone de ping et que ma distance d'arret est superieure ou egale à ma distance de sécurité
                    if distance_noeud_obstacle < noeud_obstacle.distance_securite and self.distance_arret() <= distance_noeud_obstacle:
                        
                        if self.vitesse < noeud_obstacle.vitesse_max:
                            if not self.gestionnaire_vitesse.courbe_est_active(self.gestionnaire_vitesse.ACCELERATION+self.id_noeud(noeud_obstacle)):
                                self.gestionnaire_vitesse.genere_courbe_acceleration_noeud(noeud_obstacle)
                        elif self.vitesse == noeud_obstacle.vitesse_max:
                            if not self.gestionnaire_vitesse.courbe_est_active(self.gestionnaire_vitesse.ROULE+self.id_noeud(noeud_obstacle)):
                                self.gestionnaire_vitesse.genere_courbe_roule_noeud(noeud_obstacle)
                        else:
                            if not self.gestionnaire_vitesse.courbe_est_active(self.gestionnaire_vitesse.FREINAGE+self.id_noeud(noeud_obstacle)):
                                self.gestionnaire_vitesse.genere_courbe_freinage_noeud(noeud_obstacle)
            
            # si il n'y a pas d'obstacle noeud
            else:
                desactiver_courbes = [GestionnaireVitesse.FREINAGE,
                                    GestionnaireVitesse.ARRET]
                self.gestionnaire_vitesse.desactiver_courbes(desactiver_courbes)
    
    def id_noeud(self, noeud: Noeud):
        return self.gestionnaire_vitesse.NOEUD+noeud.nom
        
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

            else:
                # si le noeud est une intersection
                if type(noeud_depasse) in (Intersection_X, Intersection_T):
                # si le noeud est une intersection
                    noeud_depasse.retirer_usager(self)
                # recherche le chemin depuis le noeud depasse
                chemin, distances = self.recherche_chemin(noeud_depasse)
                self.chemin: list[Noeud] = chemin
                self.distances = distances
                # update les variables de position sur le graphes
                self.ancienne_arete = self.arete_actuelle
                self.arete_actuelle = self.trouver_arete_entre_noeuds(self.chemin[0], self.chemin[1])
                self.update_orientation()
                # si le prochain noeud n'est pas une entré-sortie
                if type(self.chemin[1]) != EntreeSortie:
                    self.prochaine_arete = self.trouver_arete_entre_noeuds(self.chemin[1], self.chemin[2])
                    self.update_orientation_prochain_chemin()
                else:
                    self.prochaine_arete = None
                
                # update les variables de position sur le graphes
                self.arete_actuelle.push_voiture(self)
                self.ancienne_arete.voitures.remove(self)

    def update_position(self):
        distance_parcourue, self.etat = self.gestionnaire_vitesse.recuperer_position_etat()

        delta_t = time.time() - self.time
        reste_distance = 0
        if self.direction.projection(abs(self.direction)) >= 0:
            if self.direction*distance_parcourue+self.position > self.arete_actuelle.position_arrivee.projection(self.direction):
                reste_distance = distance_parcourue - (self.arete_actuelle.position_arrivee - self.position).projection(self.direction)
        else:
            if self.direction*distance_parcourue+self.position < self.arete_actuelle.position_arrivee.projection(abs(self.direction)):
                reste_distance = distance_parcourue - (self.arete_actuelle.position_arrivee - self.position).projection(self.direction)

        self.position = (
            self.position + (
            (distance_parcourue-reste_distance)*self.direction()
            )+ (reste_distance*(self.prochaine_arete.position_arrivee-self.prochaine_arete.position_depart).unitaire())
        )
        self.time = time.time()

    def depasse_noeud(self):
        # selon de la voiture renvoie si elle a dépassé le prochain point sur le chemin
        prochain_noeud = self.chemin[1]
        if self.direction_prochain_chemin == Vecteur2D(1, 0):
            if self.position.x > prochain_noeud.position.x + prochain_noeud.size.x:
                return True
        elif self.direction_prochain_chemin == Vecteur2D(-1, 0):
            if self.position.x < prochain_noeud.position.x - prochain_noeud.size.x:
                return True
        elif self.direction_prochain_chemin == Vecteur2D(0, 1):
            if self.position.y > prochain_noeud.position.y + prochain_noeud.size.y:
                return True
        elif self.direction_prochain_chemin == Vecteur2D(0, -1):
            if self.position.y < prochain_noeud.position.y - prochain_noeud.size.y:
                return True

        return False

    def recherche_chemin(self, noeud_depart: Noeud):
        # Recherche chemin à partir de dernier point passé
        
        distances = {noeud_depart: 0}

        chemin = {noeud: float('inf') for noeud in self.graphe}
        noeud_parent = {noeud: None for noeud in self.graphe}
        chemin[noeud_depart] = 0
        queue = [(0, noeud_depart)]
        print("Chemin :", chemin, "\nQueue :", queue)
        while queue:
            dist, noeud = queue.pop(0)

            print(dist, noeud)

            if chemin[noeud] < dist:
                print("On passe, car chemin[noeud]<dist : ", chemin[noeud], "<", dist)
                continue
            print("Voici le contenu de notre point ",noeud, "\n",self.graphe[noeud])
            for (noeud_arrivee, arete) in self.graphe[noeud]:
                print("Examine : ", noeud_arrivee, arete)
                new_distance = chemin[noeud] + arete.get_poids()
                
                if new_distance < chemin[noeud_arrivee]:
                    distances[noeud_arrivee] = arete.longueur
                    print("On a trouvé un chemin plus court")
                    chemin[noeud_arrivee] = new_distance
                    print("New chemin :", chemin)
                    queue.append((new_distance, noeud_arrivee))
                    print("New queue :", queue)
                    noeud_parent[noeud_arrivee] = noeud
                    print("Noeuds parents :", noeud_parent)
            print("next point")
        print(chemin)

        parcours = []
        noeud = self.noeud_arrivee
        while noeud != noeud_depart:
            parcours.append(noeud)
            noeud = noeud_parent[noeud]
 
        # Add the start node manually
        parcours.append(noeud_depart)
        return parcours, distances

    def distance_securite(self, vitesse: float) -> float:
        return self.distance_deceleration(vitesse, 0) + self.distance_marge_securite

    def distance_deceleration(self, vitesse_initiale, vitesse_finale) -> float:
        temps_deceleration = abs(vitesse_initiale/3.6 - vitesse_finale/3.6) / self.deceleration
        distance = 1/2 * self.deceleration * temps_deceleration**2 + vitesse_initiale * temps_deceleration
        return distance
    
    def distance_arret(self):
        return self.distance_deceleration(self.vitesse, 0) + self.distance_marge_securite
        
    def distance_acceleration(self, vitesse_initiale, vitesse_finale) -> float:
        temps_acceleration = abs(vitesse_finale/3.6 - vitesse_initiale/3.6) / self.acceleration
        distance = 1/2 * self.acceleration * temps_acceleration**2 + vitesse_initiale * temps_acceleration
        return distance

    def intention(self):
        return self.direction, self.direction_prochain_chemin
            
    def update_orientation(self):
        self.direction = (self.arete_actuelle.position_arrivee - self.arete_actuelle.position_depart) / (self.arete_actuelle.position_arrivee - self.arete_actuelle.position_depart).norme()

    def update_orientation_prochain_chemin(self):
        if self.prochaine_arete is not None:
            self.direction_prochain_chemin = (self.prochaine_arete.position_arrivee - self.prochaine_arete.position_depart) / (self.prochaine_arete.position_arrivee - self.prochaine_arete.position_depart).norme()
        else:
            self.direction_prochain_chemin = None

    def trouver_arete_entre_noeuds(self, noeud_depart: Noeud, noeud_arrivee: Noeud) -> Arete:
        """
        Renvoie l'arête commune entre deux noeuds.
        Paramètres: noeud_depart (Noeud), noeud_arrivee (Noeud)
        Renvoie: arete (Arete)
        """

        for arete in noeud_depart.aretes:
            if arete in noeud_arrivee.aretes:
                return arete

    def distance_entite(self, position_entite: Vecteur2D):
        return (position_entite - self.position).norme_manathan()

    def trouver_voiture_sur_mon_chemin(self):
        # renvoie ou pas une voiture qui est dans ma distance de securite et sur mon chemin

        longueur = 0
        for i in range(len(self.chemin)-1):
            noeud_depart = self.chemin[i]
            noeud_arrivee = self.chemin[i+1]
            arete = self.trouver_arete_entre_noeuds(noeud_depart, noeud_arrivee)
            if i != 0:
                if longueur < self.distance_securite(self.vitesse):
                    if arete.a_des_voitures():
                        voiture_obstacle = arete.voitures[-1]
                        longueur += (noeud_depart.position - voiture_obstacle.position).norme_manathan()
                        if longueur < self.distance_securite(self.vitesse):
                            return voiture_obstacle, longueur
                        else:
                            return None, None
                    else:
                        longueur += arete.longueur
                else:
                    return None, None
            else:
                if arete.voitures[0] != self and len(arete.voitures) > 1:
                   voiture_obstacle = arete.voitures[arete.voitures.index(self)-1]
                   longueur += (self.position - voiture_obstacle.position).norme_manathan()
                   return voiture_obstacle, longueur
                else:
                    longueur += (self.position - noeud_arrivee.position).norme_manathan()
        return None, None

    def trouver_noeuds_sur_mon_chemin(self):
        # renvoie ou pas tous les noeuds qui sont dans ma distance de securite et sur mon chemin
        
        noeuds: list[Noeud] = []
        longueur = 0
        for i in range(len(self.chemin)-1):
            if i != 0:
                noeud_devant = self.chemin[i]
                if longueur < self.distance_securite(self.vitesse):
                    if noeud_devant.est_empruntee():
                        noeuds.append((noeud_devant, longueur))
                    longueur += (noeud_devant.position - noeuds[i].position).norme_manathan()
                else:
                    return noeuds
            else:
                longueur += (noeuds[1].position - self.position).norme_manathan()
        return noeuds

    def genere_couleur(self):
        couleurs = ['red', 'blue', 'green', 'yellow', 'orange', 'purple', 'pink', 'brown', 'cyan', 'magenta']
        return random.choice(couleurs)

    def __eq__(self, voiture) -> bool:
        return self.id == voiture.id

    def recuperer_position(self):
        angle = -math.atan2(self.orientation.y, self.orientation.x)
        x = self.position.get_x()+Noeud.size.get_x()/4*math.sin(angle)
        y = self.position.get_y()+Noeud.size.get_x()/4*math.cos(angle)
        return (Vecteur2D(x,y), angle)