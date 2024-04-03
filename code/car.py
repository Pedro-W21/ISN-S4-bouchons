import random
import math
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
    def __init__(self, id, position, vitesse, kp, dist_securite):
        #Implémentation données pour affichage
        self.id = id
        self.position = Vecteur2D(position[0], position[1]) #[x,y]
        

        #Implémentation PID
        self.vitesse = vitesse
        self.kp = kp
        
        #Variables primaires (ne changeront plus)
        self.generate_color
        self.calculer_vitesse_max
        self.distance_securite = dist_securite
        self.arrete_actuelle = None
        self.prochaine_arrete = None

    def update(self):
        pass
        
    def reassign(self, position, vitesse, kp, direction, dist_securite):
        #Implémentation données pour affichage
        self.position = position #[x,y]
        self.direction = direction # "degrés"

        #Implémentation PID
        self.vitesse = vitesse
        self.kp = kp
        
        #Variables primaires (ne changeront plus)
        self.generate_color
        self.calculer_vitesse_max
        self.distance_securite = dist_securite

    def orientation(self):
        pass

    def generate_color(self):
        colors = ['red', 'blue', 'green', 'yellow', 'orange', 'purple', 'pink', 'brown', 'cyan', 'magenta']
        randomIndex = math.floor(random.random() * colors.length)
        self.couleur = colors[randomIndex]

    def calculer_vitesse_max(self):
        # Calcul de la vitesse initiale en fonction de kp
        vitesse_ref = 90
        # Ajuster la plage de vitesse en fonction de kp
        plage_vitesse_min  = vitesse_ref - 10
        plage_vitesse_max = vitesse_ref + (self.kp * 10)
        # Génération d'une vitesse aléatoire dans la plage ajustée
        self.vitesse_max = random.randint(plage_vitesse_min, plage_vitesse_max)

    def PID(self, distance_obstacle):
        instant_error = distance_obstacle-self.distance_securite

        componentP = self.kp*instant_error

        consigne = math.floor(componentP)

        return max(min(consigne,self.vitesse_max), 0)
    def regulier_vitesse(distance_securite, distance_freinage, anticipation, agressivite, vitesse_max, vitesse_initiale, distance_point):
        if distance_point < distance_freinage(anticipation, agressivite):
            nouvelle_vitesse = 0
        elif distance_point < distance_securite(anticipation):
            # Calcul de la nouvelle vitesse de manière progressive
            proportion_distance = distance_point / distance_securite(anticipation)
            augmentation_vitesse = vitesse_max * proportion_distance - vitesse_initiale
            nouvelle_vitesse = vitesse_initiale + augmentation_vitesse
        else:
            nouvelle_vitesse = vitesse_max
        
        return nouvelle_vitesse

    def update_position(self, distance_obstacle, time_elapsed):
        # Appeler la méthode PID pour calculer la vitesse cible en fonction de la distance à l'obstacle
        # Puis mettre à jour la vitesse actuelle avec la vitesse cible
        self.vitesse = self.PID(distance_obstacle, time_elapsed)
        
        # Mettre à jour la position en fonction de la nouvelle vitesse
        self.position[0] += self.vitesse * math.cos(self.orientation) * time_elapsed
        self.position[1] += self.vitesse * math.sin(self.orientation) * time_elapsed

    def intention(self):
        return self.orientation, self.direction_prochain_chemin()

    def direction_prochain_chemin(self):
        vect = (self.parcours[1].position - self.parcours[0].position) - (self.parcours[2] - self.parcours[1])
        vect.vecteur_unitaire()
        return vect
