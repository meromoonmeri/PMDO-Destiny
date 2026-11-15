# AUDIT — Fenêtres & jeux de lumière de la Guilde Destiny

**Périmètre** : les 15 salles de `guilde_destiny_interieur`, 4 ambiances (`jour`, `aube`, `crepuscule`, `nuit`).
**Méthode** : lecture seule des `.rsground`, des 56 `.dir` de fenêtres, de `guilde_destiny_decors.lua`, des 15 `init.lua` et de `meteo_reverie.lua`. Aucune modification de `game/`.
**Outil reproductible** : `tools/audit_guilde_fenetres_ambiances.py` → `audit_fenetres.json`.

## Verdict

**Aucune anomalie bloquante. 14 fenêtres sur 14 ont bien leurs 4 ambiances et un jeu de lumière cohérent ; les 15 salles appliquent le bon filtre d'ambiance.**

| Contrôle | Résultat |
|---|---|
| Salles couvertes | **15 / 15** appellent `AppliquerAmbianceEtFenetres` avec leur propre identifiant |
| Fenêtres déclarées | **14** (9 salles) — les 6 autres salles n'ont **aucune fenêtre dessinée** dans l'art DS |
| Modes d'appel | `Init` + `Enter` + `GameLoad` → l'ambiance est réévaluée aussi au rechargement de sauvegarde |
| `.dir` d'ambiance | **56 / 56** présents (4 par fenêtre) |
| Complétude | **14 / 14** fenêtres ont les 4 variantes |
| Dimensions | **14 / 14** conformes à l'emplacement déclaré |
| Variantes réellement distinctes | **14 / 14** (857 à 2 023 pixels diffèrent entre deux ambiances) |
| Assombrissement de la salle | **15 / 15** monotone jour > aube > crépuscule > nuit |
| Vitre plus lumineuse que le mur la nuit | **13 / 14** |
| Anomalies | **0** |
| Avertissements | **3** (voir plus bas) |

## Détail par fenêtre

`contraste` = luminance de la vitre ÷ luminance moyenne de la salle, **après** application du filtre moteur `WorldAmbianceTint` (`GroundMap.cs`).

| Salle | Fenêtre | Taille | Ambiances | Variantes | Vitre jour → nuit | Contraste nuit | État |
|---|---|---|---|---|---|---|---|
| `accueil` | Fenetre_Gauche | 144×264 | 4/4 | 2023 px | 183 → 41 | 1.06 | ✅ |
| `accueil` | Fenetre_Droite | 144×264 | 4/4 | 1438 px | 163 → 36 | 0.93 | ⚠️ |
| `bureau_maitre` | Fenetre_Centre | 64×88 | 4/4 | 1673 px | 243 → 50 | 1.16 | ✅ |
| `chambre_heros` | Fenetre_Centre | 56×72 | 4/4 | 1103 px | 239 → 48 | 1.18 | ✅ |
| `cuisine` | Fenetre_Gauche | 48×72 | 4/4 | 857 px | 240 → 48 | 1.20 | ✅ |
| `cuisine` | Fenetre_Droite | 48×72 | 4/4 | 859 px | 238 → 48 | 1.19 | ✅ |
| `dortoir_nord_1` | Fenetre_Centre | 64×72 | 4/4 | 1251 px | 240 → 49 | 1.29 | ✅ |
| `dortoir_nord_2` | Fenetre_Centre | 64×72 | 4/4 | 1251 px | 240 → 49 | 1.29 | ✅ |
| `grand_salon` | Fenetre_Gauche | 48×96 | 4/4 | 1029 px | 230 → 45 | 1.10 | ✅ |
| `grand_salon` | Fenetre_Droite | 56×96 | 4/4 | 992 px | 234 → 44 | 1.09 | ✅ |
| `missions` | Fenetre_Gauche | 56×96 | 4/4 | 1189 px | 222 → 45 | 1.13 | ✅ |
| `missions` | Fenetre_Droite | 56×96 | 4/4 | 1183 px | 225 → 45 | 1.12 | ✅ |
| `refectoire` | Fenetre_Gauche | 64×80 | 4/4 | 1536 px | 243 → 49 | 1.16 | ✅ |
| `refectoire` | Fenetre_Droite | 64×80 | 4/4 | 1193 px | 242 → 49 | 1.15 | ✅ |

