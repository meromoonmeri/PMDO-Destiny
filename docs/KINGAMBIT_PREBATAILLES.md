# Kingambit — les 18 wooshes façon PMD

La variante **PMD à fondu blanc** est active sur `dojos-kingambit-pmd`. La première variante (grands rubans et sceaux) reste consultable au commit `7fcd061` ; ses banques et sons, devenus inactifs, ne sont pas chargés aux côtés de la nouvelle série.

## Enchaînement en jeu

1. Le maître et ses deux cadets apparaissent comme avant. `DestinyDojoTroupeJouer` garde son appel existant ; le module ajoute le woosh seulement dans une finale Kingambit 3F, après le trio en place.
2. Deux impulsions donnent le départ. Neuf traînées fines entrent en cinq vagues de directions alternées. Elles reprennent le placement, le délai et le son `EVT_Battle_Transition` de [`COMMON.BossTransition`](../base/Data/Script/origin/common.lua). Il n’y a pas de sceau central.
3. Le moteur exécute `GAME:FadeOut(true, 30)`. Les bandes expirent au blanc complet, maintenu 10 ticks ; `GAME:FadeIn(12)` rend la même arène visible. Le woosh dure 178 ticks (2,97 s à 60 i/s), amorce et retour compris.
4. L’événement natif `BeginBattleEvent` à `-5` reprend avec `map_clear_check`. Aucun tour n’est ajouté. Ni les équipes, ni les cartes, ni la musique, ni les apparitions météo, ni la scène Dazzling ne changent dans cette variante.

Les quatre textures 256 × 64 et leurs miroirs sont dans chaque `Kingambit_Prebataille_PMD_<type>.dir`. Décor et caméra sont ceux du donjon, pas un panneau précalculé. La banque vanilla sert de repli si celle d’un type manque. Le module restaure le mode de jeu et quitte le blanc en cas d’erreur de raccord.

## Signatures

| Type | Maître | Traînée |
|---|---|---|
| Normal | Lockpin | Échos d’ivoire |
| Feu | Braségali | Pointes de braise |
| Eau | Tortank | Crêtes d’écume |
| Plante | Jungko | Filets de feuilles |
| Électrik | Élecsprint | Sauts d’étincelles |
| Glace | Oniglali | Échardes de givre |
| Combat | Lucario | Chevrons d’impact |
| Poison | Ectoplasma | Bulles de miasme |
| Sol | Laggron | Failles de sable |
| Vol | Dracaufeu | Plumes d’alizé |
| Psy | Alakazam | Réfraction |
| Insecte | Dardargnan | Rafales d’essaim |
| Roche | Tyranocif | Pierres taillées |
| Spectre | Branette | Veilleuses fuyantes |
| Dragon | Altaria | Sillage d’écailles |
| Ténèbres | Démolosse | Entailles nocturnes |
| Acier | Métalosse | Rails d’argent |
| Fée | Gardevoir | Poudre d’étoiles |

Douze textures utilisent un dessin généré dédié. Vol, Psy, Insecte, Roche, Spectre et Ténèbres adaptent une texture générée en variant sa silhouette, ses détails et sa vitesse. Le [dossier de l’aperçu](../art/previews/kingambit_wooshes_pmd/) inclut les sources et la provenance des textures.

```sh
python art/previews/kingambit_wooshes_pmd/Sources/texturer_wooshes_pmd.py --pmdo base --out /tmp/wooshes-pmd
lua tools/tests/test_dojo_kingambit_prebatailles.lua
```

Le générateur nécessite Python, Pillow, NumPy et SciPy. Le banc isolé PMDO Linux 0.8.12 ouvre directement chaque finale. Les 18 capturées retrouvent le combat natif avec le trio attendu ; le plateau blanc couvre l’image pendant 5 à 6 images enregistrées à 30 i/s. Le son est celui du moteur. Ce n’est pas un essai de parcours complet de Destiny, ni de build Windows.
