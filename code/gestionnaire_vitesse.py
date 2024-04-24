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
        self.courbe_courante = self.genere_courbe_acceleration_arete(self.voiture.arete_actuelle)

    def desactiver_courbes(self, nom_courbes: list[str], position_finale: Vecteur2D=None):
        for nom_courbe in nom_courbes:
            if nom_courbe in (self.ARRET, self.FREINAGE):
                for courbe in self.courbes[nom_courbe]:
                    if courbe.position_finale == position_finale:
                        self.courbes[nom_courbe].remove(courbe)
            else:
                self.courbes[nom_courbe] = []

    def genere_courbe_suivie_voiture(self, voiture_obstacle):
        courbe_voiture_obstacle = voiture_obstacle.gestionnaire_position.courbe_courante
        distance_securite_finale = self.voiture.distance_securite(courbe_voiture_obstacle.position_finale)
        courbe = Courbe(self.voiture.position, courbe_voiture_obstacle.position_arrivee - distance_securite_finale, self.voiture.position, courbe_voiture_obstacle.position_finale)
        self.courbes[self.SUIVRE_VOITURE].append(courbe)

    def cree_courbe(self, position_depart: Vecteur2D, position_arrivee: Vecteur2D, position_initiale: float, position_finale: float):
        position_depart_float = position_depart.scalaire(abs(self.voiture.direction))
        position_arrivee_float = position_arrivee.scalaire(abs(self.voiture.direction))
        return Courbe(position_depart_float, position_arrivee_float, position_initiale, position_finale)
    
    def genere_courbe_freinage(self, position_finale: float):
    def genere_courbe_freinage(self, position_finale: float, position_depart: float):
        courbe = Courbe(self.voiture.position, position_finale, self.voiture.position, position_finale)
        self.courbes[self.FREINAGE].append(courbe)

    
    def genere_courbe_freinage_noeud(self, noeud_obstacle: Noeud):
        self.genere_courbe_freinage(noeud_obstacle.position - noeud_obstacle.distance_securite, noeud_obstacle.position_max)

    def genere_courbe_acceleration(self, position_finale: float):
        courbe = Courbe(self.voiture.position, self.voiture.distance_acceleration(self.voiture.position, position_finale), self.voiture.position, position_finale)
        self.courbes[self.ACCELERATION].append(courbe)

    
    def genere_courbe_acceleration_arete(self, arete: Arete):
        self.genere_courbe_acceleration(arete.position_max)

    
    def genere_courbe_acceleration_noeud(self, noeud: Noeud):
        self.genere_courbe_acceleration(noeud.position_max)

    def genere_courbe_roule_position_max(self, position_finale: Vecteur2D, position_max: float):
        courbe = self.cree_courbe(self.voiture.position, position_finale, position_max, position_max)
        self.courbes[self.ROULE].append(courbe)

    def genere_courbe_roule_arete(self, arete: Arete):
        self.genere_courbe_roule_position_max(arete.position_arrivee, arete.position_max)
    
    def genere_courbe_roule_noeud(self, noeud: Noeud):
        self.genere_courbe_roule_position_max(noeud.position_arrivee, noeud.position_max)

    
    def genere_courbe_arret(self, position_finale: Vecteur2D):
        courbe = self.cree_courbe(self.voiture.position, position_finale, self.voiture.position, 0)
        self.courbes[self.ARRET].append(courbe)

    def genere_courbe_arret_noeud(self, noeud: Noeud):
        self.genere_courbe_arret(noeud.position - Noeud.size)

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
        return bool(self.courbes[nom_courbe])