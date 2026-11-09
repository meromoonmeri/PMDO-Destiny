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

- Juste après le quiz, un prologue montre le héros déjà endormi au marqueur `reveil` de `zrv2_zone_reveil_nuit`, la prairie ZRV2 face à l'océan : sur fond noir, ses pensées (« Où suis-je… », « Qui suis-je… », « Tout me semble si flou… », « J’ai sommeil… ») précèdent un fondu qui se lève sur lui, puis bascule chez le partenaire. La viewport 320 × 240 s'ouvre au centre Y=136 (vue Y 16..256 : lune, sommet, mer et héros en bas), descend lentement vers le panorama Y=152, puis se rapproche du héros sans faire sortir toute la montagne du cadre.
- Au départ en solo, le partenaire sort de sa maison, dépasse le croisement et hésite sur le chemin de l’est devant l’entrée. Le héros reste le même personnage, placé en tête de réserve sans retirer son objet tenu. Après un KO ou un abandon du partenaire, le héros n’est pas ajouté à l’équipe : le partenaire se réveille près de l’entrée, puis peut repartir ou faire une pause et revenir au seuil est. Pendant cette pause, s’il s’engage dans le sentier nord-sud vers le bas de la carte, il se ressaisit (« Je ne vais pas me dégonfler… Je dois traverser Lost Wood ») et remonte vers le croisement.
- Après la réussite de l’aller, le héros est retrouvé en réserve par son identité de héros ; un rechargement ne le duplique pas. La scène de retrouvailles utilise les marqueurs natifs de la prairie ZRV2 : le partenaire entre par `entrance` au sud, remonte le sentier et rejoint le héros au point `reveil`, face à la mer et à la montagne. La caméra l'accompagne en travelling depuis le sud, remonte vers le panorama (centre Y=152) lorsque le duo regarde la crête, dérive lentement pendant l'évocation du rêve, puis termine sur ce panorama avant le fondu du retour.
- Lost Wood possède deux segments : le segment 0 parcourt les générateurs 1 → 7 pour l’aller, affichés **1F → 7F** avec des escaliers montants (`stairs_go_up`) ; le segment 1 reparcourt les générateurs 7 → 1 pour le retour en duo, affichés en étages négatifs **B1F → B7F** avec des escaliers descendants (`stairs_go_down`, et `stairs_secret_down` pour l’escalier secret). Un échec du retour ramène à `zrv2_zone_reveil_nuit`, tandis que son succès débouche sur `cliffdaytest` au jour.
- Les mentions de **Lost Wood** dans les dialogues de la quête examinés sont vertes ; aucun identifiant de donjon n’a été changé. Les autres noms seront à colorer lorsqu’ils seront employés dans des dialogues narratifs.
- Sur `cliffdaytest_nuit`, la caméra est bornée à la carte et rendue au joueur après les scènes. Le Pichu décoratif a été retiré des `MapChars` des deux falaises. Sur `cliffdaytest`, l’arrivée Destiny enchaîne avec la rencontre de la Team Dazzling : Adagio (Tsareena), meneuse ambitieuse et manipulatrice, Aria (Mawile), aigrie et moqueuse, et Sonata (Lopunny), tête en l’air et comique malgré elle. Elles remontent le chemin sud vers une mission à l’est, posent sous les sparkles, prennent le duo de haut puis repartent. Les deux cartes Cliff portent la BGM `Cliff Camp.ogg`, doublée par la boucle de ressac `Destiny_Falaise_Mer.ogg`.

## Vérifications et limites

- Import réel du DTEF dans PMDO 0.8.12 : signatures, variantes, durées, alpha et pixels visibles identiques sur **1 641 images de cellules**. Le moteur normalise certains RGB de pixels totalement transparents, sans effet visible.
- **73 728 paires** d’autotiles adjacents vérifiées : 47 configurations de murs couvertes, 91,15 % des pixels de bord identiques, écart RGB moyen 1,82/255. Des coins restent imparfaits et la matière peut paraître répétitive : ces chiffres ne valent pas approbation artistique.
- Banc Linux : KO, abandon, pause et reprise en solo ; rechargement vers les retrouvailles ; échec puis réussite du retour duo ; déplacement et caméra après le retour. Les issues de donjon ont été **forcées**, et la longue discussion a été sautée sur ce banc : ce n’est pas un parcours intégral des sept étages ni un test Windows. Le risque normal du donjon continue à s’appliquer aux membres actifs, notamment à leur équipement après un KO en duo.
- Scène des falaises de jour : l’ancienne cinématique centrée sur Pichu n’est plus utilisée. La nouvelle rencontre Dazzling est vérifiée par chargement Lua et simulation stubée, mais ses déplacements, portraits, sparkles et l’équilibre BGM/ressac doivent encore être confirmés dans le moteur.
- L’audit a également détecté une grille de collision incohérente sur `glacier_cliff_aurora_v1` et une couverture géométrique limitée sur certaines cartes, dont la Source. Ces cas ne sont pas corrigés par ce lot ; ne pas étirer ou remplacer leurs collisions sans une source fiable et un parcours de validation.
