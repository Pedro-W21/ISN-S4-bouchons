import numpy as np
import matplotlib.pyplot as plt

a = 2
b = -1
c = 2*np.exp(-1)
d = 1/2

def fonction_vitesse_e(t):
    return (a*t+b)*np.exp(-np.abs(a*t+b)) / c + d

def fonction_vitesse_lineaire(t):
    return t

def fonction_position_e(t):
    return (1/(2*a*c) * ((a*c*d*t + np.exp(b+a*t)*(-1+b+a*t)) * (1 - np.sign(b + a*t)) + (a*c*d*t - np.exp(-b-a*t)* (1+b+a*t)) * (1 + np.sign(b + a*t))) +1/2)

def fonction_position_lineaire(t):
    return (1/2) * (t**2)

class Courbe:
    def __init__(self, vitesse_initiale, vitesse_finale, duree, temps_simulation) -> None:
        self.vitesse_initiale = vitesse_initiale
        self.vitesse_finale = vitesse_finale
        self.duree = duree
        self.temps_depart = temps_simulation

        self.last_position = 0

    def result_negatif(self, temps_simuation):
        if temps_simuation > self.temps_depart + self.duree:
            vitesse = self.vitesse_finale
            position = self.vitesse_finale * (temps_simuation - self.temps_depart) + self.last_position
        else:
            vitesse = fonction_vitesse_e((temps_simuation - self.temps_depart)/self.duree) * (self.vitesse_finale - self.vitesse_initiale) + self.vitesse_initiale
            position = (1-fonction_position_e((temps_simuation - self.temps_depart)/self.duree)) * abs(self.vitesse_finale - self.vitesse_initiale) * (temps_simuation - self.temps_depart) + min(vitesse_finale, vitesse_initiale) * (temps_simuation-self.temps_depart)      
        
        deplacement = position - self.last_position
        self.last_position = position
        return vitesse, deplacement
    
    def result_positif(self, temps_simuation):
        if temps_simuation > self.temps_depart + self.duree:
            vitesse = self.vitesse_finale
            position = self.vitesse_finale * (temps_simuation - self.temps_depart) + self.last_position
        else:
            vitesse = fonction_vitesse_e((temps_simuation - self.temps_depart)/self.duree) * (self.vitesse_finale - self.vitesse_initiale) + self.vitesse_initiale
            position = fonction_position_e((temps_simuation - self.temps_depart)/self.duree) * abs(self.vitesse_finale - self.vitesse_initiale) * (temps_simuation - self.temps_depart) + min(vitesse_finale, vitesse_initiale) * (temps_simuation-self.temps_depart)      
        
        deplacement = position - self.last_position
        self.last_position = position
        return vitesse, deplacement

    def result(self, temps_simuation):
        if self.vitesse_finale - self.vitesse_initiale < 0:
            return self.result_negatif(temps_simuation)
        else:
            return self.result_positif(temps_simuation)

vitesse_initiale = 1
vitesse_finale = 1
fps = 60
t0 = 0
tf = 9999
liste_temps = np.arange(0, tf*fps+1, 1) * 1/fps

courbe = Courbe(vitesse_initiale, vitesse_finale, tf-t0, t0)


vitesses = []
positions = []
position = 0
for t in liste_temps:
    vitesse, deplacement = courbe.result(t)
    vitesses.append(vitesse)
    position += deplacement
    positions.append(position)




plt.plot(liste_temps, positions, label='Position exacte')
plt.plot(liste_temps, vitesses, label='Vitesse')
plt.xlabel('t')
plt.ylabel('position / vitesse')
plt.title('Évolution de la position et de la vitesse')
plt.legend()
plt.grid(True)
plt.show()


