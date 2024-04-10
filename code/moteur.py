class Moteur:
    def __init__(self, acceleration_max, couple_Nm, masse_voiture, couple_ch, acceleration_moyenne, freinage_moyen):
        self.acceleration_max = acceleration_max
        self.couple_Nm = couple_Nm
        self.masse_voiture = masse_voiture
        self.couple_ch = couple_ch
        self.acceleration_moyenne = acceleration_moyenne
        self.freinage_moyen = freinage_moyen

    def calculer_vitesse_max(self):
        vitesse_max = (self.acceleration_max * self.masse_voiture) / self.couple_Nm
        return vitesse_max

    def calculer_acceleration_moyenne(self):
        acceleration_moyenne = self.acceleration_moyenne * self.masse_voiture
        return acceleration_moyenne

    def calculer_freinage_moyen(self):
        freinage_moyen = self.freinage_moyen * self.masse_voiture
        return freinage_moyen
    
class Frein:

    def __init__(self) -> None:
        pass