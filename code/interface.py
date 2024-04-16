import customtkinter as ctk
from customtkinter import *
import json
from PIL import Image
import os
from os.path import abspath, dirname
from recup_donnees import Model
import numpy as np
import tkinter as tk
import math
from carte import Carte
from noeud import Noeud
from arete import Arete
from simulation import Simulation
from voiture import Voiture

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
BLUE = from_rgb((170, 170, 255))




class App(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.geometry('1200x800')
        self.title('Interface du début')
        #self.bind('<Motion>', self.motion)

        # Calculer la taille du cadre en fonction des dimensions de l'écran mais marche pas
        self.columnconfigure(0, weight=1, uniform='a')
        self.columnconfigure(1, weight=4, uniform='a')
        self.rowconfigure(0, weight=1, uniform='a')
        self.rowconfigure(1, weight=1, uniform='a')

        self.frame_modele = CTkFrame(self, fg_color='#4C6085')
        self.frame_modele.grid(row=0, column=0, pady=5, padx=5, sticky='nsew')

        self.frame_parametres = CTkFrame(self, fg_color='#4C6085')
        self.frame_parametres.grid(row=1, column=0, pady=5, padx=5, sticky='nsew')

        self.frame_carte = CTkFrame(self, fg_color='#4C6085')
        self.frame_carte.grid(row=0, column=1, rowspan=2, pady=5, padx=5, sticky='nsew')
        #initialisation des routes
        self.routes = {}
        self.simulation = None
        self.mode_affichage = "rien"
        self.largeur_carte = 10
        self.hauteur_carte = 10
        self.fini_affichage = False
        self.en_train_dafficher = False


        self.setup_frame_canvas()
        #actualise le dic des routes
        self.ajout_routes()

        #crée les tabviews
        self.tabview()

        #crée la tabview modele et création
        self.tabview_modele()
        self.tabview_creation()

        #cree la tabview parametres
        self.tabview_parametres_voitures()

        

        self.grille_affichee = False #initialisation de l'affichage grille


    def ajout_routes(self):
        """
        Ajout des routes dans le dictionnaire routes
        paramètres : aucun
        :return: aucun (actualise le dictionnaire "routes")
        """
        with open("routes.json", "r") as file:
            self.routes = json.load(file)

    def tabview(self):
        """
        Création des Tabview pour les différents onglets relatifs aux paramètres de la simulation
        paramètres : aucun
        :return:  aucun
        """
        self.tabview_model = CTkTabview(self.frame_modele, border_color='#32322C', border_width=2)
        self.tabview_model.pack(fill=BOTH, expand=True, padx=5, pady=5)

        self.tabview_parametres = CTkTabview(self.frame_parametres, border_color='#32322C', border_width=2)
        self.tabview_parametres.pack(fill=BOTH, expand=True, padx=5)


        self.modele = self.tabview_model.add('Modèle existant')
        self.creation = self.tabview_model.add('Création')

        self.parametres = self.tabview_parametres.add('Paramètres véhicules')

        self.update()


    ########## TABVIEW MODELE ##########
    def tabview_modele(self):
        """
        Importation/ creation modèle de route
        paramètres : aucun
        :return: la route choisie sous forme de ?
        """
        liste_nom_routes = []
        for nom_route in self.routes.keys():
            liste_nom_routes.append(nom_route)


        self.nom_route_combox = CTkComboBox(master=self.modele, values=liste_nom_routes)
        self.nom_route_combox.pack(side=TOP,expand=True)


        #toujours utile ce bouton ?
        #self.visualisation_route = CTkButton(master=self.modele, text="Visualiser la route")
        #self.visualisation_route.pack(side=TOP, expand=True)




        self.bouton_resize = CTkButton(master=self.modele, text="redimensionner le canvas")
        self.bouton_resize.pack(side=TOP, expand=True)
        self.bouton_resize.bind('<Button-1>', self.resize_func)

    def fonction_resize_canvas(self, event=None):
        if self.mode_affichage == "edition":
            if self.mode_avant == "simulation":
                self.canvas_affichage.delete("all")
                self.grille_canvas = []
            self.affiche_carte_dans_canvas(event)
        elif self.mode_affichage == "simulation":
            if self.mode_avant == "edition":
                self.canvas_affichage.delete("all")
                self.grille_canvas = []
            self.affiche_carte_dans_canvas(event)
            self.update_affiche_sim(event)
        self.mode_avant = self.mode_affichage

    def tabview_creation(self):

        self.longueur_x_Label = CTkLabel(master=self.creation, text="longueur (x)")
        self.longueur_x_Label.pack(side=TOP, expand=True)
        self.longueur_x_Label_affichees = CTkLabel(master=self.creation, text="", text_color="white")
        self.longueur_x_Label_affichees.pack(side=TOP, expand=True)
        self.largeur_x_scale = CTkSlider(master=self.creation, progress_color="white", from_=10, to=50, command=self.afficher_scale_creation)
        self.largeur_x_scale.pack(side=TOP, expand=True)


        self.hauteur_y_Label = CTkLabel(master=self.creation, text="hauteur (y)")
        self.hauteur_y_Label.pack(side=TOP, expand=True)
        self.hauteur_y_Label_affichees = CTkLabel(master=self.creation, text="", text_color="gold")
        self.hauteur_y_Label_affichees.pack(side=TOP, expand=True)
        self.hauteur_y_scale = CTkSlider(master=self.creation, progress_color="gold", from_=10, to=50, command=self.afficher_scale_creation)
        self.hauteur_y_scale.pack(side=TOP, expand=True)

        self.creer_route = CTkButton(master=self.creation, text="créer une route", fg_color="purple")
        self.creer_route.pack(side=TOP, expand=True)
        self.creer_route.bind('<Button-1>', self.creer_nouvelle_carte)

        self.generer_carte = CTkButton(master=self.creation, text="générer une carte")
        self.generer_carte.pack(side=TOP, expand=True)
        self.generer_carte.bind("<Button-1>", self.generer_carte_test)

        self.filtre_route = CTkButton(master=self.creation, text="appliquer le filtre")
        self.filtre_route.pack(side=TOP, expand=True)
        self.filtre_route.bind('<Button-1>', self.filtre_correction_carte)

        self.transforme_into_noeuds = CTkButton(master=self.creation, text="tester la conversion")
        self.transforme_into_noeuds.pack(side=TOP, expand=True)
        self.transforme_into_noeuds.bind('<Button-1>', self.test_transforme)
    
    def generer_carte_test(self, event=None):
        if self.mode_affichage == "edition":
            self.largeur_carte = int(self.largeur_x_scale.get())
            self.hauteur_carte = int(self.hauteur_y_scale.get())
            carte = Carte.genere_aleatoirement_2(self.largeur_carte, self.hauteur_carte)
            self.grille_route = carte.grille
            self.affiche_carte_dans_canvas()


    def test_transforme(self, event=None):
        carte = Carte(self.largeur_carte,self.hauteur_carte,self.grille_route)
        noeuds:list[Noeud] = carte.into_aretes_noeuds()
        for noeud in noeuds:
            for arete in noeud.aretes:
                self.affiche_arete(arete)

    def grille_to_canvas_pos(self, xc, yc):
        return (int(self.xo + xc * self.echelle), int(self.yo + yc * self.echelle))

    def affiche_arete(self, arete: Arete):
        sx = Noeud.size.get_x()
        sy = Noeud.size.get_y()
        x0, y0 = self.grille_to_canvas_pos(arete.position_depart.get_x() / sx, arete.position_depart.get_y() / sy)
        x1, y1 = self.grille_to_canvas_pos(arete.position_arrivee.get_x() / sx, arete.position_arrivee.get_y() / sy)
        decalage = int(self.echelle * 0.5)
        self.canvas_affichage.create_line(x0 + decalage, y0 + decalage, x1 + decalage, y1 + decalage, arrow="first",fill=BLUE)

    def afficher_scale_creation(self, event):
        """
        Récupère la valeur des sliders relatifs à la taille de l'écran
        :param event:
        :return: aucun (affiche la valeur des sliders)
        """
        longueur_x = self.largeur_x_scale.get()
        hauteur_y = self.hauteur_y_scale.get()
    
        if longueur_x < 10:
            self.longueur_x_Label_affichees.configure(text=f"{str(longueur_x)[0]}")
    
        if longueur_x == 100:
            self.longueur_x_Label_affichees.configure(text=f"{str(longueur_x)}")
    
        if longueur_x >= 10 and longueur_x < 100:
            self.longueur_x_Label_affichees.configure(text=f" {str(longueur_x)[:2]}")
    
        if hauteur_y < 10:
            self.hauteur_y_Label_affichees.configure(text=f"{str(hauteur_y)[0]}")
    
        if hauteur_y == 100:
            self.hauteur_y_Label_affichees.configure(text=f"{str(hauteur_y)}")
    
        if hauteur_y >= 10 and hauteur_y < 100:
            self.hauteur_y_Label_affichees.configure(text=f" {str(hauteur_y)[:2]}")


    def resize_func(self, event):
        """
        bloque le resize
        :param event:
        :return:
        """
        self.resizable(False, False)
        self.bool_previsualisation = False


    def creer_nouvelle_carte(self, event):
        """
        Création d'une nouvelle carte
        paramètres : aucun
        :return: aucun
        """
        print(f"longueur {int(self.largeur_x_scale.get())}, largeur : {int(self.hauteur_y_scale.get())}")

        if not self.en_train_dafficher :

            self.en_train_dafficher = True #pour savoir si on a affiché la grille
            self.largeur_carte = int(self.largeur_x_scale.get())
            self.hauteur_carte = int(self.hauteur_y_scale.get())

            self.canvas_affichage.delete("all")
            self.grille_canvas = []
            self.voitures = []
            self.grille_route = np.zeros((self.largeur_carte, self.hauteur_carte))
            self.routes_placees = 0

            self.previsualisation = False
            self.mode_affichage = "edition"
            self.mode_avant = "edition"
            self.affiche_carte_dans_canvas()
            self.en_train_dafficher = False

    def lance_simulation(self, event):
        self.filtre_correction_carte()

        carte = Carte(self.largeur_carte,self.hauteur_carte,self.grille_route)
        self.simulation = Simulation(carte, self.nombre_voiture_scale.get(), self.niveau_agressivite.get())

        self.mode_affichage = "simulation"

    ########## TABVIEW PARAMETRES ##########
    def tabview_parametres_voitures(self):
        """
        Création des paramètres pour les voitures (nombre de voitures, niveau d'agressivité)
        paramètres : aucun

        :return: aucun
        """



        self.nombre_voitures_Label = CTkLabel(master=self.parametres, text="nb voitures selectionnées")
        self.nombre_voitures_Label.pack(side=TOP, expand=True)
        self.nombre_voitures_Label_affichees = CTkLabel(master=self.parametres, text="", text_color="purple")
        self.nombre_voitures_Label_affichees.pack(side=TOP, expand=True)
        self.nombre_voiture_scale = CTkSlider(master=self.parametres, progress_color="purple", from_=1, to=100, command=self.afficher_scale_voitures)
        self.nombre_voiture_scale.pack(side=TOP, expand=True)


        self.niveau_agressivite_Label = CTkLabel(master=self.parametres, text="niveau d'agressivité")
        self.niveau_agressivite_Label.pack(side=TOP, expand=True)

        self.niveau_agressivite_Label_affichees = CTkLabel(master=self.parametres, text="", text_color="red")
        self.niveau_agressivite_Label_affichees.pack(side=TOP, expand=True)

        self.niveau_agressivite = CTkSlider(master=self.parametres, progress_color="red", from_=1, to=100, command=self.afficher_scale_voitures)
        self.niveau_agressivite.pack(side=TOP, expand=True)

        self.lance_simu_button = CTkButton(master=self.parametres, text="lancer simulation de test")
        self.lance_simu_button.pack(side=TOP, expand=True)
        self.lance_simu_button.bind("<Button-1>", self.lance_simulation)

        self.stop_simu_button = CTkButton(master=self.parametres, text="arrêter simulation")
        self.stop_simu_button.pack(side=TOP, expand=True)
        self.stop_simu_button.bind("<Button-1>", self.stop_simulation)

        self.carte_france_button = CTkButton(master=self.parametres, text="carte de France de l'agressivité")
        self.carte_france_button.pack(side=TOP, expand=True)
        self.carte_france_button.bind('<Button-1>', self.affichage_france)

        self.validation_para_button = CTkButton(master=self.parametres, text = "Coquin, valide !", text_color='black', fg_color ='pink')
        self.validation_para_button.pack(side=TOP, expand=True)
        self.validation_para_button.bind('<Button-1>', self.validew)

        self.bool_carte_affichee = False
    
    def stop_simulation(self, event):
        self.mode_affichage = "edition"

        self.simulation = None

    def afficher_scale_voitures(self, event):
        """
        Récupère la valeur des sliders relatifs aux voitures
        :param event:
        :return: aucun (affiche la valeur des sliders)
        """
        nb_voitures = self.nombre_voiture_scale.get()
        niveau_agressivite = self.niveau_agressivite.get()

        if nb_voitures < 10:
            self.nombre_voitures_Label_affichees.configure(text=f"{str(nb_voitures)[0]}")

        if nb_voitures == 100:
            self.nombre_voitures_Label_affichees.configure(text=f"{str(nb_voitures)}")

        if nb_voitures >= 10 and nb_voitures < 100:
            self.nombre_voitures_Label_affichees.configure(text=f" {str(nb_voitures)[:2]}")

        if niveau_agressivite < 10:
            self.niveau_agressivite_Label_affichees.configure(text=f"{str(niveau_agressivite)[0]}")

        if niveau_agressivite == 100:
            self.niveau_agressivite_Label_affichees.configure(text=f"{str(niveau_agressivite)}")

        if niveau_agressivite >= 10 and niveau_agressivite < 100:
            self.niveau_agressivite_Label_affichees.configure(text=f" {str(niveau_agressivite)[:2]}")

    def validew(self, event):
        model = Model()
        scale_1 = self.nombre_voiture_scale.get()
        scale_2 = self.niveau_agressivite.get()
        model.get_data(scale_1)
        model.get_data(scale_2)
        
    def affichage_france(self, event):
        """
        Affichage de la carte de France de l'agressivité
        :param event:
        :return: aucun (affiche la carte de France)
        """
        if not self.bool_carte_affichee :

            self.bool_carte_affichee = True


            self.france_topLevel= CTkToplevel(master=self)
            self.france_topLevel.geometry('500x500')
            self.france_topLevel.title("carte de France de l'agressivité")

            carte_France = CTkImage(light_image=Image.open('../photos/carte France.jpg'), size=(500, 500))
            carte_France_Label = CTkLabel(master=self.france_topLevel, image= carte_France, text="")
            carte_France_Label.pack(fill=BOTH, expand=True)


            # wait plutot que mainloop pour pouvoir changer ensuite le booleen et réafficher le booleen si désiré
            self.france_topLevel.wait_window()

            self.bool_carte_affichee = False



######### canvas du milieu ###############

    def setup_frame_canvas(self):




        self.label_affichage = CTkLabel(master =self.frame_carte, text="Affichage de la carte et de la simulation")
        self.label_affichage.pack(fill="x")
        self.largeur_canvas = 100
        self.hauteur_canvas = 100
        self.xo = 0
        self.yo = 0
        self.last_mouse_coords = None
        self.grille_canvas = []
        self.voitures = []
        self.voitures_canvas = []
        self.grille_route = np.zeros((self.largeur_carte, self.hauteur_carte))
        self.routes_placees = 0
        
        self.canvas_affichage = tk.Canvas(self.frame_carte, background="green")

        self.canvas_affichage.bind("<Configure>", self.fonction_resize_canvas)
        self.canvas_affichage.bind("<B1-Motion>", self.fonction_clique_gauche_canvas)
        self.canvas_affichage.bind("<Button-1>", self.fonction_clique_gauche_canvas)
        self.canvas_affichage.bind("<Button-3>", self.fonction_clique_droit_canvas)
        self.canvas_affichage.bind("<B3-Motion>", self.fonction_clique_droit_canvas)
        self.canvas_affichage.pack(fill="both", expand=True)
        self.frame_carte.grid(column=1, row=0, sticky='nsew')
        self.affiche_carte_dans_canvas()
        self.after(50, self.constant_canvas_update)

    def fonction_clique_gauche_canvas(self, event=None):
        if self.mode_affichage == "edition":
            
            self.rajoute_route_click(event)
        elif self.mode_affichage == "simulation":
            pass
    def fonction_clique_droit_canvas(self, event=None):
        if self.mode_affichage == "edition":
            self.enleve_route_click(event)
        elif self.mode_affichage == "simulation":
            pass
    
    def constant_canvas_update(self, event=None):
        if self.mode_affichage == "edition":
            self.surligne_case_selectionnee()
        elif self.mode_affichage == "simulation" and self.simulation != None:
            self.update_affiche_sim()
        self.after(50, self.constant_canvas_update)

    def update_affiche_sim(self, event=None):
        self.simulation.update()
        sx = Noeud.size.get_x()
        sy = Noeud.size.get_y()
        tx, ty = Voiture.size.get_x() / sx, Voiture.size.get_y() / sy
        tx, ty = self.grille_to_canvas_pos(tx, ty)
        tx *= 0.5
        ty *= 0.5
        sx, sy = Noeud.size.get_x(), Noeud.size.get_y()
        if len(self.voitures_canvas) != len(self.voitures) or len(self.voitures) == 0:
            self.voitures:list[Voiture] = self.simulation.recuperer_voitures()
            self.canvas_affichage.delete(self.voitures_canvas)
            self.voitures_canvas = []
            for voiture in self.voitures:
                xv, yv = voiture.position.get_x() / sx, voiture.position.get_y() / sy
                x_aff, y_aff = self.grille_to_canvas_pos(xv, yv)
                self.voitures_canvas.append(self.canvas_affichage.create_rectangle(x_aff - tx, y_aff - ty, x_aff + tx, y_aff + ty, fill=BLUE))
        elif len(self.voitures_canvas) == len(self.voitures):
            for (i, voiture) in enumerate(self.voitures):
                xv, yv = voiture.position.get_x() / sx, voiture.position.get_y() / sy
                x_aff, y_aff = self.grille_to_canvas_pos(xv, yv)
                self.canvas_affichage.moveto(self.voitures_canvas[i], x_aff - tx, y_aff - ty)

    def resize_voitures(self):
        sx = Noeud.size.get_x()
        sy = Noeud.size.get_y()
        tx, ty = Voiture.size.get_x() / sx, Voiture.size.get_y() / sy
        tx, ty = self.grille_to_canvas_pos(tx, ty)
        tx *= 0.5
        ty *= 0.5
        sx, sy = Noeud.size.get_x(), Noeud.size.get_y()
        if len(self.voitures_canvas) != len(self.voitures) or len(self.voitures) == 0:
            self.voitures:list[Voiture] = self.simulation.recuperer_voitures()
            self.canvas_affichage.delete(self.voitures_canvas)
            self.voitures_canvas = []
            for voiture in self.voitures:
                xv, yv = voiture.position.get_x() / sx, voiture.position.get_y() / sy
                x_aff, y_aff = self.grille_to_canvas_pos(xv, yv)
                self.voitures_canvas.append(self.canvas_affichage.create_rectangle(x_aff - tx, y_aff - ty, x_aff + tx, y_aff + ty, fill=BLUE))
        elif len(self.voitures_canvas) == len(self.voitures):
            for (i, voiture) in enumerate(self.voitures):
                xv, yv = voiture.position.get_x() / sx, voiture.position.get_y() / sy
                x_aff, y_aff = self.grille_to_canvas_pos(xv, yv)
                self.canvas_affichage.coords(self.voitures_canvas[i], x_aff - tx, y_aff - ty, x_aff + tx, y_aff + ty)


    def rajoute_route_click(self, event=None):
        coords = self.calcul_coordonnees_souris_carte()
        if coords != None:
            xc, yc = coords
            if self.position_posable(xc, yc):
                if self.grille_route[xc,yc] == 0:
                    self.routes_placees += 1
                self.grille_route[xc,yc] = 1
                self.canvas_affichage.itemconfigure(self.grille_canvas[yc * self.largeur_carte + xc], fill=self.couleur_de_case(xc, yc))
    def enleve_route_click(self, event=None):
        coords = self.calcul_coordonnees_souris_carte()
        if coords != None:
            xc, yc = coords
            if self.grille_route[xc,yc] == 1:
                self.routes_placees -= 1
            self.grille_route[xc,yc] = 0
            self.canvas_affichage.itemconfigure(self.grille_canvas[yc * self.largeur_carte + xc], fill=self.couleur_de_case(xc, yc))

    def surligne_case_selectionnee(self):
        coords = self.calcul_coordonnees_souris_carte()
        if coords != None:
            xc, yc = coords
            if self.last_mouse_coords == None:
                self.canvas_affichage.itemconfigure(self.grille_canvas[yc * self.largeur_carte + xc], fill=self.couleur_de_curseur(xc, yc))
            else:
                lxc, lyc = self.last_mouse_coords
                self.update_affichage_case(lxc, lyc)
                self.canvas_affichage.itemconfigure(self.grille_canvas[yc * self.largeur_carte + xc], fill=self.couleur_de_curseur(xc, yc))
        elif self.last_mouse_coords != None:
            lxc, lyc = self.last_mouse_coords
            self.update_affichage_case(lxc, lyc)
        self.last_mouse_coords = coords
        

    def update_affichage_case(self, xc, yc):
         self.canvas_affichage.itemconfigure(self.grille_canvas[yc * self.largeur_carte + xc], fill=self.couleur_de_case(xc, yc))

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
        if self.largeur_canvas != self.canvas_affichage.winfo_width() or self.hauteur_canvas != self.canvas_affichage.winfo_height() or not self.fini_affichage:
            self.fini_affichage = True
            self.calcul_echelle()
            self.xo, self.yo = 0, 0
            if self.canvas_affichage.winfo_height() < self.canvas_affichage.winfo_width():
                self.xo = self.canvas_affichage.winfo_width()//2 - self.canvas_affichage.winfo_height()//2
            else:
                self.yo = self.canvas_affichage.winfo_height()//2 - self.canvas_affichage.winfo_width()//2

            if len(self.grille_canvas) != self.largeur_carte * self.hauteur_carte:
                self.grille_canvas = []
                self.canvas_affichage.delete('all')
                nx = np.ones(self.largeur_carte+1) * self.xo + np.arange(0, self.largeur_carte+1) * self.echelle
                ny = np.ones(self.hauteur_carte+1) * self.yo + np.arange(0, self.hauteur_carte+1) * self.echelle
                for y in range(self.hauteur_carte):
                    for x in range(self.largeur_carte):
                        self.grille_canvas.append(self.canvas_affichage.create_rectangle(nx[x], ny[y], nx[x+1], ny[y+1], fill=self.couleur_de_case(x, y), outline=from_rgb((0,0,0))))
            else:
                nx = np.ones(self.largeur_carte+1) * self.xo + np.arange(0, self.largeur_carte+1) * self.echelle
                ny = np.ones(self.hauteur_carte+1) * self.yo + np.arange(0, self.hauteur_carte+1) * self.echelle
                for y in range(self.hauteur_carte):
                    for x in range(self.largeur_carte):
                        rect = self.grille_canvas[y * self.largeur_carte + x]
                        self.canvas_affichage.coords(rect, nx[x], ny[y], nx[x+1], ny[y+1])
                        self.canvas_affichage.itemconfigure(rect, fill=self.couleur_de_case(x, y))
            self.fini_affichage = False

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
        self.echelle = max(2, int(math.floor(dimension_minimum_canvas/dimension_maximum_carte)))


    def ajout_routes2(self):
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

    def affichage_route3(self, liste_route):
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

    def case_dedans_valide(self, xc, yc):
        checks = [(-1,0), (1,0), (0, 1), (0, -1)]
        ret = True
        if self.point_dans_grille_ou_0(xc, yc) == 1:
            total = 0
            for (dx, dy) in checks:
                total += self.point_dans_grille_ou_0(xc + dx, yc + dy)
            if total <= 1:
                ret = False
        return ret
    
    def case_bord_valide(self, xc, yc):
        checks = [-1, 1]
        bads = 0
        goods = 0
        ret = True
        if xc == 0 or xc == self.largeur_carte - 1:
            for dy in checks:
                bads += self.point_dans_grille_ou_0(xc, yc + dy)
            for dx in checks:
                goods += self.point_dans_grille_ou_0(xc + dx, yc)
        if yc == 0 or yc == self.hauteur_carte - 1:
            for dx in checks:
                bads += self.point_dans_grille_ou_0(xc + dx, yc)
            for dy in checks:
                goods += self.point_dans_grille_ou_0(xc, yc + dy)
        if bads > 0 and goods == 0:
            ret = False
        elif goods == 0:
            ret = False
        return ret
            

    def filtre_correction_carte(self, event=None):
        carte = Carte(self.largeur_carte, self.hauteur_carte, self.grille_route)
        carte.filtre_correction_carte()
        self.grille_route = carte.grille
        self.affiche_carte_dans_canvas()

    def applique_changements(self, changements):
        for xc, yc in changements:
            if self.grille_route[xc, yc] != 0:
                self.grille_route[xc, yc] = 0
                self.routes_placees -= 1
            self.update_affichage_case(xc, yc)
        

    

        
        

if __name__ == "__main__":
    os.chdir(dirname(abspath(__file__)))

    app = App()
    app.mainloop()
