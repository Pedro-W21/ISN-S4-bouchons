import math
from simulation.arete import Arete
from utils.vecteur_2d import Vecteur2D
from simulation.noeud import Noeud, Virage, Intersection_T, Intersection_X, EntreeSortie
from simulation.gestionnaire_vitesse import GestionnaireVitesse

class Voiture:

    size = Vecteur2D(2, 1.75) # m [longueur, largeur]
    
    distance_marge_securite = (size.x + size.y)*1.5
    marge_noeud = (size.x+Noeud.size.get_x())/2
    def __init__(self, graphe: dict):
        self.affiche = False
        self.graphe = graphe 

    def demarrage(self, id, agressivite: float, noeud_depart: Noeud, noeud_arrivee: Noeud, couleur: str, temps_simulation):
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
        self.id = id

        self.immobile = 0
        self.temps_simulation = temps_simulation
        self.temps_demarage = temps_simulation
        self.affiche = True

        self.noeud_depart: Noeud = noeud_depart
        self.noeud_arrivee: Noeud = noeud_arrivee
        
        self.vitesse = 0
        self.reste_distance = 0
        
        self.agressivite = agressivite # compris entre 0 et 1
        
        self.modulation_acceleration = 0.1 * agressivite

        self.acceleration = (3 + self.modulation_acceleration)
        self.deceleration = (3 + self.modulation_acceleration)

        self.deceleration_demarage = 0.6 #m/s^2 -> acceleration pour passer de 0 à 0.01 m/s en 1/60s
        self.acceleration_demarage = 0.6 #m/s^2 -> acceleration pour passer de 0 à 0.01 m/s en 1/60s

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

        self.position = noeud_depart.position-(self.direction*(self.marge_noeud))
        
        self.gestionnaire_vitesse = GestionnaireVitesse(self)

        self.etat = GestionnaireVitesse.ACCELERATION

        self.distance_voiture_obstacle: float = 0
        self.voiture_obstacle: Voiture = None
        self.noeuds_obstacles_longueur = []

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

        voiture_obstacle, distance_voiture_obstacle = self.trouver_voiture_sur_mon_chemin()
        self.distance_voiture_obstacle = distance_voiture_obstacle
        self.voiture_obstacle = voiture_obstacle

        noeuds_obstacles_longueur: list[tuple[Noeud, float]] = self.trouver_noeuds_sur_mon_chemin()

        self.noeuds_obstacles_longueur = noeuds_obstacles_longueur

        if not noeuds_obstacles_longueur:
            desactiver_courbes = [GestionnaireVitesse.FREINAGE,GestionnaireVitesse.ARRET]
            self.gestionnaire_vitesse.desactiver_courbes(desactiver_courbes)
            if voiture_obstacle:
                self.generation_courbe(voiture_obstacle)
            else:
                self.generation_courbe(self.arete_actuelle)
                self.gestionnaire_vitesse.desactiver_courbes([GestionnaireVitesse.SUIVRE_VOITURE]) 
        else: 
            desactiver_courbes = [GestionnaireVitesse.ROULE,
                                    GestionnaireVitesse.ACCELERATION]
            self.gestionnaire_vitesse.desactiver_courbes(desactiver_courbes)
            
            for i in range(len(noeuds_obstacles_longueur)):
                noeud_obstacle = noeuds_obstacles_longueur[i][0]
                distance_noeud_obstacle = noeuds_obstacles_longueur[i][1]
                if i == 0:
                    if not noeud_obstacle.est_un_usager(self) and self.distance_securite(noeud_obstacle.vitesse_max, self.marge_noeud*1.1) > distance_noeud_obstacle:
                        # La voiture demande si elle peut passer
                        est_empruntee = noeud_obstacle.est_empruntee()
                        usagers_differents = self.ancient_usagers != noeud_obstacle.get_usagers()
                        voie_est_libre = usagers_differents and noeud_obstacle.voie_est_libre(self)
                        if (not est_empruntee) or (voie_est_libre):
                            self.gestionnaire_vitesse.desactiver_courbes([GestionnaireVitesse.ARRET, GestionnaireVitesse.ROULE])
                            noeud_obstacle.enregistrer_usager(self, self.direction, self.direction_prochain_chemin)
                            self.ancient_usagers = {}

                            self.generation_courbe(noeud_obstacle)
                        else:
                            self.generation_courbe(noeud_obstacle, arret=True)
                            self.ancient_usagers = noeud_obstacle.get_usagers().copy()
                    else:
                        self.generation_courbe(noeud_obstacle)

                elif distance_noeud_obstacle < self.distance_securite(noeud_obstacle.vitesse_max, self.marge_noeud):
                        self.generation_courbe(noeud_obstacle)

            if voiture_obstacle:
                noeud_obstacle = noeuds_obstacles_longueur[i][0]
                distance_noeud_obstacle = noeuds_obstacles_longueur[i][1]
                if not self.gestionnaire_vitesse.courbe_est_active(self.gestionnaire_vitesse.ARRET+self.id_noeud(noeud_obstacle)) or distance_voiture_obstacle < distance_noeud_obstacle:
                    self.generation_courbe(voiture_obstacle)
            else:
                self.gestionnaire_vitesse.desactiver_courbes([GestionnaireVitesse.SUIVRE_VOITURE]) 

    def generation_courbe(self, objet, arret=False):
        """
        Génère une courbe de vitesse en fonction de l'objet et du besoin ciblé.

        Args:
            objet: L'objet (Arete ou Noeud) pour lequel générer la courbe de vitesse.
            arret (bool, optional): Indique si l'arrêt est en cours. Par défaut False.

        Returns:
            None
        """
        if arret:
            if not self.gestionnaire_vitesse.courbe_est_active(self.gestionnaire_vitesse.ARRET+self.id_noeud(objet)):
                self.gestionnaire_vitesse.genere_courbe_arret_noeud(objet.nom)
        elif isinstance(objet, Arete):
            if self.vitesse < objet.vitesse_max:
                if not self.gestionnaire_vitesse.courbe_est_active(self.gestionnaire_vitesse.ACCELERATION):
                    self.gestionnaire_vitesse.genere_courbe_acceleration_arete(objet)
                    self.gestionnaire_vitesse.desactiver_courbes([GestionnaireVitesse.ROULE, GestionnaireVitesse.FREINAGE])
            elif self.vitesse == objet.vitesse_max:
                if not self.gestionnaire_vitesse.courbe_est_active(self.gestionnaire_vitesse.ROULE):
                    self.gestionnaire_vitesse.genere_courbe_roule_arete(objet)
                    self.gestionnaire_vitesse.desactiver_courbes([GestionnaireVitesse.ACCELERATION, GestionnaireVitesse.FREINAGE])
            elif not self.gestionnaire_vitesse.courbe_est_active(self.gestionnaire_vitesse.FREINAGE):
                    self.gestionnaire_vitesse.genere_courbe_freinage_arete(objet)
                    self.gestionnaire_vitesse.desactiver_courbes([GestionnaireVitesse.ACCELERATION, GestionnaireVitesse.ROULE])
        elif isinstance(objet, Noeud):
            if self.vitesse == 0:
                if not self.gestionnaire_vitesse.courbe_est_active(self.gestionnaire_vitesse.ACCELERATION):
                    self.gestionnaire_vitesse.genere_courbe_acceleration_arete(self.prochaine_arete)
                    self.gestionnaire_vitesse.desactiver_courbes([GestionnaireVitesse.ROULE, GestionnaireVitesse.FREINAGE])
            if self.vitesse < objet.vitesse_max:
                if not self.gestionnaire_vitesse.courbe_est_active(self.gestionnaire_vitesse.ACCELERATION+self.id_noeud(objet)):
                        self.gestionnaire_vitesse.genere_courbe_acceleration_noeud(objet)
            elif self.vitesse == objet.vitesse_max:
                if not self.gestionnaire_vitesse.courbe_est_active(self.gestionnaire_vitesse.ROULE+self.id_noeud(objet)):
                    self.gestionnaire_vitesse.genere_courbe_roule_noeud(objet)
            elif not self.gestionnaire_vitesse.courbe_est_active(self.gestionnaire_vitesse.FREINAGE+self.id_noeud(objet)):
                    self.gestionnaire_vitesse.genere_courbe_freinage_noeud(objet)
        elif isinstance(objet, Voiture):
            desactiver_courbes = [GestionnaireVitesse.ROULE,GestionnaireVitesse.ACCELERATION]
            if not self.gestionnaire_vitesse.courbe_est_active(self.id_voiture(objet)):
                desactiver_courbes.append(GestionnaireVitesse.SUIVRE_VOITURE)
                self.gestionnaire_vitesse.desactiver_courbes(desactiver_courbes) 
                self.gestionnaire_vitesse.genere_courbe_suivie_voiture(objet)
            else:
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
    
    def id_voiture(self, voiture: Noeud):
        """
        Génère le nom unique d'une courbe pour un noeud donné.

        Args:
            noeud (Noeud): Le noeud pour lequel générer le nom.

        Returns:
            str: Le nom unique de la courbe associée au noeud donné
        """
        return self.gestionnaire_vitesse.SUIVRE_VOITURE+str(voiture.id)+voiture.etat
        
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
        Gérer les cas d'immobilité du véhicule pour différents cas afin de libérer une intersection ou un bouchon

        Returns:
            None
        """
        self.vitesse, distance_parcourue, self.etat = self.gestionnaire_vitesse.recuperer_position_etat()
        if self.vitesse == 0:
            self.immobile += 1
            distance_parcourue = 0
            noeud_obstacle = self.chemin[1]
            distance_noeud_obstacle = (noeud_obstacle.position - self.position).norme_manathan()
            if self.etat.startswith(self.gestionnaire_vitesse.SUIVRE_VOITURE) and distance_noeud_obstacle > self.marge_noeud:
                noeud_obstacle.retirer_usager(self)
        self.position += (self.direction) * distance_parcourue
        if self.vitesse != 0:
            self.immobile = 0
        #Fixé de manière indicative pour 25 secondes d'immobilité maximum
        if self.immobile > 750:
            self.affiche = False
            self.arete_actuelle.voitures.remove(self)
            self.chemin[0].retirer_usager(self)
            if len(self.chemin) > 1:
                self.chemin[1].retirer_usager(self)
    
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
        if self.depassement_noeud(noeud_a_depasser):
            self.ancienne_direction = self.direction
            
            chemin, distances = self.recherche_chemin(noeud_a_depasser)
            self.chemin: list[Noeud] = chemin
            self.distances = distances

            if noeud_a_depasser != self.noeud_depart and chemin[0] != self.noeud_arrivee:
                self.ancienne_arete = self.arete_actuelle
                self.arete_actuelle = self.trouver_arete_entre_noeuds(self.chemin[0], self.chemin[1])
                self.update_orientation()
                if self.vitesse == self.arete_actuelle.vitesse_max:
                    self.gestionnaire_vitesse.desactiver_courbes([GestionnaireVitesse.ROULE])
                    self.gestionnaire_vitesse.genere_courbe_roule_arete(self.arete_actuelle) 
                if type(self.chemin[1]) != EntreeSortie:
                        self.prochaine_arete = self.trouver_arete_entre_noeuds(self.chemin[1], self.chemin[2])
                        self.update_orientation_prochain_chemin()
                else:
                    self.prochaine_arete = None
                self.arete_actuelle.push_voiture(self)
                self.ancienne_arete.voitures.remove(self)

    def depassement_noeud(self, noeud_a_depasser):
        """
        Vérifie si l'objet courant a dépassé un nœud spécifié, ajuste sa position en conséquence 
        et renvoie le signal approprié pour mettre à jour les paramètres de la voiture.

        Parameters:
        noeud_a_depasser (Noeud): Le nœud que l'objet courant doit dépasser.

        Returns:
        bool: True si l'objet courant a dépassé le nœud et sa position a été ajustée, sinon False.
        """
        marge_sup_x = (self.size.x/2+(Noeud.size.x/2-self.size.x)/2)*self.direction_prochain_chemin.y*self.direction.x
        marge_sup_y = (self.size.x/2+(Noeud.size.x/2-self.size.x)/2)*self.direction_prochain_chemin.x*self.direction.y
        if self.direction == Vecteur2D(1, 0):
            if self.position.x >= noeud_a_depasser.position.x-marge_sup_x:
                self.position.x = noeud_a_depasser.position.x
                return True
        elif self.direction == Vecteur2D(-1, 0):
            if self.position.x <= noeud_a_depasser.position.x+marge_sup_x:
                self.position.x = noeud_a_depasser.position.x
                return True
        elif self.direction == Vecteur2D(0, 1):
            if self.position.y >= noeud_a_depasser.position.y+marge_sup_y:
                self.position.y = noeud_a_depasser.position.y
                return True
        elif self.direction == Vecteur2D(0, -1):
            if self.position.y <= noeud_a_depasser.position.y-marge_sup_y:
                self.position.y = noeud_a_depasser.position.y
                return True
        return False

    def usage_noeuds(self):
        """
        Vérifie si le véhicule cesse d'utiliser un noeud sur son chemin et le retire en conséquence.

        Returns:
            Noeud: Le noeud retiré par le véhicule, s'il y en a un.
        """
        noeud_a_seloigner = self.chemin[0]
        taille_sup = self.marge_noeud
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
        if noeud_depart == self.noeud_arrivee:
            return [noeud_depart], {noeud_depart: 0}
        distances = {noeud_depart: 0}
        chemin = {noeud: float('inf') for noeud in self.graphe}
        noeud_parent = {noeud: None for noeud in self.graphe}
        chemin[noeud_depart] = 0
        queue = [(0, noeud_depart)]
        
        while queue:
            dist, noeud = queue.pop(0)
            if dist > chemin[noeud]:
                continue
            
            for (noeud_arrivee, arete) in self.graphe[noeud]:
                new_distance = chemin[noeud] + arete.get_poids()
                
                if new_distance < chemin[noeud_arrivee]:
                    distances[noeud_arrivee] = new_distance
                    chemin[noeud_arrivee] = new_distance
                    queue.append((new_distance, noeud_arrivee))
                    noeud_parent[noeud_arrivee] = noeud
        parcours = []
        noeud = self.noeud_arrivee
        while noeud != noeud_depart:
            parcours.append(noeud)
            noeud = noeud_parent[noeud]
        parcours.append(noeud_depart)
        return parcours[::-1], distances

    def distance_securite(self, vitesse: float, marge:float) -> float:
        """
        Calcule la distance de sécurité en fonction d'une vitesse.

        Args:
            vitesse (float): Une vitesse.

        Returns:
            float: La distance de sécurité.
        """
        return self.distance_deceleration(vitesse, 0) + marge
    
    def temps_mouvement(self, vitesse_initiale, vitesse_finale, acceleration) -> float:
        """
        Calcule le temps nécessaire pour passer d'une vitesse initiale à une vitesse finale avec une accélération constante.

        Args:
            vitesse_initiale (float): La vitesse initiale.
            vitesse_finale (float): La vitesse finale.
            acceleration (float): L'accélération utilisée pour le mouvement.

        Returns:
            float: Le temps nécessaire pour effectuer le mouvement.
        """
        return abs(vitesse_initiale - vitesse_finale) / acceleration
    
    def temps_mouvement_deceleration(self, vitesse_initiale, vitesse_finale) -> float:
        """
        Calcule le temps nécessaire pour passer d'une vitesse initiale à une vitesse finale en décélération.

        Args:
            vitesse_initiale (float): La vitesse initiale.
            vitesse_finale (float): La vitesse finale.

        Returns:
            float: Le temps nécessaire pour effectuer le mouvement en décélération.
        """
        return self.temps_mouvement(vitesse_initiale, vitesse_finale, self.deceleration)
    
    def distance_deceleration(self, vitesse_initiale, vitesse_finale) -> float:
        """
        Calcule la distance de décélération nécessaire pour passer d'une vitesse initiale à une vitesse finale.

        Args:
            vitesse_initiale (float): La vitesse initiale du véhicule en m/s.
            vitesse_finale (float): La vitesse finale du véhicule en m/s.

        Returns:
            float: La distance de décélération.
        """
        temps_deceleration = self.temps_mouvement_deceleration(vitesse_initiale, vitesse_finale)
        distance = 1/2 * self.deceleration * temps_deceleration**2 + vitesse_initiale * temps_deceleration
        return distance
    
    def update_orientation(self):
        """
        Met à jour les directions en partant du principe qu'on vient de changer d'arête

        Returns:
            None
        """
        self.direction = (self.arete_actuelle.position_arrivee - self.arete_actuelle.position_depart).unitaire()

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

    def trouver_voiture_sur_mon_chemin(self):
        """
        Trouve une voiture sur le chemin du véhicule qui se trouve dans sa zone de sécurité.

        Returns:
            tuple: Une paire contenant la voiture obstacle et la distance jusqu'à elle, si elle existe. Sinon, une paire de None.
        """
        longueur = 0
        dist_secu = self.distance_securite(self.vitesse,self.distance_marge_securite)
        for i in range(len(self.chemin)-1):
            noeud_depart = self.chemin[i]
            noeud_arrivee = self.chemin[i+1]
            if i != 0:
                arete = self.trouver_arete_entre_noeuds(noeud_depart, noeud_arrivee)
                if longueur < dist_secu:
                    if arete.a_des_voitures():
                        voiture_obstacle = arete.voitures[-1]
                        if voiture_obstacle != self:
                            longueur += (noeud_depart.position - voiture_obstacle.position).norme_manathan()
                            if longueur < dist_secu:
                                return voiture_obstacle, longueur
                        elif len(arete.voitures)>1:
                            voiture_obstacle = arete.voitures[arete.voitures.index(self)-1]
                            if voiture_obstacle != self:
                                longueur += (noeud_depart.position - voiture_obstacle.position).norme_manathan()
                                if longueur < dist_secu:
                                    return voiture_obstacle, longueur
                    longueur += arete.longueur-0.5*Noeud.size.get_x()
                else:
                    return None, None
            else:
                arete = self.arete_actuelle
                if arete.a_des_voitures():
                    myposition = arete.voitures.index(self)
                    if myposition>0:
                        voiture_obstacle = arete.voitures[myposition-1]
                        distance_a_voiture = (self.position - voiture_obstacle.position).norme_manathan()
                        if distance_a_voiture < dist_secu:
                            return voiture_obstacle, distance_a_voiture
                longueur += (self.position - noeud_arrivee.position).norme_manathan()-0.5*Noeud.size.get_x()
        return None, None

    def trouver_noeuds_sur_mon_chemin(self):
        """
        Trouve tous les noeuds sur le chemin du véhicule qui se trouvent dans sa zone de sécurité.

        Returns:
            list: Une liste contenant des tuples de noeuds et de distances jusqu'à eux.
        """

        noeuds: list[Noeud] = []
        longueur = 0
        for i in range(len(self.chemin)-1):
            noeud_devant = self.chemin[i]
            if i == 0:
                longueur += (self.chemin[1].position - self.position).norme_manathan()
            else:
                if isinstance(noeud_devant,(Intersection_X, Intersection_T)):
                    if longueur <= self.distance_securite(self.vitesse, self.marge_noeud*1.1):
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