# Éclipse X + Prisme fendu — préparation d’une capture en jeu

## Demande
Intégrer la version 04 « Éclipse X + Prisme fendu » à une copie de test de Destiny, puis enregistrer une vraie capture du jeu en MP4. Ne pas présenter le rendu hors moteur comme une capture réelle.

## État
- La vidéo existante est `~/Reference-Guildhouse/Mega-sans-colonnes/04-Eclipse-X-Prisme.mp4` : maquette hors moteur, Dracaufeu vers Méga-Dracaufeu X, 4,8 s, 30 i/s.
- Les notes `~/Reference-Guildhouse/Mega-sans-colonnes/Credits-et-notes.md` précisent que la version 04 n’est pas un effet importable en l’état. Les scripts locaux `Sources/fusion_eclipse_prisme.py` et `Sources/rendre.py` cités dans ces notes ne sont pas présents dans le workspace persistant.
- Les cycles V2 d’origine et le son Mega Stones ont été récupérés dans `Sources/`, avec le manifeste et la licence. Ce ne sont pas les couches reconstruites ni l’intégration de la version 04.
- L’archive officielle Windows Destiny 0.7.8 a été téléchargée et vérifiée : SHA-256 `bc0df2c724bdae26211a9b980527cc39fcc0545fea60522d1452e649da925eb0`. Une copie extraite et son préfixe Wine ont été installés temporairement dans `~/.cache/destiny-test/` (dossier non garanti persistant).
- Wine et Xvfb ont lancé le vrai exécutable Destiny jusqu’à son écran d’avertissement « press any key ». La capture interne de cet écran a confirmé l’affichage. Le processus s’est ensuite terminé avec le code 137 avant la transformation. Cause précise non confirmée.
- Aucun MP4 de la version 04 capturé en jeu n’a été produit. Aucun fichier de jeu utilisateur, sauvegarde ou dépôt distant n’a été modifié.

## Travail restant
1. Reconstituer les calques et synchronisations exacts de la fusion à partir des cycles et de la vidéo de référence ; retrouver si possible les scripts de rendu manquants.
2. Convertir les couches en ressources et événements PMDO réels ; synchroniser un vrai changement de forme de Dracaufeu en Méga-Dracaufeu X sur une sauvegarde de test, sans altérer le projet utilisateur.
3. Relancer et stabiliser le jeu dans un environnement graphique adapté ; tester le rendu, les timings et les ressources en jeu.
4. Enregistrer l’écran du moteur en MP4 et préciser tout montage sonore éventuel.

## Sources
- Guilde Treehouse PMD, cycles V2 au commit `63f1e4806f1e382ca6e00b984a5730d5cd1553d6` : https://github.com/meromoonmeri/guilde-treehouse-pmd/tree/63f1e4806f1e382ca6e00b984a5730d5cd1553d6/renders/mega_evolution_v2
- Mega Stones de Deeshura, commit `31a26eb9ed3030b6b51ef7a6f2b70bc09ad3ec3a`, son et licence : https://github.com/Deeshura/Mega_Stones/tree/31a26eb9ed3030b6b51ef7a6f2b70bc09ad3ec3a
- PMDO-Destiny 0.7.8 : https://github.com/meromoonmeri/PMDO-Destiny/releases/tag/v0.7.8

## Nouvel essai après clarification
- Le jeu normal a atteint le menu de sélection de langue sous Wine/Xvfb avec rendu logiciel, avant d'être tué (code 137) après la sélection. Le processus affichait environ 981 Mo RSS peu avant son arrêt ; cela suggère une limite mémoire, sans la démontrer.
- Les deux scripts de création de la variante 04 restent introuvables ; l'effet n'est toujours pas importé et il n'existe pas de capture en jeu de cette variante. Une ancienne capture de Méga-Dracaufeu X utilise une autre animation et ne répond pas à la demande.

