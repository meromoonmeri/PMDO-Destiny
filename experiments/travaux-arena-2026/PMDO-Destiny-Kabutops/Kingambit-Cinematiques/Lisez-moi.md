# Kingambit — la trappe et les 18 finales

**Les scènes sont jouées par le moteur.** L’aperçu est une capture de PMDO 0.8.12, pas une animation ajoutée au montage.

- [Voir la vidéo : la trappe, puis les 18 finales](Kingambit-La-trappe-et-les-18-finales.mp4) · [Chapitres](Chapitres.md)
- [Télécharger la retouche à essayer sur une copie de Destiny v0.7.7](Kingambit-Cinematiques-pour-v0.7.7.zip)
- [Patch Git](Sources/Kingambit-Cinematiques.patch) · [Notes d’intégration](Sources/Integration.md) · [Empreintes](Empreintes.json)

## Dans le jeu

Parlez à **Kaito**, choisissez un type et confirmez « Descendre ». Le duo prend place sur le sceau. Les deux pênes reculent, les panneaux coulissent et le rebord masque les sprites à mesure qu’ils tombent. La silhouette et les couleurs de la trappe du biome restent reconnaissables.

Au troisième étage, la salle s’éteint. **« ??? »** parle sans portrait et le noir reste en place jusqu’à la fin de la lecture. Trois signaux propres au type annoncent les places de la troupe : les gouttes d’Eau, les cyclones de Vol, le prisme de Psy, les lanternes de Spectre, etc. Le maître et ses cadets entrent ; après la réplique avec portrait, le woosh PMD précède le combat. Les 18 scènes ont des dialogues en français. La troupe et la condition de victoire restent inchangées.

## Pour essayer la retouche

Fermez le jeu et sauvegardez `SAVE`. Utilisez **une copie non modifiée de Destiny v0.7.7**. À côté de `JOUER_A_DESTINY.bat`, fusionnez les dossiers `Content` et `Data` du ZIP avec ceux de la copie, puis lancez-la normalement. Ne remplacez pas un `event.lua` personnalisé. Pour revenir en arrière, reprenez l’installation d’origine.

Le colis ne contient ni sauvegarde, ni carte à remplacer, ni exécutable. Le commit [0c0a13f](https://github.com/meromoonmeri/PMDO-Destiny/commit/0c0a13f75e13ab95132b66b282dae1b369ef885b), basé sur `3d86bd8`, a été poussé et vérifié sur `wip/reverie-integration-kingambit-cafe` ([preuve du push](Etat-du-push.txt)). `main`, `dojos-kingambit-pmd` et la préversion `v0.7.7` restent inchangés. Aucune CI lancée manuellement et aucune nouvelle release. La retouche a été testée sous Linux avec PMDO 0.8.12.

## Contrôles

- [Les 18 finales](Controles/PMDO-18-finales.txt) : déclenchement natif du combat, trois combattants aux cases prévues, formes d’origine, `map_clear_check` et fin du mode cinématique. Le banc saute les deux premiers étages pour cette série, pas le démarrage du combat.
- [Le duo](Controles/PMDO-trappe-duo.txt), [le solo](Controles/PMDO-trappe-solo.txt) et [le partenaire en tête](Controles/PMDO-trappe-chef-inverse.txt) : vraie action de Kaito, pênes, chute, position immobile de Kaito et entrée à l’étage 1.
- [Repli Spectre](Controles/PMDO-repli-spectre.txt) : lumière manquante dans une copie de test, scène écourtée mais combat démarré.
- [Tests Lua et ressources](Controles/Tests-Lua-et-ressources.txt) · [Noir et chapitres](Controles-video.json) · [Piste son de la trappe](Controles/Audio-trappe.json).
