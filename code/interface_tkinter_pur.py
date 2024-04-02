import tkinter as tk
import json
from PIL import Image, ImageTk
import os
from os.path import abspath, dirname

class Fenetre(tk.Tk):
    def __init__(self):
        super().__init__()

        self.geometry('1200x800')
        self.resizable(True, True)
        self.title('Interface de test tkinter')


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

        self.frame_canvas_affichage = tk.Frame(self,highlightbackground="black", highlightthickness=3)
        self.label_affichage = tk.Label(self.frame_canvas_affichage, text="Affichage de la carte et de la simulation", font="Calibri 16 bold")
        self.label_affichage.pack(side=tk.TOP, fill="x")
        self.canvas_affichage = tk.Canvas(self.frame_canvas_affichage, background="green")
        self.canvas_affichage.pack(fill="both", expand=True)
        self.frame_canvas_affichage.grid(column=1, row=0, sticky='nsew')

        self.previsualisation = False

        

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
        if not self.previsualisation :
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