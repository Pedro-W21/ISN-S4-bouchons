import customtkinter as ctk
from customtkinter import *
import json
from PIL import Image
import os
from os.path import abspath, dirname
from recup_donnees import Model




class App(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.geometry('1200x800')
        self.resizable(True, True)
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

        #actualise le dic des routes
        self.ajout_routes()

        #crée les tabviews
        self.tabview()

        #crée la tabview modele
        self.tabview_modele()

        #cree la tabview parametres
        self.tabview_parametres_voitures()


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

        self.tabview_carte = CTkTabview(self.frame_carte, border_color='#32322C', border_width=2)
        self.tabview_carte.pack(fill=BOTH, expand=True, padx=5, pady=5)

        self.modele = self.tabview_model.add('Modèle de route')
        self.parametres = self.tabview_parametres.add('Paramètres véhicules')
        self.carte = self.tabview_carte.add('Carte')

        self.update()

    def motion(self, event):
        x, y = event.x, event.y
        print('{}, {}'.format(x, y))

    def affiche_dims(self, event):
        print(f"{self.carte.winfo_height()} {self.carte.winfo_width()}")

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
        self.nom_route_combox.place(x=125, y=50, anchor="center")

        self.visualisation_route = CTkButton(master=self.modele, text="Visualiser la route")
        self.visualisation_route.place(x=125, y=125, anchor="center")
        self.visualisation_route.bind('<Button-1>', self.previsualisation_route)

        self.bouton_dims = CTkButton(master=self.modele, text="afficher les dimensions du canvas")
        self.bouton_dims.place(x=125, y=175, anchor="center")
        self.bouton_dims.bind("<Button-1>", self.affiche_dims)

        self.creer_route = CTkButton(master=self.modele, text="créer une route", fg_color="purple")
        self.creer_route.place(x=125, y=250, anchor="center")
        self.creer_route.bind('<Button-1>', self.creer_nouvelle_route)

        self.bool_previsualisation = False
    def creer_nouvelle_route(self, event):
        """
        Création d'une nouvelle route
        paramètres : aucun
        :return: aucun, ajoute une nouvelle route (nouveau dictionnaire) à self.routes
        """
        print('créer une nouvelle route')
    def previsualisation_route(self, event):
        """
        Prévisualisation de la route choisie
        paramètres : aucun
        :return: aucun, affiche la route choisie
        """
        for i in range(10):
            for j in range(10):
                label = CTkLabel(master=self.carte, text="", fg_color="blue")
                label.grid(row=i, column=j)




    def affichage_route(self, liste_route):
        """
        Affichage de la route choisie
        paramètres : liste_route
        :return: aucun, affiche la route choisie
        """
        route_types = {
            "route_vertical": "../photos/route_vertical.png",
            "route_horizontal": "../photos/route_horizontal.png",
            "route_haut_gauche": "../photos/route_gauche.png",
            "route_bas_droite": "../photos/route_bas_droite.png",
            "croix": "../photos/route_croix.png"
        }

        for name, positions in liste_route.items():
            for position in positions:
                self.create_route_label(route_types[name], position)

    def create_route_label(self, image_path, position):
        """
        Création d'un label pour chaque route
        :param image_path:
        :param position:
        :return: aucun (affiche les routes)
        """
        route_image = CTkImage(light_image=Image.open(image_path), size=(100, 100))
        route_label = CTkLabel(master=self.carte, image=route_image, text="")
        route_label.place(x=position[0], y=position[1], anchor="center")
        route_label.image = route_image

    ########## TABVIEW PARAMETRES ##########
    def tabview_parametres_voitures(self):
        """
        Création des paramètres pour les voitures (nombre de voitures, niveau d'agressivité)
        paramètres : aucun

        :return: aucun
        """

        self.nombre_voiture_scale = CTkSlider(master=self.parametres, progress_color="purple", from_=1, to=100, command=self.afficher_scale)
        self.nombre_voiture_scale.place(x=125, y=75, anchor="center")

        self.nombre_voitures_Label = CTkLabel(master=self.parametres, text="nb voitures selectionnées")
        self.nombre_voitures_Label.place(x=125, y=25, anchor="center")
        self.nombre_voitures_Label_affichees = CTkLabel(master=self.parametres, text="", text_color="purple")
        self.nombre_voitures_Label_affichees.place(x=125, y=50, anchor="center")


        self.niveau_agressivite = CTkSlider(master=self.parametres, progress_color="red", from_=1, to=100, command=self.afficher_scale)
        self.niveau_agressivite.place(x=125, y=175, anchor="center")

        self.niveau_agressivite_Label = CTkLabel(master=self.parametres, text="niveau d'agressivité")
        self.niveau_agressivite_Label.place(x=125, y=125, anchor="center")
        self.niveau_agressivite_Label_affichees = CTkLabel(master=self.parametres, text="", text_color="red")
        self.niveau_agressivite_Label_affichees.place(x=125, y=150, anchor="center")


        self.carte_france_button = CTkButton(master=self.parametres, text="carte de France de l'agressivité")
        self.carte_france_button.place(x=125, y=250, anchor="center")
        self.carte_france_button.bind('<Button-1>', self.affichage_france)

        self.validation_para_button = CTkButton(master=self.parametres, text = "Coquin, valide !", text_color='black', fg_color ='pink')
        self.validation_para_button.place(x=105, y=320, anchor="center")
        self.validation_para_button.bind('<Button-1>', self.validew)

        self.bool_carte_affichee = False
    def afficher_scale(self, event):
        """
        Récupère la valeur des sliders
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
        print(123,model.data)
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


if __name__ == "__main__":
    os.chdir(dirname(abspath(__file__)))

    app = App()
    app.mainloop()
