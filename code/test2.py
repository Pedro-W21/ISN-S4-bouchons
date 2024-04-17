from math import sqrt


distance_securite = 6
temps_deceleration = sqrt(distance_securite * 2 / (8 / 3.6))
vitesse_max = temps_deceleration * 8 

print(vitesse_max)


temps_deceleration = abs(0 - vitesse_max) / 8
distance_securite = 1/2 * (8 / 3.6) * temps_deceleration**2
print(distance_securite)

