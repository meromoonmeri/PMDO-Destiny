# Guilde de Réverie Town — effectif et animations de repas

Le nom `GUILDE_EFFECTIF_075.md` vient du chantier d’origine. Ces changements font partie de la [mise à jour 0.7.4](REVERIE_074.md), pas d’une version séparée.

**État intégré : dix convives au réfectoire, chacun avec un vrai `Eat`.**
L’émote de miettes, reprise d’Halcyon (`Data/Emote/eating.json` +
`Content/Particle/Emote_Eating.dir`), s’ajoute au mouvement du corps.
Les explications du premier lot d’émotes et des planches source sont conservées
ci-dessous ; elles ne décrivent pas toutes l’état final des ressources natives.

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
| `Noctali` | Explorateur et cartographe | Ténèbres | M | 1 | 18 | — | — |
| `Dimoret` | Éclaireuse | Ténèbres / Glace | F | 2 | 4 | `notice` | — |
| `Draby` | Jeune recrue, leader de la Team Star | Dragon | M | 3 | 2 | `glowing` | — |
| `Pandespiegle` | Recrue à l’entraînement | Combat | M | 2 | 5 | `notice` | — |
| `Capumain` | Recrue chargée des livraisons | Normal | F | 2 | 12 | `happy` | — |

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
guilde.Manger(acteur, id, cycles?)     -- vrai Eat en boucle ; cycles règle uniquement les miettes
guilde.Bouchee(acteur)                 -- un seul cycle du corps et des miettes
guilde.Repas(liste?, duree?)           -- repas collectif désynchronisé, puis FinRepas
guilde.RepasImmediat(liste?)           -- salle déjà en repas (pas de coroutine)
guilde.FinRepas(liste?)                -- coupe l'émote, repose les corps, remet Mélofée en pose
guilde.Poser / Deposer / PoseDeService
guilde.Fiche(id)                       -- ligne lisible pour les journaux
```

Deux points de sûreté :

1. `Manger` ne lance l'animation de corps `Eat` que si la planche de l'espèce la
   référence réellement (`GetAnimIndex` ≥ 0 **et** `GetReferencedAnimIndex` = index) ;
   sinon la fonction renvoie `false` et ne joue pas les miettes seules.
2. `Acteurs()` ignore silencieusement les membres absents de la carte : une carte
   qui n'accueille que trois PNJ marche sans réglage.

## 6. Branchement dans le réfectoire

`ground/guilde_destiny_refectoire/init.lua` installe les dix PNJ sur le
plancher existant dans `Enter` et `GameLoad`. `InstallerConvive` réutilise le
PNJ s’il est déjà dans la sauvegarde et contrôle son `Eat`. Aucune carte,
porte ni collision du décor n’est modifiée. Le repas est déjà en cours quand
le joueur entre. Parler à un membre interrompt son animation, affiche son
rôle et sa réplique, puis le remet face à sa place et relance le repas.

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

- **Lua** (17 groupes) : effectif complet et identifiants uniques, résolution par
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

## 8. Animations natives livrées

Les dix feuilles utilisées en jeu (forme 0, peau normale, sexe du membre)
contiennent l’action **`Eat` = 48**. Les vrais `Eat` du moteur pour Noctali et
Capumain sont conservés ; ceux de Mélofée, Canarticho, Cizayox, Gardevoir,
Draby, Dimoret, Simisage et Pandespiègle sont intégrés dans l’override `game`.
Les conteneurs de base restent intacts. Les offsets des `.chara` et de
`game/Content/Chara/index.idx` sont reconstruits ensemble.

```bash
python tools/tests/test_guilde_eat_runtime.py
```

Ce contrôle lit les conteneurs réellement résolus, rejette les alias, cases
vides et pistes fixes, puis vérifie l’accès à chaque convive et à la sortie.
Les autres fiches d’animation ci-dessous restent des sources : ce lot
n’intègre pas de nouvelles scènes dans le hall ou les dortoirs.

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
- à l’étape des émotes seules, aucun import de planche dédiée n’avait été réalisé ;
  le calot reste une émote de service indépendante. L’intégration native ultérieure
  porte seulement sur `Eat` (§ 8).

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
| poses successives | Gardevoir, Canarticho, Simisage, Mélofée, Cizayox, Dimoret | poses déjà dessinées du même Pokémon |

Ces six espèces n'ont **aucune animation de repas** dans SpriteCollab — et
aucune n'a de `Eat` non plus. Mais leurs planches d'attaque en contiennent
l'essentiel : les poses « bras levés », « les deux mains devant la figure »,
« une pince puis les deux ». Leur `Eat` est donc une **suite de poses** :
repos, une main, repos, l'autre main — quatre images de 6, 8, 6 et 8 ticks.

### Les poses retenues

| Membre | Une main | Puis l'autre | Ce qu'on voit |
|---|---|---|---|
| Gardevoir | `Attack` 2 | `Double` 0 | les mains s'ouvrent, puis montent devant le visage |
| Canarticho | `Swing` 1 | `Attack` 0 | il lève son poireau, puis le ramène |
| Simisage | `Attack` 0 | `Swing` 2 | une main part, l'autre suit |
| Mélofée | `Attack` 3 | `Dance` 2 | une main, puis les deux |
| Cizayox | `Attack` 9 | `Attack` 0 | une pince, puis les deux |
| Dimoret | `Attack` 1 | `Shoot` 3 | une griffe, puis les deux |

### La cadence de référence

C'est **6, 8, 6 et 8 ticks** : la cadence du `Eat` d'origine des membres
validés (Noctali, Draby, Capumain) et celle du `Eat` de Kirlia. Les cinq poses
successives la suivent aussi.

### Le `Eat` calqué de Gardevoir

| Famille | Membres | Source |
|---|---|---|
| calquée | Gardevoir | mouvement du `Eat` de Kirlia (0281) |

Gardevoir n'a pas d'animation de repas, mais **Kirlia**, sa pré-évolution, en a
une : même morphologie, même artiste. Son `Eat` est donc **mesuré image par
image**, puis ce mouvement est appliqué au casque et au corps de Gardevoir, dans
les huit directions. Aucun pixel de Kirlia n'est repris : seul son mouvement
l'est.

| Image | Pente mesurée chez Kirlia | Descente | Appliqué à Gardevoir |
|---|---:|---:|---:|
| 1 | 0,00 px par rangée | 0 px | 0,00 |
| 2 | +0,20 px par rangée | +1 px | +0,30 |
| 3 | 0,00 px par rangée | 0 px | 0,00 |
| 4 | −0,20 px par rangée | +1 px | −0,30 |

`mesurer_calque()` cherche, pour chaque image, la rotation de tête — une pente en
pixels par rangée autour du cou, plus une descente — qui superpose le mieux la
tête de la référence à celle de sa première image. Elle retrouve seule le
mouvement : **la tête bascule d'un côté, revient, bascule de l'autre**, le corps
et la robe ne bougent pas.

La pente est ensuite multipliée par **1,5** : les cornes de Kirlia rendent son
basculement très lisible, alors que le casque rond de Gardevoir demande un peu
plus d'amplitude pour que le geste se voie. La cadence et le nombre d'images
sont ceux de la référence.

Techniquement, la bascule est une translation **rangée par rangée** de la tête :
la rangée du haut part le plus loin, celle du cou ne bouge pas. Une translation
par rangée est injective — aucun pixel ne disparaît, aucun trou n'apparaît dans
la silhouette. Deux tentatives précédentes sont écartées : déplacer puis
redessiner ses bras laissait des pixels orphelins, et une simple translation par
bandes donnait un hochement, pas un basculement.

`pose_dans_cellule()` découpe l'image dans sa planche d'origine, la recadre sur
son dessin, puis la repose **sur le même sol et le même axe** que l'`Idle` du
membre, ramenée dans la cellule s'il le faut. Les cellules d'`Attack` font
souvent 72 × 88 alors que l'`Idle` tient dans 32 × 64 : la pose est donc réduite
à la place disponible sans jamais déborder.

Sur les vues de **face** et de **dos** (rangées 0 et 4), la seconde pose est
retournée en miroir : c'est le même geste fait de l'autre côté, donc l'autre
bras. Sur les **profils**, un miroir ferait regarder le personnage dans le
mauvais sens : la pose reste telle quelle.

Rien n'est redessiné ni emprunté à un autre Pokémon : on choisit et on ordonne
des poses que le dessinateur de l'espèce a déjà faites. Un garde-fou
(`ecart_premiers()`) prévient si une pose retenue est identique au repos —
c'est le piège de ces planches, où la première image d'`Attack` est souvent
l'`Idle` lui-même.

### Le cas Pandespiègle

Son `Eat` dérivé (balancement de son `Idle`) a été validé tel quel : il ne change
pas. Comme les autres, il reste remplaçable par un vrai dessin — même nom de
fichier, même `AnimData.xml`.

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
python tools/importer_eat_guilde.py
python tools/tests/test_guilde_eat_runtime.py
```

L’import est idempotent ; il reprend le conteneur du mod ou, à défaut, celui
de la base et conserve les autres variantes. Les planches `Wake`, `Sleep` et
`Pose` ne sont pas injectées par cet outil.

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

