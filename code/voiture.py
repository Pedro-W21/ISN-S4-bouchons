import math
import time
from arete import Arete
from vecteur_2d import Vecteur2D
from noeud import Noeud, Virage, Intersection_T, Intersection_X, EntreeSortie
from gestionnaire_vitesse import GestionnaireVitesse

class Voiture:

    #size = Vecteur2D(3.86, 2.14) # m [longueur, largeur]
    size = Vecteur2D(2, 1.75) # m [longueur, largeur]
    
    distance_marge_securite = size.x + size.y

    def __init__(self, id: int, graphe: dict):
        self.id = id
        self.affiche = False
        self.graphe = graphe
        

    def demarrage(self, agressivite: float, noeud_depart: Noeud, noeud_arrivee: Noeud, couleur: str):
        print(noeud_depart.position/Noeud.size.x)

        self.position = noeud_depart.position


        
        self.affiche = True

        self.noeud_depart: Noeud = noeud_depart
        self.noeud_arrivee: Noeud = noeud_arrivee
        
        self.vitesse = 0

        self.agressivite = agressivite # compris entre 0 et 1
        
        self.modulation_acceleration = 3 * agressivite

        self.acceleration = (5 + self.modulation_acceleration) / 3.6
        self.deceleration = (5 + self.modulation_acceleration)  / 3.6

        self.deceleration_demarage = 0.6 #m/s^2 -> acceleration pour passer de 0 à 0.01 m/s en 1/60s
        self.acceleration_demarage = 0.6 #m/s^2 -> acceleration pour passer de 0 à 0.01 m/s en 1/60s

        #Variables primaires (ne changeront plus)
        self.couleur = couleur
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


        self.direction = (self.arete_actuelle.position_arrivee - self.arete_actuelle.position_depart).unitaire()
        self.ancienne_direction = self.direction
        self.direction_prochain_chemin = Vecteur2D(0, 0)
        
        self.update_orientation_prochain_chemin()

        self.arete_actuelle.push_voiture(self)
        self.noeud_depart.enregistrer_usager(self, self.direction, self.direction_prochain_chemin)

        self.ancient_usagers = {}

        self.etat = GestionnaireVitesse.ACCELERATION


    def update(self):
        self.update_position_graphe()
        self.update_vitesse()
        self.update_position()
        
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
            # print("On a désactivé :", desactiver_courbes)
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
            print("Voici mes obstacles :\nVoitures ? ", voiture_obstacle, distance_voiture_obstacle, "\nNoeuds ? ", noeuds_obstacles_longueur)
            # si il y a des obstacles
            desactiver_courbes = [GestionnaireVitesse.ROULE,
                                    GestionnaireVitesse.ACCELERATION]
            self.gestionnaire_vitesse.desactiver_courbes(desactiver_courbes)
            # print("On a désactivé :", desactiver_courbes)

            if voiture_obstacle:
                # TODO : implementer un meilleur check vérifier l'id de la voiture (pour plus tard non essentiel)
                if not self.gestionnaire_vitesse.courbe_est_active(GestionnaireVitesse.SUIVRE_VOITURE):
                    self.gestionnaire_vitesse.genere_courbe_suivie_voiture(voiture_obstacle, distance_voiture_obstacle)
            else:
                self.gestionnaire_vitesse.desactiver_courbes([GestionnaireVitesse.SUIVRE_VOITURE])
                # print("On a désactivé :", [GestionnaireVitesse.SUIVRE_VOITURE])

            
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
                            # print("On a désactivé :", GestionnaireVitesse.ARRET)
                            print("Je vais bientôt passer un noeud, je m'enregistre")
                            noeud_obstacle.enregistrer_usager(self, self.direction, self.direction_prochain_chemin)
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
                # print("On a désactivé :", GestionnaireVitesse.ARRET)
    
    def id_noeud(self, noeud: Noeud):
        return self.gestionnaire_vitesse.NOEUD+noeud.nom
        
    def update_position_graphe(self):
        self.depasse_noeud()
        noeud_depasse: Noeud = self.changement_arete()
        # si on depasse un noeud
        if noeud_depasse:
            #print("Voitures dans l'arete actuelle : ",self.arete_actuelle.voitures)
            if noeud_depasse == self.noeud_depart:
                noeud_depasse.retirer_usager(self)
                chemin, distances = self.recherche_chemin(noeud_depasse)
                self.chemin: list[Noeud] = chemin
                self.distances = distances
            elif noeud_depasse == self.noeud_arrivee:
                # desactive la voiture
                # print("Dépassement noeud de fin")
                self.affiche = False
                self.arete_actuelle.voitures.remove(self)
                # print("Je viens de me retirer : ",self.arete_actuelle.voitures)

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
                # si le prochain noeud n'est pas une entré-sortie
                if type(self.chemin[1]) != EntreeSortie:
                    self.prochaine_arete = self.trouver_arete_entre_noeuds(self.chemin[1], self.chemin[2])
                    self.update_orientation_prochain_chemin()
                else:
                    self.prochaine_arete = None
                
                # update les variables de position sur le graphes
                self.arete_actuelle.push_voiture(self)
                self.ancienne_arete.voitures.remove(self)
                # print("Je viens de me retirer : ",self.arete_actuelle.voitures)


    def update_position(self):
        print("Avec l'état : ", self.etat)
        distance_parcourue, self.vitesse, self.etat = self.gestionnaire_vitesse.recuperer_position_etat()
        print("Nouvelle vitesse calculée : ", self.vitesse)

        distance_au_point = (self.arete_actuelle.position_arrivee - self.position).norme_manathan()
        reste_distance = 0
        
        if distance_parcourue >= distance_au_point:
            reste_distance = distance_parcourue - distance_au_point
            distance_parcourue = distance_au_point
        
        print("Distance totale parcourue", distance_parcourue, " Selon la prochaine arête ", reste_distance)
        print("J'update ma position : ", self.position)

        self.position = self.position + (self.direction * distance_parcourue) + (self.direction_prochain_chemin * reste_distance)
        

        print("Nouveau : ", self.position)
        print("Vitesse : " ,self.vitesse)
        print()
    
    def depasse_noeud(self):
        vecteur = (self.arete_actuelle.position_arrivee - self.position).unitaire()
        print("Vecteur :", vecteur, "Direction", self.direction)
        if vecteur != self.direction:
            print('dépassement noeud')
            self.update_orientation()

    def changement_arete(self):
        # selon de la voiture renvoie si elle a dépassé le prochain point sur le chemin
        # print("Je dépasse un noeud")
        prochain_noeud = self.chemin[1]
        taille_sup = prochain_noeud.size.x/2
        
        distance = (prochain_noeud.position - self.position).norme()
        if ((prochain_noeud.position - self.position).projection(self.direction).valeur_projetee() < 0 or self.direction != self.ancienne_direction) and distance > taille_sup:
            print("J'ai changé d'arête")
            return prochain_noeud
        
    def recherche_chemin(self, noeud_depart: Noeud):
        # print("Noeud depart", noeud_depart, "Noeud arrivee", self.noeud_arrivee)
        distances = {noeud_depart: 0}
        chemin = {noeud: float('inf') for noeud in self.graphe}
        noeud_parent = {noeud: None for noeud in self.graphe}
        chemin[noeud_depart] = 0
        queue = [(0, noeud_depart)]
        
        while queue:
            # print("queue ", queue)
            # print("Etat des lieux--------------\nDistances", distances, "\nChemin", chemin, "\nNoeud_parents", noeud_parent)
            dist, noeud = queue.pop(0)
            # print("\n\nOn examine le noeud", noeud, "avec une distance partant de", dist)
            if dist > chemin[noeud]:
                # print("Continue")
                continue
            
            for (noeud_arrivee, arete) in self.graphe[noeud]:
                # print("On peut atteindre", noeud_arrivee, "par", arete)
                new_distance = chemin[noeud] + arete.get_poids()
                
                if new_distance < chemin[noeud_arrivee]:
                    distances[noeud_arrivee] = new_distance
                    chemin[noeud_arrivee] = new_distance
                    queue.append((new_distance, noeud_arrivee))
                    # print("On peut atteindre", noeud_arrivee, " depuis le noeud, en minimisant la distance", noeud)
                    noeud_parent[noeud_arrivee] = noeud
            # print("new queue ", queue)
        # print("out")
        parcours = []
        # print(noeud_parent)
        noeud = self.noeud_arrivee
        while noeud != noeud_depart:
            parcours.append(noeud)
            noeud = noeud_parent[noeud]
        parcours.append(noeud_depart)
        
        return parcours[::-1], distances

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
        self.ancienne_direction = self.direction
        self.direction = self.direction_prochain_chemin

    def update_orientation_prochain_chemin(self):
        if self.prochaine_arete is not None:
            self.direction_prochain_chemin = (self.prochaine_arete.position_arrivee - self.prochaine_arete.position_depart).unitaire()
        else:
            self.direction_prochain_chemin = self.direction

    def trouver_arete_entre_noeuds(self, noeud_depart: Noeud, noeud_arrivee: Noeud) -> Arete:
        """
        Renvoie l'arête commune entre deux noeuds.
        Paramètres: noeud_depart (Noeud), noeud_arrivee (Noeud)
        Renvoie: arete (Arete)
        """
        for arete in noeud_depart.aretes:
            for arete2 in noeud_arrivee.aretes:
                if arete.is_equal(arete2, inverted=True):
                    return arete
        return None

    def distance_entite(self, position_entite: Vecteur2D):
        return (position_entite - self.position).norme_manathan()

    def trouver_voiture_sur_mon_chemin(self):
        # renvoie ou pas une voiture qui est dans ma distance de securite et sur mon chemin

        longueur = 0
        for i in range(len(self.chemin)-1):
            noeud_depart = self.chemin[i]
            noeud_arrivee = self.chemin[i+1]
            if i != 0:
                arete = self.trouver_arete_entre_noeuds(noeud_depart, noeud_arrivee)
                if longueur < self.distance_securite(self.vitesse):
                    if arete.a_des_voitures():
                        # print("Voitures dans l'arête suivante :", arete.voitures)
                        voiture_obstacle = arete.voitures[-1]
                        if voiture_obstacle != self:
                            longueur += (noeud_depart.position - voiture_obstacle.position).norme_manathan()
                            if longueur < self.distance_securite(self.vitesse):
                                # print("Voiture obstacle trouvée, dans les arêtes suivantes", voiture_obstacle, longueur)
                                return voiture_obstacle, longueur
                        elif len(arete.voitures)>1:
                            voiture_obstacle = arete.voitures[arete.voitures.index(self)-1]
                            if voiture_obstacle != self:
                                longueur += (noeud_depart.position - voiture_obstacle.position).norme_manathan()
                                if longueur < self.distance_securite(self.vitesse):
                                    # print("Voiture obstacle trouvée, dans les arêtes suivantes", voiture_obstacle, longueur)
                                    return voiture_obstacle, longueur
                        else:
                            longueur += arete.longueur
                    else:
                        longueur += arete.longueur
                else:
                    return None, None
            elif noeud_depart:
                arete = self.trouver_arete_entre_noeuds(noeud_depart, noeud_arrivee)
                if arete.a_des_voitures():
                    if arete.voitures[0] != self and len(arete.voitures) > 2:
                        voiture_obstacle = arete.voitures[arete.voitures.index(self)-1]
                        longueur += (self.position - voiture_obstacle.position).norme_manathan()
                        # print("Voiture obstacle trouvée, dans le noeud de départ", voiture_obstacle, longueur)
                        return voiture_obstacle, longueur
                else:
                    longueur += (self.position - noeud_arrivee.position).norme_manathan()
        return None, None

    def trouver_noeuds_sur_mon_chemin(self):
        # renvoie ou pas tous les noeuds qui sont dans ma distance de securite et sur mon chemin
        
        noeuds: list[Noeud] = []
        longueur = 0
        for i in range(len(self.chemin)-1):
            noeud_devant = self.chemin[i]
            if i == 0:
                longueur += (self.chemin[1].position - self.position).norme_manathan()
            else:
                if longueur < self.distance_securite(self.vitesse):
                    if noeud_devant.est_empruntee() and not noeud_devant.est_un_usager(self):
                        noeuds.append((noeud_devant, longueur))
                longueur += (self.chemin[i+1].position - self.chemin[i].position).norme_manathan()
        return noeuds

    def recuperer_position(self):
        angle = -math.atan2(self.direction.y, self.direction.x)
        x = self.position.get_x()+Noeud.size.get_x()/4*(math.sin(angle)+2)
        y = self.position.get_y()+Noeud.size.get_y()/4*(math.cos(angle)+2)
        return (Vecteur2D(x,y), angle)