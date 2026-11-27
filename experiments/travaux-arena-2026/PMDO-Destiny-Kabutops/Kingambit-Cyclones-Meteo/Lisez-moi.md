# Dojo Kingambit — Cyclones, pluie et canicule

Révision des **quatre entrées demandées** sur le lot *Spawns et Méga* (`be14e78c`). Les autres apparitions, les 18 troupes, leurs cartes, leurs pierres et l’addon de Méga-Évolution restent inchangés. Les maîtres ne Méga-Évoluent pas automatiquement.

| Finale | Animation d’entrée | Méga-Évolution montrée dans la vidéo |
|:--|:--|:--|
| Vol | Cyclones bleu pâle : des rubans s’enroulent, montent et s’ouvrent pour le plongeon de la troupe. La fin se défait en rafales. | Dracaufeu → **Méga-Dracaufeu X**, Dracaufite X |
| Dragon | Cyclones violets plus larges : un cercle se referme en vortex ; la troupe bondit dans l’œil, puis les rubans éclatent en volutes. | Altaria → **Méga-Altaria**, Altarite |
| Eau | Une averse oblique précède les trois colonnes descendantes. Des ronds et des éclaboussures restent au sol à leur pied. | Tortank → **Méga-Tortank**, Tortankite |
| Feu | Un miroitement de chaleur précède les trois colonnes de flammes. Les filets d’air ondulent et les braises remontent après l’impact. | Braségali → **Méga-Braségali**, Braségalite |

## Aperçus en jeu

- `Apercu-Cyclones-Meteo-et-Mega.mp4` enchaîne l’entrée, puis la transformation pour chacun des quatre types. Les huit passages sont chapitrés.
- `Les-quatre-Mega-Evolutions.mp4` ne montre que les transformations, avec un zoom pixel à pixel sur le porteur.

Les images viennent de **PMDO 0.8.12**. Les quatre intros tournent dans leurs finales habituelles, avec trois adversaires. Pour la démonstration Méga, on joue un Pokémon de l’espèce du chef, puis on active sa pierre **depuis le sac** sur une sauvegarde de test. Ceci ne simule pas un nouveau déclenchement par le boss. Les sons proviennent des banques déjà utilisées par le jeu, recalés au montage. Les captures ont été faites sur un banc isolé, pas lors d’un nouveau parcours depuis le hall de Destiny.

## Patch et banques

Ce ZIP est un **complément** du lot `Kingambit-Spawns-et-Mega`, pas une installation autonome. Sur la révision locale `be14e78c`, importer `Cyclones-Meteo.bundle` ou appliquer `Cyclones-Meteo-depuis-Spawns-Mega.patch.xz`, pas les deux. L’addon `Mega_Stones_Reverie` déjà livré reste le même.

Depuis la racine du clone Destiny, en remplaçant `/chemin/vers/Integration` par le dossier extrait :

```sh
git bundle verify /chemin/vers/Integration/Cyclones-Meteo.bundle
git fetch /chemin/vers/Integration/Cyclones-Meteo.bundle refs/heads/dojos-cyclones-meteo:refs/heads/dojos-cyclones-meteo
git switch dojos-cyclones-meteo
```

Ou : `xz -dc /chemin/vers/Integration/Cyclones-Meteo-depuis-Spawns-Mega.patch.xz | git apply`. Aucun exécutable, push, changement de sauvegarde ou copie d’indices globaux n’est inclus.

### Format des effets

- **Vol, Dragon :** 24 poses chacun, 4 ticks par pose (60 Hz), calques `Sol` et `Air` séparés. Les bandes issues des dessins générés sont cisaillées et animées en profondeur ; amorce, rotation et dissipation ont chacune leurs poses. Chaque combattant a son propre cyclone, décalé de 6 ticks.
- **Eau, Feu :** colonnes locales de 16 poses, ancre centrée et sommet hors écran. La pluie/canicule est une banque `BG` indépendante répétée sur toute l’image : 26 poses, dont début et fin transparents. C’est un effet visuel temporaire, sans changement de météo de combat. Le miroitement est dessiné en pixel art, pas appliqué par un shader aux Pokémon.
- **Planches** PNG : RGBA à alpha droit pour l’édition. **Content** `.dir` : textures à alpha prémultiplié pour la composition dans le moteur. `Index-Cyclones-Meteo.json` donne les tailles, ancres, ordre de lecture, phases et empreintes.
- **Sources** : quatre dessins produits au générateur, cutouts et scripts d’atelier. La commande de régénération de `animer_cyclones_meteo.py` prend le ZIP précédent comme source des colonnes validées. Les scripts du banc ne sont pas inclus dans le patch Destiny.

Le dossier `Preuves` rassemble les tests Lua, les traces des quatre activations et les contrôles des banques. Les crédits du lot précédent restent applicables aux ressources PMD et à *Mega Stones* de Deeshura.
