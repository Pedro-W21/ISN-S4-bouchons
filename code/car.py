import random
import math
from arrete import Arrete
from vecteur_2d import Vecteur2D
from noeud import Noeud

"""
On fait 
voiture = Voiture(...1)
voiture.__init__(...2)
ou 
voiture = Voiture(...1)
voiture.reassign(...2)

"""


class Voiture:

    ROULE = "ROULE"
    RALENTI = "RALENTI"
    ARRETEE = "ARRETEE"
    FREINE = "FREINE"


    def __init__(self, id, position, vitesse, kp, dist_securite):
    def __init__(self, id, position, objectif, vitesse, agressivite,size, road_size):
        #Implémentation données pour affichage
        self.id = id
        self.position = Vecteur2D(position[0], position[1]) #[x,y]
        self.objectif = Vecteur2D(objectif[0], objectif[1])
        #Implémentation PID
        self.vitesse = vitesse
        self.agressivite = agressivite
        self.size = size #longueur/largeur
        #Variables primaires (ne changeront plus)
        self.generate_color
        self.calculer_vitesse_max
        self.distance_securite = dist_securite
        self.arrete_actuelle: Arrete = None
        self.prochaine_arrete: Arrete = None
        self.road_size = road_size
        marge = 0.75*size[0]*(1-self.agressivite)
        self.distance_modulation_voiture = 0.5*size[0]+0.25*size[1]+marge
        self.distance_securite_voiture = self.distance_modulation_voiture*1.5
        marge = 0.5*size[1]
        self.distance_arret_point = 0.5*self.road_size+0.5*size[0]+marge
        self.distance_securite_point = 4*self.road_size+0.5*size[0]+marge*(2-self.agressivite)
        self.acceleration = 0
        self.noeuds = {} # {Noeud:"stop",Noeud:"pass",Noeud:"slow",Noeud:"regulate"]

    def update(self):
        pass
        
    def reassign(self, position, objectif, vitesse, kp):
        self.position = Vecteur2D(position[0], position[1]) #[x,y]
        self.objectif = Vecteur2D(objectif[0], objectif[1])
        #Implémentation PID
        self.vitesse = vitesse
        self.kp = kp
        #Variables primaires (ne changeront plus)
        self.generate_color()
        self.calculer_vitesse_max()
        self.distance_securite = dist_securite

        self.status = self.ROULE

        self.generate_color
        self.calculer_vitesse_max

        self.noeuds = {} # {Noeud:"stop",Noeud:"pass",Noeud:"slow",Noeud:"regulate"]

    
    def intention(self):
        return self.orientation, self.direction_prochain_chemin()

    def direction_prochain_chemin(self):
        vect = (self.noeuds[2].position - self.noeuds[1].position) - (self.noeuds[2] - self.noeuds[1])
        vect.vecteur_unitaire()
        return vect
    
    def trouver_arete(self, noeud_depart, noeud_arrivee):
        for arete in noeud_depart.aretes:
            if arete == [noeud_depart, noeud_arrivee]:
                return arete
            
    def orientation(self):
        dir_x = self.arrete_actuelle.position_depart.x - self.arrete_actuelle.position_arrivee.x / abs(self.arrete_actuelle.position_depart.x - self.arrete_actuelle.position_arrivee.x)
        dir_y = self.arrete_actuelle.position_depart.y - self.arrete_actuelle.position_arrivee.y / abs(self.arrete_actuelle.position_depart.y - self.arrete_actuelle.position_arrivee.y)
        return dir_x, dir_y
        liste_noeuds = list(self.noeuds.keys())
        vect = (liste_noeuds[1].position - liste_noeuds[0].position)
        return vect.vecteur_unitaire()

    def generate_color(self):
        colors = ['red', 'blue', 'green', 'yellow', 'orange', 'purple', 'pink', 'brown', 'cyan', 'magenta']
        randomIndex = math.floor(random.random() * colors.length)
        self.couleur = colors[randomIndex]

    def calculer_vitesse_max(self):
        # Calcul de la vitesse initiale en fonction de kp
        vitesse_ref = 90
        # Ajuster la plage de vitesse en fonction de kp
        plage_vitesse_min  = vitesse_ref - 10
        plage_vitesse_max = vitesse_ref + (self.agressivite * 15)
        # Génération d'une vitesse aléatoire dans la plage ajustée
        self.vitesse_max = random.randint(plage_vitesse_min, plage_vitesse_max)

    def reguler_vitesse(self, agressivite, vitesse_max, vitesse_initiale, distance_point):
        ##Utiliser self.contrainte_plus_proche
        #TODO
        #Déclencher newcurve sur un changement de phase
        #si rien ne pose problème avant une dist_secu suffisante
        #self.followcurve
        #si on doit s'arrêter bientôt
        #self.followcurve
        pass

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

    def update_position(self, distance_obstacle, time_elapsed):
        # Appeler la méthode PID pour calculer la vitesse cible en fonction de la distance à l'obstacle
        # Puis mettre à jour la vitesse actuelle avec la vitesse cible
        self.vitesse = self.PID(distance_obstacle, time_elapsed)
        
        # Mettre à jour la position en fonction de la nouvelle vitesse
        self.position.x += self.vitesse * math.cos(self.orientation()) * time_elapsed
        self.position.y += self.vitesse * math.sin(self.orientation()) * time_elapsed

    def intention(self):
        return self.orientation(), self.direction_prochain_chemin()

    def direction_prochain_chemin(self):
        dir_x = self.prochaine_arrete.position_depart.x - self.prochaine_arrete.position_arrivee.x / abs(self.prochaine_arrete.position_depart.x - self.prochaine_arrete.position_arrivee.x)
        dir_y = self.prochaine_arrete.position_depart.y - self.prochaine_arrete.position_arrivee.y / abs(self.prochaine_arrete.position_depart.y - self.prochaine_arrete.position_arrivee.y)
        return dir_x, dir_y

    def update_position(self):
        self.reguler_vitesse()

    def contrainte_plus_proche(self):
        # On obtient tous les points pouvant constituer des arêtes contenant des voitures sous la distance de sécurité
        distance_totale = 0
        noeuds_a_traiter = [(self,0)]
        prochain_noeuds = iter(self.noeuds.items())
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
            arete = self.trouver_arete(noeuds_a_traiter[i][0], noeuds_a_traiter[i+1][0])
            for voiture in arete.voitures:
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