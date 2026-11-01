# Lost Wood — autotiles, scénario et cadrage

## Ressources

- `art/dtef/LostWoodDestiny/tileset.dtef.xml` et les 35 PNG voisins constituent un paquet DTEF 24 × 24 pour l’éditeur PMDO 0.8.12. Ouvrir **Data → AutoTiles → Edit → Import DTEF** et sélectionner ce fichier XML en gardant les PNG dans le même dossier. L’import crée des autotiles dans l’éditeur ; pour ne pas écraser par mégarde les identifiants de la quête, faire une sauvegarde avant de remplacer des données existantes.
- Les trois planches principales `tileset_0/1/2.png` contiennent les sections **Wall / Secondary / Floor**, chacune en grille 6 × 8. Les 47 configurations de voisinage sont couvertes ; des variantes décoratives existent pour les cas prévus par les définitions natives.
- Les 32 images `tileset_0_frame…` conservent les deux couches de l’eau existante, chacune avec 16 phases, respectivement 25 et 15 ticks par phase à 60 ticks/s. Les images sont des calques transparents, pas 32 images statiques de remplacement.
- Dans la quête, les nouvelles matières sont déjà intégrées à `LostWoodFloor.tile` et `LostWoodWall.tile`. Les 49 et 57 positions de cellules, leurs adresses et la taille des fichiers sont inchangées par rapport à la version précédente : l’index natif existant reste compatible. Les définitions d’autotiles, les sept étages et la feuille secondaire animée ne sont pas remplacés.

## Origine et reconstruction

Les trois images dans `art/lost_wood_sources/` sont des matières et un guide **générés à la demande pour ce projet** ; il s’agit d’une interprétation visuelle, pas de tuiles canoniques. Les 47 masques de raccord sont calculés selon le voisinage PMDO ; des détails ont été dessinés en pixels par-dessus. L’eau vient des ressources Lost Wood déjà présentes dans la quête, et non de ces générations. Les autres cartes et leurs ressources ne sont pas modifiées.

Avec Python 3 et Pillow installés, depuis la racine d’un clone complet :

```bash
python tools/generer_autotiles_lost_wood.py
python tools/generer_dtef_lost_wood.py
python tools/tests/test_lost_wood_dtef.py
python tools/tests/test_lost_wood_raccords.py
python tools/tests/test_lost_wood_reproduction.py
lua tools/tests/test_lost_wood.lua
```

Le premier générateur produit des feuilles dans `build/lost_wood_generation/` en utilisant les feuilles natives actuelles comme gabarits d’adresses ; il ne les écrase pas. Le second reconstruit le paquet dans `build/LostWoodDestiny/` à partir des données du jeu. Les résultats obtenus lors de la validation sont identiques aux fichiers livrés, à l’octet pour ces deux feuilles et le paquet DTEF.

## Scénario et caméra

- Juste après le quiz, une scène nocturne sur `zrv2_zone_reveil_nuit` montre le héros endormi au milieu des fleurs avant un fondu noir menant au départ du partenaire sur `cliffdaytest_nuit`.
- Au départ en solo sur `cliffdaytest_nuit`, le partenaire sort de sa maison et marche tout du long sur le chemin menant à l’entrée orientale de **Lost Wood** (sans s’arrêter devant le croisement). Le héros reste le même personnage, placé en tête de réserve sans retirer son objet tenu. Après un KO ou un abandon du partenaire, le héros n’est pas ajouté à l’équipe : le partenaire se réveille près de l’entrée, puis peut repartir ou faire une pause et revenir au seuil est.
- Après la réussite de l’aller, le partenaire débouche sur `zrv2_zone_reveil_nuit` ; le héros est retrouvé en réserve par son identité de héros sans duplication au rechargement. Durant cette longue cinématique de rencontre façon *Pokémon Donjon Mystère*, le héros reste muet (mouvements de tête, animations et pensées intérieures entre parenthèses sans son de voix), le joueur saisit son prénom (`UI:NameMenu`), le partenaire s’avance vers la montagne accompagné d’un lent mouvement de caméra avec son portrait émerveillé (`Inspired`) en parlant de son rêve de former une équipe d’explorateurs, interroge le héros via un menu à choix multiples, l’invite à le suivre jusqu’à **Réverie Town**, la capitale des explorateurs, puis tous deux prennent la pose devant le panorama nord avant un fondu au noir ponctué d’un texte blanc sur fond noir (`WaitShowVoiceOver`) et la traversée de **Lost Wood** en sens inverse (`7F -> 1F`, escaliers `stairs_back_up`).
- À la sortie de ce trajet inverse, le duo arrive au grand jour sur `cliffdaytest` : devant sa maison, le partenaire explique qu’il/elle vit ici, qu’il/elle est orphelin(e) et que **Tatie Kangourex** s’occupe de lui/elle, puis présente au croisement **Réverie Town**, les équipes de secours et d’explorateurs ainsi que les Guildes à travers le monde avant de descendre vers `WaterfallVillageCapital`.
- Les mentions de **Lost Wood** dans les dialogues de la quête sont vertes et celles de **Réverie Town** / **Tatie Kangourex** dorées ; aucun identifiant de donjon n’a été changé.
- Sur `zrv2_zone_reveil_nuit`, `cliffdaytest_nuit` et `cliffdaytest`, la caméra est bornée à la carte (`ScrollEdge.Clamp`) et rendue au joueur après les scènes. Hors prologue (`SV.Destiny.RetourAccompli` absent), la saynète Team Dazzling reste disponible sur `cliffdaytest`.

## Vérifications et limites

- Import réel du DTEF dans PMDO 0.8.12 : signatures, variantes, durées, alpha et pixels visibles identiques sur **1 641 images de cellules**. Le moteur normalise certains RGB de pixels totalement transparents, sans effet visible.
- **73 728 paires** d’autotiles adjacents vérifiées : 47 configurations de murs couvertes, 91,15 % des pixels de bord identiques, écart RGB moyen 1,82/255. Des coins restent imparfaits et la matière peut paraître répétitive : ces chiffres ne valent pas approbation artistique.
- Banc Linux : KO, abandon, pause et reprise en solo ; rechargement vers les retrouvailles ; échec puis réussite du retour duo ; déplacement et caméra après le retour. Les issues de donjon ont été **forcées**, et la longue discussion a été sautée sur ce banc : ce n’est pas un parcours intégral des sept étages ni un test Windows. Le risque normal du donjon continue à s’appliquer aux membres actifs, notamment à leur équipement après un KO en duo.
- Scène des falaises de jour : présence des quatre acteurs et retour de la caméra vérifiés sur un banc où les dialogues ont été abrégés. Le début de la scène peut encore masquer Pichu derrière l’avant-plan d’origine : à reprendre visuellement sans modifier les cartes à l’aveugle.
- L’audit a également détecté une grille de collision incohérente sur `glacier_cliff_aurora_v1` et une couverture géométrique limitée sur certaines cartes, dont la Source. Ces cas ne sont pas corrigés par ce lot ; ne pas étirer ou remplacer leurs collisions sans une source fiable et un parcours de validation.
