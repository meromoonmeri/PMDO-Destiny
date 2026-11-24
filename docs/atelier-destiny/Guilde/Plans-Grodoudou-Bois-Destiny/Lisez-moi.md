# La guilde de Grodoudou, en bois de Destiny

Neuf décors vides à la définition des plans de **G01P02 à G01P10**. La façade et les six salles supplémentaires du réseau Treehouse ne font pas partie de ce lot.

- **Atlas** : `Explorer-les-9-salles.html` s’ouvre hors ligne. Sélectionner une salle pour comparer avec la carte de Grodoudou par superposition ou passer à la taille réelle. Les deux états de porte sont disponibles dans la salle commune.
- **Planches** : `Les-9-salles-jour.png` et `Les-9-salles-nuit.png`. Toutes les surfaces y sont affichées à la même échelle de réduction.
- **PNG/Jour** et **PNG/Nuit** : 20 PNG RGBA à la définition des références, sans fond. Dans chaque ambiance, `G01P04.png` a la porte ouverte, `G01P04-porte-fermee.png` a la porte fermée.
- **Géométrie** : `Geometrie.json` indique le contour de sol relevé visuellement, les vitres, les emplacements des escaliers, de la porte et des seuils. C’est un relevé de décor, **pas** une grille de collisions ni un paquet à installer dans le jeu.

## Traitement

Parquet et panneaux de bois remontés à partir de pixels de la guilde Destiny distribuée. Les colonnes, le bois des lisières, les encadrements, le battant et les marches s’appuient sur ses éléments graphiques. L’essai génératif n’intervient que dans le micro-contraste des marches. Aucune pierre, végétation, table, comptoir ni couchage n’est repris. La version nocturne emploie la teinte du décor Destiny `(97, 118, 159)` et les baies passent aux bleus nocturnes.

Les proportions et les positions de fenêtre et de sortie sont relevées sur les neuf références. Les échelles de fond des P02–04 sont remplacées sur leur axe par des escaliers encastrés ; la porte du P04 reste à droite, conformément au plan de Grodoudou. Les raccords visuels aux seuils ne prolongent pas un passage au-delà de son emplacement d’origine.

## Contrôles

Les 20 PNG ont été vérifiés : dimensions, égalité des silhouettes jour/nuit, surface de plancher opaque, neuf bandes de raccord opaques, raccord visible au pied des arches et des escaliers. Les neuf salles ont été comparées aux références à la même échelle. Aucun script, aucune carte jouable et aucune collision du jeu n’ont été modifiés.

| ID | Salle | Définition | Raccords de plancher contrôlés |
| --- | --- | ---: | ---: |
| G01P02 | Vestibule | 408 × 312 px | 1 |
| G01P03 | Salle des missions | 696 × 456 px | 0 |
| G01P04 | Salle commune — 2e sous-sol | 648 × 432 px | 2 |
| G01P05 | Chambre de Grodoudou | 408 × 384 px | 1 |
| G01P06 | Réfectoire | 504 × 360 px | 1 |
| G01P07 | Chambre de l’équipe | 384 × 312 px | 1 |
| G01P08 | Couloir des dortoirs | 256 × 360 px | 2 |
| G01P09 | Dortoir nord | 432 × 336 px | 1 |
| G01P10 | Dortoir sud | 432 × 336 px | 0 |

## Sources graphiques

- [Project Pokémon, galeries de Pokémon Donjon Mystère : Explorateurs du Ciel](https://projectpokemon.org/home/gallery/category/12-pok%C3%A9mon-mystery-dungeon-explorers-of-sky/) — références G01P02A–G01P10A employées pour le relevé et le comparateur.
- [PMDO Destiny, distribution Windows 0.7.3](https://github.com/meromoonmeri/PMDO-Destiny/releases/tag/v0.7.3) — textures et objets de la guilde Treehouse extraits du ZIP. Voir `../Salles-du-jeu/Provenance.md` pour la provenance détaillée et la comparaison des ressources graphiques entre les versions.
