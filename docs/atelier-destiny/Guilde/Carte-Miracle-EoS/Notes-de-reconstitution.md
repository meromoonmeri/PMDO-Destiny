# La Carte Miracle en mouvement

Deux extraits de **Pokémon Donjon Mystère : Explorateurs du Ciel** rejoués avec les décors, poses et sons du jeu. C’est une reconstitution, pas un enregistrement d’émulateur ni la carte finale de Destiny.

- **`Carte-Miracle-En-Action.html`** — ouvrir dans un navigateur et cliquer sur **Tout jouer**. **Voir et entendre le déblocage** saute directement au repère et à la fanfare. **Flash rouge** s’arrête sur une pose rouge ; **½×** ralentit sans abaisser la hauteur du son. **Vue entière** ôte le recadrage DS. Aucun téléchargement pendant la lecture.
- **`Carte-Miracle-En-Action.mp4`** — le déblocage de l’Île Blizzard suivi du trajet de démonstration vers l’île, en environ 13,4 secondes. La fanfare commence vers **0:06,7**, le voyage commence vers **0:09,3**. Son stéréo.
- **`Calques/`** — PNG à transparence conservée, positions et séquences en JSON, fanfare et extrait de musique en MP3. `Calques/Fond-nu-EoS-556x366.png` est une copie octet pour octet du fond déjà validé. Dans le lecteur, **Fond nu** remplace le terrain DS par ce PNG et garde les effets sur des calques distincts. Aucun relief ajouté à ce PNG.

## 01 — Déblocage de l’Île Blizzard

Scène `P01P01A/s02p0101.ssb`, versions US et EU : `SetMode(3)`, palier **6**, `ChangeLevel(7)`, caméra sur le **point 47** à **(76, 276)**. Le cadre 256 × 192 est borné au coin **(0, 144)**. Le jeu laisse finir la transition avant les messages *« Les nuages se sont levés sur la Région Gelée et ses alentours. »* et *« En outre… »*. Il déclenche ensuite **`BlinkMark(47)`**, **`SetArrow(47)`** et **`me_Play(6)`** avant l’annonce d’accès à l’île. Le script passe au palier 8 à la fin de la scène.

| Élément | Relevé dans les fichiers |
|---|---|
| Nuages | Masque basculé au noir ; fondu 16 images en sortie et 16 au retour. Un grand banc + quatre petits dans `s01p01a1.wan` ; compteur de 240 images et 30 avant le déplacement, comptées depuis le basculement. |
| Jaune fixe | `SetMark` → état 1 → séquence **9** de l’OBJ 155 `s01p01a2.wan`. Pose 2 du WAN. |
| Jaune ↔ rouge | `BlinkMark` → état 2 → séquence **11** : poses **2, 9, 4, 9, 2** (jaune, jaune atténué, rouge, atténué, jaune), 4 images chacune, boucle de 20. Le rouge n’est donc pas un code permanent « donjon fermé ». |
| Flèche | `SetArrow` → séquence **13**, poses 5/6, 20 images chacune. Son coin est décalé de **(+4, −20)** puis **(+4, −19)** par rapport au point. |
| Audio | **ME nº 6** (`ME_NUM_DUNGEON_` dans `me0006.smd`), extrait du jeu diffusé sous le titre **Area Uncovered**. Le script ne déclenche pas d’autre effet `se_Play` dans ce passage de carte. |

Le point et la flèche sont repris directement du WAN ; ni recoloration ni redessin. La pose bleue de ce même fichier est conservée dans les calques, **mais ni la scène de l’Île ni le voyage montré ne l’utilisent**. L’aperçu n’assimile pas le bleu à un état de progression. Les textes du jeu attendent normalement les actions du joueur : la durée de lecture a été réglée pour la démonstration. La caméra est cadrée sur le point 47 dès l’avant/après pour rendre le dégagement lisible. Les autres repères de sauvegarde ne sont pas simulés.

## 02 — Départ et arrivée du Pokémon

- **Caverne Saline**, à sélectionner dans **Destination du voyage** : scène `G01P04A/m23a0101.ssb`. Le script passe en **mode 1**, force les deux repères fixes, fixe le départ à **184** (Bourg-Trésor, alias **181**, **212, 180**) et joue **Wigglytuff’s Guild Remix**. Il attend 60 images, lance **`MoveCamera(36)`** vers la **Caverne Saline (196, 156)**, attend la fin du mouvement, affiche le nom du donjon et attend encore 60 images. Le palier 5 suit la progression de cette partie du récit ; le passage lui-même ne force pas de palier. Le trajet natif est très court : environ un quart de seconde. Pour le voir en détail, mets le lecteur au ralenti ou choisis **En route** puis utilise les flèches du clavier hors des contrôles.
- **Île Blizzard**, trajet de démonstration : même départ et même déplacement de mode 1, destination **47** sur la carte dégagée (palier 8). Ce raccord permet de revoir plus longuement la marche après le déblocage. **Le raccord à l’île n’est pas une cinématique originale de la cartouche.**

