from courbe import Courbe

# circular import incoming
from voiture import Voiture
from vecteur_2d import Vecteur2D
from noeud import Noeud
from arrete import Arrete

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

    def recuperer_vitesse(self):
        # TODO: refaire toute la classe pour optimiser et gerer plusieurs noeuds d'affiler
        etat = []
        vitesses = []
        if self.courbe_par_defaut.active and (self.voiture.position - self.position_depart_par_defaut).norme_manathan() < self.courbe_par_defaut.position_arrivee:
            vitesses.append(self.courbe_par_defaut.result(self.voiture.position - self.position_depart_par_defaut).norme_manathan())
            etat.append(self.ROULE)
        else:
            raise RangeError("La voiture est hors de la courbe")

        if self.courbe_acceleration.active and (self.voiture.position - self.position_depart_acceleration).norme_manathan() < self.courbe_acceleration.position_arrivee:
            vitesses.append(self.courbe_acceleration.result(self.voiture.position - self.position_depart_acceleration).norme_manathan())
            etat.append(self.ACCELERATION)
        else:
            raise RangeError("La voiture est hors de la courbe")

        if self.courbe_obstacle_voiture.active and (self.voiture.position - self.position_depart_obstacle_voiture).norme_manathan() < self.courbe_obstacle_voiture.position_arrivee:
            vitesses.append(self.courbe_obstacle_voiture.result(self.voiture.position - self.position_depart_obstacle_voiture).norme_manathan())
            etat.append(self.SUIVRE_VOITURE)
        else:
            raise RangeError("La voiture est hors de la courbe")
        if self.courbe_obstacle_noeud.active and (self.voiture.position - self.position_depart_obstacle_noeud).norme_manathan() < self.courbe_obstacle_noeud.position_arrivee:
            vitesses.append(self.courbe_obstacle_noeud.result(self.voiture.position - self.position_depart_obstacle_noeud).norme_manathan())
            etat.append(self.FREINAGE)
        else:
            raise RangeError("La voiture est hors de la courbe")
        
        if self.courbe_arret.active and (self.voiture.position - self.position_depart_arret).norme_manathan() < self.courbe_arret.position_arrivee:
            vitesses.append(self.courbe_arret.result(self.voiture.position - self.position_depart_arret).norme_manathan())
            etat.append(self.ARRET)
        else:
            raise RangeError("La voiture est hors de la courbe")
        
        vitesse = min(vitesses)
        self.etat = etat[vitesses.index(vitesse)]
        self.update_courbe_courante() 
        return vitesse, self.etat
