# Fond nu de Destiny et nuages de la Carte Miracle

## Le fond à utiliser pour dessiner

**`Fond-nu-EoS-556x366.png` est le PNG de ton dépôt, copié octet pour octet.** Il ne contient ni terre, ni relief, ni lieu. Le quadrillage, la rose des vents et la bordure fixe font partie du fichier. Aucun voile mobile n’est intégré au PNG.

- **Provenance :** [`meromoonmeri/projet-pmdo/source/user_committed_map_background.png`](https://github.com/meromoonmeri/projet-pmdo/blob/37b2157ed730d958d83afe2fa1bb974570ecb46b/source/user_committed_map_background.png), retrouvé grâce au [README de méthode de `projet-creation-pmdo`](https://github.com/meromoonmeri/projet-creation-pmdo/blob/8d2a5b8d9dadef254a0773bb36d633888148adcd/source/world_map_userfond_v1/README.md). C’est le même fichier que `image.png` sur `main` dans `projet-pmdo` (même blob Git).
- **Nature :** c’est la version nue du dépôt dans le style EoS, pas un calque de jeu sans terre. Dans `S01P01A`, le calque inférieur natif porte déjà les terres. Je ne l’ai donc pas livré comme fond de dessin. Il n’y a ni fond PSMD recoloré, ni géographie d’un des anciens atlas dans le kit.
- **Intégrité :** 556 × 366 px, PNG RVB ; SHA-256 `67e1bf2020a11b1d0dcdb4ea9400eb4cd75e2ada19b48f80c8420f5ea798c1d3`.

## Ce qui est dans la planche, et ce qui bouge vraiment

La carte principale `S01P01A` est une grille **2 × 4 de paliers de 504 × 336 px**, soit **1008 × 1344 px** dans les données du jeu. Les huit paliers ont exactement le même calque inférieur. C’est **le masque de nuages supérieur** qui diffère. Dans la [planche World Map de The Spriters Resource](https://www.spriters-resource.com/ds_dsi/pokemonmysterydungeonexplorersofsky/asset/59283/), les huit premiers panneaux sont les composites de ces paliers, avec des séparateurs de 3 px. L’extraction recomposée correspond à ces huit panneaux **pixel pour pixel en RVB**. Le panneau repéré de points jaunes n’est pas un neuvième palier. La couverture du calque supérieur passe de 78,15 % au premier palier à 0 % au huitième ; cela ne mesure pas une durée.

**L’animation entre paliers ne vient pas de cette planche.** Le test du jeu passe en mode 3, puis lance `worldmap_ChangeLevel(n)` pour la cible `n` (2 à 8). `worldmap_SetLevel(n)` sélectionne un état sans lancer les sprites du dégagement. L’animation est rendue sur l’écran supérieur ; dans le cas courant du test, caméra et opacité ne servent pas à agrandir ou à dissoudre le masque.

| Phase | Comportement vérifié dans le moteur |
|---|---|
| Changement de palier | Fondu **de l’écran supérieur** vers le noir, demandé sur **16 images** ; le moteur passe à la vue du nouveau palier. |
| Réapparition | Retour du noir sur **16 images**. Le nouveau masque fixe est déjà en place derrière les objets mobiles. |
| Départ des nuages | Le moteur instancie **un grand banc propre au palier et quatre petits nuages**, tirés du même `s01p01a1.wan`. Chaque objet a sa position et son vecteur de vitesse. Le compteur est initialisé à **240 images**. |
| Mouvement | La position reste initiale pendant **30 images**, puis évolue à vitesse constante. Pour le compteur restant `r`, le déplacement est `max(0, 240 − r − 30) × v / 256` pixels sur chaque axe (`v` est la vitesse signée, en virgule fixe 8.8). Le retour du noir est inclus au début de ce compteur. À environ 60 i/s, cela donne **~4 s de compteur, dont ~0,5 s de délai initial**. |
| Opacité | Les poses mobiles sont des sprites à pixels opaques ou transparents. La boucle de déplacement ne réduit pas leur alpha et ne les redimensionne pas. Le noir est un réglage de luminosité de l’écran, **pas** un fondu entre deux images de la carte. Le passage au noir masque aussi le remplacement du masque fixe. |

Les neuf poses exportées servent à tous les paliers : **deux formes pour les petits nuages, sept grands bancs**. Les neuf séquences WAN concernées bouclent chacune sur **une seule pose** de 4 images ; le déplacement des silhouettes vient du moteur, pas d’un cycle de redessin du nuage. Les bancs sont découpés en fragments par le jeu ; les PNG les réunissent en une image avec un pivot indiqué dans le JSON.

### Départs et directions des grands bancs

Coordonnées dans un palier 504 × 336, origine en haut à gauche ; +x vers la droite, +y vers le bas. Les valeurs `vx, vy` ci-dessous sont celles des tables du jeu ; les diviser par 256 pour obtenir des pixels par image. Un point d’ancrage peut être au bord alors que la silhouette s’étend à l’intérieur (voir `coin_relatif`).

| Palier cible | Ancre du banc `(x, y)` | `(vx, vy)` | Direction | Cible caméra demandée par le test |
|---:|---:|---:|---|---:|
| 2 | (376, 336) | (+191, +169) | Sud-est | 15 |
| 3 | (336, 112) | (−172, −189) | Nord-ouest | 25 |
| 4 | (64, 0) | (−162, −198) | Nord-ouest | 30¹ |
| 5 | (376, 0) | (+295, −82) | Nord-est | 35 |
| 6 | (0, 200) | (−85, +241) | Sud-ouest | 42 |
| 7 | (0, 336) | (−80, +242) | Sud-ouest | 47 |
| 8 | (0, 0) | (−235, −100) | Nord-ouest | 68 |

¹ Le repère 30 est enregistré sur `S01P01B`, pas `S01P01A`. Le script demande ce repère, mais le moteur filtre les repères par carte. L’aperçu fournit pour ce seul palier un **cadrage d’étude**, pas un cadrage DS présenté comme vérifié.

### Exemple vérifié : le Lac des Brumes

Le script `V00P02/m01a06a.ssb` propose **Clear clouds** et **Presentation Test** ([description du menu de test par The Cutting Room Floor](https://tcrf.net/Pok%C3%A9mon_Mystery_Dungeon:_Explorers_of_Sky/Debug_Rooms)). Les versions US et EU du script donnent les mêmes **158 instructions et arguments**, indépendamment des chaînes de texte. L’ordre du test de présentation, une fois l’écran de carte actif :

```text
worldmap_ChangeLevel(2)
worldmap_SetCamera(15)
WaitSubScreen()
worldmap_SetArrow(15)  ; Wait(60)
worldmap_DeleteArrow()
worldmap_BlinkMark(15) ; Wait(60)
worldmap_SetMark(15)   ; Wait(30)
```

`SetCamera(15)` est un **recentrage sur un point**, borné pour ne pas dépasser les bords. Ce n’est pas la commande de déplacement progressif `MoveCamera`, que le menu **Overall Presentation Check** emploie séparément. Pour la cible 15, le point de carte est **(412, 228)** ; avec la fenêtre **256 × 192**, le centre est borné à **(376, 228)**, donc le coin supérieur gauche est **(248, 132)**. Le banc glisse alors vers le bas et la droite à environ **(+0,746, +0,660) px/image**. Les quatre petits nuages ne partent pas tous dans la même direction.

**Limite de la vérification :** ce relevé provient du script, des données et de la lecture du moteur, pas d’un enregistrement DS image par image. Les temps en secondes sont des conversions nominales, non des mesures vidéo. `WaitSubScreen()` attend la fin de la présentation ; les `Wait(60)` de l’exemple sont les pauses de flèche et de clignotement, pas la durée du dégagement.

## Fichiers prêts pour l’atelier

| Fichier | Usage |
|---|---|
| `Fond-nu-EoS-556x366.png` | Fond exact pour tracer la future géographie. À garder comme calque de référence verrouillé. |
| `Calques/Etats-fixes-504x336/Palier-01.png` à `Palier-08.png` | Huit masques RGBA à taille native (le dernier est entièrement transparent). Aucun pixel de terre. |
| `Calques/Sprites-mobiles/Pose-*.png` | Neuf sprites détourés par leurs vraies données de transparence, pas par couleur approximative. |
| `Calques/Trajectoires.json` | Les **35 trajectoires** (7 × 5), positions, vitesses, durée, pivots de poses et cibles du test. Pas de coordonnées de lieux Destiny. |
| `Fond-nu-et-nuages-EoS.html` | Aperçu autonome : ouvre sur le PNG nu ; **États fixes** affiche les masques ; **Animation** rejoue chaque arrivée au palier et permet d’avancer image par image. **Cadre DS** recadre sans zoom animé. |

Dans l’aperçu, le parchemin de 556 × 366 px est mis à l’échelle de la grille 504 × 336 **uniquement pour l’étude**. Le rendu démarre au palier précédent par choix de comparaison, quel que soit le palier actif d’une sauvegarde EoS. Le retour du noir et le mouvement reprennent les paramètres relevés ; le chargement, l’état d’une sauvegarde, la flèche et les repères ne sont pas simulés. Ce n’est pas une capture du jeu. Ni le fichier de dessin ni le jeu n’ont été modifiés.

## Sources primaires et reproduction

- **Fichiers du jeu, copie indexée par `pret/pmd-sky`, révision `9fa563873cec324993a614ea8ce03433add10e46`.** [`MAP_BG/s01p01a.bma`](https://github.com/pret/pmd-sky/blob/9fa563873cec324993a614ea8ce03433add10e46/files/MAP_BG/s01p01a.bma), `.bpc`, `.bpl` : carte, tuiles et palettes. [`GROUND/s01p01a1.wan`](https://github.com/pret/pmd-sky/blob/9fa563873cec324993a614ea8ce03433add10e46/files/GROUND/s01p01a1.wan) : sprites du dégagement.
- **Script du jeu :** [`m01a06a.ssb` EU](https://github.com/pret/pmd-sky/blob/9fa563873cec324993a614ea8ce03433add10e46/files/language-specific/EU/SCRIPT/V00P02/m01a06a.ssb) / [US](https://github.com/pret/pmd-sky/blob/9fa563873cec324993a614ea8ce03433add10e46/files/language-specific/US/SCRIPT/V00P02/m01a06a.ssb). Décompilé avec [SkyTemple Files](https://github.com/skytemple/skytemple-files) 1.8.5 ; lecture dans `Sources/Script-test.exps`. [SkyTemple documente `Wait` en images](https://wiki.skytemple.org/index.php?title=List_of_Opcodes).
- **Moteur :** [`overlay_11.s`, dispatch des opcodes et drapeau d’animation](https://github.com/pret/pmd-sky/blob/9fa563873cec324993a614ea8ce03433add10e46/asm/overlay_11.s#L6610-L6631). [`overlay_11_0230CE30.s`](https://github.com/pret/pmd-sky/blob/9fa563873cec324993a614ea8ce03433add10e46/asm/overlay_11_0230CE30.s#L2962-L3846) : ordre de changement de palier, fondu (`0x10`) et chargement des sprites. [`ov11_02310344`](https://github.com/pret/pmd-sky/blob/9fa563873cec324993a614ea8ce03433add10e46/asm/overlay_11_0230CE30.s#L4054-L4147) : décrément par image, soustraction de 30 (`0x1e`), calcul de la position en 8.8. [`overlay_11_022ECD24_data.s`](https://github.com/pret/pmd-sky/blob/9fa563873cec324993a614ea8ce03433add10e46/asm/overlay_11_022ECD24_data.s#L2111-L2187) : comptes, bancs et petits nuages ; `0xf0` = 240. [Table des points](https://github.com/pret/pmd-sky/blob/9fa563873cec324993a614ea8ce03433add10e46/asm/main_rodata_020A2808.s#L9683-L9738), [bornes `ov11_0230F28C`](https://github.com/pret/pmd-sky/blob/9fa563873cec324993a614ea8ce03433add10e46/asm/overlay_11_0230CE30.s#L2886-L2943).
- **Reproduction :** `python -m pip install skytemple-files==1.8.5`, puis `python Sources/Construire.py`. Le script télécharge seulement les ressources listées des dépôts publics. Pour refaire le contrôle pixel par pixel, ajouter `--planche chemin/vers/la_planche.png` avec la planche World Map. `Verification-assets.json` rapporte les contrôles effectués et les empreintes des entrées. Les ROM, le terrain de la carte canonique et les atlas précédents ne sont pas inclus.
