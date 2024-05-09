import math
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
        

    def demarrage(self, agressivite: float, noeud_depart: Noeud, noeud_arrivee: Noeud, couleur: str, temps_simulation):
        """
        Initialise les paramètres nécessaires au démarrage d'un véhicule.

        Args:
            agressivite (float): Niveau d'agressivité du conducteur, compris entre 0 et 1.
            noeud_depart (Noeud): Noeud de départ du véhicule.
            noeud_arrivee (Noeud): Noeud d'arrivée du véhicule.
            couleur (str): Couleur du véhicule.

        Returns:
            None
        """

        self.temps_simulation = temps_simulation
        self.affiche = True

        self.noeud_depart: Noeud = noeud_depart
        self.noeud_arrivee: Noeud = noeud_arrivee
        
        self.vitesse = 0

        self.agressivite = agressivite # compris entre 0 et 1
        
        self.modulation_acceleration = 0.1 * agressivite

        self.acceleration = (2 + self.modulation_acceleration)
        self.deceleration = (2 + self.modulation_acceleration)

        self.deceleration_demarage = 0.6 #m/s^2 -> acceleration pour passer de 0 à 0.01 m/s en 1/60s
        self.acceleration_demarage = 0.6 #m/s^2 -> acceleration pour passer de 0 à 0.01 m/s en 1/60s

        #Variables primaires (ne changeront plus)
        self.couleur = couleur
        chemin, distances = self.recherche_chemin(noeud_depart)
        self.chemin: list[Noeud] = chemin
        self.distances = distances

        self.arete_actuelle: Arete = self.trouver_arete_entre_noeuds(self.chemin[0], self.chemin[1])

        if not isinstance(self.chemin[1],EntreeSortie):
            self.prochaine_arete: Arete = self.trouver_arete_entre_noeuds(self.chemin[1], self.chemin[2])
        else:
            self.prochaine_arete = None
        self.ancienne_arete: Arete = None

        self.direction = (self.arete_actuelle.position_arrivee - self.arete_actuelle.position_depart).unitaire()
        self.ancienne_direction = self.direction
        self.direction_prochain_chemin = Vecteur2D(0, 0)
        
        self.update_orientation_prochain_chemin()

        self.arete_actuelle.push_voiture(self)
        self.noeud_depart.enregistrer_usager(self, self.direction, self.direction_prochain_chemin)

        self.ancient_usagers = {}

        self.position = noeud_depart.position-(self.direction*(Noeud.size.get_x()/2+self.size.get_x()/2))
        
        self.gestionnaire_vitesse = GestionnaireVitesse(self)

        self.etat = GestionnaireVitesse.ACCELERATION



        self.distance_voiture_obstacle: float = 0
        self.voiture_obstacle: Voiture = None


    def update(self, temps_simulation: float):
        """
        Met à jour l'orientation de la voiture, son appartenance aux objets de la map, la vitesse et sa position.

        Returns:
            None
        """
        self.temps_simulation = temps_simulation
        self.update_position_graphe()
        self.update_vitesse()
        self.update_position()
        
    def update_vitesse(self):
        """
        Met à jour les courbes de vitesse suivies du véhicule en fonction des obstacles détectés sur sa trajectoire.

        Returns:
            None
        """
        # identification des obstacles dans ma zone de sécurité
        voiture_obstacle: Voiture = None
        distance_voiture_obstacle: float = None

        
        # voiture_obstacle, distance_voiture_obstacle = self.trouver_voiture_sur_mon_chemin()
        self.distance_voiture_obstacle = distance_voiture_obstacle
        self.voiture_obstacle = voiture_obstacle
        noeuds_obstacles_longueur: list[tuple[Noeud, float]] = self.trouver_noeuds_sur_mon_chemin()

        # Si il n'y pas d'obstacles
        if not voiture_obstacle and not noeuds_obstacles_longueur:
             
            #Je desactive toutes les autres courbes
            desactiver_courbes = [GestionnaireVitesse.FREINAGE,
                                    GestionnaireVitesse.SUIVRE_VOITURE,
                                    GestionnaireVitesse.ARRET]
            self.gestionnaire_vitesse.desactiver_courbes(desactiver_courbes)
            # si on est pas à la vitesse max
            
            if self.vitesse < self.arete_actuelle.vitesse_max:
                print("Je suis en train d'accélérer")
                if not self.gestionnaire_vitesse.courbe_est_active(self.gestionnaire_vitesse.ACCELERATION):
                    self.gestionnaire_vitesse.genere_courbe_acceleration_arete(self.arete_actuelle)
                    self.gestionnaire_vitesse.desactiver_courbes([GestionnaireVitesse.ROULE, GestionnaireVitesse.FREINAGE])
            elif self.vitesse == self.arete_actuelle.vitesse_max:
                print("Je suis en train de rouler")
                if not self.gestionnaire_vitesse.courbe_est_active(self.gestionnaire_vitesse.ROULE):
                    self.gestionnaire_vitesse.genere_courbe_roule_arete(self.arete_actuelle)
                    self.gestionnaire_vitesse.desactiver_courbes([GestionnaireVitesse.ACCELERATION, GestionnaireVitesse.FREINAGE])
            else:
                print("Je suis en train de freiner")
                if not self.gestionnaire_vitesse.courbe_est_active(self.gestionnaire_vitesse.FREINAGE):
                    self.gestionnaire_vitesse.genere_courbe_freinage_arete(self.arete_actuelle)
                    self.gestionnaire_vitesse.desactiver_courbes([GestionnaireVitesse.ACCELERATION, GestionnaireVitesse.ROULE])
     
        else:
            print("Voici mes obstacles :\nVoitures ? ", voiture_obstacle, distance_voiture_obstacle, "\nNoeuds ? ", noeuds_obstacles_longueur)
            # si il y a des obstacles
            desactiver_courbes = [GestionnaireVitesse.ROULE,
                                    GestionnaireVitesse.ACCELERATION]
            self.gestionnaire_vitesse.desactiver_courbes(desactiver_courbes)

            if voiture_obstacle:
                # TODO : implementer un meilleur check vérifier l'id de la voiture (pour plus tard non essentiel)
                if not self.gestionnaire_vitesse.courbe_est_active(GestionnaireVitesse.SUIVRE_VOITURE):
                    self.gestionnaire_vitesse.genere_courbe_suivie_voiture(voiture_obstacle, distance_voiture_obstacle)
            else:
                self.gestionnaire_vitesse.desactiver_courbes([GestionnaireVitesse.SUIVRE_VOITURE])

            
            for i in range(len(noeuds_obstacles_longueur)):
                print("Noeud obstacle", i)
                # si c'est le premier noeud et que c'est une intersection
                noeud_obstacle = noeuds_obstacles_longueur[i][0]
                distance_noeud_obstacle = noeuds_obstacles_longueur[i][1]
                
                if i == 0:
                    print("Je suis dans une intersection")
                    # si je suis dans la zone de ping
                    print("Distance noeud obstacle", self.distance_entite(noeud_obstacle.position), "Distance securite", noeud_obstacle.distance_securite)
                    if self.distance_entite(noeud_obstacle.position) < noeud_obstacle.distance_securite and not noeud_obstacle.est_un_usager(self):
                        
                        # je demande si je peux passer
                        # ceci est optimise pour ne pas faire de calcul inutile
                        est_empruntee = noeud_obstacle.est_empruntee()
                        usagers_differents = self.ancient_usagers != noeud_obstacle.get_usagers()
                        voie_est_libre = usagers_differents and noeud_obstacle.voie_est_libre(self)
                        print("Est empruntee", est_empruntee, "Voie est libre", voie_est_libre, "Usagers differents", usagers_differents)
                        #voie pas empruntée ou voie libre
                        if (not est_empruntee) or (voie_est_libre):
                        
                            self.gestionnaire_vitesse.desactiver_courbes([GestionnaireVitesse.ARRET])
                            print("Je vais bientôt passer un noeud, je m'enregistre comme usager")
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
                            print("La voix est occupée")
                            if not self.gestionnaire_vitesse.courbe_est_active(self.gestionnaire_vitesse.ARRET+self.id_noeud(noeud_obstacle)):
                                self.gestionnaire_vitesse.genere_courbe_arret_noeud(distance_noeud_obstacle, noeud_obstacle.nom)
                            self.ancient_usagers = noeud_obstacle.get_usagers().copy()
                    
                    else:
                        print("Je ne suis pas dans la zone de ping, j'adapte mon allure")
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
                    print("Autre noeud de type intersection")
                    # si je suis dans la zone de ping et que ma distance d'arret est superieure ou egale à ma distance de sécurité
                    print("Distance noeud obstacle", distance_noeud_obstacle, "Distance securite", noeud_obstacle.distance_securite, "Distance arret", self.distance_arret())
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
            if len(noeuds_obstacles_longueur) == 0:
                print("Aucun obstacle noeud")
                desactiver_courbes = [GestionnaireVitesse.FREINAGE,
                                    GestionnaireVitesse.ARRET]
                self.gestionnaire_vitesse.desactiver_courbes(desactiver_courbes)
    
    def id_noeud(self, noeud: Noeud):
        """
        Génère le nom unique d'une courbe pour un noeud donné.

        Args:
            noeud (Noeud): Le noeud pour lequel générer le nom.

        Returns:
            str: Le nom unique de la courbe associée au noeud donné
        """
        return self.gestionnaire_vitesse.NOEUD+noeud.nom
        
    def update_position_graphe(self):
        """
        Ensemble des fonctions à appeler pour mettre à jour l'orientation, le chemin et les arêtes.

        Returns:
            None
        """
        self.depasse_noeud()
        self.usage_noeuds()
        


    def update_position(self):
        """
        Met à jour la position du véhicule en fonction de sa vitesse et de son état actuel.

        Returns:
            None
        """
        self.vitesse, distance_parcourue, self.etat = self.gestionnaire_vitesse.recuperer_position_etat()

        distance_au_point = (self.arete_actuelle.position_arrivee - self.position).norme_manathan()
        reste_distance = 0

        print("vitesse", self.vitesse, "distance parcourue", distance_parcourue, self.etat)
        
        if distance_parcourue >= distance_au_point:
            reste_distance = distance_parcourue - distance_au_point
            distance_parcourue = distance_au_point

        self.position = self.position + (self.direction * distance_parcourue) + (self.direction_prochain_chemin * reste_distance)
    
    def depasse_noeud(self):
        """
        Détermine si le véhicule dépasse un noeud sur son chemin et met à jour toutes les arêtes en fonction

        Returns:
            None
        """
        if len(self.chemin) > 1:
            noeud_a_depasser = self.chemin[1]
        else:
            return
        decalage = self.direction.abs()*(-self.direction.valeur_projetee()*self.direction_prochain_chemin.valeur_projetee())
        decalage = 0
        vecteur = (self.chemin[1].position+ decalage*Noeud.size.get_x()/4 - self.position).unitaire()
        if vecteur != self.direction:
            self.update_orientation()
            
            chemin, distances = self.recherche_chemin(noeud_a_depasser)
            self.chemin: list[Noeud] = chemin
            self.distances = distances

            if noeud_a_depasser != self.noeud_depart and chemin[0] != self.noeud_arrivee:
                self.ancienne_arete = self.arete_actuelle
                self.arete_actuelle = self.trouver_arete_entre_noeuds(self.chemin[0], self.chemin[1])
                if type(self.chemin[1]) != EntreeSortie:
                        self.prochaine_arete = self.trouver_arete_entre_noeuds(self.chemin[1], self.chemin[2])
                        self.update_orientation_prochain_chemin()
                else:
                    self.prochaine_arete = None

                self.arete_actuelle.push_voiture(self)
                self.ancienne_arete.voitures.remove(self)

    def usage_noeuds(self):
        """
        Vérifie si le véhicule cesse d'utiliser un noeud sur son chemin et le retire en conséquence.

        Returns:
            Noeud: Le noeud retiré par le véhicule, s'il y en a un.
        """
        noeud_a_seloigner = self.chemin[0]
        taille_sup = noeud_a_seloigner.size.x/2+self.size.x/2
        distance = (noeud_a_seloigner.position - self.position).norme_manathan()
        if distance > taille_sup and (noeud_a_seloigner.position - self.position).projection(self.direction).valeur_projetee() < 0:
            if noeud_a_seloigner == self.noeud_arrivee:
                self.affiche = False
                self.arete_actuelle.voitures.remove(self)
            noeud_a_seloigner.retirer_usager(self)
            return noeud_a_seloigner
        
    def recherche_chemin(self, noeud_depart: Noeud):
        """
        Recherche le chemin optimal entre un noeud de départ et le noeud d'arrivée du véhicule.

        Args:
            noeud_depart (Noeud): Le noeud de départ.

        Returns:
            tuple: Une paire contenant le chemin optimal (une liste de noeuds) et les distances réelles associées.
        """
        # print("Noeud depart", noeud_depart, "Noeud arrivee", self.noeud_arrivee)
        if noeud_depart == self.noeud_arrivee:
            return [noeud_depart], {noeud_depart: 0}
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
        """
        Calcule la distance de sécurité en fonction d'une vitesse.

        Args:
            vitesse (float): Une vitesse.

        Returns:
            float: La distance de sécurité.
        """
        return self.distance_deceleration(vitesse, 0) + self.distance_marge_securite

    def distance_deceleration(self, vitesse_initiale, vitesse_finale) -> float:
        """
        Calcule la distance de décélération nécessaire pour passer d'une vitesse initiale à une vitesse finale.

        Args:
            vitesse_initiale (float): La vitesse initiale du véhicule en m/s.
            vitesse_finale (float): La vitesse finale du véhicule en m/s.

        Returns:
            float: La distance de décélération.
        """
        temps_deceleration = abs(vitesse_initiale/3.6 - vitesse_finale/3.6) / self.deceleration
        distance = 1/2 * self.deceleration * temps_deceleration**2 + vitesse_initiale * temps_deceleration
        return distance
    
    def distance_arret(self):
        """
        Calcule la distance d'arrêt en fonction de la vitesse actuelle.

        Returns:
            float: La distance d'arrêt.
        """
        return self.distance_deceleration(self.vitesse, 0) + self.distance_marge_securite
        
    def distance_acceleration(self, vitesse_initiale, vitesse_finale) -> float:
        """
        Calcule la distance d'accélération nécessaire pour passer d'une vitesse initiale à une vitesse finale.

        Args:
            vitesse_initiale (float): La vitesse initiale du véhicule en m/s.
            vitesse_finale (float): La vitesse finale du véhicule en m/s.

        Returns:
            float: La distance de décélération.
        """
        temps_acceleration = abs(vitesse_finale/3.6 - vitesse_initiale/3.6) / self.acceleration
        distance = 1/2 * self.acceleration * temps_acceleration**2 + vitesse_initiale * temps_acceleration
        return distance

    def intention(self):
        """
        Retourne les intentions de déplacement du véhicule.

        Returns:
            tuple: Une paire contenant la direction actuelle et la direction vers la prochaine destination.
        """
        return self.direction, self.direction_prochain_chemin
            
    def update_orientation(self):
        """
        Met à jour les directions en partant du principe qu'on vient de changer d'arête

        Returns:
            None
        """
        self.ancienne_direction = self.direction
        self.direction = self.direction_prochain_chemin

    def update_orientation_prochain_chemin(self):
        """
        Cacule la direction de l'arête suivante

        Returns:
            None
        """
        if self.prochaine_arete is not None:
            self.direction_prochain_chemin = (self.prochaine_arete.position_arrivee - self.prochaine_arete.position_depart).unitaire()
        else:
            self.direction_prochain_chemin = self.direction

    def trouver_arete_entre_noeuds(self, noeud_depart: Noeud, noeud_arrivee: Noeud) -> Arete:
        """
        Trouve l'arête reliant deux noeuds donnés.

        Args:
            noeud_depart (Noeud): Le noeud de départ.
            noeud_arrivee (Noeud): Le noeud d'arrivée.

        Returns:
            Arete: L'arête reliant les deux noeuds, s'il en existe une. Sinon, retourne None.
        """
        for arete in noeud_depart.aretes:
            for arete2 in noeud_arrivee.aretes:
                if arete.is_equal(arete2, inverted=True):
                    return arete
        return None

    def distance_entite(self, position_entite: Vecteur2D):
        """
        Calcule la distance entre la position actuelle du véhicule et une entité donnée.

        Args:
            position_entite (Vecteur2D): La position de l'entité.

        Returns:
            float: La distance entre le véhicule et l'entité.
        """
        return (position_entite - self.position).norme_manathan()

    def trouver_voiture_sur_mon_chemin(self):
        """
        Trouve une voiture sur le chemin du véhicule qui se trouve dans sa zone de sécurité.

        Returns:
            tuple: Une paire contenant la voiture obstacle et la distance jusqu'à elle, si elle existe. Sinon, une paire de None.
        """
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
            else:
                arete = self.arete_actuelle
                if arete.a_des_voitures():
                    myposition = arete.voitures.index(self)
                    if myposition>0:
                        voiture_obstacle = arete.voitures[arete.voitures.index(self)-1]
                        longueur += (self.position - voiture_obstacle.position).norme_manathan()
                        # print("Voiture obstacle trouvée, dans le noeud de départ", voiture_obstacle, longueur)
                        return voiture_obstacle, longueur
                else:
                    longueur += (self.position - noeud_arrivee.position).norme_manathan()
        return None, None

    def trouver_noeuds_sur_mon_chemin(self):
        """
        Trouve tous les noeuds sur le chemin du véhicule qui se trouvent dans sa zone de sécurité.

        Returns:
            list: Une liste contenant des tuples de noeuds et de distances jusqu'à eux.
        """
        # renvoie ou pas tous les noeuds qui sont dans ma distance de securite et sur mon chemin
        
        noeuds: list[Noeud] = []
        longueur = 0
        for i in range(len(self.chemin)-1):
            print("Trouver les noeuds sur mon chemin", i)
            noeud_devant = self.chemin[i]
            if i == 0:
                longueur += (self.chemin[1].position - self.position).norme_manathan()
            else:
                print("Distance securite", self.distance_securite(self.vitesse), longueur)
                if isinstance(noeud_devant,(Intersection_X, Intersection_T)):
                    if longueur < self.distance_securite(self.vitesse):
                        print("Je suis dans la distance de securite")
                        if noeud_devant.est_empruntee() and not noeud_devant.est_un_usager(self):
                            print("J'append le noeud")
                            noeuds.append((noeud_devant, longueur))
                longueur += (self.chemin[i+1].position - self.chemin[i].position).norme_manathan()
        return noeuds

    def recuperer_position(self):
        """
        Calcule une position selon l'orientation pour placer la voiture sur la droite ou la gauche de la route.

        Returns:
            tuple: Un tuple contenant la position (Vecteur2D) ajustée et l'angle (float) du véhicule.
        """
        angle = -math.atan2(self.direction.y, self.direction.x)
        x = self.position.get_x()+Noeud.size.get_x()/4*(math.sin(angle)+2)
        y = self.position.get_y()+Noeud.size.get_y()/4*(math.cos(angle)+2)
        return (Vecteur2D(x,y), angle)