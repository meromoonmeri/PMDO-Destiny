# Menu-titre animé de Destiny

Écran-titre de **Pokémon Mystery Dungeon: Destiny** : mer et ciel pixel-art
animés (24 poses en boucle), en version **JOUR** ou **NUIT** selon l'heure
locale, avec apparition animée du blason **Œuf Ailé** (« opening d'anime »,
une fois par session) au-dessus du menu principal.

## Comment ça marche (moteur PMDO 0.8.12)

L'écran de titre a deux phases :

1. **« Appuyez sur une touche »** (`TitleScene`) : le moteur dessine le fond
   `TitleBG` puis `game/Content/UI/Title.png` (blason centré) et l'invite
   clignotante `game/Content/UI/Enter.png` (« PRESS ENTER »).
   `game/Content/ContentParams.xml` règle `TitleBG` sur le fond animé **JOUR**
   (copie des valeurs de la base, seul `TitleBG` change ; `TitleBGM` reste
   `Title.ogg`, fourni par la base).
2. **Menu principal** (`TopMenu`) : le service Lua persistant
   `destiny_title_anim` écoute l'événement `AddMenu` du moteur ; quand le menu
   étiqueté `TOP_MENU` apparaît, il insère **sous** le menu un calque plein
   écran affichant le fond animé du moment (JOUR 06h–19h, NUIT 19h–06h) et
   joue **une seule fois par session** la séquence d'ouverture du blason
   (`Destiny_Logo_Anime_Opening`, 24 poses, ≈ 8,6 s), puis retire le calque
   d'ouverture : le fond jour/nuit continue en boucle derrière le menu.

Forcer un mode (debug/préférence) : dans
`game/Data/Script/destiny/services/destiny_title_anim/init.lua`,
`DestinyTitleAnim.ForceMode = 'jour'` ou `'nuit'` (nil = automatique).

## Fichiers

| Fichier | Rôle |
|---|---|
| `game/Content/BG/Title_Screen_Background_Jour.dir` | Fond animé JOUR (320×240, 24 poses, sans logo) |
| `game/Content/BG/Title_Screen_Background_Nuit.dir` | Fond animé NUIT (320×240, 24 poses, sans logo) |
| `game/Content/Object/Destiny_Logo_Anime_Opening.dir` | Séquence d'apparition du blason (320×240, 24 poses) |
| `game/Content/UI/Title.png` | Blason Œuf Ailé centré (320×240) — phase 1 |
| `game/Content/UI/Enter.png` | Invite « PRESS ENTER » (74×11) — phase 1 |
| `game/Content/ContentParams.xml` | `TitleBG = Title_Screen_Background_Jour` (reste identique à la base) |
| `game/Data/Script/destiny/main.lua` | Enregistre le service (chargé par `LuaEngine.ModDoFile "main"`) |
| `game/Data/Script/destiny/services/destiny_title_anim/init.lua` | Le service (API `origin.common` / `origin.services.baseservice` de la base PMDO) |
| `art/Logo_PMD_Destiny_Oeuf_Ailes_HD.png` | Logo source détouré (872×629), hors jeu |

## Provenance et reconstruction

Création de l'auteur du projet, depuis son atelier
[`meromoonmeri/projet-creation-pmdo`](https://github.com/meromoonmeri/projet-creation-pmdo),
branche `arena/637b0828-projet-creation-pmdo`, commit
`24c84f45c8bdd62969ef58de8b22ce2a874d415a` (dépôt sans licence publique ;
import à la demande de l'auteur, comme les cartes — voir `CREDITS.md`).

Les binaires `.dir`/PNG n'étaient commités dans aucun dépôt (ZIP livrés en
artefacts de session) : ils ont été **reconstruits le 27/10/2026** avec le
pipeline d'origine (`source/moteur_pmd_destiny_fangame.py`, mêmes fonctions et
paramètres que `source/pmd_destiny_fangame_v1/build.py`), à partir des quatre
images générées par l'auteur (`bruts/` : logo, nuages, mer jour, mer nuit sur
fond magenta — aucun pixel d'une référence commerciale n'entre dans les
sorties ; les `references/` de l'atelier ne servent qu'à la composition).

**Preuve de fidélité** : les trois `.dir` reconstruits ont exactement les
tailles consignées dans le `metadata.json` commité de l'atelier
(`renders/pmd_destiny_fangame_v1/metadata.json`, clé `destiny_menu`) :
JOUR `file_bytes = 390 408`, NUIT `435 032`, Opening `429 887` — reconstruction
identique à l'octet près. Le pilote utilisé est conservé hors dépôt
(`import_work/menu_rebuild.py`, régénérable) ; le service Lua est repris
verbatim de l'atelier (seul l'en-tête de provenance a été ajouté).

Hors périmètre (volontairement non importés, décision de l'auteur) : les
cartes vitrines `pmd_destiny_menu_jour/nuit` (DSTJ/DSTN), les scripts
d'opening/intro et la cinématique Pichu du `fangame_base` de l'atelier.

## Tests à faire en jeu

1. Lancer le jeu : phase 1 = fond JOUR animé + blason + « PRESS ENTER »
   clignotant ; aucune zone magenta/vide.
2. Appuyer sur une touche : l'animation du blason (éclat, impact, reflet)
   passe une fois (≈ 8,6 s) puis le menu reste sur le fond animé.
3. Revenir au menu dans la même session : pas de second opening.
4. Tester la variante NUIT (heure ≥ 19h ou `ForceMode = 'nuit'`) : ciel
   étoilé, étoile filante, mer lunaire.
5. Vérifier que « Nouvelle partie » démarre toujours sur `destiny_hub`,
   et que le ZIP Windows (`tools/build_windows.py`) intègre les fichiers.
