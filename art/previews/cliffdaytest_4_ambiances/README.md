# cliffdaytest — aperçus « en jeu »

Aperçus produits hors moteur en rejouant le pipeline de dessin de RogueEssence
(`BaseGroundScene.DrawGame`) : fond `LayeredBG` (ciel + nuages, avec `MapLoc` et
défilement `BGMovement`), puis les calques de tuiles **à leur phase d'animation
réelle** (la mer a 8 phases à `FrameLength` 10, soit un cycle de 1,33 s).

## Fichiers

| Fichier | Contenu |
|---|---|
| `planche_vue_ecran_entree.png` | Les 4 ambiances, cadre de jeu 320×240, à l'arrivée par `Dazzling_Entry_South` |
| `ecrans_en_jeu_6_vues.png` | 6 écrans de jeu légendés : entrée sud, maison Pichu, côte ouest (aube), le large (crépuscule), lune et étoiles (nuit), le village (nuit) |
| `avant_apres_4_ambiances.png` | Avant / après le correctif des tuiles orphelines, pour les 4 ambiances |
| `anime_{jour,aube,crepuscule,nuit}.webp` | Bande côtière animée (ciel, nuages qui défilent, mer 8 phases), 3 s en boucle |

## Régénérer

```bash
python3 tools/render_ground_moteur.py cliffdaytest cliffdaytest_aube \
        cliffdaytest_crepuscule cliffdaytest_nuit --out /tmp/apercu

python3 tools/render_ground_moteur.py cliffdaytest --anime --bande 300 \
        --out art/previews/cliffdaytest_4_ambiances
```

## Ce que montrait l'aperçu avant le correctif

Le calque « Terrain — animation 4 phases » des quatre cartes référençait
6 637 cases vers des emplacements absents de
`PICHU_CLIFF_DAY_TERRAIN[_AUBE|_CREP|_NUIT]_FILTRE` (26 548 références avec les
4 phases), toutes au-dessus de la ligne de côte. `GraphicsManager.GetTile`
renvoie alors `BaseSheet.LoadError()` — le `defaultTex`, un damier noir/magenta
32×32 — et `TileLayer.Draw` le dessine **par-dessus** la mer déjà peinte : le
ciel, la mer et les nuages disparaissaient sous les damiers.

Les sous-calques orphelins ont été retirés (commit `0e59286b`), ce qui ne change
aucun pixel du terrain jouable. `tools/tests/test_cliffdaytest_integrite.py`
vérifie désormais que toute référence `TexLoc` existe dans sa planche.
