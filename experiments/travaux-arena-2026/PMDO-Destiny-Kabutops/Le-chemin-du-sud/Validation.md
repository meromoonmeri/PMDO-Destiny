# Le chemin du sud — retour de Nilo

**Révision :** `37e6b5cdcfb46a064239c7c6983ef4840d27d408`, après [Le pardon des vasques](../Le-pardon-des-vasques/Validation.md) (`920e5d5`). Le travail porte sur la scène d’après-duel, les tests et les notes 0.7.6. Le combat, les cartes et la cinématique d’accueil de Réverie Town ne sont pas modifiés par cette retouche.

## Ce qui se passe à l’écran

1. Kabutops reconnaît son erreur, se souvient des vasques paisibles et s’excuse auprès de Nilo et du duo. Après le retrait des quatre Kabuto, il dit au revoir à Nilo, puis s’enfouit à son tour.
2. Nilo descend. Lyra remonte le passage et s’arrête sur le même axe, à 32 px de Nilo : « J’ai entendu du bruit. Que s’est-il passé ? » Nilo raconte l’accusation et le sauvetage. Le héros, soulagé, propose de reprendre le chemin du sud.
3. Lyra confirme le retour à Réverie Town. Les quatre acteurs s’engagent dans le coude sud à l’écran. Un fondu noir termine la scène.
4. PMDO affiche le vrai bilan d’expédition « La dernière sortie », comme dans le déroulé de Halcyon : **journal, validation, retour en ville**. Aucun faux journal ni jingle doublé. L’événement d’accueil existant reçoit l’équipe à Réverie Town.

## Vérification

- [Tests locaux](Preuves/Tests-locaux.txt) : cinq K.O., ordre des répliques et du Tunnel, jalons avant le noir, clôture native unique, chemin sur le sable sans rencontrer les collisions sur trois phases de rendu. Les tests de non-régression et les audits Lua passent.
- [Trace du duel avec les capacités habituelles](Preuves/Trace-controle-avec-les-capacites-natives.txt) et [trace de la prise finale](Preuves/Trace-victoire-et-retour.txt) : le chef seul K.O. laisse le combat en cours ; les cinq K.O. précèdent l’entrée en phase 3. La fixture reste locale : duo niveau 50, chef à 1 PV pour le contrôle, et Lance-Flammes/Décharge pour raccourcir le duel de la seconde prise. Ce n’est pas un test d’équilibrage.
- [Journal moteur du retour](Preuves/Journal-retour.txt) : après le bilan, PMDO sauvegarde et charge `WaterfallVillageCapital`, puis `reverie_centre`. L’accueil se joue jusqu’au bout, l’équipe reçoit la Gelée Royale, l’événement passe à `termine` et [le jeu rend la main](Preuves/Retour-au-joueur.png).
- [Contrôle du rendu](Preuves/Ressources-du-profil.txt) : les deux cartes proviennent du payload original. La première prise a révélé des damiers dus à l’effet de pluie absent du profil réduit. La seconde impose la pluie de test avec le véritable `Rain.dir` (blob `5700c5f`). La place et les acteurs s’affichent sans damier, sans retouche de carte ni de ressource distribuée.

## Repères dans la vidéo

| Moment | Repère |
| --- | ---: |
| Au revoir de Kabutops | 0:29 |
| Lyra s’arrête et interroge Nilo | 0:36 |
| Départ par le sud | 0:58 |
| [Journal de victoire natif](Preuves/Journal-de-victoire.png) | 1:02 |
| [Accueil de Léo à Réverie Town](Preuves/Accueil-en-ville.png) | 1:13 |
| [Retour au contrôle](Preuves/Retour-au-joueur.png) | 2:48 |

## Fichiers

- [Capture en jeu](Le-retour-de-Nilo.mp4) : 2 min 48 s, sans coupe interne, avec le [son natif du jeu](Preuves/Audio-natif.txt).
- [Patch de la retouche](Le-chemin-du-sud.patch) à partir de `920e5d5` ; [bundle Git](Destiny-v0.7.6-Retour-Nilo.bundle) depuis la base publique `37138a7`, importé et contrôlé au [SHA exact](Preuves/Integration.txt).
- [Notes 0.7.6](Notes-v0.7.6.md), [repères vidéo](Preuves/Chronometrage.txt) et [sommes SHA-256](SHA256SUMS.txt).

## Push

**Effectué et vérifié :** la [branche WIP sur GitHub](https://github.com/meromoonmeri/PMDO-Destiny/tree/wip/reverie-integration-kingambit-cafe) pointe sur `37e6b5cdcfb46a064239c7c6983ef4840d27d408`. Le [journal du push](Preuves/Publication.txt) confirme le passage de `37138a7` à ce SHA sans forcer. 

**Préversion Windows publiée :** [v0.7.6](https://github.com/meromoonmeri/PMDO-Destiny/releases/tag/v0.7.6), tag sur ce même SHA. Le [build vérifié](https://github.com/meromoonmeri/PMDO-Destiny/actions/runs/44891174901) est réussi ; le ZIP complet et le delta 0.7.5 → 0.7.6 ont passé le contrôle des SHA-256 et des CRC après téléchargement. [Preuve de publication](Preuves/Release-v0.7.6.json). La chronique des habitants ne fait pas partie de cette version.
