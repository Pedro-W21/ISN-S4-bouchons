from utils.courbe import Courbe
from utils.vecteur_2d import Vecteur2D
from simulation.noeud import Noeud
from simulation.arete import Arete

class RangeError(Exception):
    
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class GestionnaireVitesse:

    # Différents états possibles d'une voiture
    ACCELERATION = "ACCELERATION"
    FREINAGE = "FREINAGE"
    SUIVRE_VOITURE = "SUIVRE_VOITURE"
    ARRET = "ARRET"
    ROULE = "ROULE"
    NOEUD = "NOEUD"

    temps_simulation = 0

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
        """
        Désactive les courbes spécifiées.

        Args:
            nom_courbes (list[str]): Une liste de noms de courbes à désactiver.

        Returns:
            None
        """
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
            """
            Vide toutes les courbes du gestionnaire de vitesse.

            Cette méthode parcourt toutes les clés du dictionnaire de courbes et vide chaque liste associée.
            """
            for key in self.courbes.keys():
                self.courbes[key] = []

    def cree_courbe(self, vitesse_initiale: float, vitesse_finale: float, acceleration: float):
            """
            Génère une courbe de vitesse en fonction de la vitesse initiale, de la vitesse finale et de l'accélération.

            Args:
                vitesse_initiale (float): La vitesse initiale de la courbe.
                vitesse_finale (float): La vitesse finale de la courbe.
                acceleration (float): L'accélération de la courbe.

            Returns:
                Courbe: La courbe de vitesse générée.
            """
            if vitesse_initiale == vitesse_finale:
                duree = 9999
            else:
                duree = self.voiture.temps_mouvement(vitesse_initiale, vitesse_finale, acceleration)
            return Courbe(vitesse_initiale, vitesse_finale, duree, self.voiture.temps_simulation)

    def genere_courbe_suivie_voiture(self, voiture_obstacle):
            """
            Génère une courbe de suivi de voiture en fonction de la voiture obstacle.

            Args:
                voiture_obstacle: La voiture obstacle à suivre.

            Returns:
                None
            """
            courbe = self.cree_courbe(self.voiture.vitesse, 0, self.voiture.deceleration)
            self.courbes[self.SUIVRE_VOITURE+str(voiture_obstacle.id)+voiture_obstacle.etat] = [(courbe, self.voiture.position)]
    
    def genere_courbe_freinage(self, vitesse_finale: float, nom_courbe = FREINAGE):
        """
        Génère une courbe de freinage pour ralentir la voiture jusqu'à une vitesse finale donnée.

        Args:
            vitesse_finale (float): La vitesse finale à atteindre.
            nom_courbe (str, optional): Le nom de la courbe de freinage. Par défaut, il est défini comme FREINAGE.

        Returns:
            None

        Raises:
            ValueError: Si la vitesse finale est supérieure à la vitesse actuelle de la voiture.
        """
        if vitesse_finale <= self.voiture.vitesse:
            courbe = self.cree_courbe(self.voiture.vitesse, vitesse_finale, self.voiture.deceleration)
            if nom_courbe == self.FREINAGE:
                self.courbes[nom_courbe].append((courbe, self.voiture.position))
            else:
                self.courbes[nom_courbe] =[(courbe, self.voiture.position)]
        else:
            raise ValueError(f"Vous ne générez pas une courbe de freinage : not {vitesse_finale} <= {self.voiture.vitesse}")

    def genere_courbe_freinage_noeud(self, noeud_obstacle: Noeud):
        """
        Génère une courbe de freinage pour un nœud donné.

        Args:
            noeud_obstacle (Noeud): Le nœud obstacle pour lequel générer la courbe de freinage.

        Returns:
            None
        """
        self.genere_courbe_freinage(noeud_obstacle.vitesse_max, nom_courbe=self.FREINAGE+self.NOEUD+noeud_obstacle.nom)

    def genere_courbe_freinage_arete(self, arete: Arete):
        """
        Génère une courbe de freinage pour une arête donnée.

        Args:
            arete (Arete): L'arête pour laquelle générer la courbe de freinage.
        """
        self.genere_courbe_freinage(arete.vitesse_max)

    def genere_courbe_acceleration(self, vitesse_finale: float, nom_courbe = ACCELERATION):
        """
        Génère une courbe d'accélération pour atteindre la vitesse finale spécifiée.

        Args:
            vitesse_finale (float): La vitesse finale à atteindre.
            nom_courbe (str, optional): Le nom de la courbe. Par défaut, ACCELERATION.

        Returns:
            None
        """
        courbe = self.cree_courbe(self.voiture.vitesse, vitesse_finale, self.voiture.acceleration)
        if nom_courbe == self.ACCELERATION:
            self.courbes[nom_courbe].append((courbe, self.voiture.position))
        else:
            self.courbes[nom_courbe] =[(courbe, self.voiture.position)]
    
    def genere_courbe_acceleration_arete(self, arete: Arete):
        """
        Génère une courbe d'accélération pour une arête donnée.

        Args:
            arete (Arete): L'arête pour laquelle générer la courbe d'accélération.

        Returns:
            None
        """
        self.genere_courbe_acceleration(arete.vitesse_max)

    def genere_courbe_acceleration_noeud(self, noeud: Noeud):
        """
        Génère une courbe d'accélération pour un nœud donné.

        Args:
            noeud (Noeud): Le nœud pour lequel générer la courbe d'accélération.

        Returns:
            None
        """
        self.genere_courbe_acceleration(noeud.vitesse_max, nom_courbe=self.ACCELERATION+self.NOEUD+noeud.nom)

    def genere_courbe_roule_vitesse_max(self, vitesse_max: float, nom_courbe = ROULE):
        """
        Génère une courbe de vitesse maximale pour la voiture et l'ajoute au gestionnaire de courbes.

        Args:
            vitesse_max (float): La vitesse maximale de la voiture.
            nom_courbe (str, optional): Le nom de la courbe. Par défaut, il est défini comme "ROULE".

        Returns:
            None
        """
        courbe = self.cree_courbe(vitesse_max, vitesse_max, self.voiture.acceleration)
        if nom_courbe == self.ROULE:
            self.courbes[nom_courbe].append((courbe, self.voiture.position))
        else:
            self.courbes[nom_courbe] =[(courbe, self.voiture.position)]

    def genere_courbe_roule_arete(self, arete: Arete):
        """
        Génère une courbe roule pour une arête donnée.

        Args:
            arete (Arete): L'arête pour laquelle générer la courbe de roulement.
        """
        self.genere_courbe_roule_vitesse_max(arete.vitesse_max)
    
    def genere_courbe_roule_noeud(self, noeud: Noeud):
        """
        Génère une courbe roule pour un nœud donné.

        Args:
            noeud (Noeud): Le nœud pour lequel générer la courbe de roulement.

        Returns:
            None
        """
        self.genere_courbe_roule_vitesse_max(noeud.vitesse_max, nom_courbe=self.ROULE+self.NOEUD+noeud.nom)

    def genere_courbe_arret(self, nom_courbe = ARRET):
        """
        Génère une courbe d'arrêt pour la voiture.

        Args:
            nom_courbe (str, optional): Le nom de la courbe. Par défaut, ARRET.

        Returns:
            None
        """
        courbe = self.cree_courbe(self.voiture.vitesse, 0, self.voiture.deceleration)
        if nom_courbe == self.ARRET:
            self.courbes[nom_courbe].append((courbe, self.voiture.position))
        else:
            self.courbes[nom_courbe] =[(courbe, self.voiture.position)]

    def genere_courbe_arret_noeud(self, nom_noeud):
        """
        Génère une courbe d'arrêt pour un nœud spécifié.

        Args:
            nom_noeud (str): Le nom du nœud pour lequel générer la courbe d'arrêt.

        Returns:
            None
        """
        self.genere_courbe_arret(nom_courbe=self.ARRET+self.NOEUD+nom_noeud)

    def trouver_etat_par_courbe(self, courbe: Courbe) -> str:
        """
        Trouve l'état correspondant à une courbe donnée.

        Args:
            courbe (Courbe): La courbe à rechercher.

        Returns:
            str: L'état correspondant à la courbe donnée.

        """
        for etat, tuples in self.courbes.items():
            courbes = [courbe for courbe, _ in tuples]
            if courbe in courbes:
                return etat

    def liste_courbes(self):
        """
        Renvoie une liste de toutes les courbes présentes dans le gestionnaire de vitesse.

        Returns:
            list: Une liste contenant toutes les courbes présentes dans le gestionnaire de vitesse.
        """
        return [courbe for valeurs in self.courbes.values() for courbe, _ in valeurs]
    
    def recuperer_position_etat(self) -> tuple[float, float, str]:
        """
        Récupère la position, la vitesse et l'état actuels du gestionnaire de vitesse.

        Returns:
            tuple[float, float, str]: Un tuple contenant la vitesse, la position et l'état actuels.
        """
        vitesses: dict[float: Courbe] = {}
        for courbe in self.liste_courbes():
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
        """
        Vérifie si une courbe est active.

        Args:
            nom_courbe (str): Le nom de la courbe à vérifier.

        Returns:
            bool: True si la courbe est active, False sinon.
        """
        return self.courbes.get(nom_courbe, False)