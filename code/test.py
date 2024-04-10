import numpy as np

import matplotlib.pyplot as plt



# Paramètres
a = 0
b = 1/np.pi
c = 1
d = 0


# Création des données
x = np.linspace(-10, 10, 100)
y = np.arctan(a + b*np.arctan(c*x - d))


# Affichage de la courbe
plt.plot(x, y)
plt.xlabel('x')
plt.ylabel(f'arctan({a} + {b}*arctan({c}*x + {d}))')
plt.title('Courbe de arctan(a + b*arctan(c*x + d))')
plt.grid(True)
plt.show()