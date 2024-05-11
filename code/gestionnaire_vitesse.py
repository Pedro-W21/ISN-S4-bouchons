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
            self.ARRET: [],
            self.ROULE: []
        }

        self.voiture = voiture
        self.position_depart_courante: Vecteur2D = self.voiture.position
        self.genere_courbe_acceleration_arete(self.voiture.arete_actuelle)
        self.courbe_courante = self.courbes[self.ACCELERATION][0][0]
        self.marge_noeud = (voiture.size.x+Noeud.size.get_x())/2

    def desactiver_courbes(self, nom_courbes: list[str]):
        if nom_courbes == ["ALL"]:
            self.desactiver_toutes_courbes()
            return
        else:
            courbes_a_supprimer = []
            for nom_courbe in self.courbes.keys():
                for a_supprimer in nom_courbes:
                    if nom_courbe.startswith(a_supprimer):
                        courbes_a_supprimer.append(nom_courbe)
            
            for courbe in courbes_a_supprimer:
                if self.NOEUD in courbe or self.SUIVRE_VOITURE in courbe:
                    del self.courbes[courbe]
                else:
                    self.courbes[courbe] = []

    def desactiver_toutes_courbes(self):
        for key in self.courbes.keys():
            self.courbes[key] = []

    def cree_courbe(self, vitesse_initiale: float, vitesse_finale: float, acceleration: float):
        if vitesse_initiale == vitesse_finale:
            duree = 9999
        else:
            duree = self.voiture.temps_mouvement(vitesse_initiale, vitesse_finale, acceleration)
        return Courbe(vitesse_initiale, vitesse_finale, duree, self.voiture.temps_simulation)

    """def genere_courbe_suivie_voiture(self, voiture_obstacle, distance_voiture_obstacle_initiale: float):
        vitesse, position = voiture_obstacle.gestionnaire_vitesse.courbe_courante.result_e(self.voiture.temps_simulation)
        deplacement_voiture_obstacle_total_depuis_t = voiture_obstacle.gestionnaire_vitesse.courbe_courante.position_finale - position
        distance = deplacement_voiture_obstacle_total_depuis_t + distance_voiture_obstacle_initiale - self.voiture.distance_securite(voiture_obstacle.gestionnaire_vitesse.courbe_courante.vitesse_finale)
        courbe = self.cree_courbe(distance, self.voiture.vitesse, voiture_obstacle.gestionnaire_vitesse.courbe_courante.vitesse_finale)
        self.courbes[self.SUIVRE_VOITURE+voiture_obstacle.id] = [(courbe, self.voiture.position)]
    """
    def genere_courbe_freinage(self, vitesse_finale: float, nom_courbe = FREINAGE):
        if vitesse_finale <= self.voiture.vitesse:
            courbe = self.cree_courbe(self.voiture.vitesse, vitesse_finale, self.voiture.deceleration)
            if nom_courbe == self.FREINAGE:
                self.courbes[nom_courbe].append((courbe, self.voiture.position))
            else:
                self.courbes[nom_courbe] =[(courbe, self.voiture.position)]
        else:
            return ValueError(f"Vous ne générez pas une courbe de freinage : not {vitesse_finale} <= {self.voiture.vitesse}")
    
    def genere_courbe_freinage_noeud(self, noeud_obstacle: Noeud):
        self.genere_courbe_freinage(noeud_obstacle.vitesse_max, nom_courbe=self.FREINAGE+self.NOEUD+noeud_obstacle.nom)

    def genere_courbe_freinage_arete(self, arete: Arete):
        self.genere_courbe_freinage(arete.vitesse_max)

    def genere_courbe_acceleration(self, vitesse_finale: float, nom_courbe = ACCELERATION):
        courbe = self.cree_courbe(self.voiture.vitesse, vitesse_finale, self.voiture.acceleration)
        if nom_courbe == self.ACCELERATION:
            self.courbes[nom_courbe].append((courbe, self.voiture.position))
        else:
            self.courbes[nom_courbe] =[(courbe, self.voiture.position)]
    
    def genere_courbe_acceleration_arete(self, arete: Arete):
        self.genere_courbe_acceleration(arete.vitesse_max)

    def genere_courbe_acceleration_noeud(self, noeud: Noeud):
        self.genere_courbe_acceleration(noeud.vitesse_max, nom_courbe=self.ACCELERATION+self.NOEUD+noeud.nom)

    def genere_courbe_roule_vitesse_max(self, vitesse_max: float, nom_courbe = ROULE):
        courbe = self.cree_courbe(vitesse_max, vitesse_max, self.voiture.acceleration)
        if nom_courbe == self.ROULE:
            self.courbes[nom_courbe].append((courbe, self.voiture.position))
        else:
            self.courbes[nom_courbe] =[(courbe, self.voiture.position)]

    def genere_courbe_roule_arete(self, arete: Arete):
        self.genere_courbe_roule_vitesse_max(arete.vitesse_max)
    
    def genere_courbe_roule_noeud(self, noeud: Noeud):
        self.genere_courbe_roule_vitesse_max(noeud.vitesse_max, nom_courbe=self.ROULE+self.NOEUD+noeud.nom)

    def genere_courbe_arret(self, nom_courbe = ARRET):
        courbe = self.cree_courbe(self.voiture.vitesse, 0, self.voiture.deceleration)
        if nom_courbe == self.ARRET:
            self.courbes[nom_courbe].append((courbe, self.voiture.position))
        else:
            self.courbes[nom_courbe] =[(courbe, self.voiture.position)]

    def genere_courbe_arret_noeud(self, nom_noeud):
        self.genere_courbe_arret(nom_courbe=self.ARRET+self.NOEUD+nom_noeud)

    def trouver_etat_par_courbe(self, courbe: Courbe) -> str:
        for etat, tuples in self.courbes.items():
            courbes = [courbe for courbe, _ in tuples]
            if courbe in courbes:
                return etat

    def liste_courbes(self):
        return [courbe for valeurs in self.courbes.values() for courbe, _ in valeurs]
    
    def recuperer_position_etat(self) -> tuple[float, float, str]:
        vitesses: dict[float: Courbe] = {}
        for courbe in self.liste_courbes():
            print("oui1")
            vitesse, position = courbe.result(self.voiture.temps_simulation)
            vitesses[vitesse] = courbe, position
        if list(vitesses.keys()) != []:
            vitesse = min(list(vitesses.keys()))

            self.courbe_courante, position = vitesses[vitesse]
        
            self.etat = self.trouver_etat_par_courbe(vitesses[vitesse][0])
            self.vitesse = vitesse
            self.position = position
        else:
            vitesse = 0
            position = 0

            self.etat = "Null"
        
        return vitesse, position, self.etat
    
    def courbe_est_active(self, nom_courbe: str) -> bool:
        return self.courbes.get(nom_courbe, False)