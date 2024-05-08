import time
from courbe import Courbe
from vecteur_2d import Vecteur2D
from noeud import Noeud
from arete import Arete

#TODO LA VITESSE MAX NEST PAS IMPLEMENTEE

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
        self.genere_courbe_acceleration_arete(self.voiture.arete_actuelle)
        self.courbe_courante = self.courbes[self.ACCELERATION][0][0]
        

    def desactiver_courbes(self, nom_courbes: list[str]):
        for nom_courbe in self.courbes.keys():
            for a_supprimer in nom_courbes:
                if nom_courbe.startswith(a_supprimer) or a_supprimer == "ALL":
                    if self.NOEUD in nom_courbe:
                        del self.courbes[nom_courbe]
                    else:
                        self.courbes[nom_courbe] = []
    
    def cree_courbe(self, distance_finale: float, vitesse_initiale: float, vitesse_finale: float, acceleration: float = 8):
        print("Création courbe gestionnaire_vitese : ")
        print("vitesse_initiale", vitesse_initiale)
        print("vitesse_finale", vitesse_finale)
        print("distance_finale", distance_finale, "\n")

        return Courbe(vitesse_initiale, vitesse_finale, 0, distance_finale, self.voiture.acceleration)

    def genere_courbe_suivie_voiture(self, voiture_obstacle, distance_voiture_obstacle_initiale: float):
        vitesse, position = voiture_obstacle.gestionnaire_vitesse.courbe_courante.result_e(time.time())
        deplacement_voiture_obstacle_total_depuis_t = voiture_obstacle.gestionnaire_vitesse.courbe_courante.position_finale - position
        distance = deplacement_voiture_obstacle_total_depuis_t + distance_voiture_obstacle_initiale - self.voiture.distance_securite(voiture_obstacle.gestionnaire_vitesse.courbe_courante.vitesse_finale)
        courbe = self.cree_courbe(distance, self.voiture.vitesse, voiture_obstacle.gestionnaire_vitesse.courbe_courante.vitesse_finale)
        self.courbes[self.SUIVRE_VOITURE].append((courbe, self.voiture.position))
    
    def genere_courbe_freinage(self, distance_finale: float, vitesse_finale: float, nom_courbe = FREINAGE):
        if vitesse_finale <= self.voiture.vitesse:
            courbe = self.cree_courbe(self.voiture.position, distance_finale, self.voiture.vitesse, vitesse_finale, self.voiture.deceleration)
            self.courbes[nom_courbe].append((courbe, self.voiture.position))
        else:
            return ValueError(f"Vous ne générez pas une courbe de freinage : not {vitesse_finale} <= {self.voiture.vitesse}")
    
    def genere_courbe_freinage_noeud(self, noeud_obstacle: Noeud):
        self.genere_courbe_freinage(self.voiture.distance_deceleration(self.voiture.vitesse, noeud_obstacle.vitesse_max), noeud_obstacle.vitesse_max, nom_courbe=self.FREINAGE+self.NOEUD+noeud_obstacle.nom)

    def genere_courbe_freinage_arete(self, arete: Arete):
        self.genere_courbe_freinage(self.voiture.distance_deceleration(self.voiture.vitesse, arete.vitesse_max), arete.vitesse_max)

    def genere_courbe_acceleration(self, vitesse_finale: float, nom_courbe = ACCELERATION):
        courbe = self.cree_courbe(self.voiture.distance_acceleration(self.voiture.vitesse, vitesse_finale), self.voiture.vitesse, vitesse_finale, self.voiture.acceleration)
        self.courbes[nom_courbe].append((courbe, self.voiture.position))
    
    def genere_courbe_acceleration_arete(self, arete: Arete):
        self.genere_courbe_acceleration(arete.vitesse_max)

    def genere_courbe_acceleration_noeud(self, noeud: Noeud):
        self.genere_courbe_acceleration(noeud.vitesse_max, nom_courbe=self.ACCELERATION+self.NOEUD+noeud.nom)

    def genere_courbe_roule_vitesse_max(self, distance_finale: Vecteur2D, vitesse_max: float, nom_courbe = ROULE):
        courbe = self.cree_courbe(999999999, self.voiture.vitesse, vitesse_max)
        self.courbes[nom_courbe].append((courbe, self.voiture.position))

    def genere_courbe_roule_arete(self, arete: Arete):
        self.genere_courbe_roule_vitesse_max((self.voiture.position - arete.position_arrivee).norme_manathan() + arete.size.x * 3, arete.vitesse_max)
    
    def genere_courbe_roule_noeud(self, noeud: Noeud):
        self.genere_courbe_roule_vitesse_max((self.voiture.position - noeud.position).norme_manathan() + noeud.size[0]/2, noeud.vitesse_max, nom_courbe=self.ROULE+self.NOEUD+noeud.nom)

    def genere_courbe_arret(self, distance_finale: float, nom_courbe = ARRET):
        courbe = self.cree_courbe(distance_finale, self.voiture.vitesse, 0, self.voiture.deceleration)
        self.courbes[nom_courbe].append((courbe, self.voiture.position))

    def genere_courbe_arret_noeud(self, distance_noeud: float, nom_noeud):
        self.genere_courbe_arret(distance_noeud - Noeud.size, nom_courbe=self.ARRET+self.NOEUD+nom_noeud)

    def trouver_etat_par_courbe(self, courbe: Courbe) -> str:
        for etat, tuples in self.courbes.items():
            courbes = [courbe for courbe, _ in tuples]
            if courbe in courbes:
                return etat

    def liste_courbes(self):
        return [courbe for valeurs in self.courbes.values() for courbe, _ in valeurs]
    
    def recuperer_position_etat(self):
        vitesses: dict[float: Courbe] = {}
        print("liste_courbes", len(self.liste_courbes()))
        for courbe in self.liste_courbes():
            vitesse, position, test = courbe.result_e_test(time.time())
            vitesses[vitesse] = courbe, position
        vitesse = min(min(list(vitesses.keys())),100)

        self.courbe_courante, position = vitesses[vitesse]
        
        
        self.etat = self.trouver_etat_par_courbe(vitesses[vitesse][0])
        self.vitesse = vitesse
        self.position = position

        return vitesse, position, self.etat
    
    def courbe_est_active(self, nom_courbe: str) -> bool:
        return self.courbes.get(nom_courbe, False)