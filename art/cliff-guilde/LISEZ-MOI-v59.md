# Guilde Cliff v5.9 — cartes jouables (WebP → PMDO)

Conversion des 4 WebP `art/cliff-guilde/webp/` (480×520, 240 frames) en cartes PMDO 0.8.12 jouables.

## Cartes (Data/Ground/, 60×65 cases 8 px)
- `guilde_cliff_jour.rsground` (1,6 Mo) — Jour
- `guilde_cliff_aube.rsground` (1,6 Mo) — Aube
- `guilde_cliff_crepuscule.rsground` (1,7 Mo) — Crépuscule
- `guilde_cliff_nuit.rsground` (1,6 Mo) — Nuit

Chaque carte : 2 calques
- `00_Guilde_Cliff` : base (falaise, plateau, guilde placée par l'utilisateur — préservée, aucun placement arbitraire)
- `01_Mer_Animee_12Phases` : mer 12 phases (FrameLength 8 = 133 ms @60 i/s), extraite des WebP

## Tilesets (Content/Tile/, 8 tuiles)
- `Destiny_GuildeCliff_{Jour,Aube,Crepuscule,Nuit}_059.tile` (base, 2874-3112 tuiles)
- `Destiny_GuildeCliff_{Jour,Aube,Crepuscule,Nuit}_Mer_059.tile` (mer, 4368-5607 tuiles)

## Zone + scripts
- `Data/Zone/destiny_cliff_tests.json` : 4 maps ajoutées (9 au total, Released false pour les nouvelles)
- `Data/Script/destiny/ground/guilde_cliff_{amb}/init.lua` : squelettes (FadeIn + RespawnAllies)

## Collisions (provisoires, à vérifier au moteur)
Herbe libre (vert-jaune), bords bloqués, couloir escalier central libre (x 27-32, y≥43).
Jour : 329 cases libres (cf. candidat 0.6.0 : 327). Aube/crépuscule/nuit : 126-129 (détection herbe moins sensible en sombre).
**À régler dans l'éditeur** — l'utilisateur placera guilde/arbres et renverra les cartes modifiées.

## Limites v5.9
- Nuages : fixes (peints dans la base, comme les WebP sources — pas de parallaxe .dir branchée)
- Porte : état base (ouverture/fermeture des WebP non branchée en interaction)
- Aucun test de chargement PMDO 0.8.12, déplacement, partenaire, sauvegarde, Windows ou CI effectué ici (sandbox sans moteur)
- `tools/validate.py` non exécuté (dépôt incomplet dans le sandbox) — à lancer avant publication

## Installation (depuis votre machine)
```bash
# Copiez v59/Data/Ground/*.rsground → game/Data/Ground/
# Copiez v59/Content/Tile/*.tile → game/Content/Tile/
# Copiez v59/Data/Script/destiny/ground/guilde_cliff_*/ → game/Data/Script/destiny/ground/
# Fusionnez v59/Data/Zone/destiny_cliff_tests.json dans game/Data/Zone/
python tools/validate.py
# Testez dans PMDO 0.8.12 (Ground Editor + partie), puis CI
```
