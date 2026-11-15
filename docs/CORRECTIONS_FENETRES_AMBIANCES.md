# Fenêtres & ambiances de la Guilde Destiny — corrections

**État final : 0 anomalie, 0 avertissement.** Audit reproductible : `tools/audit_guilde_fenetres_ambiances.py`.
Commit : **`0e07c46`** sur `wip/reverie-integration-kingambit-cafe`.

## Le défaut que vous avez repéré

Dans l'accueil, les 4 ambiances des fenêtres étaient **quasi identiques** : seuls **7,6 %** des pixels changeaient entre le jour et la nuit, contre 36 % pour la salle des missions.

**Cause** — le générateur classait les pixels « bois » par une règle de couleur *et* une comparaison au décor brut de la pièce (`diff < 22`). Or dans l'accueil, le ciel de jour est **crème** et le mur alentour aussi : toute la baie était classée « bois ». Comme seuls les pixels de verre reçoivent la compensation et les variantes d'ambiance, l'accueil n'avait **aucune** fenêtre qui changeait.

C'était le cas pour **les 13 fenêtres**, pas seulement l'accueil — c'est simplement là que ça se voyait le plus.

## Ce que fait le nouveau générateur

`tools/refaire_fenetres_ambiances.py` — 56 `.dir` régénérés.

| Avant | Après |
|---|---|
| Bois/verre par heuristique de couleur sur le décor | **Séparation structurelle** : est verre toute composante non-orange (`r − g < 25`) qui **ne touche pas le bord** de l'image. Le cadre et les meneaux touchent toujours le bord → exclus mécaniquement. |
| Ciel conservé avec son dithering d'origine | **Dégradé vertical 4 tons** par ambiance : jour crème, aube rosée, crépuscule braise, nuit étoilée |
| Compensation écrasée quand `wt` était mal détecté | Calcul en **couleur effective** (ce que voit le joueur) puis division par `WorldAmbianceTint` → la vitre ressort sur le mur |
| Cadre modifié dans certains cas | **Cadre DS strictement intact**, alpha intact, rien touché hors du verre |

### Résultat mesuré (luminance effective de la vitre, après filtre moteur)

| Fenêtre | Jour | Aube | Crépuscule | Nuit |
|---|---|---|---|---|
| accueil / Gauche | 163,3 | 137,3 | 102,2 | **52,0** |
| accueil / Droite | 162,1 | 136,5 | 101,7 | **51,9** |
| missions / Gauche | 159,6 | 134,6 | 100,1 | **51,2** |
| dortoir_nord / Centre | 170,6 | 144,0 | 109,1 | **54,4** |
| bureau_maître / Centre | 176,5 | 147,4 | 112,7 | **56,3** |

Décroissance régulière sur les 14 fenêtres. Les **14 ressortent la nuit** (contraste vitre/salle ≥ 2,3 en moyenne) — la pire baie était à **0,93** avant, c'est-à-dire *moins lumineuse que le mur*.

## L'ambiance, en plus

Deux défauts trouvés en chemin, corrigés aussi :

1. **Pas de mise à jour en direct.** `meteo.Appliquer()` sort immédiatement pour les intérieurs : une salle gardait l'ambiance de son entrée, même si le moment changeait.
   → `guilde_decors.SynchroniserAmbiance(map, id)` appelé dans les **15 `Update`**, vérification toutes les 30 frames ; filtre moteur **et** `.dir` de fenêtres suivent.
2. **Override mort.** `SV.Destiny.GuildeAmbiance` était lu en priorité mais **jamais écrit**.
   → `guilde_decors.ForcerAmbiance(map, id, moment)` et `LibererAmbiance(map, id)` : une cinématique peut désormais figer l'ambiance d'une salle, et la rendre à l'horloge du monde ensuite.

## Vérifications

- audit : **15/15** salles couvertes, **56/56** `.dir`, **14/14** variantes distinctes, **14/14** fenêtres lumineuses la nuit, **0** anomalie, **0** avertissement ;
- **129** fichiers Lua compilés sans erreur ;
- tests au vert : `test_guilde_destiny_accueil`, `test_suivi_interieurs`, `test_guilde_enrolement`, `test_batiments_interieurs` ;
- `index.idx` régénéré ;
- serveur d'aperçu resynchronisé (112/112 variantes à jour ; la version « sauvegarde c2766e5 » garde volontairement ses anciens assets).

## Pièces jointes

| Fichier | Contenu |
|---|---|
| `avant_apres_fenetres.png` | 4 fenêtres × 4 ambiances, **avant** (DS 673e05b) / **après** |
| `apres_ambiances_4_salles.png` | Rendu en jeu : 4 salles × 4 ambiances, fenêtres compositées et filtrées |
| `planche_positions.png` | Les 15 salles au jour, fenêtres encadrées |
| `planche_ambiances.png` | Les 9 salles à fenêtres × 4 ambiances |
| `audit_fenetres.json` | Rapport complet par fenêtre |
| `lumieres_par_ambiance.json` | Luminance salle / vitre par ambiance |

## Reste à décider

Les **6 salles sans fenêtre** (`carrefour`, `couloir_est`, `couloir_ouest`, `dortoir_sud_1`, `dortoir_sud_2`, `reserve`) restent sans baie : c'est conforme à l'art DS d'origine. Si vous voulez qu'elles en aient, il faut dessiner de nouveaux emplacements — dites-moi et je les ajoute avec les 4 ambiances.
