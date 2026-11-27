# La Carte Miracle — Destiny

Ouvre **`Carte-Miracle-Destiny.html`** pour jouer, dans le lecteur ou dans un navigateur. Le fichier contient la carte, les calques, le carnet, les itinéraires et le son : aucune connexion n’est nécessaire.

## Les nuages se lèvent

**Réverie est dégagée dès le départ.** Les quatre continents, les Haltes et les quatre nouveaux ensembles insulaires forment **9 zones** à dévoiler. Au premier repère atteint dans une zone, ses bancs de nuages s’écartent puis se dissipent. Les autres bancs restent immobiles ; une zone ouverte le reste, même si l’on revient à un autre repère du même massif. Les lieux et leurs illustrations ne bougent pas, et le repère passe au rouge dès l’arrivée.

- **Circuit des nuages** parcourt toutes les zones encore voilées. **4×** accélère les trajets sans accélérer la levée des nuages. Avec **Suivre l’équipe**, la caméra cadre la zone qui s’ouvre ; en **Carte entière**, tu peux voir le voile se lever depuis la vue du monde.
- **Nuages**, sous la carte, affiche ou masque le voile sans déverrouiller de repère ni effacer la progression. **Pause** suspend aussi l’ouverture. Avec le réglage système de mouvement réduit, la zone se dévoile sans déplacement de nuages.
- Pour revoir la mise en scène sans toucher à ta partie, ouvre **`Ouverture-des-nuages-Destiny.mp4`**. Pour la rejouer dans la carte, **Recommencer** remet les nuages et les repères dans leur état de départ.

Les deux petits sprites de nuages de la Carte Miracle d’*Explorateurs du Ciel* sont recomposés en bancs pour la géographie de Destiny. Le voile est un calque à part : aucune texture ni position de lieu n’a été modifiée pour cet effet.

## Expédition des archipels

La carte compte **25 repères**, dont **5 nouveaux**. Le **Circuit des archipels** les enchaîne en partant de la position actuelle. Tu peux aussi choisir une destination et y partir directement.

| Zone | Repères | Origine |
| --- | --- | --- |
| Archipel volcanique, au nord-ouest | **Volcan Géant**, **Cratère Obscur** | Donjons d’*Explorateurs du Ciel*, redessinés d’après leur région sur la Carte Miracle et adaptés à Destiny. |
| Bois fleuri, au nord-est | **Bois des Pétales** | Île originale Destiny : bosquets rosés et verts, source et terrasses ocre. |
| Île rocheuse, au centre | **Grotte des Améthystes** | Île originale Destiny : collines étagées, cristaux lilas et grotte. |
| Atoll, au sud-est | **Atoll des Coraux** | Île originale Destiny : récif, lagon turquoise, ligne de dunes et petite palmeraie. |

Sources des références EoS : [Volcan Géant](https://www.pokepedia.fr/Volcan_G%C3%A9ant) et [Cratère Obscur](https://www.pokepedia.fr/Crat%C3%A8re_Obscur), avec leurs captures de localisation. Le grand cône et la caldeira sont deux repères du même massif sur **cette** carte. Les nouvelles positions et les trajets décrivent Destiny, pas une reproduction exacte de la géographie ou des donjons du jeu.

## Jouer

- Au départ, l’équipe est à **Réverie Town** et la **Fosse Cascade** est présélectionnée. Clique sur **Partir vers ce repère** ou choisis un autre site sur la carte ou dans le carnet. Vers une autre île, l’équipe rejoint un embarcadère, prend la barque et termine à pied sur la nouvelle rive. Dans les nouveaux biomes, les marcheurs évitent le lagon, la lave et la source.
- Les lieux et le décor sont fixes, y compris la fumée, les coulées, la cascade, la houle et la spirale. À l’arrivée, le repère passe au rouge une seule fois, **sans clignoter**, et le carnet indique **Repère débloqué !**.
- **Tour de Réverie** relie la Fosse Cascade au Passage Aquatique. **Circuit des marées** relie la Mer Houleuse, la Balise de Nacre, la Spirale du Jusant et la Grotte d’Ocre. Les deux circuits d’origine restent disponibles.
- **Son**, **Pause**, **1× / 2× / 4×** et **Recommencer** contrôlent l’expédition. La progression est conservée si le navigateur autorise le stockage local ; dans l’aperçu isolé, elle peut être limitée à la session ouverte.
- Glisser pour explorer, molette ou pincement pour zoomer. Clavier : `+`, `−`, flèches et `0` pour la vue du monde. **Trajet** affiche ou masque le chemin.

## Fichiers et fabrication

- **`Carte-Complete-Destiny.png`** : la carte fixe (1112 × 732), sans interface ni repères. Le parchemin validé et les 26 silhouettes d’origine sont conservés pixel pour pixel en dehors des ajouts.
- **`Archipels-Destiny-Magenta.png`** : les quatre nouveaux décors sur une planche magenta séparée, agrandie au pixel près. `Calques/Archipels/` contient les PNG magenta et détourés de chaque zone à l’échelle de la carte ; `06-Archipels.png` les place sur un calque transparent unique. `Generations/Archipels/` conserve les quatre bruts du générateur.
- **`Apercu-Expedition-Destiny.mp4`** : la traversée de Réverie et les cinq nouvelles découvertes, filmées dans le lecteur. Les sprites de marche, le signal de découverte et les repères s’appuient sur les ressources de l’atelier EoS. Cette première vidéo montre les archipels sans le voile.
- **`Ouverture-des-nuages-Destiny.mp4`** : la levée des nuages dans les neuf zones, de Réverie à la carte entière. **`Apercu-Nuages-Destiny.gif`** : deux ouvertures en boucle, extraites de la vidéo.
- **`Atlas.json`** : coordonnées des symboles et des arrivées, embarcadères, routes et emplacement des calques. `Sources/Nuages.json` définit le voile indépendamment de l’atlas. `lore: true` identifie les huit lieux connus de Destiny ; `origine: "eos"` distingue les deux lieux de référence ajoutés.
- Lance **`python Sources/Autonome.py`** pour reconstruire l’HTML depuis le kit. Dans l’espace de travail complet, `Sources/Construire.py` assemble les peintures du générateur sans dessiner de terrain, avec `Fond-Nu-EoS`, `Carte-Miracle-EoS`, `Atlas-Destiny-Nouvelles-Terres` et le monobloc magenta approuvé. Le jeu, la ROM et le dépôt distant n’ont pas été modifiés.
