import tkinter as tk
import json
from PIL import Image, ImageTk
import os
from os.path import abspath, dirname
import math
import numpy as np

def from_rgb(rgb):
    """prend un tuple rgb et le transforme en string héxadécimal de couleur tkinter
    -----------------------------------
    Entrées : tuple rgb de 0 à 255 (R,G,B)

    Sortie : string d'héxadécimal

    note : fonction prise d'internet.
    """
    return "#%02x%02x%02x" % rgb

BLANC = from_rgb((255,255,255))
NOIR = from_rgb((0,0,0))
ROUGE = from_rgb((255,0,0))
VERT = from_rgb((0,255,0))

class Fenetre(tk.Tk):
    def __init__(self):
        super().__init__()

        self.geometry('1200x800')
        self.resizable(True, True)
        self.title('Interface de test tkinter')

        self.largeur_carte = 25
        self.hauteur_carte = 25
        self.echelle = 16 # Nombre de pixels de coté d'une case sur la grille

        self.columnconfigure(0, weight=1, uniform='a')
        self.columnconfigure(1, weight=4, uniform='a')
        self.rowconfigure(0, weight=4, uniform='a')
        self.rowconfigure(1, weight=1, uniform='a')

        self.frame_param_carte = tk.Frame(self, highlightbackground="black", highlightthickness=3)
        
        self.label_param_carte = tk.Label(self.frame_param_carte, text="Paramètres de la carte", font="Calibri 16 bold")
        self.label_param_carte.pack(side=tk.TOP, fill="x")

        self.ajout_routes()

        self.bouton_afficher_carte = tk.Button(self.frame_param_carte, text="Affiche la ville", command=self.essaie_affiche)
        self.bouton_afficher_carte.pack(side=tk.TOP, fill="x")

        self.frame_generation_carte = tk.Frame(self.frame_param_carte, highlightbackground="black", highlightthickness=3)
        self.label_gen_carte = tk.Label(self.frame_generation_carte, text="Génération de carte")
        self.label_gen_carte.pack(side=tk.TOP, fill="x")
        self.slider_largeur_carte = tk.Scale(self.frame_generation_carte, from_=10, to=50, orient="horizontal", label="Largeur")
        self.slider_largeur_carte.pack(side=tk.TOP, fill="x")
        self.slider_hauteur_carte = tk.Scale(self.frame_generation_carte, from_=10, to=50, orient="horizontal", label="Hauteur")
        self.slider_hauteur_carte.pack(side=tk.TOP, fill="x")
        self.bouton_genere_carte = tk.Button(self.frame_generation_carte, text="génère la carte")
        self.bouton_genere_carte.pack(side=tk.TOP, fill="x")

        self.frame_generation_carte.pack(side=tk.TOP, fill="x")

        self.frame_sauvegarde = tk.Frame(self.frame_param_carte, highlightbackground="black", highlightthickness=3)

        self.label_sauvegarde = tk.Label(self.frame_sauvegarde, text="sauvegarde de carte")
        self.label_sauvegarde.pack(side=tk.TOP, fill="x")
        self.sauvegarde_entry = tk.Entry(self.frame_sauvegarde)
        self.sauvegarde_entry.pack(side=tk.TOP, fill="x")
        self.bouton_sauvegarde = tk.Button(self.frame_sauvegarde, text="Sauvegarder avec ce nom")
        self.bouton_sauvegarde.pack(side=tk.TOP, fill="x")

        self.frame_sauvegarde.pack(side=tk.TOP, fill="x")

        self.frame_param_simu = tk.Frame(self, highlightbackground="black", highlightthickness=3)

        self.label_param_simu = tk.Label(self.frame_param_simu, text="Paramètres de\nla simulation", font="Calibri 16 bold")
        self.label_param_simu.pack(side=tk.LEFT, fill="y")

        self.frame_sliders = tk.Frame(self.frame_param_simu, highlightbackground="black", highlightthickness=3, padx=5)
        self.frame_sliders.rowconfigure(0, weight=1, uniform="a")
        self.frame_sliders.rowconfigure(1, weight=1, uniform="a")
        self.nb_voit_label = tk.Label(self.frame_sliders, text="Nombre de voitures")
        self.nb_voit_label.grid(column=0, row=0, sticky='nsew')
        self.agressivite_label = tk.Label(self.frame_sliders, text="Agressivité")
        self.agressivite_label.grid(column=0, row=1, sticky='nsew')
        self.slider_nb_voitures = tk.Scale(self.frame_sliders, from_=1, to=100, orient="horizontal")
        self.slider_nb_voitures.grid(row=0, column=1, sticky='nsew')
        self.slider_agressivite = tk.Scale(self.frame_sliders, from_=1, to=100, orient="horizontal")
        self.slider_agressivite.grid(row=1, column=1, sticky='nsew')

        self.frame_sliders.pack(side=tk.LEFT, fill="y")
        self.frame_param_simu.grid(column=0, row=1, columnspan=2, sticky='nsew')
        self.frame_param_carte.grid(column=0, row=0, sticky='nsew')
        self.setup_frame_canvas()
        

        self.previsualisation = False

        self.after(1000, self.affiche_carte_dans_canvas)
        self.after(50, self.surligne_case_selectionnee)

    def setup_frame_canvas(self):
        self.frame_canvas_affichage = tk.Frame(self,highlightbackground="black", highlightthickness=3)
        self.label_affichage = tk.Label(self.frame_canvas_affichage, text="Affichage de la carte et de la simulation", font="Calibri 16 bold")
        self.label_affichage.pack(side=tk.TOP, fill="x")
        self.largeur_canvas = 100
        self.hauteur_canvas = 100
        self.xo = 0
        self.yo = 0
        self.last_mouse_coords = None
        self.grille_canvas = []
        self.grille_route = np.zeros((self.largeur_carte, self.hauteur_carte))
        self.routes_placees = 0
        self.canvas_affichage = tk.Canvas(self.frame_canvas_affichage, background="green")
        self.canvas_affichage.bind("<Configure>", self.affiche_carte_dans_canvas)
        self.canvas_affichage.bind("<B1-Motion>", self.rajoute_route_click)
        self.canvas_affichage.bind("<B3-Motion>", self.enleve_route_click)
        self.canvas_affichage.pack(fill="both", expand=True)
        self.frame_canvas_affichage.grid(column=1, row=0, sticky='nsew')

    def rajoute_route_click(self, event=None):
        coords = self.calcul_coordonnees_souris_carte()
        if coords != None:
            xc, yc = coords
            if self.position_posable(xc, yc):
                if self.grille_route[xc,yc] == 0:
                    self.routes_placees += 1
                self.grille_route[xc,yc] = 1
                self.canvas_affichage.itemconfigure(self.grille_canvas[yc * self.hauteur_carte + xc], fill=self.couleur_de_case(xc, yc))
    def enleve_route_click(self, event=None):
        coords = self.calcul_coordonnees_souris_carte()
        if coords != None:
            xc, yc = coords
            if self.grille_route[xc,yc] == 1:
                self.routes_placees -= 1
            self.grille_route[xc,yc] = 0
            self.canvas_affichage.itemconfigure(self.grille_canvas[yc * self.hauteur_carte + xc], fill=self.couleur_de_case(xc, yc))

    def surligne_case_selectionnee(self):
        coords = self.calcul_coordonnees_souris_carte()
        if coords != None:
            xc, yc = coords
            if self.last_mouse_coords == None:
                self.canvas_affichage.itemconfigure(self.grille_canvas[yc * self.hauteur_carte + xc], fill=self.couleur_de_curseur(xc, yc))
            else:
                lxc, lyc = self.last_mouse_coords
                self.canvas_affichage.itemconfigure(self.grille_canvas[lyc * self.hauteur_carte + lxc], fill=self.couleur_de_case(lxc, lyc))
                self.canvas_affichage.itemconfigure(self.grille_canvas[yc * self.hauteur_carte + xc], fill=self.couleur_de_curseur(xc, yc))
        elif self.last_mouse_coords != None:
            lxc, lyc = self.last_mouse_coords
            self.canvas_affichage.itemconfigure(self.grille_canvas[lyc * self.hauteur_carte + lxc], fill=self.couleur_de_case(lxc, lyc))
        self.last_mouse_coords = coords
        self.after(50, self.surligne_case_selectionnee)

    def calcul_coordonnees_souris_carte(self):
        xs, ys = self.winfo_pointerxy()
        xs -= self.canvas_affichage.winfo_rootx() + self.xo
        ys -= self.canvas_affichage.winfo_rooty() + self.yo
        xc, yc = xs // self.echelle, ys // self.echelle
        ret = None
        if 0 <= xc < self.largeur_carte and 0 <= yc < self.hauteur_carte:
            ret = (xc, yc)
        return ret

    def couleur_de_case(self, xc, yc):
        ret = BLANC
        if self.grille_route[xc, yc] == 1:
            ret = NOIR
        return ret

    def couleur_de_curseur(self, xc, yc):
        ret = ROUGE
        if self.position_posable(xc, yc):
            ret = VERT
        return ret

    def affiche_carte_dans_canvas(self, event=None):
        if self.largeur_canvas != self.canvas_affichage.winfo_width() or self.hauteur_canvas != self.canvas_affichage.winfo_height():
            self.calcul_echelle()
            self.xo, self.yo = 0, 0
            if self.canvas_affichage.winfo_height() < self.canvas_affichage.winfo_width():
                self.xo = self.canvas_affichage.winfo_width()//2 - self.canvas_affichage.winfo_height()//2
            else:
                self.yo = self.canvas_affichage.winfo_height()//2 - self.canvas_affichage.winfo_width()//2
            
            if len(self.grille_canvas) == 0:
                self.canvas_affichage.delete('all')
                nx = np.ones(self.largeur_carte+1) * self.xo + np.arange(0, self.largeur_carte+1) * self.echelle
                ny = np.ones(self.hauteur_carte+1) * self.yo + np.arange(0, self.hauteur_carte+1) * self.echelle
                for y in range(self.hauteur_carte):
                    for x in range(self.largeur_carte):
                        self.grille_canvas.append(self.canvas_affichage.create_rectangle(nx[x], ny[y], nx[x+1], ny[y+1], fill=from_rgb((255,255,255)), outline=from_rgb((0,0,0))))
            elif 0 < len(self.grille_canvas) < self.largeur_carte * self.hauteur_carte:
                pass
            else:
                nx = np.ones(self.largeur_carte+1) * self.xo + np.arange(0, self.largeur_carte+1) * self.echelle
                ny = np.ones(self.hauteur_carte+1) * self.yo + np.arange(0, self.hauteur_carte+1) * self.echelle
                for y in range(self.hauteur_carte):
                    for x in range(self.largeur_carte):
                        rect = self.grille_canvas[y * self.largeur_carte + x]
                        self.canvas_affichage.coords(rect, nx[x], ny[y], nx[x+1], ny[y+1])
                        #self.canvas_affichage.itemconfigure() 

    def position_posable(self, xc, yc) -> bool:
        positions_a_check_coins = [[(-1, -1), (-1, 0), (0, -1)], [(-1, 1), (-1, 0), (0, 1)], [(1,1), (0,1), (1,0)], [(1, -1), (0, -1), (1,0)]] # triplets de positions de coins
        ret = True
        for triplet in positions_a_check_coins:
            compte = 0
            for (dx, dy) in triplet:
                compte += self.point_dans_grille_ou_0(xc + dx, yc + dy)
            if compte == 3:
                ret = False

        positions_a_check_cotes = [(-1,0), (1,0), (0, 1), (0, -1)]
        total_cotes = 0
        for (dx, dy) in positions_a_check_cotes:
            total_cotes += self.point_dans_grille_ou_0(xc + dx, yc + dy)
        if total_cotes == 0 and self.routes_placees > 0:
            ret = False
        return ret
    def point_dans_grille_ou_0(self, xc, yc) -> int:
        ret = 0
        if 0 <= xc < self.largeur_carte and 0 <= yc < self.hauteur_carte:
            ret = self.grille_route[xc,yc]
        return ret
    def calcul_echelle(self):
        self.largeur_canvas = self.canvas_affichage.winfo_width()
        self.hauteur_canvas = self.canvas_affichage.winfo_height()
        dimension_minimum_canvas = min(self.largeur_canvas, self.hauteur_canvas)
        dimension_maximum_carte = max(self.largeur_carte, self.hauteur_carte)
        self.echelle = int(math.floor(dimension_minimum_canvas/dimension_maximum_carte))


    def ajout_routes(self):
        """
        Ajout des routes dans le dictionnaire routes
        paramètres : aucun
        :return: aucun (actualise le dictionnaire "routes")
        """
        with open("routes.json", "r") as file:
            self.routes = json.load(file)

        self.liste_cartes = tk.Listbox(self.frame_param_carte)
        for route in self.routes.keys():
            self.liste_cartes.insert("end", route)
        self.liste_cartes.pack(side=tk.TOP, fill="x")


    def essaie_affiche(self, event=None):
        if not self.previsualisation and False: # LE AND FALSE EST JUSTE RAJOUTE POUR DESACTIVER LA FEATURE
            self.previsualisation = True

            route_choisie = self.liste_cartes.get("active")
            self.label_affichage.configure(text=f"Visualisation de la carte {route_choisie}")


            self.affichage_route(self.routes[route_choisie])

            self.previsualisation = False

    def affichage_route(self, liste_route):
        route_types = {
            "route_vertical": "../photos/route_vertical.png",
            "route_horizontal": "../photos/route_horizontal.png",
            "route_haut_gauche": "../photos/route_gauche.png",
            "route_bas_droite": "../photos/route_bas_droite.png",
            "croix": "../photos/route_croix.png"
        }

        self.images = {
            type_route:ImageTk.PhotoImage(Image.open(route_path)) for type_route, route_path in route_types.items()
        }
        for name, positions in liste_route.items():
            for position in positions:
                self.canvas_affichage.create_image(position[0], position[1], image=self.images[name], anchor=tk.NW)
        self.update()
        self.update_idletasks()

if __name__ == "__main__":
    os.chdir(dirname(abspath(__file__)))

    fenetre = Fenetre()
    fenetre.mainloop()