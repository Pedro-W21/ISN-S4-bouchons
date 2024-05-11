import customtkinter as ctk
from customtkinter import TOP, BOTH, BOTTOM, RIGHT, LEFT, INSERT, EXTENDED, END
from PIL import Image as PILImage
import os
from os.path import abspath, dirname
import numpy as np
import tkinter as tk
from tkinter import messagebox
import math
from carte import Carte
from noeud import Noeud
from arete import Arete
from simulation import Simulation
from voiture import Voiture
import time

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
DARK_BLUE = from_rgb((0, 0, 170))

class App(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.geometry('1200x850')
        self.minsize(1000, 800)
        self.title('Interface du début')
        #self.bind('<Motion>', self.motion)

        # Calculer la taille du cadre en fonction des dimensions de l'écran mais marche pas
        self.columnconfigure(0, weight=1, uniform='a')
        self.columnconfigure(1, weight=3, uniform='a')
        self.rowconfigure(0, weight=1, uniform='a')
        self.rowconfigure(1, weight=1, uniform='a')

        self.frame_modele = ctk.CTkFrame(self, fg_color='#4C6085')
        self.frame_modele.grid(row=0, column=0, pady=5, padx=5, sticky='nsew')

        self.frame_parametres = ctk.CTkFrame(self, fg_color='#4C6085')
        self.frame_parametres.grid(row=1, column=0, pady=5, padx=5, sticky='nsew')

        self.frame_carte = ctk.CTkFrame(self, fg_color='#4C6085')
        self.frame_carte.grid(row=0, column=1, rowspan=2, pady=5, padx=5, sticky='nsew')
        #initialisation des routes
        self.routes = []
        self.simulation = None
        self.simulation_en_cours = False
        self.max_voiture = 100
        self.mode_avant = "rien"
        self.mode_affichage = "edition"
        self.largeur_carte = 10
        self.hauteur_carte = 10
        self.ms_entre_update = 50
        self.fini_affichage = False
        self.en_train_dafficher = False


        self.setup_frame_canvas()

        #crée les tabviews
        self.tabview()

        #crée la tabview modele et création
        self.tabview_modele()
        self.tabview_creation()
        self.tabview_generation()

        #cree la tabview parametres
        self.tabview_parametres_voitures()

        

        self.grille_affichee = False #initialisation de l'affichage grille


    def ajout_routes(self):
        """
        Ajout des routes sauvegardées dans la liste des routes
        paramètres : aucun
        :return: aucun (actualise le dictionnaire "routes")
        """
        fichiers = os.listdir("../routes")
        if self.routes != fichiers:
            self.routes.clear()
            for route in fichiers:
                self.routes.append(route)
            self.nom_route_combox.configure(values=self.routes)
            if self.nom_route_combox.get() not in self.routes:
                self.nom_route_combox.set("Choisissez ici")
                self.bouton_chargement.grid_forget()
                self.bouton_supprimer.grid_forget()
                self.carte_choisie_bool = False
        self.after(2000, self.ajout_routes)


    def tabview(self):
        """
        Création des Tabview pour les différents onglets relatifs aux paramètres de la simulation
        paramètres : aucun
        :return:  aucun
        """
        self.tabview_model = ctk.CTkTabview(self.frame_modele, border_color='#32322C', border_width=2)
        self.tabview_model.pack(fill=BOTH, expand=True, padx=5, pady=5)

        self.tabview_parametres = ctk.CTkTabview(self.frame_parametres, border_color='#32322C', border_width=2)
        self.tabview_parametres.pack(fill=BOTH, expand=True, padx=5)


        self.modele = self.tabview_model.add('Modèle existant')
        self.creation = self.tabview_model.add('Création')
        self.generation = self.tabview_model.add('Génération')

        self.parametres = self.tabview_parametres.add('Paramètres véhicules')

        self.update()

    ########## TABVIEW MODELE ##########
    def tabview_modele(self):
        """
        Importation/ creation modèle de route
        paramètres : aucun
        :return: la route choisie sous forme de ?
        """

        self.modele.columnconfigure(0, weight=1, uniform='a')
        self.modele.rowconfigure(0, weight=1, uniform='a')
        self.modele.rowconfigure(1, weight=1, uniform='a')
        self.modele.rowconfigure(2, weight=1, uniform='a')
        self.modele.rowconfigure(3, weight=1, uniform='a')



        self.carte_choisie_bool = False
        self.nom_route_combox = ctk.CTkComboBox(master=self.modele, values=["Choisissez ici"], command= self.afficher_bouton_valider, width=150)
        self.nom_route_combox.grid(row=0, column=0)
        #self.nom_route_combox.pack(side=TOP,expand=True, fill="x")




        self.image_sauvegarde = ctk.CTkImage(light_image=PILImage.open('../photos/sauvegarde.png'), size=(30, 30))

        self.bouton_valider = ctk.CTkButton(master=self.modele, text="   sauvegarder la carte", image=self.image_sauvegarde, compound="left")
        self.bouton_valider.grid(row=3, column=0, padx=10)
        #self.bouton_valider.pack(side=BOTTOM, expand=True, fill="x")
        self.bouton_valider.bind("<Button-1>", self.topLevel_validation_carte)
        

        self.bouton_chargement = ctk.CTkButton(master=self.modele, text="charger la carte choisie")
        
        self.bouton_chargement.bind("<Button-1>", self.charge_carte)

        self.bouton_supprimer = ctk.CTkButton(master=self.modele, text="Supprimer la carte")
        #self.bouton_supprimer.grid(row=3, column=0, padx=10)
        self.bouton_supprimer.bind("<Button-1>", self.supprime_carte)

        self.ajout_routes()

    def supprime_carte(self, event=None):
        """
        supprime la carte choisie dans la combobox

        input : event, inutilisé mais indispensable pour utiliser cette fonction en callback
        return : rien

        effets secondaires : suppression de fichier
        """
        if self.nom_route_combox.get() != "Choisissez ici":
            try:
                os.remove("../routes/" + self.nom_route_combox.get())
            except Exception:
                print("erreur pour supprimer")

    def afficher_bouton_valider(self,event=None):
        if self.nom_route_combox.get() != "Choisissez ici" and not self.carte_choisie_bool:
            self.bouton_chargement.grid(row=1, column=0, padx=10)
            self.bouton_supprimer.grid(row=2, column=0, padx=10)
            self.carte_choisie_bool = True
        elif self.nom_route_combox.get() == "Choisissez ici":
            self.bouton_chargement.grid_forget()
            self.bouton_supprimer.grid_forget()
            self.carte_choisie_bool = False





    def topLevel_validation_carte(self, event=None):
        """
        Crée une fenêtre de validation de la carte
        """

        self.toplevel = ctk.CTkToplevel()
        self.toplevel.title("Sauvegarder la carte")
        self.toplevel.geometry("300x125")
        self.toplevel.resizable(False, False)
        self.toplevel.grab_set()


        self.entree_sauvegarde = ctk.CTkEntry(master=self.toplevel, placeholder_text="Nom du fichier")
        self.entree_sauvegarde.pack(side=TOP, pady=15)
        self.bouton_sauvegarde = ctk.CTkButton(master=self.toplevel, text="sauvegarder la carte actuelle")
        self.bouton_sauvegarde.pack(side=TOP, pady=10)
        self.bouton_sauvegarde.bind("<Button-1>", self.sauvegarde_carte)





    def assure_existence_dossier_routes(self):
        """
        garanti que le dossier "../routes/" existe à la fin de cette fonction

        input : rien
        return : rien

        effets secondaires : création du dossier routes
        """
        if "routes" not in os.listdir("../"):
            os.mkdir("../routes")

    def nom_fichier_valide(self,nom:str):
        """
        renvoie True si nom est un nom de fichier valide sans extension, False sinon

        input : nom, str 
        return : booléen
        """
        caracteres_interdits = [":", ".", "#", "/", "'\'", "\n"]
        return not any(cara in nom for cara in caracteres_interdits) and len(nom.strip()) > 1


    def sauvegarde_carte(self, event=None):
        """
        gère la sauvegarde de la carte actuelle dans le fichier de nom donné par l'utilisateur dans l'Entry associé

        input : event, inutilisé mais nécessaire pour l'utiliser comme callback
        output : aucun

        effets secondaires : changement du système de fichier et/ou mise à jour du texte dans le Entry
        """
        nom = self.entree_sauvegarde.get()

        if self.nom_fichier_valide(nom):
            carte = Carte(self.largeur_carte, self.hauteur_carte, self.grille_route)
            self.assure_existence_dossier_routes()
            carte.sauvegarder_carte(nom.strip() + ".json")
            self.toplevel.destroy()
            
        else:
            print('non valide')
            self.entree_sauvegarde.delete(0, END)
            messagebox.showinfo("Information", "Le nom du fichier ne doit pas contenir de caractères spéciaux")
            # self.entree_sauvegarde.delete(0, END)
            # self.entree_sauvegarde.insert(INSERT, "Nom invalide")

    def charge_carte(self, event=None):
        """
        gère le chargement de la carte choisie par l'utilisateur

        input : event, inutilisé mais nécessaire pour l'utiliser comme callback
        output : aucun

        effets secondaires : changement de la carte en cours d'édition et mise à jour de l'affichage
        """
        nom = self.nom_route_combox.get()
        carte = Carte.charger_carte(nom)
        if carte != None:
            self.stop_simulation()
            self.largeur_carte = carte.largeur
            self.hauteur_carte = carte.hauteur
            self.grille_route = carte.grille
            self.affiche_carte_dans_canvas()


    def fonction_resize_canvas(self, event=None):
        """
        gère le redimensionnement du canvas, peu importe la source

        input : event, inutilisé mais nécessaire pour l'utiliser comme callback
        output : aucun

        effets secondaires : changement de l'affichage dans le canvas
        """
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
            self.affiche_sim()
        self.mode_avant = self.mode_affichage

    def tabview_generation(self):
        """
        paramétrise la partie "génération" de l'interface d'édition de carte

        input : aucun
        return : aucun

        effets secondaires : création et agencement 
        """
        self.largeur_x_Label_gen = ctk.CTkLabel(master=self.generation, text="largeur (x)")
        self.largeur_x_Label_gen.pack(side=TOP, expand=True, fill="x")
        self.largeur_x_Label_affichees_gen = ctk.CTkLabel(master=self.generation, text=f"{self.largeur_carte}", text_color="white")
        self.largeur_x_Label_affichees_gen.pack(side=TOP, expand=True, fill="x")
        self.largeur_x_scale_gen = ctk.CTkSlider(master=self.generation, progress_color="white", from_=10, to=50, command=self.afficher_scale_generation)
        self.largeur_x_scale_gen.set(self.largeur_carte)
        self.largeur_x_scale_gen.pack(side=TOP, expand=True, fill="x")


        self.hauteur_y_Label_gen = ctk.CTkLabel(master=self.generation, text="hauteur (y)")
        self.hauteur_y_Label_gen.pack(side=TOP, expand=True, fill="x")
        self.hauteur_y_Label_affichees_gen = ctk.CTkLabel(master=self.generation, text=f"{self.hauteur_carte}", text_color="white")
        self.hauteur_y_Label_affichees_gen.pack(side=TOP, expand=True, fill="x")
        self.hauteur_y_scale_gen = ctk.CTkSlider(master=self.generation, progress_color="white", from_=10, to=50, command=self.afficher_scale_generation)
        self.hauteur_y_scale_gen.set(self.hauteur_carte)
        self.hauteur_y_scale_gen.pack(side=TOP, expand=True, fill="x")

        self.nb_noeuds_label_gen = ctk.CTkLabel(master=self.generation, text="nombre de noeuds maximum à poser")
        self.nb_noeuds_label_gen.pack(side=TOP, expand=True, fill="x")
        self.nb_noeuds_label_affichees_gen = ctk.CTkLabel(master=self.generation, text=f"{5}", text_color="white")
        self.nb_noeuds_label_affichees_gen.pack(side=TOP, expand=True, fill="x")
        self.nb_noeuds_scale_gen = ctk.CTkSlider(master=self.generation, progress_color="white", from_=1, to=100, command=self.afficher_scale_generation)
        self.nb_noeuds_scale_gen.set(5)
        self.nb_noeuds_scale_gen.pack(side=TOP, expand=True, fill="x")

        self.dst_noeuds_label_gen = ctk.CTkLabel(master=self.generation, text="distance minimale entre noeuds")
        self.dst_noeuds_label_gen.pack(side=TOP, expand=True, fill="x")
        self.dst_noeuds_label_affichees_gen = ctk.CTkLabel(master=self.generation, text=f"{1}", text_color="white")
        self.dst_noeuds_label_affichees_gen.pack(side=TOP, expand=True, fill="x")
        self.dst_noeuds_scale_gen = ctk.CTkSlider(master=self.generation, progress_color="white", from_=1, to=min(self.largeur_carte, self.hauteur_carte) - 2, command=self.afficher_scale_generation)
        self.dst_noeuds_scale_gen.set(1)
        self.dst_noeuds_scale_gen.pack(side=TOP, expand=True, fill="x")


        self.generer_carte = ctk.CTkButton(master=self.generation, text="générer une carte aléatoirement")
        self.generer_carte.pack(side=TOP, expand=True, fill="x")
        self.generer_carte.bind("<Button-1>", self.generer_carte_test)

    def tabview_creation(self):
        """
        paramétrise la partie "création" de l'interface d'édition de carte

        input : aucun
        return : aucun

        effets secondaires : création et agencement des widgets tkinter associés à cette tab
        """
        self.largeur_x_Label = ctk.CTkLabel(master=self.creation, text="largeur (x)")
        self.largeur_x_Label.pack(side=TOP, expand=True, fill="x")
        self.largeur_x_Label_affichees = ctk.CTkLabel(master=self.creation, text=f"{self.largeur_carte}", text_color="white")
        self.largeur_x_Label_affichees.pack(side=TOP, expand=True, fill="x")
        self.largeur_x_scale = ctk.CTkSlider(master=self.creation, progress_color="white", from_=10, to=50, command=self.afficher_scale_creation)
        self.largeur_x_scale.set(self.largeur_carte)
        self.largeur_x_scale.pack(side=TOP, expand=True, fill="x")


        self.hauteur_y_Label = ctk.CTkLabel(master=self.creation, text="hauteur (y)")
        self.hauteur_y_Label.pack(side=TOP, expand=True, fill="x")
        self.hauteur_y_Label_affichees = ctk.CTkLabel(master=self.creation, text=f"{self.hauteur_carte}", text_color="white")
        self.hauteur_y_Label_affichees.pack(side=TOP, expand=True, fill="x")
        self.hauteur_y_scale = ctk.CTkSlider(master=self.creation, progress_color="white", from_=10, to=50, command=self.afficher_scale_creation)
        self.hauteur_y_scale.set(self.hauteur_carte)
        self.hauteur_y_scale.pack(side=TOP, expand=True, fill="x")

        self.creer_route = ctk.CTkButton(master=self.creation, text="créer une grille vide")
        self.creer_route.pack(side=TOP, expand=True, fill="x")
        self.creer_route.bind('<Button-1>', self.creer_nouvelle_carte)

        self.filtre_route = ctk.CTkButton(master=self.creation, text="appliquer le filtre")
        self.filtre_route.pack(side=TOP, expand=True, fill="x")
        self.filtre_route.bind('<Button-1>', self.filtre_correction_carte)

        self.transforme_into_noeuds = ctk.CTkButton(master=self.creation, text="tester la conversion")
        self.transforme_into_noeuds.pack(side=TOP, expand=True, fill="x")
        self.transforme_into_noeuds.bind('<Button-1>', self.test_transforme)
    
    def generer_carte_test(self, event=None):
        """
        génère et affiche une carte à partir des paramètres donnés par l'utilisateur

        input : event, inutilisé mais nécessaire dans la définition pour l'utiliser en tant que callback
        return : rien

        effets secondaires : changement et écrasement de la carte stockée dans self.grille_route, et affichage de la nouvelle carte dans le canvas
        """
        if self.mode_affichage == "edition":
            self.stop_simulation()
            self.largeur_carte = int(self.largeur_x_scale_gen.get())
            self.hauteur_carte = int(self.hauteur_y_scale_gen.get())
            noeuds = int(self.nb_noeuds_scale_gen.get())
            distance_entre_noeuds = int(self.dst_noeuds_scale_gen.get())
            carte = Carte.genere_aleatoirement(self.largeur_carte, self.hauteur_carte, noeuds, distance_entre_noeuds)
            self.grille_route = carte.grille
            self.affiche_carte_dans_canvas()


    def test_transforme(self, event=None):
        carte = Carte(self.largeur_carte,self.hauteur_carte,self.grille_route)
        noeuds:list[Noeud] = carte.into_aretes_noeuds()
        for noeud in noeuds:
            for arete in noeud.aretes:
                self.affiche_arete(arete)

    def grille_to_canvas_pos(self, xc, yc):
        """
        transforme une position dans la grille entière en position d'affichage utilisable dans la création ou la modifications d'objets du canvas

        input : xc, yc entiers
        return : tuple xg, yg de coordonnées entières transformées dans la base du canvas

        """
        return (int(self.xo + xc * self.echelle), int(self.yo + yc * self.echelle))

    def affiche_arete(self, arete: Arete):
        """
        Affiche l'arête donnée sur le canvas d'affichage au bon endroit

        input : arete de type Arete
        return : rien

        effets secondaires : changement de l'affichage dans le canvas
        """
        sx = Noeud.size.get_x()
        sy = Noeud.size.get_y()
        x0, y0 = self.grille_to_canvas_pos(arete.position_depart.get_x() / sx, arete.position_depart.get_y() / sy)
        x1, y1 = self.grille_to_canvas_pos(arete.position_arrivee.get_x() / sx, arete.position_arrivee.get_y() / sy)
        decalage = int(self.echelle * 0.5)
        self.canvas_affichage.create_line(x0 + decalage, y0 + decalage, x1 + decalage, y1 + decalage, arrow="first",fill=BLUE)

    def afficher_scale_generation(self, event):
        """
        met à jour les scale dans le tabview de génération

        input : event, inutilisé mais nécessaire pour utiliser cette fonction en callback
        output : rien

        effets secondaires : modification de l'affichage des scale
        """

        largeur_x = self.largeur_x_scale_gen.get()
        hauteur_y = self.hauteur_y_scale_gen.get()
        noeuds = self.nb_noeuds_scale_gen.get()
        distance = self.dst_noeuds_scale_gen.get()
        
        self.largeur_x_Label_affichees_gen.configure(text=f"{str(int(largeur_x))}")
        
        self.hauteur_y_Label_affichees_gen.configure(text=f"{str(int(hauteur_y))}")

        self.nb_noeuds_label_affichees_gen.configure(text=f"{str(int(noeuds))}")

        max_dist = min(int(largeur_x), int(hauteur_y)) - 2

        self.dst_noeuds_label_affichees_gen.configure(text=f"{str(int(distance))}")
        self.dst_noeuds_scale_gen.set(min(distance, max_dist))
        self.dst_noeuds_scale_gen.configure(to=max_dist)

    def afficher_scale_creation(self, event):
        """
        Récupère la valeur des sliders relatifs à la taille de l'écran
        :param event:
        :return: aucun (affiche la valeur des sliders)
        """
        largeur_x = self.largeur_x_scale.get()
        hauteur_y = self.hauteur_y_scale.get()
    
        self.largeur_x_Label_affichees.configure(text=f"{str(int(largeur_x))}")
        
        self.hauteur_y_Label_affichees.configure(text=f"{str(int(hauteur_y))}")


    def creer_nouvelle_carte(self, event):
        """
        Création d'une nouvelle carte
        paramètres : aucun
        :return: aucun
        """
        #print(f"longueur {int(self.largeur_x_scale.get())}, largeur : {int(self.hauteur_y_scale.get())}")
        self.stop_simulation()
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

    def lance_simulation(self, event = None):
        """
        lance la simulation si la carte actuelle associée est valide

        input : event, inutilisé mais nécessaire pour utiliser cette fonction en callback
        return : rien

        effets secondaires : changement de mode d'utilisation du canvas
        """
        
        if self.carte_valide():
            self.filtre_correction_carte()
            carte = Carte(self.largeur_carte,self.hauteur_carte,self.grille_route)
            self.simulation = Simulation(carte, int(self.nombre_voiture_scale.get()), self.niveau_agressivite.get())

            self.mode_affichage = "simulation"
            self.met_a_jour_infos_simu(True)
        else:
            messagebox.showinfo("Erreur de simulation", "La carte actuelle n'est pas utilisable pour une simulation")

    ########## TABVIEW PARAMETRES ##########
    def tabview_parametres_voitures(self):
        """
        Création des paramètres pour les voitures (nombre de voitures, niveau d'agressivité)
        paramètres : aucun

        :return: aucun
        """
        
        self.nombre_voitures_Label = ctk.CTkLabel(master=self.parametres, text="nb voitures selectionnées")
        self.nombre_voitures_Label.pack(side=TOP, expand=True, fill="x")
        self.nombre_voitures_stringvar = ctk.StringVar(master=self.parametres)
        self.nombre_voitures_stringvar.trace_add("write", self.affiche_entry_nb_voitures)
        self.nombre_voitures_entry = ctk.CTkEntry(master=self.parametres, textvariable=self.nombre_voitures_stringvar)
        self.nombre_voitures_entry.pack(side=TOP)
        self.nombre_voitures_entry.insert(0, "1")
        # self.nombre_voitures_Label_affichees = ctk.CTkLabel(master=self.parametres, text=f"{1}")
        # self.nombre_voitures_Label_affichees.pack(side=TOP, expand=True, fill="x")
        self.nombre_voiture_scale = ctk.CTkSlider(master=self.parametres, from_=1, to=self.max_voiture, command=self.afficher_scale_voitures)
        self.nombre_voiture_scale.pack(side=TOP, expand=True, fill="x")
        self.nombre_voiture_scale.set(1)

        self.niveau_agressivite_Label = ctk.CTkLabel(master=self.parametres, text="niveau d'agressivité")
        self.niveau_agressivite_Label.pack(side=TOP, expand=True, fill="x")
        self.niveau_agressivite_stringvar = ctk.StringVar(master=self.parametres)
        self.niveau_agressivite_stringvar.trace_add("write", self.affiche_entry_agressivite)
        self.niveau_agressivite_entry = ctk.CTkEntry(master=self.parametres, textvariable=self.niveau_agressivite_stringvar)
        self.niveau_agressivite_entry.pack(side=TOP)
        self.niveau_agressivite_entry.insert(0, "10")
        # self.niveau_agressivite_Label_affichees = ctk.CTkLabel(master=self.parametres, text=f"{10}")
        # self.niveau_agressivite_Label_affichees.pack(side=TOP, expand=True, fill="x")
        self.niveau_agressivite = ctk.CTkSlider(master=self.parametres, from_=1, to=100, command=self.afficher_scale_voitures)
        self.niveau_agressivite.set(10)
        self.niveau_agressivite.pack(side=TOP, expand=True, fill="x")

        self.iter_par_sec_Label = ctk.CTkLabel(master=self.parametres, text="Itérations de simulation par seconde")
        self.iter_par_sec_Label.pack(side=TOP, expand=True, fill="x")
        self.iter_par_sec_stringvar = ctk.StringVar(master=self.parametres)
        self.iter_par_sec_stringvar.trace_add("write", self.affiche_entry_ips)
        self.iter_par_sec_entry = ctk.CTkEntry(master=self.parametres, textvariable=self.iter_par_sec_stringvar)
        self.iter_par_sec_entry.pack(side=TOP)
        self.iter_par_sec_entry.insert(0, "20")
        self.iter_par_sec = ctk.CTkSlider(master=self.parametres, from_=5, to=30, command=self.afficher_scale_voitures)
        self.iter_par_sec.set(20)
        self.iter_par_sec.pack(side=TOP, expand=True, fill="x")

        self.vitesse_de_simu_Label = ctk.CTkLabel(master=self.parametres, text="Vitesse de simulation")
        self.vitesse_de_simu_Label.pack(side=TOP, expand=True, fill="x")
        self.vitesse_de_simu_Label_affichees = ctk.CTkLabel(master=self.parametres, text=f"{1.0}")
        self.vitesse_de_simu_Label_affichees.pack(side=TOP, expand=True, fill="x")
        self.vitesse_de_simu = ctk.CTkSlider(master=self.parametres, from_=0.25, to=2.0, number_of_steps=7, command=self.afficher_scale_voitures)
        self.vitesse_de_simu.set(1.0)
        self.vitesse_de_simu.pack(side=TOP, expand=True, fill="x")

        self.lance_simu_button = ctk.CTkButton(master=self.parametres, text="Lancer une simulation")
        self.lance_simu_button.pack(side=TOP, expand=True, fill="x")
        self.lance_simu_button.bind("<Button-1>", self.pause_play_simulation)

        self.stop_simu_button = ctk.CTkButton(master=self.parametres, text="arrêter simulation")
        self.stop_simu_button.pack(side=TOP, expand=True, fill="x")
        self.stop_simu_button.bind("<Button-1>", self.stop_simulation)

        self.carte_france_button = ctk.CTkButton(master=self.parametres, text="carte de France de l'agressivité")
        # self.carte_france_button.pack(side=TOP, expand=True, fill="x")
        self.carte_france_button.bind('<Button-1>', self.affichage_france)

        self.bind("<space>", self.frame_by_frame)

        self.bool_carte_affichee = False

    def selectionne_voiture(self, event=None):
        """
        permet de sélectionner une voiture et d'afficher ses caractéristiques
        input : event, utile pour retrouver l'ID du canvas de la voiture en question
        return : rien

        effets secondaires : modification de l'affichage
        """
        voiture_cliquee = event.widget.find_withtag("current")[0]
        i = 0
        while i < len(self.voitures_canvas) and voiture_cliquee != self.voitures_canvas[i]:
            i += 1
        self.voiture_select = self.voitures[i]
        self.label_info_id_select.configure(text=f"ID de la voiture : {self.voiture_select.id}")
        self.label_info_id_select.grid(column=1, row=0, sticky="W", padx=5)
        pos, angle = self.voiture_select.recuperer_position()
        xv, yv = pos.get_x() / Noeud.size.get_x(), pos.get_y() / Noeud.size.get_y()
        pos_voiture = self.grille_to_canvas_pos(xv, yv)
        rayon_cercle = self.echelle * 0.4 * (min(Voiture.size.get_x(), Voiture.size.get_y())/Noeud.size.get_x())
        if self.selection_voiture_select != None:
            self.canvas_affichage.delete(self.selection_voiture_select)
        self.selection_voiture_select = self.canvas_affichage.create_oval(pos_voiture[0] - rayon_cercle, pos_voiture[1] - rayon_cercle, pos_voiture[0] + rayon_cercle, pos_voiture[1] + rayon_cercle, outline=NOIR, fill=BLANC)
        self.label_info_pos_select.grid(column=2, row=0, sticky="W", padx=5)
        self.label_info_vitesse_select.grid(column=3, row=0, sticky="W", padx=5)
        self.label_info_distance_obstacles.grid(column=4, row=0, sticky="W", padx=5)
        self.label_info_obstacles_noeuds.grid(column=1, columnspan=3, row=1, sticky="W", padx=5)
        self.label_info_obstacles_voitures.grid(column=4, columnspan=1, row=1, sticky="W", padx=5)

    def update_affichage_voiture_select(self):
        """
        met à jour les labels et les objets de canvas liés à la voiture sélectionnée

        input:rien
        return:rien

        effets secondaires : mise à jour de l'interface
        """
        if self.voiture_select != None:
            if self.voiture_select.affiche:
                self.label_info_pos_select.configure(text=f"Position : {(int(self.voiture_select.position.get_x() * 100.0/Noeud.size.get_x())/100.0, int(self.voiture_select.position.get_y() * 100.0/Noeud.size.get_y())/100.0)}")
                self.label_info_vitesse_select.configure(text=f"Vitesse : {int(self.voiture_select.vitesse * 100.0/Noeud.size.get_x()) / 100.0}")
                if self.last_chemin_len != len(self.voiture_select.chemin):
                    for fleche in self.chemin_voiture_select:
                        self.canvas_affichage.delete(fleche)
                    self.chemin_voiture_select = []
                    for i in range(len(self.voiture_select.chemin) - 1):
                        start_node = self.voiture_select.chemin[i]
                        start_node_pos = self.grille_to_canvas_pos(start_node.position.get_x()/Noeud.size.get_x(), start_node.position.get_y()/Noeud.size.get_y())
                        end_node = self.voiture_select.chemin[i + 1]
                        end_node_pos = self.grille_to_canvas_pos(end_node.position.get_x()/Noeud.size.get_x(), end_node.position.get_y()/Noeud.size.get_y())
                        self.chemin_voiture_select.append(self.canvas_affichage.create_line(start_node_pos[0] + 0.5 * self.echelle, start_node_pos[1] + 0.5 * self.echelle, end_node_pos[0] + 0.5 * self.echelle, end_node_pos[1] + 0.5 * self.echelle, arrow="last", fill=BLUE))
                    self.last_chemin_len = len(self.voiture_select.chemin)
                else:
                    for (i,fleche) in enumerate(self.chemin_voiture_select):
                        start_node = self.voiture_select.chemin[i]
                        start_node_pos = self.grille_to_canvas_pos(start_node.position.get_x()/Noeud.size.get_x(), start_node.position.get_y()/Noeud.size.get_y())
                        end_node = self.voiture_select.chemin[i + 1]
                        end_node_pos = self.grille_to_canvas_pos(end_node.position.get_x()/Noeud.size.get_x(), end_node.position.get_y()/Noeud.size.get_y())
                        self.canvas_affichage.coords(fleche, start_node_pos[0] + 0.5 * self.echelle, start_node_pos[1] + 0.5 * self.echelle, end_node_pos[0] + 0.5 * self.echelle, end_node_pos[1] + 0.5 * self.echelle)
                        
                pos, angle = self.voiture_select.recuperer_position()
                xv, yv = pos.get_x() / Noeud.size.get_x(), pos.get_y() / Noeud.size.get_y()
                pos_voiture = self.grille_to_canvas_pos(xv, yv)
                rayon_cercle = 0.4 * self.echelle * min(Voiture.size.get_x(), Voiture.size.get_y())/Noeud.size.get_x()
                self.canvas_affichage.coords(self.selection_voiture_select, pos_voiture[0] - rayon_cercle, pos_voiture[1] - rayon_cercle, pos_voiture[0] + rayon_cercle, pos_voiture[1] + rayon_cercle)
                self.canvas_affichage.tag_raise(self.selection_voiture_select)
                if self.voiture_select.voiture_obstacle != None:
                    self.label_info_distance_obstacles.configure(text=f"Distance à voiture : {(int(self.voiture_select.distance_voiture_obstacle/100.0)*100.0)/Noeud.size.get_x()}")
                    self.label_info_obstacles_voitures.configure(text=f"ID voiture obstacle : {self.voiture_select.voiture_obstacle.id}")
                else:
                    self.label_info_distance_obstacles.configure(text=f"Pas de voiture obstacle")
                    self.label_info_obstacles_voitures.configure(text=f"Pas de voiture obstacle")
                positions_distances_noeuds_obstacles = []
                for (noeud, distance) in self.voiture_select.noeuds_obstacles_longueur:
                    position = (noeud.position.get_x()/Noeud.size.get_x(), noeud.position.get_y()/Noeud.size.get_y())
                    positions_distances_noeuds_obstacles.append((position, int((distance/Noeud.size.get_x()) * 100.0)/100.0))
                if len(positions_distances_noeuds_obstacles) > 0:
                    self.label_info_obstacles_noeuds.configure(text=f"Noeuds obstacles : {positions_distances_noeuds_obstacles}")
                else:
                    self.label_info_obstacles_noeuds.configure(text=f"Pas de Noeuds obstacles")
            else:
                self.deselectionne_voiture()

    def deselectionne_voiture(self, event=None):
        """
        fait disparaître tous les affichages liés à une voiture sélectionnée

        input : event, inutilisé mais nécessaire pour utiliser cette fonction en callback
        return : rien

        effets secondaires : modifie l'affichage dans le canvas
        """
        self.label_info_id_select.grid_forget()
        self.label_info_pos_select.grid_forget()
        self.label_info_vitesse_select.grid_forget()
        self.label_info_distance_obstacles.grid_forget()
        self.label_info_obstacles_noeuds.grid_forget()
        self.label_info_obstacles_voitures.grid_forget()
        for fleche in self.chemin_voiture_select:
            self.canvas_affichage.delete(fleche)
        self.chemin_voiture_select = []
        self.canvas_affichage.delete(self.selection_voiture_select)
        self.selection_voiture_select = None
        self.voiture_select = None
        self.last_chemin_len = -1

    def frame_by_frame(self, event=None):
        """
        avance la simulation d'une itération si elle est existante et en pause
        input : event, inutilisé mais nécessaire pour utiliser cette fonction en callback
        return : rien

        effets secondaires : avancée de la simulation
        """
        if self.simulation != None and not self.simulation_en_cours:
            self.simulation.update(True, (1.0/self.iter_par_sec.get())*self.vitesse_de_simu.get())
            self.met_a_jour_infos_simu(False)

    def recupere_nombre_entier(self, texte):
        """
        prends un mot et récupère un nombre entier ou une chaîne de chars vide
        input : texte, str à filtrer
        return : un str contenant que des chiffres ou rien

        """
        nombres = "0123456789"
        a_enlever = []
        for (pos, chara) in enumerate(texte):
            if chara not in nombres:
                a_enlever.append(pos)
        resultat = ""
        for pos in range(len(texte)):
            if pos not in a_enlever:
                resultat += texte[pos]
        return resultat
            
    def affiche_entry_nb_voitures(self, event=None, arg2=None, arg3=None):
        """
        met à jour le scale du nombre de voitures si l'entry est modifiée
        input : event, arg2, arg3 : inutilisé mais nécessaire pour utiliser cette fonction en callback de trace
        return : rien

        effets secondaires : modification du scale de nombre de voitures 
        """
        texte = self.nombre_voitures_stringvar.get()
        resultat = self.recupere_nombre_entier(texte)
        try:
            resultat = str(min(self.max_voiture, int(resultat)))
            self.nombre_voitures_stringvar.set(resultat)
            nb_voitures = int(resultat)
            self.nombre_voiture_scale.set(nb_voitures)
            if self.simulation != None:
                self.simulation.mettre_a_jour_nombre_voiture(nb_voitures)
        except Exception:
            if resultat != "":
                print("problémo dans affiche_entry_voitures")
    
    def affiche_entry_agressivite(self, event=None, arg2=None, arg3=None):
        """
        met à jour le scale de l'agressivité si besoin
        input : event, arg2, arg3 : inutilisé mais nécessaire pour utiliser cette fonction en callback de trace
        return : rien

        effets secondaires : modification du scale d'agressivité
        """
        texte = self.niveau_agressivite_stringvar.get()
        resultat = self.recupere_nombre_entier(texte)
        try:
            resultat = str(min(100,int(resultat)))
            self.niveau_agressivite_stringvar.set(resultat)
            agressivite = int(resultat)/100.0
            self.niveau_agressivite.set(int( resultat))
            if self.simulation != None:
                self.simulation.mettre_a_jour_agressivite(agressivite)
        except Exception:
            if resultat != "":
                print("problémo dans affiche_entry_agressivite")

    def affiche_entry_ips(self, event=None, arg2=None, arg3=None):
        """
        met à jour le scale de l'agressivité si besoin
        input : event, arg2, arg3 : inutilisé mais nécessaire pour utiliser cette fonction en callback de trace
        return : rien

        effets secondaires : modification du scale d'agressivité
        """
        texte = self.iter_par_sec_stringvar.get()
        resultat = self.recupere_nombre_entier(texte)
        try:
            resultat = str(min(30,int(resultat)))
            self.iter_par_sec_stringvar.set(resultat)
            self.iter_par_sec.set(int( resultat))
        except Exception:
            if resultat != "":
                print("problémo dans affiche_entry_agressivite")

    def pause_play_simulation(self, event):
        """
        permet de mettre en pause la simulation ou de la relancer si elle est en pause
        input : event, inutilisé mais nécessaire pour utiliser cette fonction en callback
        return : rien

        effets secondaires : changement de l'état de pause de la simulation, qui affecte la mise à jour de celle-ci
        """
        if self.simulation == None:
            self.lance_simulation()
            if self.simulation != None:
                self.simulation_en_cours = True
                self.lance_simu_button.configure(text="Mettre en pause la simulation")
        elif self.simulation_en_cours:
            self.simulation_en_cours = False
            self.lance_simu_button.configure(text="Reprendre la simulation")
        else:
            self.simulation_en_cours = True
            self.lance_simu_button.configure(text="Mettre en pause la simulation")

    def stop_simulation(self, event=None):
        """
        arrête la simulation en cours

        input : event, inutilisé mais nécessaire pour utiliser cette fonction en callback
        return : rien

        effets secondaires : modification de l'affichage dans le canvas et élimination de la simulation actuelle
        """
        self.mode_affichage = "edition"
        for voit in self.voitures_canvas:
            self.canvas_affichage.delete(voit)
        self.voitures = []
        self.lance_simu_button.configure(text="Lancer une simulation")
        self.simulation = None
        self.met_a_jour_infos_simu(True)
        self.deselectionne_voiture()

    def afficher_scale_voitures(self, event):
        """
        Récupère la valeur des sliders relatifs aux voitures
        :param event:
        :return: aucun (affiche la valeur des sliders)
        """
        nb_voitures = self.nombre_voiture_scale.get()
        niveau_agressivite = self.niveau_agressivite.get()
        ips = self.iter_par_sec.get()
        self.ms_entre_update = int((1.0/ips) * 1000)
        vitesse_simu = self.vitesse_de_simu.get()

        self.nombre_voitures_entry.delete(0, END)
        self.nombre_voitures_entry.insert(0, f"{str(int(nb_voitures))}")

        self.niveau_agressivite_entry.delete(0, END)
        self.niveau_agressivite_entry.insert(0, f"{str(int(niveau_agressivite))}")

        self.iter_par_sec_entry.delete(0, END)
        self.iter_par_sec_entry.insert(0, f"{str(int(ips))}")

        self.vitesse_de_simu_Label_affichees.configure(text=f"{str(vitesse_simu)}")

        if self.simulation != None:
            self.simulation.mettre_a_jour_nombre_voiture(int(nb_voitures))
            self.simulation.mettre_a_jour_agressivite(niveau_agressivite/100.0)
        
    def affichage_france(self, event):
        """
        Affichage de la carte de France de l'agressivité
        :param event:
        :return: aucun (affiche la carte de France)
        """
        if not self.bool_carte_affichee :

            self.bool_carte_affichee = True


            self.france_topLevel= ctk.CTkToplevel(master=self)
            self.france_topLevel.geometry('500x500')
            self.france_topLevel.title("carte de France de l'agressivité")

            carte_France = ctk.CTkImage(light_image=Image.open('../photos/carte France.jpg'), size=(500, 500))
            carte_France_Label = ctk.CTkLabel(master=self.france_topLevel, image= carte_France, text="")
            carte_France_Label.pack(fill=BOTH, expand=True)


            # wait plutot que mainloop pour pouvoir changer ensuite le booleen et réafficher le booleen si désiré
            self.france_topLevel.wait_window()

            self.bool_carte_affichee = False

    def met_a_jour_infos_simu(self, moment_de_changement):
        """
        met à jour et affiche le frame d'informations de la simulation si la simulation est là
        input : moment_de_changement, booléen indiquant si c'est un moment où la frame (pas son contenu) doit être caché ou montré
        return : rien

        effets secondaires : modification de l'affichage de la frame d'infos
        """
        if self.simulation != None:
            if moment_de_changement:
                self.canvas_affichage.pack_forget()
                self.frame_infos.pack(fill="x")
                self.canvas_affichage.pack(fill="both", expand=True)
            self.label_info_temps.configure(text=f"Temps : {int(self.simulation.temps_simulation * 100.0)/100.0}")
            self.label_info_voitures.configure(text=f"Voitures visibles : {len(self.voitures)}")

        else:
            if moment_de_changement:
                self.frame_infos.pack_forget()


    ######### canvas du milieu ###############

    def setup_frame_canvas(self):
        """
        crée le contenu du frame contenant l'affichage et les attributs liés à l'affichage dans le canvas

        input : rien
        output : rien

        effets secondaires : agencement du canvas et de son frame et affichage d'une carte vide par défaut sur le canvas
        """

        self.label_affichage = ctk.CTkLabel(master =self.frame_carte, text="Affichage de la carte et de la simulation")
        self.label_affichage.pack(fill="x")


        self.frame_infos = ctk.CTkFrame(master=self.frame_carte)
        self.frame_infos.columnconfigure(0, weight=1, uniform='a')
        self.frame_infos.columnconfigure(1, weight=1, uniform='a')
        self.frame_infos.columnconfigure(2, weight=1, uniform='a')
        self.frame_infos.columnconfigure(3, weight=1, uniform='a')
        self.frame_infos.columnconfigure(4, weight=1, uniform='a')

        self.frame_infos.rowconfigure(0, weight=1, uniform='a')
        self.frame_infos.rowconfigure(1, weight=1, uniform='a')

        self.label_info_temps = ctk.CTkLabel(self.frame_infos, text=f"Temps : {0.0}")
        self.label_info_temps.grid(column=0, row=0, sticky="W", padx=5)
        self.label_info_voitures = ctk.CTkLabel(self.frame_infos, text=f"Voitures visibles : {0}")
        self.label_info_voitures.grid(column=0, row=1, sticky="W", padx=5)
        self.label_info_id_select = ctk.CTkLabel(self.frame_infos, text="", bg_color=DARK_BLUE)
        self.label_info_vitesse_select = ctk.CTkLabel(self.frame_infos, text="", bg_color=DARK_BLUE)
        self.label_info_pos_select = ctk.CTkLabel(self.frame_infos, text="", bg_color=DARK_BLUE)
        self.label_info_distance_obstacles = ctk.CTkLabel(self.frame_infos, text="", bg_color=DARK_BLUE)
        self.label_info_obstacles_voitures = ctk.CTkLabel(self.frame_infos, text="", bg_color=DARK_BLUE)
        self.label_info_obstacles_noeuds = ctk.CTkLabel(self.frame_infos, text="", bg_color=DARK_BLUE)

        self.voiture_select = None
        self.chemin_voiture_select = []
        self.selection_voiture_select = None
        self.last_chemin_len = -1

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
        self.after(100, self.affiche_carte_dans_canvas)

    def fonction_clique_gauche_canvas(self, event=None):
        """
        gère le clique gauche dans le canvas en fonction du mode d'affichage de celui-ci

        input : event, inutilisé mais nécessaire pour utiliser cette méthode en callback
        return : rien

        effets secondaires : rajout de route en mode édition avec mise à jour de l'affichage si besoin
        """
        if self.mode_affichage == "edition":
            self.rajoute_route_click(event)

        elif self.mode_affichage == "simulation":
            pass
    def fonction_clique_droit_canvas(self, event=None):
        """
        gère le clique droit dans le canvas en fonction du mode d'affichage de celui-ci
        
        input : event, inutilisé mais nécessaire pour utiliser cette méthode en callback
        return : rien

        effets secondaires : enlèvement de route en mode édition avec mise à jour de l'affichage si besoin
        """
        if self.mode_affichage == "edition":
            self.enleve_route_click(event)
        elif self.mode_affichage == "simulation":
            pass
    
    def constant_canvas_update(self, event=None):
        """
        fonction auto-appelante qui gère les mises à jour constante de l'état du programme en fonction du mode d'affichage

        input : event, inutilisé mais nécessaire pour utiliser cette méthode en callback
        return : rien

        effets secondaires : surlignage conditionnel de la case en dessous du curseur en mode edition, et mise à jour de la simulation et de l'affichage des voitures en mode simulation 
        """
        debut = time.monotonic()
        if self.mode_affichage == "edition":
            self.surligne_case_selectionnee()
        elif self.mode_affichage == "simulation" and self.simulation != None:
            if self.simulation_en_cours:
                self.simulation.update(True, (1.0/self.iter_par_sec.get())*self.vitesse_de_simu.get())
            self.affiche_sim()
            self.met_a_jour_infos_simu(False)
            self.update_affichage_voiture_select()
        duree = int((time.monotonic() - debut) * 1000.0)
        ms_jusquau_prochain = 1
        if duree < self.ms_entre_update:
            ms_jusquau_prochain = self.ms_entre_update - duree
        self.after(ms_jusquau_prochain, self.constant_canvas_update)

    def aff_to_state_voiture(self, voiture:Voiture) -> str:
        """
        renvoie le paramétrage nécessaire de l'objet canvas lié à cette voiture

        input : voiture de type Voiture
        return : str, soit "normal" pour une voiture à afficher, soit "hidden" pour une voiture à cacher
        """
        ret = "normal"
        if not voiture.affiche:
            ret = "hidden"
        return ret

    def get_transformed_car_coords(self, tx:int, ty:int, angle:float) -> tuple[int, int]:
        """
        renvoie les décalages x et y en pixel d'affichage autour du centre de la voiture correspondant à l'orientation de la voiture

        input : 
            - tx, ty, les décalages entiers calculés à partir de la taille standard orienté horizontalement de la voiture
            - angle : flottant représentant l'orientation par rapport à l'horizontale de la voiture, l'angle doit être en radians
        return : tuple (rtx, rty) d'entiers représentant les décalages transformés (la transformation peut être nulle)
        """
        ret = (tx, ty)
        if abs(math.sin(angle)) > 0.9:
            ret = (ty, tx)
        return ret

    def affiche_sim(self):
        """
        affiche l'état actuel des voitures de la simulation

        input : rien
        return : rien

        effets secondaires : changement de l'affichage sur le canvas, destruction d'objets dans le canvas, modification de self.voitures_canvas et self.voitures
        """
        sx = Noeud.size.get_x()
        sy = Noeud.size.get_y()
        tx, ty = Voiture.size.get_x() / sx, Voiture.size.get_y() / sy
        tx, ty = tx * self.echelle, ty * self.echelle
        tx *= 0.5
        ty *= 0.5
        sx, sy = Noeud.size.get_x(), Noeud.size.get_y()
        self.voitures:list[Voiture] = self.simulation.recuperer_voitures()
        if len(self.voitures_canvas) != len(self.voitures) or len(self.voitures) == 0:
            for voit in self.voitures_canvas:
                self.canvas_affichage.delete(voit)
            self.voitures_canvas = []
            for voiture in self.voitures:
                pos, angle = voiture.recuperer_position()
                xv, yv = pos.get_x() / sx, pos.get_y() / sy
                x_aff, y_aff = self.grille_to_canvas_pos(xv, yv)
                rtx, rty = self.get_transformed_car_coords(tx, ty, angle)
                voit = self.canvas_affichage.create_rectangle(x_aff - rtx, y_aff - rty, x_aff + rtx, y_aff + rty, fill=voiture.couleur, state=self.aff_to_state_voiture(voiture))
                self.canvas_affichage.tag_bind(voit, "<Button-1>", self.selectionne_voiture)
                self.voitures_canvas.append(voit)
        elif len(self.voitures_canvas) == len(self.voitures):
            for (i, voiture) in enumerate(self.voitures):
                pos, angle = voiture.recuperer_position()
                xv, yv = pos.get_x() / sx, pos.get_y() / sy
                x_aff, y_aff = self.grille_to_canvas_pos(xv, yv)
                rtx, rty = self.get_transformed_car_coords(tx, ty, angle)
                self.canvas_affichage.coords(self.voitures_canvas[i], x_aff - rtx, y_aff - rty, x_aff + rtx, y_aff + rty)
                self.canvas_affichage.itemconfigure(self.voitures_canvas[i], fill=voiture.couleur, state=self.aff_to_state_voiture(voiture))


    def rajoute_route_click(self, event=None):
        """
        rajoute une route et l'affiche en dessous du curseur sur la carte actuelle si la position est valide

        input : event, inutilisé mais nécessaire pour l'utiliser en callback
        return : rien

        effets secondaire : mise à jour de l'affichage, et de self.grille_route
        """
        coords = self.calcul_coordonnees_souris_carte()
        if coords != None:
            xc, yc = coords
            if self.position_posable(xc, yc):
                if self.grille_route[xc,yc] == 0:
                    self.routes_placees += 1
                self.grille_route[xc,yc] = 1
                self.canvas_affichage.itemconfigure(self.grille_canvas[yc * self.largeur_carte + xc], fill=self.couleur_de_case(xc, yc))
    def enleve_route_click(self, event=None):
        """
        enlève une route et affiche le changement en dessous du curseur sur la carte actuelle

        input : event, inutilisé mais nécessaire pour l'utiliser en callback
        return : rien

        effets secondaire : mise à jour de l'affichage, et de self.grille_route
        """
        coords = self.calcul_coordonnees_souris_carte()
        if coords != None:
            xc, yc = coords
            if self.grille_route[xc,yc] == 1:
                self.routes_placees -= 1
            self.grille_route[xc,yc] = 0
            self.canvas_affichage.itemconfigure(self.grille_canvas[yc * self.largeur_carte + xc], fill=self.couleur_de_case(xc, yc))

    def surligne_case_selectionnee(self):
        """
        surligne la case en dessous du curseur sur la carte en vert si l'utilisateur peut poser une route dessus, et rouge sinon

        input : rien
        return : rien

        effets secondaires : mise à jour de l'affichage, plus précisément de la dernière case survolée et de la nouvelle case survolée
        """
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
        

    def update_affichage_case(self, xc:int, yc:int):
        """
        met à jour la couleur de la case en (xc, yc) dans la grille avec la couleur de la case associée

        input :
            - xc : entier de coordonnée horizontale dans la carte actuelle
            - yc : entier de coordonnée verticale dans la carte actuelle
        return : rien
        
        effets secondaires : modification de l'affichage de la case en (xc, yc)
        """
        self.canvas_affichage.itemconfigure(self.grille_canvas[yc * self.largeur_carte + xc], fill=self.couleur_de_case(xc, yc))

    def calcul_coordonnees_souris_carte(self):
        """
        renvoie les coordonnées du curseur de la souris dans la carte si le curseur est dedans, None sinon

        input : rien
        return : tuple d'entiers (xc, yc) de coordonnées valides dans la carte actuelle ou None
        """
        xs, ys = self.winfo_pointerxy()
        xs -= self.canvas_affichage.winfo_rootx() + self.xo
        ys -= self.canvas_affichage.winfo_rooty() + self.yo
        xc, yc = xs // self.echelle, ys // self.echelle
        ret = None
        if 0 <= xc < self.largeur_carte and 0 <= yc < self.hauteur_carte:
            ret = (xc, yc)
        return ret

    def couleur_de_case(self, xc:int, yc:int) -> str:
        """
        renvoie la couleur de la case à afficher dans le canvas en fonction de sa valeur

        input : 
            - xc : entier de coordonnée horizontale dans la carte actuelle
            - yc : entier de coordonnée verticale dans la carte actuelle
        return : str de couleur HEX utilisable par Ctk, blanc si pas de route, noir si route
        """
        ret = BLANC
        if self.grille_route[xc, yc] == 1:
            ret = NOIR
        return ret

    def couleur_de_curseur(self, xc:int, yc:int):
        """
        renvoie la couleur de la case à afficher dans le canvas en fonction de si il est possible de poser une route dessus

        input : 
            - xc : entier de coordonnée horizontale dans la carte actuelle
            - yc : entier de coordonnée verticale dans la carte actuelle
        return : str de couleur HEX utilisable par Ctk, rouge si pas posable, vert si posable
        """
        ret = ROUGE
        if self.position_posable(xc, yc):
            ret = VERT
        return ret

    def affiche_carte_dans_canvas(self, event=None):
        """
        affiche la carte actuelle dans le canvas si elle n'est pas déjà en cours d'affichage ou si le canvas a changé de taille

        input : event, inutilisé mais nécessaire pour l'utiliser en callback
        return : rien

        effets secondaires : mise à jour de l'affichage de la carte, de self.xo, self.yo l'origine de la carte dans le canvas, self.grille_canvas et de self.fini_affichage
        """
        if self.largeur_canvas != self.canvas_affichage.winfo_width() or self.hauteur_canvas != self.canvas_affichage.winfo_height() or not self.fini_affichage:
            for voiture in self.voitures_canvas:
                self.canvas_affichage.delete(voiture)
            self.voitures_canvas = []
            self.fini_affichage = True
            self.calcul_echelle()
            self.xo, self.yo = (max(self.hauteur_carte - self.largeur_carte, 0) * self.echelle) // 2, (max(self.largeur_carte - self.hauteur_carte, 0) * self.echelle) // 2
            if self.canvas_affichage.winfo_height() < self.canvas_affichage.winfo_width():
                self.xo += self.canvas_affichage.winfo_width()//2 - self.canvas_affichage.winfo_height()//2
            else:
                self.yo += self.canvas_affichage.winfo_height()//2 - self.canvas_affichage.winfo_width()//2

            if len(self.grille_canvas) != self.largeur_carte * self.hauteur_carte:
                self.canvas_affichage.delete(*self.grille_canvas)
                self.grille_canvas = []
                nx = np.ones(self.largeur_carte+1) * self.xo + np.arange(0, self.largeur_carte+1) * self.echelle
                ny = np.ones(self.hauteur_carte+1) * self.yo + np.arange(0, self.hauteur_carte+1) * self.echelle
                for y in range(self.hauteur_carte):
                    for x in range(self.largeur_carte):
                        case_canvas = self.canvas_affichage.create_rectangle(nx[x], ny[y], nx[x+1], ny[y+1], fill=self.couleur_de_case(x, y), outline=from_rgb((0,0,0)))
                        self.canvas_affichage.tag_bind(case_canvas, "<Button-1>", self.deselectionne_voiture)
                        self.grille_canvas.append(case_canvas)
            else:
                nx = np.ones(self.largeur_carte+1) * self.xo + np.arange(0, self.largeur_carte+1) * self.echelle
                ny = np.ones(self.hauteur_carte+1) * self.yo + np.arange(0, self.hauteur_carte+1) * self.echelle
                for y in range(self.hauteur_carte):
                    for x in range(self.largeur_carte):
                        rect = self.grille_canvas[y * self.largeur_carte + x]
                        self.canvas_affichage.coords(rect, nx[x], ny[y], nx[x+1], ny[y+1])
                        self.canvas_affichage.itemconfigure(rect, fill=self.couleur_de_case(x, y))
            self.fini_affichage = False

    def position_posable(self, xc:int, yc:int) -> bool:
        """
        revoie un booléen indiquant si il est possible de poser une route en (xc, yc)
        
        note : nom identique mais fonctionnement légèrement différent de position_posable de Carte, car il faut prendre en compte que l'utilisateur commence avec une carte vide
        et que l'utilisateur peut mettre son curseur dans des cases non connectées au reste de la route

        input : 
            - xc : entier de coordonnée horizontale dans la carte actuelle
            - yc : entier de coordonnée verticale dans la carte actuelle
        return : booléen, True si il est possible de poser une route dans la case visée

        """
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
    
    def point_dans_grille_ou_0(self, xc:int, yc:int) -> int:
        """
        renvoie la valeur de la grille de route en (xc, yc) si elle est dans la carte ou 0 sinon

        note : identique en fonctionnement à get_at_or_0 de Carte, mais sert ici pour moins polluer le code de parcours d'attributs (pas de self.carte.get_at_or_0(...))

        input : 
            - xc : entier de coordonnée horizontale
            - yc : entier de coordonnée verticale
        return : entier, 0 ou 1 (pas un booléen car la plupart des fonctions qui appellent celle-ci le font pour compter des voisins)
        """
        ret = 0
        if 0 <= xc < self.largeur_carte and 0 <= yc < self.hauteur_carte:
            ret = self.grille_route[xc,yc]
        return ret
    
    def calcul_echelle(self):
        """
        calcule et met à jour l'échelle entre les coordonnées de canvas et de la grille de carte

        input : rien
        return : rien

        effets secondaires : mise à jour de self.largeur_canvas, self.hauteur_canvas, self.echelle
        """
        self.largeur_canvas = self.canvas_affichage.winfo_width()
        self.hauteur_canvas = self.canvas_affichage.winfo_height()
        dimension_minimum_canvas = min(self.largeur_canvas, self.hauteur_canvas)
        dimension_maximum_carte = max(self.largeur_carte, self.hauteur_carte)
        self.echelle = max(2, int(math.floor(dimension_minimum_canvas/dimension_maximum_carte)))

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

    def filtre_correction_carte(self, event=None):
        """
        corrige la carte de façon à empêcher les configurations inutilisables
        ATTENTION : NE CORRIGE PAS ENCORE LE MANQUE D'E/S

        input : event, inutilisé mais nécessaire pour l'utiliser en callback
        return : rien

        effets secondaires : modification de la carte actuelle, et mise à jour de l'affichage dans le canvas
        """
        carte = Carte(self.largeur_carte, self.hauteur_carte, self.grille_route)
        carte.filtre_correction_carte()
        self.grille_route = carte.grille
        self.affiche_carte_dans_canvas()

    def carte_valide(self):
        """
        renvoie un booléen indiquant si la carte actuelle en mémoire est valide pour une simulation

        input : rien
        return : booléen, True si
        """
        carte = Carte(self.largeur_carte, self.hauteur_carte, self.grille_route.copy())
        carte.filtre_correction_carte()
        return (carte.grille != np.zeros((self.largeur_carte, self.hauteur_carte))).any()

if __name__ == "__main__":
    os.chdir(dirname(abspath(__file__)))

    app = App()
    app.mainloop()