Dans le mode 1, la routine moteur conserve la position intermédiaire en **8.8**, la fait converger vers la destination à partir d’une vitesse de `0x200` (base : **2 px/image**) et calcule une orientation sur 8 directions d’après le mouvement. La caméra suit ce point en restant bornée aux bords de la vue. Le jeu charge le héros courant ; ici **Pikachu** est une espèce d’exemple, pas un personnage imposé par le script. Le sprite `m_ground.bin` nº 26 a été résolu via `monster.md`, puis ses 24 poses du groupe de marche 0 ont été extraites avec leurs pivots et leurs durées (8/10/8/10 images par cycle et direction). Le dernier mouvement atteint la coordonnée exacte du repère, puis le nom s’affiche en légende. On ne simule pas les étages du donjon.

## Sources et contrôles

- [Déblocage EU : `P01P01A/s02p0101.ssb`](https://github.com/pret/pmd-sky/blob/9fa563873cec324993a614ea8ce03433add10e46/files/language-specific/EU/SCRIPT/P01P01A/s02p0101.ssb) et [voyage EU : `G01P04A/m23a0101.ssb`](https://github.com/pret/pmd-sky/blob/9fa563873cec324993a614ea8ce03433add10e46/files/language-specific/EU/SCRIPT/G01P04A/m23a0101.ssb), lus avec SkyTemple Files. Les instructions de Carte Miracle comparées sont identiques en US et EU.
- [Table `MAP_MARKER_PLACEMENTS`](https://github.com/pret/pmd-sky/blob/9fa563873cec324993a614ea8ce03433add10e46/asm/main_rodata_020A2808.s#L9683), [résolution des alias](https://github.com/pret/pmd-sky/blob/9fa563873cec324993a614ea8ce03433add10e46/asm/main_0206A878.s#L102), [moteur de carte : initialisation, déplacement 8.8, objets](https://github.com/pret/pmd-sky/blob/9fa563873cec324993a614ea8ce03433add10e46/asm/overlay_11_0230CE30.s) et [table des animations de repères et trajectoires nuageuses](https://github.com/pret/pmd-sky/blob/9fa563873cec324993a614ea8ce03433add10e46/asm/overlay_11_022ECD24_data.s#L2086).
- [OBJ 155, `s01p01a2.wan`](https://github.com/pret/pmd-sky/blob/9fa563873cec324993a614ea8ce03433add10e46/files/GROUND/s01p01a2.wan) et [séquence musicale `me0006.smd`](https://github.com/pret/pmd-sky/blob/9fa563873cec324993a614ea8ce03433add10e46/files/SOUND/ME/me0006.smd). Les extraits audio sont issus du [rip sonore d’Explorateurs du Ciel](https://archive.org/details/pmd-eos-complete-soundtrack), pistes 150 et 11 ; ce ne sont pas des sons de substitution. Réencodage MP3 pour le lecteur et AAC pour la vidéo.
- `Verification-des-sources.json` consigne les coordonnées exactes, la séquence des opcodes et les empreintes des ressources. `Verification-du-lecteur.json` consigne le test Chromium sur ordinateur et mobile, l’écoute du jingle et de la musique, et le fonctionnement hors ligne en iframe sandboxée. `Verification-de-la-video.json` contrôle les images du repère et l’alignement des pistes après encodage.

### Reconstruire les fichiers

1. Avec Python, Pillow et `skytemple-files==1.8.5` : `python Sources/Extraire.py`. Le script lit les ressources citées, en cache local ou par téléchargement. Il ne modifie aucun jeu, aucune ROM, aucun dépôt distant et ne touche pas au kit de fond nu déjà livré.
2. `python Sources/Autonome.py` intègre les PNG et les MP3 dans le HTML. `node Sources/Verifier.cjs` vérifie le lecteur si Playwright et Chromium sont disponibles.
3. Avec Node, FFmpeg et les polices DejaVu : `python Sources/Film.py` pour le MP4, `python Sources/VerifierFilm.py` pour son contrôle. Le moteur de scène est partagé entre l’aperçu et le rendu vidéo.

Illustrations, sprites, textes et musique : Chunsoft / Nintendo / The Pokémon Company et leurs ayants droit. Les fichiers de travail ne contiennent pas de ROM.
