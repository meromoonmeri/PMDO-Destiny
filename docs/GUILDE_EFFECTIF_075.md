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
