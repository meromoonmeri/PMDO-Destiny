# Guilde Destiny — atelier sans verdure

Ouvre [Guilde-Destiny-Sans-Verdure.html](../Guilde-Destiny-Sans-Verdure.html) directement dans un navigateur. Tout est embarqué, y compris les quatre ambiances, les 33 objets PMU et les cartes de référence des salles régénérées.

## Les décors

| Salle dans l’atelier | Carte originale de Grodoudou | Taille |
|---|---|---:|
| Bureau du maître | G01P05 — les deux baies et le couloir sud | 408 × 384 px |
| Réfectoire | G01P06 — deux baies rondes, passage à droite | 504 × 360 px |
| Dortoirs nord I et II | G01P09 — baie ronde, petit seuil au sud | 432 × 336 px |
| Dortoirs sud I et II | G01P10 — arche au fond, sans fenêtre ni sortie au sud | 432 × 336 px |

Les quatre décors ont été **régénérés avec les cartes de Grodoudou comme géométrie et les salles natives de Destiny 0.7.7 comme référence de style** : longues lames de chêne, colonnes à bagues, encadrements et bords de racines. Le générateur produit les décors complets ; le traitement après génération se limite au redimensionnement, au recalage et au fond brun des salles natives. Aucun décor n’a été dessiné manuellement. Les détails de contour et de vitrage varient légèrement. **Original Grodoudou** affiche la carte de référence à la même échelle. Les quatre décors de jour sont également disponibles dans `Decors-Grodoudou-sans-verdure.zip`.

Dans les neuf autres salles, seul le calque **04 verdure separee** du décor natif a été masqué. Le plan, les passages, le vitrage R2 et les cadres sud existants sont conservés. Rien n’est meublé par défaut.

## Aménager et exporter

- **Comparer les 4** montre le même plan au jour, à l’aube, au crépuscule et la nuit. Les ambiances des décors générés sont déclinées à partir de la version de jour.
- Sélectionne un objet PMU et place-le sur le plan. Garde une copie indépendante avec **Exporter → Plan de l’atelier** (JSON). Si un ancien plan contient des placements dans une salle dont la géométrie a changé, rouvre-le dans [l’atelier natif](../Guilde-Destiny.html) pour ne pas perdre ce placement.
- **Image de la salle** exporte le décor courant en PNG avec l’aménagement. Les décors régénérés restent des aperçus ; aucun export de carte jouable n’est proposé pour eux.
- Pour une salle native, **Copie de carte pour Destiny** produit, à partir du `.rsground` Windows 0.7.7 intact, une copie avec le calque végétation désactivé et, si tu en as posé, le mobilier décoratif. Rien n’est installé par l’atelier. Sauvegarde l’original avant toute utilisation ; pour le cadrage, installe le correctif avant de remplacer les cartes.

Références : cartes G01P05A, G01P06A, G01P09A et G01P10A de [Pokémon Donjon Mystère : Explorateurs du Ciel, galerie Project Pokémon](https://projectpokemon.org/home/gallery/category/12-pok%C3%A9mon-mystery-dungeon-explorers-of-sky/). Voir `Verification-layouts.json` pour les mesures d’alignement et `Tests-navigateur.json` pour le contrôle de l’atelier. `Sources/Assembler.py` réassemble le HTML et réutilise les données embarquées.
