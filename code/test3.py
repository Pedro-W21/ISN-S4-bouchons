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


vitesse_initiale = 20
vitesse_finale = 10

t = np.linspace(0, 60, 600) * 1/60

vitesse = fonction_vitesse_e(t) * (vitesse_finale - vitesse_initiale) + vitesse_initiale
position = []
for ti in t:
    print(ti)
    # position.append(1/60 * vitesse[ti * 60])



# plt.plot(t, position, label='Position')
plt.plot(t, vitesse, label='Vitesse')
plt.xlabel('t')
plt.ylabel('position / vitesse')
plt.title('Évolution de la position et de la vitesse')
plt.legend()
plt.grid(True)
plt.show()