## Avancée : banc Linux et dialogue (essais isolés)
- L'exécutable Linux officiel PMDC 0.8.12 a été téléchargé dans le cache et lancé avec les données de la copie Destiny. L'index de tuiles Destiny (200 Mo) dépassait la limite mémoire du banc ; le remplacer temporairement, sur cette copie uniquement, par l'index PMDO standard (3,6 Mo) a permis de démarrer et d'ouvrir l'éditeur en mode développeur. Les cartes Destiny personnalisées peuvent ne pas fonctionner avec cet index. L'index Destiny d'origine est préservé dans `~/.cache/destiny-test/index-destiny-original.idx`. Aucune installation ni sauvegarde utilisateur n'a été modifiée.
- Nouveau module préparatoire `Sources/dialogue_mega_degrade.lua` : « Vous avez Méga-Évolué en Méga-Dracaufeu X ! », dégradé par lettre bleu clair → bleu électrique → violet. La console Lua intégrée du moteur a exécuté le fichier et généré les balises avec les accents intacts. La boîte de dialogue elle-même n'a pas encore été affichée ni testée dans un donjon ; le module n'est pas branché au déclenchement.
- L'animation Éclipse X + Prisme fendu n'a pas encore été reconstruite/intégrée. Aucun changement de forme associé ni vidéo en donjon n'a été produit. Ne pas présenter le test de console comme une preuve de la séquence.

## Capture réalisée : reconstitution expérimentale en donjon
- Un banc isolé sur l'exécutable natif PMDO 0.8.12 et les données de la copie Destiny a créé Dracaufeu et accédé réellement au donjon `ambush_forest`, étage 0. Le script de démarrage utilisé se trouve dans `Banc-test/intro_halo_banc.lua`. Ce démarrage et l'index allégé sont spécifiques au banc, pas un patch jouable à installer.
- Le script perdu de 04 n'a pas été retrouvé : `Sources/reconstruire_effet_test.py` recrée une approximation avec les cycles V2 existants et des orbites redessinées. La banque `Banc-test/Eclipse_Prism_Test.dir` a réellement été chargée et jouée dans le moteur, devant le vrai Pokémon ; ce n'est pas une restitution garantie exacte de la vidéo de référence (notamment orbites, particules, iris et éclat latéral diffèrent).
- `Banc-test/scene_mega_test.lua` synchronise l'effet avec le changement de forme de 0 vers 1 via `destiny.mega.evoluer`; QI 410 donné uniquement sur la sauvegarde jetable. Le journal `Banc-test/journal-moteur.txt` confirme `début base=0`, puis `promotion base=1`. La boîte de dialogue du moteur s'affiche avec le dégradé. Ce n'est pas encore une fonctionnalité intégrée au gameplay normal.
- `Video-test/capture-brute-sans-son.mp4` est la capture directe écran du moteur, sans son. `Video-test/Mega-Dracaufeu-X-essai-donjon.mp4` reprend la capture rognée en durée (0,8 s retirée au début) et ajoute en montage le son `Mega_Evolution.ogg` (décalage 950 ms). Le son n'a pas été capturé depuis le moteur. Aucune image hors jeu n'a été ajoutée à la vidéo.
- Il reste à reconstruire plus fidèlement les couches exactes de 04, brancher le déclenchement au gameplay et enregistrer le son natif ; ce résultat est une preuve de l'essai, pas une release ni une reproduction exacte certifiée.

## Révision V2 : fanfare dans le moteur et nouvelle capture
- `Sources/reconstruire_effet_test.py` reconstruit une seconde version : orbites plus larges et visibles devant la sphère, iris horizontal, progression bleu nuit → prisme, fissure anticipée, éclats latéraux et anneaux au sol ; toujours sans colonnes ni sprites incrustés. La banque est `Banc-test/Eclipse_Prism_Test_V2.dir`.
- Dans `Banc-test/scene_mega_test.lua`, `SOUND:PlayFanfare('Fanfare/MissionClear')` est appelé juste avant `UI:WaitShowDialogue`, après la promotion réelle 0→1. Cette fanfare est un son du jeu, pas une piste ajoutée après coup.
- Pour enregistrer le son natif, PulseAudio a été lancé avec un sink virtuel et ses options `--realtime=no --high-priority=no`; l'exécutable PMDO a été relié au sink puis FFmpeg a capturé son moniteur avec la fenêtre du jeu. La capture brute A/V est `Video-test/capture-brute-v2-son-du-jeu.mp4`. La vidéo `Video-test/Mega-Dracaufeu-X-donjon-victoire.mp4` coupe 0,5 s au début et 0,7 s à la fin et réencode, sans ajout d'image ni de son.
- Vérifications : `Banc-test/journal-moteur-v2.txt` montre début forme 0, promotion forme 1, puis fanfare + dialogue ; corrélation du signal enregistré avec le fichier d'origine MissionClear = 0,686, début vers 6,945 s dans la capture brute. Le dialogue apparaît au même moment dans la vidéo. Les scripts d'origine de 04 manquent toujours : cette V2 est plus fidèle mais n'est pas certifiée identique. Fonctionnement démontré uniquement sur banc de test, pas intégré au gameplay normal.
