# Bilan — les services du café Spinda (jus et recyclage)

Date : 5 novembre 2026. Branche `destiny-unifiee`, après la release 0.4.7
(`c8938e39`).

Le bilan du 2 novembre (`Bilan_MAJ_CAFE_LOSTWOOD_2026-11-02.md`, §6) laissait
explicitement hors de sa tranche les **services avancés du café** : « jus de
Spinda, recyclage Wynaut/Wobbuffet — dialogues en place, menus natifs non
branchés ». C'est cette tranche.

## 1. Ce qui existait avant

- L'accueil du café proposait un menu de guide (étage, salle de spectacle,
  sieste) mais aucun service de comptoir.
- Okéoké et Qulbutoké tenaient un dialogue d'atelier qui annonçait son
  ouverture « quand toutes les caisses seront enfin rangées ».
- La base PMDO fournissait déjà les briques nécessaires, jamais branchées :
  `origin/menu/juice/JuiceShopMenu.lua` (sélection d'ingrédients avec aperçu
  des gains), `origin/menu/InventorySelectMenu.lua` (sélection multiple dans
  le sac), `origin/menu/team/TeamSelectMenu.lua` (choix du membre) et le
  catalogue `COMMON.JUICE.BOOSTS` de `origin/common_shop.lua`.

## 2. Bar à jus de Spinda (accueil)

Point d'entrée : `Spinda_Action`, nouvelle entrée du menu
« Commander un jus de Spinda ».

1. Spinda annonce la tournée ; si le sac (et les objets tenus) ne contient
   aucun ingrédient utilisable, la commande est refusée en français, sans
   ouvrir de menu vide.
2. `TeamSelectMenu.runPartyMenu()` choisit qui boit le jus.
3. `JuiceShopMenu.run(...)` ouvre la sélection d'ingrédients : seuls les
   objets du catalogue sont sélectionnables, et l'aperçu natif affiche en
   direct l'effet sur les PV, l'Attaque, la Défense, l'Att. Spé., la Déf. Spé.,
   la Vitesse, l'expérience et le niveau.
4. Confirmation explicite (nom du jus, buveur, prix). En cas de refus, aucun
   ingrédient n'est consommé.
5. Les ingrédients sont retirés du sac, le son `DUN_Drink` joue, puis les
   gains sont appliqués : plafonds `MAX_STAT_BOOST`, expérience et niveaux
   recalculés comme dans la base (`EXPTable`/`Growth`), fenêtre
   `LevelUpMenu` native pour toute montée de niveau ou variation multiple.

Règles d'effet reprises telles quelles de la base : une gomme profite surtout
de son type (affinité calculée avec `PreTypeEvent.CalculateTypeMatchup`), les
herbes Mentale/Puissance/Blanche annulent les gains et l'aliment avarié
(`food_grimy`) fait perdre de l'expérience.

Économie : **100 Poké la tournée**, **la première est offerte** par la maison
(drapeau `SV.Destiny.TourneeOfferte`). Si la bourse ne suffit pas, Spinda le
dit et n'ouvre rien. Le nom de la boisson est déduit des ingrédients
réellement choisis (« Jus de gommes double », « Presse de baies »,
« Herbes infusées du grand comptoir »…).

## 3. Atelier de recyclage (premier étage)

Point d'entrée : `NewObject_1_Action` (Okéoké) et `NewObject_2_Action`
(Qulbutoké) ; les deux tiennent le même comptoir, l'un annonce, l'autre
commente. Les dialogues qui promettaient une ouverture future ont été
remplacés ; l'accueil renvoie désormais à l'étage.

1. Ouverture : dépôt de **4 objets au maximum**, choisis avec
   `InventorySelectMenu.run(...)` — les objets tenus sont exclus, les objets
   non recyclables (prix nul, `CannotDrop`) apparaissent en rouge.
2. Estimation : chaque objet vaut `cote / 2` (arrondi au Poké inférieur,
   plancher 5). La cote vient d'une table maison de **57 objets courants**
   (baies, graines, orbes, remèdes, gommes, fortifiants, aliments) ; les
   autres objets retombent sur la moitié du prix du catalogue PMDO.
3. Trouvailles du jour : cinq assortiments de trois objets, un par journée de
   ville (`SV.Destiny.JourneeVille`, donc la sieste chez Spinda) — le même
   principe que les étals Kecleon. Chaque assortiment garde une entrée à
   40 Poké pour qu'une seule baie déposée suffise déjà.
4. Seules les trouvailles couvertes par la valeur du dépôt sont proposées ;
   si aucune ne l'est, l'atelier refuse le dépôt et **rien n'est consommé**.
5. À l'acceptation : consommation du dépôt, remise de la trouvaille
   (`GAME:GivePlayerItem`), son `DUN_Money`.

