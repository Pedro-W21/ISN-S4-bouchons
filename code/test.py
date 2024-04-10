from matplotlib import pyplot as plt
import numpy as np

temps_deceleration = abs(0 - 40) / 8
print(temps_deceleration)

distance = 1/2 * (8 / 3.6) * temps_deceleration**2
print(distance)