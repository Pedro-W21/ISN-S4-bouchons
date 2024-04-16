from matplotlib import pyplot as plt
import numpy as np
import voiture as voit
import noeud as nd
import arete as art
import vecteur_2d as vec2
import carte
import interface as inter
import courbe as cr
import simulation as simu

temps_deceleration = abs(0 - 40) / 8
print(temps_deceleration)

distance = 1/2 * (8 / 3.6) * temps_deceleration**2
print(distance)

carte_test = carte.Carte.genere_aleatoirement_2(20, 20)

sim_test = simu.Simulation(carte=carte_test, nombre_voiture=10.0, agressivite=0.5)
sim_test.update()

vecteur_t1 = vec2.Vecteur2D(10.0, 10.0)
vecteur_t2 = vec2.Vecteur2D(-10.0, 5.0)

vecteur_t1 + vecteur_t2
vecteur_t2 - vecteur_t1
vecteur_t1 * 10.0

carte_test_2 = carte.Carte(20, 20)

