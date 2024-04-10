import matplotlib.pyplot as plt

# Données du véhicule
puissance = 90 * 1.36 * 1000  # Puissance en chevaux
masse = 1250  # Masse en kg

# Liste des rapports de vitesse
rapports = [0, 1/5, 1/4, 1/3, 1/2, 1]

# Calcul de l'accélération pour chaque rapport de vitesse
accelerations = [(puissance * rapport) / masse for rapport in rapports]

# Tracé du graphique
plt.plot(rapports, accelerations)
plt.xlabel('Rapport de vitesse')
plt.ylabel('Accélération')
plt.title('Accélération en fonction du rapport de vitesse')
plt.grid(True)
plt.show()