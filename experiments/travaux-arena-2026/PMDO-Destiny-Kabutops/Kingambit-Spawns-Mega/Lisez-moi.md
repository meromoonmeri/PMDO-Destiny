# Dojo Kingambit — Spawns et Méga-Évolution

Révision locale sur `936b5623` (Troupes). Le sceau du hall, Kaito, les arènes DTEF, les étages et les conditions de victoire ne changent pas. Les finales ont toujours un maître et deux cadets de sa lignée. **Les maîtres arrivent en forme de base et sont tous éligibles à la Méga-Évolution.** La Méga-Évolution n’est pas déclenchée automatiquement par l’entrée en scène.

## Les sept entrées reprécisées

| Type | Mise en scène | Maître |
|---|---|---|
| Eau | Trois chutes d’eau qui arrivent par le bord haut, sans extrémité visible. Chaque combattant sort de sa propre colonne. | Tortank |
| Feu | Trois colonnes de flammes tombent et éclatent au sol. Chaque combattant quitte sa colonne. | Braségali |
| Glace | Une nappe continue de poudreuse traverse toute la vue. Les trois apparaissent sous le voile, puis la visibilité revient. | Oniglali |
| Sol | Des brèches de sable s’ouvrent ; les combattants franchissent la lèvre de leur ouverture. | Laggron |
| Roche | Des blocs se soulèvent de part et d’autre des ouvertures. Les combattants surgissent dans les éclats. | Tyranocif |
| Électrik | Un éclair descend hors champ. Le champ statique s’étend aux trois positions. | Élecsprint |
| Poison | Un brouillard violet dérive en nappes peu élevées, inspiré des Grotadmorv du Col Céleste d’Explorateurs du Ciel ; pas de bulles. | Ectoplasma |

Les motifs de ces sept entrées ont été générés, détourés et animés à la résolution native. Normal, Plante, Combat, Vol, Insecte et Dragon incorporent aussi un motif généré. Les effets Ténèbres et Acier restent ceux de la précédente livraison (limite du générateur atteinte). Les effets Psy, Spectre et Fée restent d’origine ; le casting Spectre et Fée a été ajusté pour que leurs maîtres soient éligibles.

## Contenu du pack

- **`Planches`** : PNG RGBA à 1×, 16 poses, ordre gauche → droite et haut → bas, 4 ticks/pose à 60 Hz. Les deux calques passent respectivement sous les sprites (`Sol`) et devant (`Air`). Les longues colonnes ont des cellules hautes (384 px) pour continuer au-delà du cadre. Glace et Poison ont une nappe répétée jusqu’aux bords de l’écran (`BG`) ; elle ne fait pas partie du calque local. L’index donne la taille et l’ancre centre de chaque cellule.
- **`Integration`** : patch depuis `936b5623`, liste des fichiers, et identifiant du candidat. L’addon de pierres n’est pas fusionné avec les indices globaux de Destiny.
- **`Mega_Stones_V1.2.0-original.zip`** : distribution complète de Deeshura, inchangée (47 Méga-Gemmes et la Météorite Delta, icônes, scripts, carte et boutique, sons, données et licence). Les sprites des Pokémon n’y sont pas inclus en amont.
- **`Mega/Addon/Mega_Stones_Reverie`** : version avec animation améliorée, à installer **à la place** de l’original, jamais en même temps (même namespace et même UUID). Les 48 objets conservent leurs critères, leur forme cible, leur coût de faim, leurs effets et leur logique. Le son est celui de Deeshura. La charge reprend l’anneau et l’orbe issus de PMDCollab, avec des particules convergentes ; l’éclosion conserve l’étoile par couleur, y ajoute une onde au sol et des éclats qui s’effacent. Le nouveau sprite reste visible à l’éclosion ; le tremblement est court et discret.
- **`Sprites-PMDO`** : banques natives et index fragmentaires par source. Les 18 maîtres ont une forme Méga déclarée et une banque chargée par le moteur, sans repli vers la forme de base. Tyranocif inclut un apport ciblé : banque PMDO plus récente et activation de sa forme 1 déjà définie. Pour l’ensemble des 48 objets, le catalogue recense **37 entrées avec sprite exact dans les données cibles**, dont Tyranocif, et un complément récent pour Médicham, conservé à part et non installé. Les autres entrées ne sont pas annoncées comme disposant d’un sprite exact ; un sprite présent ne suffit pas non plus si sa forme est désactivée.
- **`Sources`**, **`Credits.md`**, **`SHA256SUMS.txt`** : dessins générés originaux retenus, motifs détourés à 1×, planches de référence, sources des VFX Méga, archive du code de Mega Stones, outils d’atelier, crédits et contrôle d’intégrité. Le dépôt nommé « PMD Guildhouse Sprite » n’a pas été identifié ; la révision n’est pas attribuée à cette source.

