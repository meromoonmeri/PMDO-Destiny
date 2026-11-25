# Carte Miracle — Destiny 4

Ouvre **`Carte-Miracle-Destiny-4.html`** dans le lecteur ou dans un navigateur. Le fichier est autonome et jouable sans réseau. Cette édition est distincte de la carte précédente et commence sa propre partie à Réverie.

## Explorer sans voir le monde à l’avance

- **Réverie est la seule zone dégagée au départ.** Le voile opaque cache les autres paysages et leurs repères. Le bouton **Carte entière** est verrouillé, y compris si l’on dézoome à la molette, au clavier ou par pincement. `0` recentre la vue de la région tant que le monde est verrouillé. Il n’y a plus de commande pour enlever le voile.
- Choisis une destination ou **Circuit des nuages**. Une première arrivée déclenche la levée des bancs sur cette zone. Les repères déjà découverts restent rouges ; les terrains, les cascades et les autres lieux sont toujours fixes. Le voile seul bouge lors de cette transition, en plus du déplacement de l’équipe et de la caméra. Le mode mouvement réduit dévoile au même point d’arrivée sans animer le voile.
- L’ouverture de la dernière des **24 zones** rend **Carte entière** utilisable. Il n’est pas nécessaire d’atteindre chacun des **45 repères** : ouvrir une zone et découvrir un repère sont deux progressions différentes. En **4×**, le circuit complet dure environ 71 s ; les paliers visuels gardent leur vitesse normale.
- Les circuits de Réverie, des marées et des archipels restent disponibles. **Suivre l’équipe**, **Trajet**, **Pause**, **Son** et **Recommencer** conservent leurs rôles. La progression est sauvegardée localement quand le navigateur l’autorise.

## Géographie et direction artistique

- Les silhouettes du noyau Destiny sont conservées. **Torselune** est repeinte en dunes, oasis, canyon et couches de grès ; **Séracine** est repeinte en crêtes glaciaires, moraines, lacs gelés et vallées de conifères.
- L’**image 4** sert de plan aux cinq ensembles occidentaux, centraux, boréaux, austraux et du Levant, subdivisés en onze régions jouables. La carte intègre **101 silhouettes relevées** dans la référence, avec leur disposition relative conservée d’un seul tenant. Le filtre de détourage élimine les specks inférieurs à six pixels dans l’image 640 × 479. Les noms sont des repères d’adaptation Destiny 4, sans prétendre identifier chaque jeu ou donjon d’origine.
- L’**image 3** sert de méthode visuelle : toutes les zones sont converties en terrain de type EoS sur un parchemin continu, sans conserver les carrés de mer bleue. Le fichier Aseprite original n’était pas joint ; c’est une nouvelle carte terminée à partir des références, pas une édition des calques du projet montré à l’écran.
- Deux créations supplémentaires, **Archipel des Alizés** et **Récifs d’Émeraude**, multiplient les îles autour de la traversée. Les petits fragments ajoutés ne sont pas tous des repères jouables séparément.
- `Generations/` conserve les neuf bruts sélectionnés du générateur. Les textures des nouvelles terres et des deux continents sont générées ; les sources procédurales les détourent, les recalent contre les silhouettes de référence, harmonisent la couleur et calculent les trajets et le voile. Les deux petits sprites de nuage et la trame du voile proviennent des ressources EoS de l’atelier précédent.

## Fichiers

- **`Destiny-4-Levee-des-nuages.mp4`** : montage de six passages d’un même circuit. La vue générale montrée en fin de vidéo est réellement déverrouillée ; les zones non montrées ont également été visitées. La vidéo ne change pas la sauvegarde.
- **`Desert-et-Glace-Magenta.png`** : les deux nouveaux continents, détourés et posés sur une planche magenta séparée.
- **`Brut-Destiny-4-Magenta.png`** : l’assemblage terrain de tout l’atlas (**contient la géographie complète**, pour l’atelier, distinct du lecteur qui la cache). Les neuf PNG dans `Generations/` sont les véritables sorties du générateur avant assemblage.
- **`Atlas.json`** : 24 zones, 45 repères, 27 embarcadères, 503 tronçons, placement des calques et ordre des circuits. La totalité des trajets maritimes a été contrôlée au pixel contre les côtes ; certains chenaux intérieurs fins sont traités comme des gués en mode marche.
- **`Calques/`** : illustrations séparées, poses de marche, marqueurs, masques d’ouverture et son. `Sources/Autonome.py` régénère l’HTML depuis ce kit. Pour recalculer les calques avant cela, `Sources/Monde.py` utilise aussi les éditions précédentes `Carte-Miracle-Destiny` et `Fond-Nu-EoS` dans l’espace de travail. Aucun jeu, ROM ou dépôt distant n’a été modifié.
