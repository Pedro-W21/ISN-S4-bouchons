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