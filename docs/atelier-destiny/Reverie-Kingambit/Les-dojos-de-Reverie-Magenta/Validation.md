# Les dojos de Réverie — candidat DTEF

**Candidat local vérifié :** `2e003fe99a270797eb95c586d6b46b247eb5ff02` (`dojos-dtef`). Il remplace le premier colis des Dojos. **Non poussé.** La branche distante `wip/reverie-integration-kingambit-cafe` est toujours à `37e6b5cdcfb46a064239c7c6983ef4840d27d408` ; ni tag ni release Windows n'ont été créés.

## À ouvrir

- [Aperçu vidéo](Apercu-video-Dojo-DTEF.mp4) — 28,7 s, 720p, sans son. Deux chutes réellement capturées dans PMDO (Normal et Fée) ; escaliers, arène de Fouinar, retour et reprise. Les images fixes des autres arènes et des trappes sont signalées comme telles.
- [Planche des 18 arènes](Les-18-arenes-DTEF.png) — 15 × 11 cases, échelle 1×. Sol, parois et relief secondaire en cellules DTEF natives, avec les variantes et pistes d'animation des biomes d'origine. Ce ne sont pas des fonds générés ni des cartes reprises d'un dojo voisin.
- [Sources et tilesheet des trappes](Sources-et-tilesheet-trappes.zip) — 8 bruts générés sur magenta, 18 calques de sol et 18 de rebord à l'échelle native, PNG d'édition et banque `.tile` sur grille de 24 px. [Planche sol](Trous_Sol_24.png) · [planche rebord](Trous_Rebord_24.png) · [repérage des lignes](Trous_index.json). En jeu, 36 DirSheets animées de 10 poses sont routées par type.
- [Atlas Map Backgrounds](Atlas-Map-Backgrounds.html) et [index CSV](Index-Map-Backgrounds.csv) — 338 fonds, 338 vignettes, sept pages de l'album Project Pokémon. Ce sont les références du prochain lot **hors labyrinthe** (exploration et boss), pas des fonds incorporés dans ce candidat. Aucun nouveau lieu hors labyrinthe n'a été ajouté ici.

Les cartes et banques des dojos Ledian et Ossatueur, le duel de Liane, la rive sud et les autres cartes de Réverie ne sont pas modifiés par la refonte. Les accès de Kingambit à l'arène annexe et aux reliques restent indépendants du menu de Kaito. L'art des arènes du labyrinthe dépend du **jeu de base**, sans copie de ses banques DTEF dans le bundle.

## Vérifié

- **Moteur PMDO Linux :** trois graines, 162 étages chargés, dont les 18 finales sur chaque graine. [Trace](Preuves/generations-162.txt).
- **Normal au clavier :** chute au 1F, deux escaliers natifs, victoire sur Fouinar (51 PV), retour au hall, EXP 459 → 591, sac à 1 objet. Deux Pokémon de test de niveau 19 ; pas un test d'équilibrage. [Parcours](Preuves/moteur-parcours.txt).
- **Reprise à froid :** sauvegarde vérifiée, EXP et victoire conservées, [marque + encore visible](Preuves/Reprise-marque-Plus.png). La chute Fée conduit au bon 1F ; l'abandon dans le menu natif ramène au hall avec l'EXP et le sac intacts. [Reprise et abandon](Preuves/moteur-fee-reprise.txt).
- **Reconstruction graphique :** 18 cartes reproduites à l'identique, 36 DirSheets et planches d'édition reproductibles. 572 feuilles de référence DTEF reconstruites en test, 23 343 cellules et poses copiées sans modification. Mise sur une seule grille, alpha binaire, frange magenta supprimée et correction de 849 pixels isolés sur l'ensemble des variantes de trappe. [Journal](Preuves/Reproduction.txt).
- **Automatisé :** neuf suites vertes (dédales, complexe, Chemins, entrées, suivi, quartiers, carrefour, Foyers, K.O.). [Journal](Preuves/Tests-locaux.txt). Les 18 maîtres n'ont pas tous été combattus manuellement.
- **Livraison Git :** bundle importé dans un autre dépôt ; application et inversion du patch avec arbres Git exacts. [Journal](Preuves/Import-et-patch.txt).

## Import local et push éventuel

Importer [le bundle](Les-dojos-DTEF.bundle) dans un clone qui contient le commit public `37e6b5c`. Le [patch compressé](Les-dojos-DTEF.patch.xz) est une alternative sur la même base. Le jeu et ses assets de base sont des dépendances ; ce ne sont pas des installateurs Windows.

```sh
git fetch /chemin/Les-dojos-DTEF.bundle refs/heads/dojos-dtef:refs/heads/dojos-dtef
git log -1 --oneline dojos-dtef
```

Pour une copie locale du jeu, reconstruire l'index de tuiles depuis un clone complet où les assets sont assemblés (`python tools/build_tile_index.py`). Pour envoyer le commit, depuis un clone authentifié et après avoir vérifié la branche distante :

```sh
git push origin refs/heads/dojos-dtef:refs/heads/wip/reverie-integration-kingambit-cafe
```

Sans forcer ; si le distant a avancé, vérifier les nouveaux commits avant d'intégrer. Ce push n'est pas une publication de release.