## Installer sur une copie de test

1. Sur un clone de Destiny contenant la révision Troupes `936b5623`, importer `Spawns-Mega.bundle` ou appliquer le patch, **pas les deux** :

   ```sh
   git bundle verify Spawns-Mega.bundle
   git fetch Spawns-Mega.bundle refs/heads/dojos-spawns-mega:refs/heads/dojos-spawns-mega
   git switch dojos-spawns-mega
   ```

   Alternative : `xz -dc Spawns-Mega-depuis-Troupes.patch.xz | git apply`. Lancer ou reconstruire la quête avec PMDO 0.8.12. Ne pas appliquer le patch à une installation dépourvue de la révision Troupes.
2. Pour la nouvelle animation des objets, copier `Mega/Addon/Mega_Stones_Reverie` dans `MODS` de PMDO, puis activer cet addon. Les pierres existantes conservent leurs identifiants. Ne pas écraser les index globaux de Destiny avec ceux de l’addon. Les banques `Sprites-PMDO` sont une collection de sources ; elles ne sont pas à recopier en bloc dans le jeu.
3. Vérifier sur une sauvegarde de test. Si vous utilisez un build autonome, reconstruire Destiny avec le script de build du projet pour conserver ses données `Data/Misc`. Le bundle et le patch sont locaux : pas de push, pas de release distante, pas de modification d’une sauvegarde utilisateur. Aucun nouveau programme Windows n’est inclus.

## Contrôles dans PMDO 0.8.12

- **18/18 introductions, 54 combattants** : moteur natif, départ direct en finale sur un banc isolé, avec les mêmes cartes, scripts d’apparition et banques que le patch. Le journal consigne, pour chaque chef, la pierre chargée, le sprite exact, puis le passage `0 → 1 → 0` via les scripts de Mega Stones. Cela ne rend pas les cadets Méga et n’ajoute aucun déclenchement de Méga-Évolution aux combats livrés.
- **Tortankite** : sélection et utilisation réelles depuis le sac ; Méga-Tortank apparaît au début de l’éclosion. En prenant un escalier ajouté uniquement au banc, Tortank retrouve sa forme de base à l’étage suivant. Les escaliers de Destiny ne sont pas modifiés.
- **48 objets** : les 48 JSON finaux sont chargés avec `DataManager.GetItem` dans PMDO 0.8.12. Comparaison avec les objets d’origine et contrôle de l’intégrité de l’archive. Tests Lua des calques, timings, positions et restauration d’une pose si un effet échoue. Application et inversion du patch vérifiées par comparaison exacte des arbres Git.

Les vidéos **Les-18-apparitions-dans-PMDO.mp4** et **Tortankite-en-jeu.mp4** sont des captures du banc ; **Apercu-Spawns-et-Mega.mp4** est un comparatif réalisé hors moteur. Les preuves et le [registre des chefs](Registre-des-boss.md) sont dans le ZIP. Ces essais ne remplacent pas une nouvelle traversée depuis le hall avec le build complet de Destiny : l’intégration dans la quête complète et l’équilibrage des 18 combats restent à vérifier sur une copie de test.