**Salles sans fenêtre (conforme)** : `carrefour`, `couloir_est`, `couloir_ouest`, `dortoir_sud_1`, `dortoir_sud_2`, `reserve`.
Vérifié sur l'art DS : ces salles n'ont aucune baie dessinée (mur plein + guirlandes). Rien à déclarer.

## Le jeu de lumière, ambiance par ambiance

Le filtre moteur `SetDestinyAmbiance(moment, true)` multiplie **le décor et les objets** par la teinte `WorldAmbianceTint` :

| Ambiance | Teinte appliquée (RGB) |
|---|---|
| `jour` | 255, 255, 255 (neutre) |
| `aube` | 224, 203, 212 (rosé) |
| `crepuscule` | 179, 146, 173 (violacé) |
| `nuit` | 97, 118, 159 (bleu froid) |

Luminance moyenne des **salles** (identique pour tout le réseau, écart ≤ 11 points) :

| Ambiance | Luminance salle | Rapport au jour |
|---|---|---|
| jour | 87 – 98 | 1.00 |
| aube | 72 – 82 | 0.83 |
| crepuscule | 55 – 62 | 0.63 |
| nuit | 38 – 43 | 0.44 |

Les **vitres** sont pré-compensées par `reconstruct_window_ds()` : seuls les pixels de verre reçoivent une compensation `(0.75 + 0.25·wt) / wt`, le cadre en bois reste bit-à-bit identique au décor. Résultat : l'ambiance du ciel (rosé, violacé, étoilé) est **conservée** au lieu d'être re-teintée par le filtre, et la vitre reste plus lumineuse que le mur.

## Avertissements (aucun n'est bloquant)

1. **`accueil` / `Fenetre_Droite` — contraste nuit 0.93.** Cette fenêtre tombe légèrement **sous** la luminance moyenne de la salle la nuit : elle cesse de luire. C'est la seule des 14. Cause : son ciel nocturne est le plus sombre des deux baies du hall, alors que le hall est la pièce la plus lumineuse. Correctif possible sans casser la couture : remonter la compensation du verre de `0.75+0.25·wt` à `0.85+0.15·wt` sur cette seule baie.

2. **`SV.Destiny.GuildeAmbiance` n'est jamais écrit.** Le registre le lit comme override prioritaire (`guilde_destiny_decors.lua:61`), mais aucun script n'y écrit : la branche est morte. En pratique l'ambiance vient toujours de `meteo_reverie.Moment()`. Soit on l'alimente (par exemple depuis une cinématique qui veut forcer une ambiance de salle), soit on retire le hook.

3. **Pas de mise à jour en direct.** `meteo.Appliquer()` sort immédiatement pour les intérieurs (`if map == nil or not exterieurs[map.AssetName] then return false end`). Si le moment change pendant que le joueur est dans une salle, le filtre **et** les `.dir` de fenêtres ne suivent qu'après une sortie/entrée (ou un rechargement, via `GameLoad`). C'est cohérent avec le reste du jeu, mais à savoir si vous voulez une horloge qui tourne en intérieur.

## Pièces jointes

| Fichier | Contenu |
|---|---|
| `planche_positions.png` | Les 15 salles au **jour**, chaque fenêtre encadrée en rouge |
| `planche_ambiances.png` | Les 9 salles à fenêtres × 4 ambiances (salle + fenêtres compositées et filtrées comme en jeu) |
| `audit_fenetres.json` | Rapport complet (tailles, variantes, luminances, contrastes) |
| `lumieres_par_ambiance.json` | Luminance salle/vitre par ambiance, pour les 15 salles |
