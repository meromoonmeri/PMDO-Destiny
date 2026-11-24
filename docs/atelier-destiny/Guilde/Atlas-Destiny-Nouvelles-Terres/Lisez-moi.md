# Les Nouvelles Terres — Pokémon Mystery Dungeon: Destiny

Cette planche remplace le découpage du premier atlas par une autre géographie. **Seuls le style pixel art d’Explorateurs du Ciel et le fond nu approuvé servent de référence visuelle.** Aucun tracé de côte, masque, carte à terres ni sprite d’île d’*Explorateurs du Ciel* n’est utilisé. Les contours, les coordonnées des lieux, les cours d’eau et les traversées sont dessinés dans `Sources/Geographie.json`. Les emblèmes de lieux sont dessinés dans `Sources/Reperes.py`.

## Lire et explorer la carte

| Terre | Silhouette et lieux |
| --- | --- |
| **Orival**, ouest | Deux branches de terre embrassent le golfe des Ramures. Miroir Suspendu, Terrasses des Lierres, Pont des Racines, Domaine des Moulins. |
| **Séracine**, nord | Un long continent avec massif enneigé **à l’intérieur** et vallées boisées. Arêtes de Vitrane, Cadran des Aurores, Gué des Cèdres. |
| **Estrel**, est | Un grand bassin ramifié à deux débouchés maritimes. Lac des Treize Rives, écluses, Salines d’Ourle, Bourg Écume et Côtes de Métano. |
| **Torselune**, sud | Une dorsale recourbée de grès et de gorges. Roc des Siffleurs, Vrille d’Ocre, Jardin de Roselame, Enclos des Boussoles. |
| **Réverie**, sud-ouest | Île et crique redessinées. Six lieux autour du village-arbre : Réverie Town, Falaise de la guilde, Fosse Cascade, Passage Aquatique, Bois Perdus et Source Irisée. |
| **Les Haltes**, détroit | Trois îles portant la Balise de Nacre, le Signal des Voiles et l’Abri du Jusant. Elles jalonnent une traversée proposée d’Orival à Estrel. |

L’atlas comprend **4 continents, 1 île de départ, 3 îles aux Haltes et 18 îlots satellites**. Dans le répertoire, huit noms appartiennent déjà au projet (les six de Réverie, Bourg Écume et Côtes de Métano). Le reste est inventé pour cette planche. **Même pour les lieux existants, les positions, proportions, tracés et connexions de la carte sont des propositions**, pas des coordonnées ni des trajets du jeu.

## Livrables

- `Nouvelles-Terres-Destiny-5560x3660.png` : planche sans texte, dessin à 1 112 × 732 px agrandi ×5 au voisin le plus proche.
- `Explorer-Nouvelles-Terres.html` : atlas autonome, sans réseau ni installation. Cliquez sur une terre, une fiche ou un repère. Zoom à la molette, au pincement ou avec **− / +** ; déplacement par glisser. Au clavier, focalisez la carte et utilisez les flèches, **− / +**, **0** pour revenir à la vue mondiale. Les calques **Noms**, **Lieux** et **Routes** sont indépendants.
- `Ile-de-Reverie.png` : détail de l’île sur le même parchemin, avec ses sentiers. 1 000 × 1 075 px.
- `Calques/Carte-Destiny-1112x732.png` : version mondiale à taille de travail ; les PNG des calques et les 34 sprites d’emblèmes sont à côté.

### Ordre de composition des calques

Tous font 1 112 × 732 px, origine en haut à gauche. De l’arrière au premier plan :

1. `00-Parchemin-1112x732.png` — fond nu ×2, sans changement de pixels.
2. `01-Continents-et-eaux.png` — terres, lacs et chenaux.
3. `02-Courants-et-voiles.png` — gravures de mer.
4. `03-Reliefs-et-forets.png` — montagnes, paliers, dunes et végétation.
5. `04-Lieux.png` — repères illustrés.
6. `05-Nuages.png` — quelques nuages fixes sur la mer.

Calques facultatifs : `06-Sentiers-Reverie.png` entre reliefs et lieux ; `07-Traversees-proposees.png` au-dessus des gravures. `Calques/Atlas.json` donne les ancres et les rectangles des emblèmes dans `Calques/Miniatures/` (droite et bas exclusifs). Pour l’export agrandi, multiplier les coordonnées par cinq.

## Sources et reconstruction

Le seul fichier raster d’entrée est `Sources/Fond-nu-original.png`, copie à l’identique du fond nu approuvé (SHA‑256 `67e1bf2020a11b1d0dcdb4ea9400eb4cd75e2ada19b48f80c8420f5ea798c1d3`). Le reste est rendu localement avec les sources du kit. Il ne faut ni ROM, ni cartes antérieures, ni connexion, ni fichier du jeu.

```sh
python -m pip install -r Sources/requirements.txt
python Sources/Dessiner.py
python Sources/Autonome.py
python Sources/Verifier-images.py
```

`Verification-carte.json` et `Verification-lecteur.json` consignent les tests. Aucune ressource du jeu, de Drive ou d’un dépôt distant n’a été modifiée.
