# Aggloméramax Pro

Aggloméramax Pro est un projet Python qui permet de créer des routes personnalisées, de les générer de manière procédurale, de les sauvegarder et de simuler la circulation de voitures dessus. Les voitures sont autonomes et peuvent donc générer des bouchons et d'autres situations de circulation réalistes.

![Bienvenue sur Aggloméramax Pro](photos/hello_world.png)

## Fonctionnalités

### Manipulation de cartes
#### Sérialisation et dé-sérialisation
- Sauvegarde de carte depuis le dossier "routes"
- Chargement de carte depuis le dossier "routes"
- Suppression de carte dans le dossier "routes"

#### Création
- Carte vierges de taille 5x5 à 50x50
- curseur vert sur la grille si il est possible de poser une route, rouge sinon
- clic gauche pour poser une route lorsque c'est possible
- clic droit pour enlever une route
- filtrage de la carte active pour lui faire respecter les règles pour l'utiliser en simulation :
    - pas de bloc 2x2 de routes
    - système de route connexe
    - au moins une entrée/sortie
    - pas de cul-de-sac

#### Génération
- Génération procédurale de taille 5x5 à 50x50
- "Nombre de noeuds maximum à poser" influe sur le nombre d'intersections, mais n'est pas une garantie minimum ou maximum du nombre de noeuds final
- "Distance minimale entre les noeuds" est une garantie forte, la distance est à compter à partir du centre des intersections.
- la génération est garantie d'obéir à toutes les règles nécessaires à l'utilisation en simulation

### Simulation

#### Fonctionnalités de la simulation
- Simulation de la circulation de voitures autonomes
- Pas de collision de voiture réelles (les collisions observées notamment aux intersections sont dues à un compromis dans le développement de l'affichage)
- virages, intersection T (à 3 voies) et intersections X (à 4 voies) gérés
- accélération et freinage de chaque voiture contrôlé individuellement
- recherche de plus court chemin pondéré par le nombre de voitures sur celui-ci au fil du temps
- Gestion des embouteillages et d'autres situations de circulation

#### Simulation dans l'interface
- choix du nombre de voitures maximum sur la route et de leur niveau d'agressivité
- choix du nombre de mises à jour de simulation par seconde voulu (coûteux en calcul, la vitesse demandée ne peut pas forcément être garantie)
- choix de la vitesse d'écoulement du temps dans la simulation (aucun impact sur la performance)
- possible de mettre en pause la simulation une fois lancée
    - lorsque la simulation est en pause, appuyez sur la barre espace pour avancer de 1 mise à jour de simulation
- arrêter la simulation et repasser en mode "manipulation de carte" automatiquement

## Installation

Pour installer les dépendances requises, exécutez la commande suivante :

```
pip install -r requirements.txt
```

Assurez-vous d'exécuter cette commande avant de lancer le projet pour garantir que toutes les dépendances sont correctement installées.

## Utilisation

Pour exécuter le projet, utilisez le script principal `main.py`.

```
python main.py
```

Interagissez directement avec la fenêtre pour dessiner, générer ou importer vos routes, et lancez la simulation avec les paramètres souhaités pour observer la circulation des voitures autonomes.

## Captures d'écran

![Exemple d'usage](photos/exemple.png)
*Cette carte est intégrée dans le projet, vous pouvez l'utiliser*

## Licence

Ce projet est sous licence MIT. Veuillez consulter le fichier `LICENSE` pour plus de détails.