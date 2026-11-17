# Animations de corps — effectif de la Guilde (v1)

Même méthode que la Team Dazzling : animations dessinées par SpriteCollab,
rangées ici par membre, prêtes à être injectées dans les `.chara` par
`tools/ajouter_pose_chara.py`. Chaque dossier contient `AnimData.xml` et le
trio `<Anim>-Anim.png`, `<Anim>-Shadow.png`, `<Anim>-Offsets.png` en huit
directions pour les animations réellement disponibles.

## Clés d'animation du moteur

Les `FrameType` viennent de `base/Base/GFXParams.xml` (ordre des `<Action>`) :

| Animation | FrameType | Usage dans le mod |
|---|---:|---|
| `Eat` | 48 | corps qui mâche pendant l'émote `eating` |
| `Wake` | 47 | réveil de la tournée du matin (`guilde_reveil`) |
| `Sleep` | 3 | dormeur avant la cloche |
| `Pose` | 50 | pose de service (mécanisme de la pose d'Audino) |

## Disponibilité par membre

| Membre | Dossier | Cellule | Eat | Wake | Sleep | Pose |
|---|---|---:|---|---|---|---|
| Gardevoir | `0282_Gardevoir/` | 24×32 · 32×40 | dérivée | dérivée | oui | dérivée |
| Canarticho | `0083_Canarticho/` | 24×24 · 24×32 | dérivée | dérivée | oui | dérivée |
| Simisage | `0512_Simisage/` | 32×48 · 32×56 | dérivée | dérivée | oui | dérivée |
| Melofee | `0035_Melofee/` | 24×24 · 32×40 | dérivée | dérivée | oui | dérivée |
| Cizayox | `0212_Cizayox/` | 32×64 · 40×40 | dérivée | dérivée | oui | dérivée |
| Noctali | `0197_Noctali/` | 24×40 · 32×32 · 32×40 | oui | oui | oui | oui |
| Dimoret | `0461_Dimoret/` | 32×40 · 32×48 | dérivée | dérivée | oui | dérivée |
| Draby | `0371_Draby/` | 24×32 · 24×40 · 32×40 | oui | oui | oui | oui |
| Pandespiegle | `0674_Pandespiegle/` | 24×32 · 24×40 | dérivée | dérivée | oui | dérivée |
| Capumain | `0190_Capumain/` | 24×40 · 32×32 · 32×40 · 40×40 | oui | oui | oui | oui |

## Injection dans un `.chara`

```sh
# le corps mâche pendant l'émote eating (FrameType 48)
python3 tools/ajouter_pose_chara.py \
  --chara game/Content/Chara/371.chara \
  --sprites art/sprites/guilde_effectif_v1/0371_Draby \
  --anim Eat --frame-type 48 --out /tmp/371.chara

# le réveil (FrameType 47)
python3 tools/ajouter_pose_chara.py --chara game/Content/Chara/371.chara \
  --sprites art/sprites/guilde_effectif_v1/0371_Draby \
  --anim Wake --frame-type 47 --out /tmp/371.chara

# la pose de service, façon Audino (FrameType 50)
python3 tools/ajouter_pose_chara.py --chara game/Content/Chara/035.chara \
  --sprites art/sprites/guilde_effectif_v1/0035_Melofee \
  --anim Pose --frame-type 50 --out /tmp/035.chara
```

Le conteneur, ses formes et ses autres animations sont conservés ;
`tools/ajouter_pose_chara.py` recadre au contenu, recentre la boîte,
conserve les marqueurs Offsets/Shadow et remet les lignes SpriteCollab dans
l'ordre Dir8 du moteur.

> Les `.chara` ne sont pas versionnés dans ce dépôt : l'injection se fait
> sur les fichiers du jeu (ou du payload) et n'a donc pas pu être rejouée ici.
> Le code du mod, lui, se rabat proprement quand une animation manque
> (`guilde_effectif.Animer` teste `GetReferencedAnimIndex`).

Les cases **dérivée** sont des animations fabriquées ici à partir de l'Idle de
l'espèce (SpriteCollab ne les dessine pas pour elle) :

- `Eat` — balancement de l'Idle joué à 4 ticks par image (mâchoire rapide) — 2 à 4 images
- `Wake` — Sleep image 1, Sleep image 1 inclinée d'1 px, puis Idle image 1 — 3 images de 6, 6, 10 ticks
- `Pose` — Idle image 1 tenue — 1 image de 30 ticks

Elles se remplacent sans rien casser le jour où un vrai dessin existe :
même nom de fichier, même `AnimData.xml`.

Régénération : `python tools/constituer_animations_guilde.py`
(cache SpriteCollab dans `~/.cache/spritecollab`, surchargeable par
`SPRITECOLLAB_CACHE`).
