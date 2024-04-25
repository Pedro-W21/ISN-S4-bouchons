import time
from courbe import Courbe
from vecteur_2d import Vecteur2D
from noeud import Noeud
from arete import Arete

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
    NOEUD = "NOEUD"

    def __init__(self, voiture):

        self.courbes = {
            self.ACCELERATION: [],
            self.FREINAGE: [],
            self.SUIVRE_VOITURE: [],
            self.ARRET: [],
            self.ROULE: []
        }

        self.voiture = voiture
        self.position_depart_courante: Vecteur2D = self.voiture.position
        self.courbe_courante = self.genere_courbe_acceleration_arete(self.voiture.arete_actuelle)
        

    def desactiver_courbes(self, nom_courbes: list[str], position_finale: Vecteur2D=None):
        for nom_courbe in nom_courbes:
            if nom_courbe in (self.ARRET, self.FREINAGE):
                for courbe in self.courbes[nom_courbe]:
                    if courbe.position_finale == position_finale:
                        self.courbes[nom_courbe].remove(courbe)
            else:
                self.courbes[nom_courbe] = []

    def cree_courbe(self, distance_finale: float, vitesse_initiale: float, vitesse_finale: float, acceleration: float = 8):
        return Courbe(0, distance_finale, vitesse_initiale, vitesse_finale, acceleration)

    def genere_courbe_suivie_voiture(self, voiture_obstacle, distance_voiture_obstacle_initiale: float):
        deplacement_voiture_obstacle_total_depuis_t = voiture_obstacle.gestionnaire_vitesse.courbe_courante.position_finale - voiture_obstacle.gestionnaire_vitesse.courbe_courante.result_e(time.time())
        distance = deplacement_voiture_obstacle_total_depuis_t + distance_voiture_obstacle_initiale - self.voiture.distance_securite(voiture_obstacle.gestionnaire_vitesse.courbe_courante.vitesse_finale)
        courbe = self.cree_courbe(distance, self.voiture.vitesse, voiture_obstacle.gestionnaire_vitesse.courbe_courante.vitesse_finale)
        self.courbes[self.SUIVRE_VOITURE].append((courbe, self.voiture.position))
    
    def genere_courbe_freinage(self, distance_finale: float, vitesse_finale: float):
        if vitesse_finale <= self.voiture.vitesse:
            courbe = self.cree_courbe(self.voiture.position, distance_finale, self.voiture.vitesse, vitesse_finale, self.voiture.deceleration)
            self.courbes[self.FREINAGE].append((courbe, self.voiture.position))
        else:
            return ValueError(f"Vous ne générez pas une courbe de freinage : not {vitesse_finale} <= {self.voiture.vitesse}")
    
    def genere_courbe_freinage_noeud(self, noeud_obstacle: Noeud):
        self.genere_courbe_freinage(self.voiture.distance_deceleration(self.voiture.vitesse, noeud_obstacle.vitesse_max), noeud_obstacle.vitesse_max)

    def genere_courbe_freinage_arete(self, arete: Arete):
        self.genere_courbe_freinage(self.voiture.distance_deceleration(self.voiture.vitesse, arete.vitesse_max), arete.vitesse_max)

    def genere_courbe_acceleration(self, vitesse_finale: float):
        courbe = self.cree_courbe(self.voiture.distance_acceleration(self.voiture.vitesse, vitesse_finale), self.voiture.vitesse, vitesse_finale, self.voiture.acceleration)
        courbe = Courbe(self.voiture.position, self.voiture.distance_acceleration(self.voiture.vitesse, vitesse_finale), self.voiture.vitesse, vitesse_finale)
        self.courbes[self.ACCELERATION].append(courbe)
    
    def genere_courbe_acceleration_arete(self, arete: Arete):
        self.genere_courbe_acceleration(arete.vitesse_max)

    def genere_courbe_acceleration_noeud(self, noeud: Noeud):
        self.genere_courbe_acceleration(noeud.vitesse_max)

    def genere_courbe_roule_vitesse_max(self, distance_finale: Vecteur2D, vitesse_max: float):
        courbe = self.cree_courbe(distance_finale, self.voiture.vitesse, vitesse_max)
        self.courbes[self.ROULE].append((courbe, self.voiture.position))

    def genere_courbe_roule_arete(self, arete: Arete):
        self.genere_courbe_roule_vitesse_max((self.voiture.position - arete.position_arrivee).norme_manathan(), arete.vitesse_max)
    
    def genere_courbe_roule_noeud(self, noeud: Noeud):
        self.genere_courbe_roule_vitesse_max((self.voiture.position - noeud.position).norme_manathan() + noeud.size[0]/2, noeud.vitesse_max)

    def genere_courbe_arret(self, distance_finale: float):
        courbe = self.cree_courbe(distance_finale, self.voiture.vitesse, 0, self.voiture.deceleration)
        self.courbes[self.ARRET].append((courbe, self.voiture.position))

    def genere_courbe_arret_noeud(self, distance_noeud: float):
        self.genere_courbe_arret(distance_noeud - Noeud.size)

    def trouver_etat_par_courbe(self, courbe: Courbe) -> str:
        for etat, courbes in self.courbes.items():
            if courbe in courbes:
                return etat

    def recuperer_position_etat(self):
        positions: dict[float: Courbe] = {}
        list_courbes: list[Courbe] = []
        for courbes in self.courbes.values():
            list_courbes += courbes

        for courbe in list_courbes:
            position = courbe.result(self.voiture.position.scalaire(abs(self.voiture.direction)))
            positions[position] = courbe

        position = min(positions.keys())

        self.courbe_courante = positions[position]

        desactiver_courbes = [self.ACCELERATION, self.FREINAGE, self.SUIVRE_VOITURE, self.ARRET, self.ROULE]
        desactiver_courbes.remove(self.voiture.etat)

        self.desactiver_courbes(desactiver_courbes)

        return position, self.trouver_etat_par_courbe(positions[position])
    
    def courbe_est_active(self, nom_courbe: str) -> bool:
        return self.courbes.get(nom_courbe, False)