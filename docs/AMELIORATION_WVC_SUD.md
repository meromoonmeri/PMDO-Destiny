# Waterfall Village — amélioration de la partie sud

Basé sur la version **la plus avancée** du Ground : celle du Drive de l'auteur
(`WaterfallVillageCapital (1).rsground`, 330 233 300 octets, modifiée le
27/10/2026, 37 calques, 41 planches). Elle remplace la version `town02`
(233 727 831 octets, 28 calques) jusque-là intégrée.

---

## 1. Ce qui n'allait pas

Le rendu hors-moteur (`docs/apercus/`) montrait trois défauts nets :

1. **Un grand vide vert au sud.** Le contenu s'arrêtait à la ligne 348 (case 8 px).
   En dessous, un **unique calque de remplissage** répétait la même case de
   gazon (`Altere_Pond_Cliffs` @ 106,5) sur 146 lignes × 200 colonnes, soit
   **29 200 cases** sans chemin, sans objet, sans collision (0 case bloquée).
2. **Des buissons posés en grille.** Le calque `Layer 34` plaçait le même
   buisson (`Metano_Town_Objects_Under` @ 64,18) à intervalle régulier : le
   motif se lit immédiatement comme un tampon automatique.
3. **Aucun réseau de chemins au sud.** Les deux ponts de bois qui franchissent
   la rivière débouchaient sur du gazon : les chemins s'arrêtaient net.

---

## 2. Ce qui a été fait

Le sud est désormais une **extension réelle du village**, construite
exclusivement par **copie de blocs natifs** de la carte elle-même : aucun
graphique inventé, aucune planche ajoutée, aucun tileset nouveau.

| Opération | Source (cases) | Destination | Cases |
|---|---|---|---:|
| Village continu | (0,216) → (200,348) | (0,366) | 26 400 |
| Berge boisée sous la rivière | (0,337) → (200,348) | (0,355) | 2 200 |
| Lisière forestière de bord | (0,337) → (200,347) | (0,490) | 2 000 |

La coupe source est **contiguë sur 132 lignes** : le réseau de chemins, les
murs, les escaliers et les bassins restent donc connectés à l'intérieur de la
zone copiée — c'est ce qui manquait à la première tentative, faite de trois
bandes non adjacentes où les chemins se coupaient aux jonctions.

Les **collisions suivent** : chaque copie reporte aussi les tags `obstacles`
de la zone source. Le sud passe de **0 à 15 994 cases bloquées** sur 26 800
(arbres, murs, maisons, bassins) — sans quoi on traverserait les arbres.

### Deux primitives d'édition nouvelles

`tools/editer_ground.py` travaille **au niveau du texte de chaque case** :
une carte PMDO est une grille de cases JSON indépendantes, donc un bloc se
copie sans jamais désérialiser les 330 Mo (interdit sur 2 Go de RAM).

- `copier` : rectangle source → destination, avec miroir optionnel, sur les
  37 calques **et** sur le tableau `obstacles` ;
- `vider` / `poser` : effacer un calque sur une zone, ou y répéter une case
  donnée (utilisé pour supprimer la grille de buissons).

**Contrôle d'intégrité obligatoire** : l'outil réécrit le fichier sans aucune
édition (`--verifier`) et compare les empreintes SHA-256. Résultat :
`2268e269…a446a` dans les deux cas — la réécriture est **exacte à l'octet**.

---

## 3. Résultat

| | Avant (Drive) | Après |
|---|---:|---:|
| Lignes avec du contenu | 0 → 348 | **0 → 499** (toute la carte) |
| Cases bloquées au sud | 0 / 26 800 | **15 994 / 26 800** |
| Calques de remplissage uniforme | 1 (29 200 cases) | 0 |
| Taille | 330 233 300 o | 330 482 389 o |
| Empreinte SHA-256 | — | `e4ee71d7…1f48b3` |
| Compressé (sans perte) | — | **1,90 Mo** |

Aperçus : `docs/apercus/WaterfallVillageCapital_etendue.png` (carte entière),
`…_sud.png` (la zone étendue), `avant_apres_sud.png` (comparaison).

---

## 4. Ce qui reste, dit franchement

- **La zone sud est une réplique** d'une bande du nord (cliff, cascade, bassin,
  maisons). Vue d'ensemble, la répétition se remarque ; à l'échelle d'un écran
  de jeu, non. Différencier demanderait de dessiner des pièces nouvelles, ce que
  la règle « pas de ressource inventée » interdit sans validation.
- **Le canevas n'a pas été agrandi** : la carte fait toujours 200 × 500 cases.
  J'ai rempli la surface existante plutôt que d'ajouter des lignes ; ajouter
  des rangées toucherait les 37 calques, les obstacles et le fond parallaxe.
  C'est faisable sur demande.
- **`FORGE` reste introuvable** dans les 113 branches des six dépôts : 262
  tuiles de la forge du nord-est ne s'affichent pas. Rien à fabriquer ici.
- Le rendu est statique : ni les PNJ, ni les animations d'eau ne sont évalués.
  **Un aperçu approuvé n'est pas une validation en jeu.**

---

## 5. Reproduction

```bash
python tools/editer_ground.py ../wvc_drive.rsground ../wvc_v5.rsground tools/scenarios/sud.json
python tools/restaurer_waterfall.py     # installe la version étendue dans game/
```