Boucle économique : la reprise vaut la **moitié** de la cote et une trouvaille
coûte sa cote **entière**, donc recycler ne peut pas créer de valeur à partir
des étals Kecleon. En revanche, les objets de valeur élevée (trésors de butin)
peuvent couvrir tout l'assortiment : c'est voulu, un trésor reste un trésor.

Bonus : tous les **cinq dépôts**, l'atelier offre une baie Oran (si la place le
permet ; sinon la dette est annoncée et rien n'est perdu).

## 4. Persistance

Ajouts à `SV.Destiny` (valeurs par défaut dans `scriptvars.lua`) :

| Clé | Rôle |
|---|---|
| `JusDecouvert` | première tournée servie |
| `JusServis` | nombre de tournées |
| `TourneeOfferte` | la tournée gratuite a été utilisée |
| `AtelierDecouvert` | première visite de l'atelier |
| `RecyclageDons` | nombre de dépôts (compteur du bonus) |

La rotation des trouvailles réutilise `JourneeVille` : aucune nouvelle
horloge, et la sieste du café continue d'être le seul moyen d'avancer.

## 5. Fichiers touchés

- `game/Data/Script/destiny/cafe_spinda.lua` (nouveau) : les deux services,
  leurs tables (ingrédients, cotes, assortiments) et les dialogues français.
- `game/Data/Script/destiny/ground/caféspindaaccueil/init.lua` : menu de
  Spinda (5 entrées), renvoi des jumeaux vers l'étage.
- `game/Data/Script/destiny/ground/spindacaféétage1/init.lua` : comptoir de
  l'atelier à la place des dialogues d'attente.
- `game/Data/Script/destiny/scriptvars.lua` : cinq clés persistées.
- `tools/test_cafe_services.py` (nouveau) : contrôles de la tranche.
- `tools/test_cafe_lostwood.py` : empreintes des salles du café remises à
  jour, et contrôle de la zone `archives` rendu conditionnel (elle n'existe
  plus dans l'arbre consolidé).
- `tools/retirer_fenetres_cafe.py` : `--check` accepte désormais une carte
  retouchée par une autre tranche **si** les blocs de fenêtre pointent
  toujours vers le mur voisin (repli structurel, pas un blanc-seing).

## 6. Contrôles effectués

- `python3 tools/validate.py` : **VALIDATION OK** (17 061 fichiers, index des
  planches reconstitué, carte de la ville restaurée depuis `payload/`).
- `python3 tools/test_cafe_services.py` : OK — 87 ingrédients du catalogue
  tous présents dans `game/Data/Item` ou `base/Data/Item`, 57 cotes de
  reprise, 5 assortiments de trouvailles (3 objets chacun, une entrée à
  40 Poké), clés de sauvegarde présentes des deux côtés (module et
  `scriptvars`), points d'entrée branchés sur les deux cartes.
- `python3 tools/test_cafe_lostwood.py` : OK (empreintes des cartes, zone de
  la ville, ressources town02, invariants Lua de la ville et des Bois Perdus).
- `python3 tools/retirer_fenetres_cafe.py --check` : OK pour les deux cartes
  supérieures du café.
- Analyse syntaxique Lua des quatre fichiers modifiés ou créés (Lupa).

Les deux contrôles du café sont autonomes (`python3 tools/test_cafe_services.py`,
`python3 tools/test_cafe_lostwood.py`) et peuvent être ajoutés à
`.github/workflows/build-windows.yml` ; le faire depuis cette session s'est
heurté à la permission `workflows` du jeton GitHub, il reste donc une action
manuelle côté dépôt.

## 7. Reste à valider au runtime PMDO (Windows)

- Ouverture réelle des deux menus (sélection d'ingrédients avec aperçu,
  sélection multiple du dépôt) en 0.8.12, et retour propre au jeu après
  annulation dans chaque sous-menu.
- Choix du buveur quand l'équipe compte plus de deux membres, et affichage de
  la fenêtre de niveau après un jus de graine Joie ou de gomme.
- Consommation effective des objets tenus (le jus accepte les objets
  équipés ; l'atelier les refuse).
- Équilibrage : prix de la tournée, cotes de reprise, rotation des
  trouvailles après une sieste, bonus du cinquième dépôt.

## 8. Volontairement hors de cette tranche

- Les **plats** (`SpecialtiesMenu`, dîners à effets massifs) de la base : ils
  supposent un déblocage de fin de guilde qui n'existe pas encore dans
  Destiny.
- Le recyclage des objets **en banque** : l'atelier ne travaille que sur le
  sac, pour rester lisible et éviter une source de Poké indirecte.
- Un menu de trouvailles paginé au-delà de trois propositions par jour.
