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

    def __init__(self, voiture):

        self.courbes = {
            self.ACCELERATION: [],
            self.FREINAGE: [],
            self.SUIVRE_VOITURE: [],
            self.ARRET: [],
            self.ROULE: []
        }

        self.voiture = voiture
        self.courbe_courante = self.genere_courbe_acceleration_arrete(self.voiture.arete_actuelle)

    def desactiver_courbes(self, nom_courbes: list[str], position_finale: Vecteur2D=None):
        for nom_courbe in nom_courbes:
            if nom_courbe in (self.ARRET, self.FREINAGE):
                for courbe in self.courbes[nom_courbe]:
                    if courbe.position_finale == position_finale:
                        self.courbes[nom_courbe].remove(courbe)
            else:
                self.courbes[nom_courbe] = []

    # vu
    def genere_courbe_suivie_voiture(self, voiture_obstacle):
        courbe_voiture_obstacle = voiture_obstacle.gestionnaire_vitesse.courbe_courante
        distance_securite_finale = self.voiture.distance_securite(courbe_voiture_obstacle.vitesse_finale)
        courbe = Courbe(self.voiture.position, courbe_voiture_obstacle.position_arrivee - distance_securite_finale, self.voiture.vitesse, courbe_voiture_obstacle.vitesse_finale)
        self.courbes[self.SUIVRE_VOITURE].append(courbe)

    # vu
    def cree_courbe(self, position_depart: Vecteur2D, position_arrivee: Vecteur2D, vitesse_initiale: float, vitesse_finale: float):
        position_depart_float = position_depart.scalaire(abs(self.voiture.direction))
        position_arrivee_float = position_arrivee.scalaire(abs(self.voiture.direction))
        return Courbe(position_depart_float, position_arrivee_float, vitesse_initiale, vitesse_finale)
    
    # vu
    def genere_courbe_freinage(self, position_finale: float, vitesse_finale: float):
        courbe = Courbe(self.voiture.position, position_finale, self.voiture.vitesse, vitesse_finale)
        self.courbes[self.FREINAGE].append(courbe)
    
    # vu
    def genere_courbe_freinage_noeud(self, noeud_obstacle: Noeud):
        self.genere_courbe_freinage(noeud_obstacle.position - noeud_obstacle.distance_securite, noeud_obstacle.vitesse_max)

    # vu
    def genere_courbe_acceleration(self, vitesse_finale: float):
        courbe = Courbe(self.voiture.position, self.voiture.distance_acceleration(self.voiture.vitesse, vitesse_finale), self.voiture.vitesse, vitesse_finale)
        self.courbes[self.ACCELERATION].append(courbe)
    
    # vu
    def genere_courbe_acceleration_arrete(self, arete: Arete):
        self.genere_courbe_acceleration(arete.vitesse_max)
    
    # vu
    def genere_courbe_acceleration_noeud(self, noeud: Noeud):
        self.genere_courbe_acceleration(noeud.vitesse_max)

    # vu
    def genere_courbe_roule_vitesse_max(self, position_finale: Vecteur2D, vitesse_max: float):
        courbe = self.cree_courbe(self.voiture.position, position_finale, vitesse_max, vitesse_max)
        self.courbes[self.ROULE].append(courbe)

    # vu
    def genere_courbe_roule_arete(self, arete: Arete):
        self.genere_courbe_roule_vitesse_max(arete.position_arrivee, arete.vitesse_max)
    
    # vu
    def genere_courbe_roule_arete(self, noeud: Noeud):
        self.genere_courbe_roule_vitesse_max(noeud.position_arrivee, noeud.vitesse_max)
    
    # vu
    def genere_courbe_arret(self, position_finale: Vecteur2D):
        courbe = self.cree_courbe(self.voiture.position, position_finale, self.voiture.vitesse, 0)
        self.courbes[self.ARRET].append(courbe)

    # vu
    def genere_courbe_arret_noeud(self, noeud: Noeud):
        self.genere_courbe_arret(noeud.position - Noeud.size)

    def trouver_etat_par_courbe(self, courbe: Courbe) -> str:
        for etat, courbes in self.courbes.items():
            if courbe in courbes:
                return etat

    def recuperer_vitesse_etat(self):
        vitesses: dict[float: Courbe] = {}
        list_courbes: list[Courbe] = []
        for courbes in self.courbes.values():
            list_courbes += courbes

        for courbe in list_courbes:
            vitesse = courbe.result(self.voiture.position.scalaire(abs(self.voiture.direction)))
            vitesses[vitesse] = courbe

        vitesse = min(vitesses.keys())

        self.courbe_courante = vitesses[vitesse]

        desactiver_courbes = [self.ACCELERATION, self.FREINAGE, self.SUIVRE_VOITURE, self.ARRET, self.ROULE]
        desactiver_courbes.remove(self.voiture.etat)

        self.desactiver_courbes(desactiver_courbes)

        return vitesse, self.trouver_etat_par_courbe(vitesses[vitesse])

    def courbe_est_active(self, nom_courbe: str) -> bool:
        return bool(self.courbes[nom_courbe])