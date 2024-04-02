import customtkinter as ctk
from customtkinter import *
from PIL import ImageTk, Image


class AffichageRoute(ctk.CTkToplevel):


    def __init__(self, liste_route):
        super().__init__()
        self.title("Affichage de la route")
        self.geometry("600x800")

        self.frame = CTkFrame(master=self, fg_color='green', width=600, height=800)
        self.frame.pack(fill=BOTH, expand=True)

        self.liste_route = liste_route
        self.affichage_route(self.liste_route)

    def create_route_label(self, image_path, position):
        route_image = CTkImage(light_image=Image.open(image_path), size=(100, 100))
        route_label = CTkLabel(master=self.frame, image=route_image, text="")
        route_label.place(x=position[0], y=position[1], anchor="center")
        route_label.image = route_image

    def affichage_route(self, liste_route):
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


if __name__ == "__main__":

    #dictionnaire test
    liste_route = {
        "route_vertical": [[150, 50], [150, 150], [150, 250], [150, 350], [150, 450], [150, 650], [150, 750], [450, 50], [450, 150], [450, 350], [450, 650], [450, 750]],
        "route_horizontal": [[50, 550], [250, 250], [350, 250], [350, 550], [250, 550], [550, 250], [550, 450], [550, 750]],
        "route_haut_gauche": [[450, 550]],
        "route_bas_droite": [[450, 450]],
        "croix": [[150, 550], [450, 250]]
    }

    app = AffichageRoute(liste_route)
    app.mainloop()
