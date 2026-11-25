# Fosse Cascade Fond — Le passage des vasques

[Cinématique avec le son de PMDO](Cinematique-Kabutops-Vasques-agrandies.mp4) · [Carte avant/après](Carte-Fosse-Cascade-Avant-Apres.png) · [Revanche](Revanche-Kabutops-Vasques-agrandies.mp4)

## Ce qui change à l’écran

1. **Le passage.** La carte passe de 480 × 360 à **576 × 528 px**, à la même échelle. Le duo arrive par un couloir rocheux au sud. Le partenaire atteint le seuil avant le héros ; un second panoramique remonte jusqu’à Nilo, resté sur la terrasse.
2. **La rive.** Après l’aveu, la musique s’arrête. Le cadre s’assombrit et un coup sourd déplace les regards vers la droite. Un seul éclair révèle Kabutops ; il quitte la rive et barre le passage avant de frapper. Ni geyser, ni voix hors champ.
3. **Le duel.** La rafale fait reculer le duo sans qu’il tourne le dos. Le cadrage et les positions rejoignent ceux du combat ; les bandes et le woosh natifs passent le relais à l’arène, sans carton. La revanche ne rejoue pas la découverte.

La salle haute est identique pixel pour pixel à l’ancienne carte. L’arène et sa planche 24 px, les collisions du duel, le niveau de Kabutops et les huit étages précédents n’ont pas changé.

## Références

- [Cotovol au Val Silencieux](https://lparchive.org/Pokmon-Mystery-Dungeon-Red-Rescue-Team/Update%2026/) — en particulier les GIF de l’arrivée, du dialogue avec Cotovol et du déplacement vers Tengalice avant l’apparition d’Électhor. La découverte de l’espace précède la menace.
- [Searing Crucible, Halcyon](https://github.com/Palikadude/Halcyon/blob/1522c7a8b7a34d70078e11ed605b21d563b0dc51/Data/Script/halcyon/ground/searing_crucible/searing_crucible_ch_5.lua) — lecture de `FirstPreBossScene` : la caméra accompagne la progression, les secousses et la coupure de musique précèdent l’arrivée de Magcargo. Aucun asset ni dialogue de ces scènes n’a été repris.

## Vérification locale

- [Plans capturés dans PMDO](Preuves/Plans-en-jeu.png) · [Trace de la première rencontre et de la revanche](Preuves/Entree-en-arene.txt) · [Tests de la Fosse, du cadrage et du générateur](Preuves/Tests.txt). Captures au format H.264/AAC, son du jeu sans bruitage ajouté. Le rendu de la VM allonge les mouvements et les attentes dans la vidéo.
- [Bilan natif de victoire](Preuves/Victoire-bilan-natif.png) et [retour au centre de Réverie](Preuves/Retour-a-Reverie-PMDO.png) vérifiés en jeu. Le duel de ce contrôle s’achève avec un Kabutops à 1 PV dans le profil de test uniquement ; aucune modification d’équilibrage n’est livrée.

## Intégration

[Bundle Git](Vasques-agrandies.bundle) · [Patch compressé](Vasques-agrandies.patch.gz). Le lot part de `37138a7ca93be920e9c47963fea21441b153ec65` et comprend aussi le raccord audio/vidéo de la précédente retouche. Le patch a été appliqué sur un index de cette base pour vérifier qu’il reproduit exactement l’arbre livré. Regénérer l’index de tuiles à l’intégration (`python tools/build_tile_index.py`) pour inclure `FGV1_PASSAGE_SUD.tile`.

Aucun push, tag, build Windows ni publication.
