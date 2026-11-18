# Guilde de Réverie Town — effectif et émotes de repas (v0.7.5)

Dix membres, dix caractères, et **une émote de repas pour chacun**, calquée sur
celle d'Halcyon (`Data/Emote/eating.json` + `Content/Particle/Emote_Eating.dir`).

---

## 1. Ce qui manquait réellement

L'asset était déjà là, mais orphelin :

| Élément | État avant | État après |
|---|---|---|
| `game/Content/Particle/Emote_Eating.dir` | présent (352 o, PNG 192×32, 6 images 32×32), identique à Halcyon | inchangé (aucune retouche d'image) |
| `game/Data/Emote/eating.json` | **absent** | créé |
| `game/Data/Emote/index.idx` | **absent** (aucune émote du mod) | créé, une seule clé ajoutée |
| scripts appelant `'eating'` | aucun | `guilde_effectif.lua` |

Conséquence de l'état initial : un `GROUND:CharSetEmote(pnj, 'eating', 0)` aurait
échoué, le moteur ne connaissant pas la clé `eating`.

## 2. La donnée, telle que portée

`game/Data/Emote/eating.json`

```json
{
  "Version": "0.8.12.0",
  "Object": {
    "$type": "RogueEssence.Data.EmoteData, RogueEssence",
    "Name": { "DefaultText": "Eating", "LocalTexts": { "fr": "Manger" } },
    "LocHeight": 10,
    "Anim": {
      "AnimIndex": "Emote_Eating", "FrameTime": 3,
      "StartFrame": -1, "EndFrame": -1, "AnimDir": 0,
      "Alpha": 255, "AnimFlip": 0
    }
  }
}
```

Valeurs reprises **à l'identique** d'Halcyon : `FrameTime 3` (cadence), `LocHeight 10`
(l'émote flotte 10 px au-dessus du centre du personnage), `AnimDir 0` (vers le bas),
`StartFrame`/`EndFrame` à −1 (les 6 images). Seule la `Version` suit le moteur de
Destiny (`0.8.12.0`, comme les autres fichiers du dépôt).

`game/Data/Emote/index.idx` ne contient **que** la clé `eating`
(`Released: true`, `SortOrder: 9`, après les neuf émotes d'origine). C'est sans
risque : `DataManager.GetIndex` compose l'index du mod par-dessus celui de base
**clé par clé** (`PathMod.FallforthPathsWithHeader` + `compositeIndex.Set`), donc
`angry…sweating` restent visibles ; une clé déjà existante serait simplement
remplacée. Le test le vérifie en relisant les neuf clés de `base/Data/Emote/index.idx`.

L'émote dure **18 images par bouchée** (6 images × `FrameTime 3`).
`cycles 0` = boucle infinie : c'est l'usage d'Halcyon dans sa salle à manger.

## 3. L'effectif (`game/Data/Script/destiny/guilde_effectif.lua`)

Chaque membre porte son rôle, ses types, son caractère — et **sa façon de manger**,
déduite de son caractère. `cycles` = nombre de bouchées (`0` = repas continu),
`delai` = désynchronisation du départ en images.

| Membre (`id` de carte) | Rôle | Types | G. | Bouchées | Délai | Sortie de repas | Pose |
|---|---|---|---|---|---|---|---|
| `Gardevoir` | Maîtresse de guilde | Psy / Fée | F | continu | 14 | — | — |
| `Canarticho` | Second | Normal / Vol | M | continu | 6 | — | — |
| `Simisage` | Cuisinier | Plante | M | 2 | 22 | `happy` | — |
| `Melofee` | Infirmière, responsable du réveil | Fée | F | continu | 10 | `happy` | **oui** |
| `Cizayox` | Combattant | Insecte / Acier | M | 1 | 8 | — | — |
| `Noctali` | Explorateur | Ténèbres | M | 1 | 18 | — | — |
| `Dimoret` | Éclaireuse | Ténèbres / Glace | F | 2 | 4 | `notice` | — |
| `Draby` | Jeune recrue, leader de la Team Star | Dragon | M | 3 | 2 | `glowing` | — |
| `Pandespiegle` | Jeune recrue | Combat | M | 2 | 5 | `notice` | — |
| `Capumain` | Recrue | Normal | F | 2 | 12 | `happy` | — |

Lecture des choix, tous calés sur la personnalité :

- **Gardevoir** et **Canarticho** mangent en continu (repas de travail, ils restent
  à table) ; ils démarrent tard (14 et 6 images) : la hiérarchie se voit dans le
  tempo, pas dans le dialogue.
- **Simisage** démarre le dernier (22 images) parce qu'il **sert avant de
  s'asseoir** — et il enchaîne sur `happy` : la seule émote du groupe qui commente
  le repas.
- **Mélofée** grignote en continu, sort sur `happy`, et garde sa **pose de service**
  hors repas (§4).
- **Cizayox** et **Noctali** ne prennent **qu'une** bouchée (discipline, réserve) ;
  Noctali attend 18 images avant d'y toucher.
- **Dimoret** mord deux fois vite (4 images) et sort sur `notice` : elle surveille.
- **Draby** engloutit trois bouchées, le premier servi (2 images), puis brille
  (`glowing`) ; **Pandespiègle** suit à 5 images ; **Capumain** chaparde plus tard
  (12 images) et finit sur `happy`.
- Les dix délais sont **tous distincts** : aucun mouvement synchrone, conformément
  au guide de mise en scène (désynchroniser, éviter les multiples de 4 identiques).

`guilde_effectif.ORDRE` donne l'ordre de présentation, `BLOCS` regroupe
direction / vie quotidienne / explorateurs / recrues, et `TEAM_STAR` =
`Draby, Pandespiegle, Capumain`.

## 4. Mélofée : la pose « façon Audino »

Dans Halcyon, la « pose spéciale » d'Audino n'est **pas** une émote : c'est la pose
générique des PNJ de guilde, obtenue par une action figée —

```lua
GROUND:CharSetAction(chara, RogueEssence.Ground.PoseGroundAction(
  chara.Position, chara.Direction,
  RogueEssence.Content.GraphicsManager.GetAnimIndex("Pose")))
```

(pas de charsheet dédiée pour les PNJ de la salle à manger ; Audino a seulement sa
propre planche `Audino_Bed` pour la scène de réveil au dortoir.)

`guilde_effectif.Poser(acteur)` reproduit exactement ce mécanisme, avec deux
replis pour ne jamais figer un sprite sur une image vide :
`Pose` via `PoseGroundAction` → `CharSetAnim('Pose', true)` →
`CharSetAnim('Idle', true)`. `Deposer` rend le corps au repos (`CharEndAnim`).

`PoseDeService(acteur)` n'agit que pour les membres marqués `pose = true`,
c'est-à-dire **Mélofée seule**. `FinRepas` la remet en pose automatiquement après
le repas : elle débarrasse debout.

## 5. API exposée

```lua
local guilde = require 'destiny.guilde_effectif'

guilde.MEMBRES / guilde.ORDRE / guilde.BLOCS / guilde.TEAM_STAR
guilde.Membre(id_ou_espece_ou_nom)   -- insensible à la casse et aux accents de saisie
guilde.ParBloc('explorateurs')
guilde.Acteurs(liste)                 -- { {membre = …, acteur = …} } des PNJ présents
guilde.Manger(acteur, id, cycles?)     -- émote « eating » (+ anim de corps « Eat » si la planche l'a)
guilde.Bouchee(acteur, id)             -- une seule bouchée
guilde.Repas(liste?, duree?)           -- repas collectif désynchronisé, puis FinRepas
guilde.RepasImmediat(liste?)           -- salle déjà en repas (pas de coroutine)
guilde.FinRepas(liste?)                -- coupe l'émote, repose les corps, remet Mélofée en pose
guilde.Poser / Deposer / PoseDeService
guilde.Fiche(id)                       -- ligne lisible pour les journaux
```

Deux points de sûreté :

1. `Manger` ne lance l'animation de corps `Eat` que si la planche de l'espèce la
   référence réellement (`GetAnimIndex` ≥ 0 **et** `GetReferencedAnimIndex` = index) ;
   sinon le personnage garde simplement son attente. Aucune espèce n'est cassée si
   elle n'a pas l'animation.
2. `Acteurs()` ignore silencieusement les membres absents de la carte : une carte
   qui n'accueille que trois PNJ marche sans réglage.

## 6. Branchement dans le réfectoire

`ground/guilde_destiny_refectoire/init.lua` (47 lignes → 56) appelle
`guilde_effectif.RepasImmediat()` dans `Init`, `Enter` et `GameLoad`, sous `pcall` :
la salle s'ouvre **repas déjà en cours**, chacun mâchant en boucle, comme la salle à
manger d'Halcyon. Tant que les PNJ ne sont pas posés sur la carte, l'appel ne fait
rien (aucun acteur trouvé) — le comportement actuel du réfectoire est inchangé.

Pour une scène jouée (arrivée des recrues, service de Simisage), utiliser `Repas`,
qui attend les délais puis coupe :

```lua
TASK:BranchCoroutine(function() guilde_effectif.Repas(nil, 120) end)
```

Aucun son de repas n'est branché : `base/Content/Sound` ne contient **aucun**
SoundEffect de type « Dinner Eating » (Halcyon, si). La règle « un seul SFX à la
fois » du guide reste donc respectée par défaut ; si le SE est ajouté plus tard,
c'est `SOUND:LoopSE('Dinner Eating')` puis `SOUND:StopSE('Dinner Eating')` autour
du `Repas`.

## 7. Vérifications

```bash
PYTHONPATH=tools/tests python3 tools/tests/test_guilde_effectif.py
```

- **Lua** (15 groupes) : effectif complet et identifiants uniques, résolution par
  espèce/casse, blocs et Team Star, une seule pose de service, cycles respectés
  par membre, cycles forcés, acteur absent, repas collectif (9 présents, 9 délais
  distincts, Draby ouvre à 2 images et Simisage ferme à 22), fin de repas (émote
  coupée à `''`, corps rendus au repos, pose rendue à Mélofée **seule**), émotes de
  sortie, `PoseDeService` (index `Pose` = 3), Repas de la Team Star, `RepasImmediat`
  sans coroutine, genre moteur.
- **Python** : `eating.json` (type, `FrameTime 3`, `LocHeight 10`, `AnimDir 0`,
  `AnimIndex Emote_Eating`), `index.idx` (une clé, `Released`, `SortOrder 9`) et
  non-régression des 9 émotes de base, en-tête du `.dir` (32×32, 0 direction,
  6 images), câblage du réfectoire.

## 8. Ce qui reste à faire pour voir les dix membres en jeu

1. **Les poser dans les cartes** de la Guilde (réfectoire, hall, dortoirs) avec les
   `id` ci-dessus : ce lot fournit le comportement, pas le placement. Les
   `.rsground` de la Guilde ne sont pas dans ce clone (seules les cartes de Réverie
   Town y sont), il faut donc soit les fichiers de carte, soit la liste des
   marqueurs et spawners souhaités.
2. **Données d'espèce** : sur les dix, seuls `scizor` et `umbreon` ont un
   `game/Data/Monster/*.json` dans ce clone ; les huit autres (gardevoir,
   farfetchd, simisage, clefairy, weavile, bagon, pancham, aipom) devront recevoir
   leur fiche d'espèce, ou être pris dans la banque PMU si elle les contient déjà.
3. **Planches de personnage** (`.chara`) : aucune n'est versionnée ici, donc les
   animations `Pose` / `Eat` / `Sleep` ne peuvent pas être vérifiées espèce par
   espèce — le code s'en accommode (replis), mais un contrôle visuel en jeu reste
   nécessaire pour Mélofée (pose) et Draby (bouchées rapides).

## 9. Aperçu visuel des émotes

`tools/apercu_emotes_guilde.py` rejoue le repas de chaque membre et produit deux
artefacts autonomes (aucune ressource externe au chargement) :

- `apercu_emotes_guilde.html` — aperçu **interactif** : une carte par membre, canvas
  animé au temps du jeu (60 images/s), avec pause, relance du repas et vitesses
  0,25× à 2×. Chaque carte affiche l'émote `eating` à la bonne hauteur (10 px),
  le nombre de bouchées, le délai de départ, l'émote de sortie, et le libellé d'état
  (attente / bouchée n/N / sortie / pose de service).
- `apercu_emotes_guilde_banc.png` — banc-titre statique : une ligne par membre avec
  son attente, les 6 images de la bouchée et son émote de sortie.

```bash
python tools/apercu_emotes_guilde.py                 # vers le dossier personnel
python tools/apercu_emotes_guilde.py --sortie /tmp   # vers un dossier donné
```

Les planches de personnages viennent de **PMDCollab / SpriteCollab** (CC BY-NC-SA,
aperçu local non commercial), téléchargées au premier lancement dans
`~/.cache/spritecollab` (surchargeable par `SPRITECOLLAB_CACHE`).

Ce que l'aperçu a confirmé, données en main :

- l'émote `eating` ne devient visible qu'à partir de son image 4 (les trois
  premières ne sont qu'une étincelle de 1 px) : elle est discrète à l'écran, c'est
  bien l'asset d'Halcyon ;
- les hauteurs diffèrent d'une émote à l'autre (`eating` 10, `happy` 16,
  `notice`/`glowing` 4) : la donnée de chaque émote est respectée ;
- l'animation de corps `Eat` n'existe que pour **Noctali, Draby et Capumain** dans
  les planches SpriteCollab ; ailleurs seule l'émote joue — exactement le repli
  prévu par `GetReferencedAnimIndex` ;
- **Mélofée n'a pas d'animation `Pose`** dans ces planches : en jeu, la chaîne de
  repli retombe donc sur son attente. Sa pose de service demande soit une planche
  qui possède `Pose`, soit la charsheet dédiée à la manière d'`Audino_Bed`.

## 10. Les émotes créées pour la Guilde (cloche et calot)

Deux émotes ont été **dessinées image par image** (`tools/creer_emotes_guilde.py`,
ré-exécutable, sans dépendance au-delà de Pillow) et enregistrées comme les autres :

| Clé | Asset | Images | FrameTime | LocHeight | Rôle |
|---|---|---|---|---|---|
| `reveil` | `Emote_Reveil.dir` | 8 | 4 | 10 | cloche de réveil de la tournée du matin |
| `pose_infirmiere` | `Emote_Pose_Infirmiere.dir` | 4 | 12 | 6 | **calot d'infirmière**, pose de service de Mélofée |

Format écrit, celui du moteur (`DirSheet.Load`) :
`Int64 taille PNG` + PNG + `Int32 largeur, hauteur, directions(0), images`.

### Pourquoi une émote et pas une charsheet comme `Audino_Bed`

Dans Halcyon, la « pose spéciale » d'Audino est portée par une **charsheet dédiée**
(`Audino_Bed`), parce qu'Audino y est *allongée dans un lit* : la planche elle-même
est redessinée. Ici, ce n'est pas transposable de façon sûre :

- `GraphicsManager.GetChara` lit `Content/Chara/{espèce}.chara` en **indexant des
  positions d'octets** (`CharaIndex.GetPosition(espèce, forme, peau, genre)`) puis
  désérialise en binaire (`CharSheet.Load(BinaryReader)`) ;
- **aucun `.chara` n'est versionné** dans ce dépôt (`base/Content/Chara` vide) : il
  n'y a pas de fichier modèle à copier, ni d'index à respecter ;
- en fabriquer un reviendrait à livrer une planche complète d'espèce, non testable
  ici (aucun moyen de vérifier le rendu en jeu dans ce dépôt).

### Ce qui rend le calot possible : le point d'ancrage « tête »

`GroundChar.Draw` n'ancre pas les émotes au centre du sprite :

```csharp
Loc head = currentCharAction.GetActionPoint(sheet, ActionPointType.Head);
currentEmote.Draw(spriteBatch, offset - head - drawOffset + Loc.UnitY * LocHeight);
```

L'émote est donc centrée sur le **point d'action « tête »** de la planche, puis
remontée de `LocHeight`. Avec `LocHeight 6`, le calot — dessiné dans le bas de sa
cellule 32×32 — vient se poser sur la tête au lieu de flotter au-dessus. Vérifié
sur la vraie planche de Mélofée (SpriteCollab) en comparant 0, 4, 6 et 9 :
**0 = sur le visage, 4 = sur les yeux, 6 = juste au-dessus des yeux, 9 = flottant.**
Le choix retenu est **6** ; c'est un simple nombre dans `pose_infirmiere.json`,
donc ajustable espèce par espèce si le point « tête » réel diffère.

### La scène de réveil (`game/Data/Script/destiny/guilde_reveil.lua`)

```lua
local reveil = require 'destiny.guilde_reveil'
reveil.Reveiller(melofee, draby)          -- un dormeur
reveil.Tournee(melofee, {'Draby','Noctali','Capumain'}, {pause = 12})  -- la tournée
```

Déroulé, calé sur les planches :

1. le dormeur passe en `Sleep` (s'il l'a) et attend `SOMMEIL = 30` images ;
2. Mélofée prend la pose de service (`PoseGroundAction`, la pose d'Audino) et la
   cloche sonne `SONNERIES = 2` cycles, soit `SONNERIE = 64` images (2 × 8 × 4) ;
3. le dormeur joue `Wake` — ou, s'il ne l'a pas, l'émote `exclaim` (sursaut) —
   puis `REVEIL = 24` images ;
4. on rend le corps au repos et **le calot reprend sa place**.

**Contrainte du moteur respectée** : `GroundChar.StartEmote` remplace l'émote en
cours, un personnage n'en porte donc qu'une. La cloche et le calot sont joués
l'un après l'autre, jamais ensemble ; le test vérifie qu'il n'y a que deux émotes
posées sur Mélofée et que le calot revient *après* la cloche.

### Retouches induites dans l'effectif

- `Poser(acteur, avec_calot)` : pose du corps (`PoseGroundAction`, puis `Pose`,
  puis `Idle`) **et** calot, désactivable quand une autre émote doit passer ;
- `Deposer(acteur)` efface désormais aussi l'émote — sinon le calot resterait
  flotter seul après la pose ;
- `FinRepas` rejoue l'émote de sortie du membre puis remet le **corps** en pose,
  **sans** calot : le calot signale la prise de garde, pas la fin d'un repas ;
- `Animer(acteur, nom, boucle)` centralise le test « la planche a-t-elle vraiment
  cette animation ? » (`GetReferencedAnimIndex`), utilisé pour `Eat`, `Sleep`,
  `Wake` et `Pose`.

### Vérifications ajoutées

- Lua, 17 groupes pour l'effectif (+2 : calot posé/retiré, `Animer` qui refuse une
  animation absente) et **4 groupes** pour `guilde_reveil` (ordre complet du
  réveil, une seule émote à la fois, repli `exclaim` sans `Wake`, tournée qui
  saute l'infirmière et les absents) ;
- Python : les trois données (`FrameTime`/`LocHeight`/`AnimIndex`), les trois
  assets (32×32, 0 direction, 6/8/4 images), l'index (3 clés, `SortOrder` 9→11,
  aucune collision avec les 9 émotes de base) et le câblage des scripts ;
- aperçu (`tools/apercu_emotes_guilde.py`) : les trois bandes d'images du mod et
  une **scène de réveil animée** (Mélofée posée, cloche, Draby qui se réveille,
  calot qui revient).

## 11. Les animations de corps des dix membres

Les émotes jouent au-dessus de la tête ; encore faut-il que **le corps** sache
mâcher, dormir, se réveiller et prendre la pose. Sur les dix membres, SpriteCollab
ne dessine `Eat`, `Wake` et `Pose` que pour **trois** d'entre eux : les sept autres
n'avaient que `Sleep` (et les animations de combat). Même méthode que la Team
Dazzling : on range les sources par membre dans `art/sprites/guilde_effectif_v1/`
(`AnimData.xml` + trio `<Anim>-Anim/Shadow/Offsets.png`), prêtes pour
`tools/ajouter_pose_chara.py`.

| Membre | Dossier | Eat | Wake | Sleep | Pose |
|---|---|---|---|---|---|
| Gardevoir | `0282_Gardevoir/` | dérivée | dérivée | SpriteCollab | dérivée |
| Canarticho | `0083_Canarticho/` | dérivée | dérivée | SpriteCollab | dérivée |
| Simisage | `0512_Simisage/` | dérivée | dérivée | SpriteCollab | dérivée |
| Melofee | `0035_Melofee/` | dérivée | dérivée | SpriteCollab | dérivée |
| Cizayox | `0212_Cizayox/` | dérivée | dérivée | SpriteCollab | dérivée |
| Noctali | `0197_Noctali/` | SpriteCollab | SpriteCollab | SpriteCollab | SpriteCollab |
| Dimoret | `0461_Dimoret/` | dérivée | dérivée | SpriteCollab | dérivée |
| Draby | `0371_Draby/` | SpriteCollab | SpriteCollab | SpriteCollab | SpriteCollab |
| Pandespiegle | `0674_Pandespiegle/` | dérivée | dérivée | SpriteCollab | dérivée |
| Capumain | `0190_Capumain/` | SpriteCollab | SpriteCollab | SpriteCollab | SpriteCollab |

### Clés d'animation (lues dans `base/Base/GFXParams.xml`)

| Animation | FrameType | Usage |
|---|---:|---|
| `Sleep` | 3 | le dormeur avant la cloche |
| `Wake` | 47 | le réveil (`guilde_reveil`) |
| `Eat` | 48 | la mâchoire pendant l'émote `eating` |
| `Pose` | 50 | la pose de service, base de la pose « façon Audino » |

Ces quatre nombres sont **recalculés par le test** depuis `GFXParams.xml` (ordre des
`<Action>`) : si le moteur bouge, le test casse au lieu de livrer une clé fausse.

### Trois familles de `Eat`

| Famille | Membres | Source |
|---|---|---|
| `SpriteCollab` | Noctali, Draby, Capumain | animation d'origine du Pokémon |
| dérivée (validée) | Pandespiègle | balancement de son `Idle`, 4 ticks par image |
| dessinée | Gardevoir, Canarticho, Simisage, Mélofée, Cizayox, Dimoret | bouchée dessinée ici |

Ces six espèces n'ont **aucune animation de repas** dans SpriteCollab. Leurs
sprites sont donc retouchés au pixel, une image sur deux.

### La bouchée, membre par membre

Chaque bouchée est une mâchoire ouverte (lèvre noire, langue sombre, lèvre
inférieure) plus un aliment et une touche d'expression, tous pris dans la palette
de l'espèce. Les positions sont relevées planche par planche (`BOUCHEES` dans
`tools/constituer_animations_guilde.py`) :

| Membre | Bouche (x, y, largeur) | Aliment | Manière |
|---|---|---|---|
| Gardevoir | 14, 12, 3 | baie rose | bouchée du bout des lèvres, rougeur à la joue |
| Canarticho | 9, 13, 4 | feuille verte | bec grand ouvert sur son poireau |
| Simisage | 13, 18, 4 | feuille verte | il mord dans une feuille |
| Mélofée | 13, 19, 3 | baie brune | petite bouchée, rougeur à la joue |
| Cizayox | 12, 29, 4 | quart de nourriture | mâchoire grande ouverte |
| Dimoret | 13, 16, 4 | quart clair et miette | il engloutit et laisse des miettes |

Quatre images, rythme **6-8-6-8** : fermée, il mord (aliment présent), fermée, il
avale (bouche vide). Les quatre images partent de la même image d'`Idle` ; les
autres images changent de pose et la bouche retomberait à côté.

Le test vérifie la lèvre noire sur toute la largeur, la langue juste en dessous,
la présence de l'aliment, et que les images 1 et 3 sont bien identiques.

Les autres animations dérivées restent en place, elles n'ont pas été mises en
cause :

- `Wake` — `Sleep` (l'image de sommeil réellement dessinée), la même inclinée d'un
  pixel, puis l'`Idle` : dormir, bouger, se lever ;
- `Pose` — l'`Idle` tenu sur une image de 30 ticks, exactement ce que fait Halcyon
  pour ses PNJ de guilde : une pose figée, pas une animation.

Chaque animation porte sa source et, si elle est fabriquée, sa recette dans
`MANIFESTE.json` ; elle se remplace sans rien casser par un vrai dessin (même nom
de fichier, même `AnimData.xml`).

### Injection dans les `.chara`

```sh
python3 tools/ajouter_pose_chara.py \
  --chara game/Content/Chara/371.chara \
  --sprites art/sprites/guilde_effectif_v1/0371_Draby \
  --anim Eat --frame-type 48 --out /tmp/371.chara
```

Puis `--anim Wake --frame-type 47` et `--anim Pose --frame-type 50`. Aucun `.chara`
n'étant versionné dans ce dépôt, l'injection n'a pas pu être rejouée ici ; le code
du mod se rabat proprement tant qu'elle n'est pas faite
(`guilde_effectif.Animer`).

### Aperçus

- `art/previews/guilde_effectif_v1/guilde_repas.gif` — les dix membres qui mâchent
  avec l'émote `eating`. Les étoiles `Lucky_Chant_Star_Yellow` ont été **retirées** :
  l'aperçu ne montre plus que le sprite et son émote.
- `art/previews/guilde_effectif_v1/guilde_animations_planche.png` — repas, pose de
  service et réveil, membre par membre.

### Vérifications

`PYTHONPATH=tools/tests python3 tools/tests/test_animations_guilde.py` : dix
membres × quatre animations, présence du trio Anim/Shadow/Offsets, géométrie des
planches (multiple exact de la cellule, nombre d'images = nombre de durées),
`Index` uniques, recette documentée pour chaque animation dérivée, et **clés
`FrameType` recalculées depuis `GFXParams.xml`**.

