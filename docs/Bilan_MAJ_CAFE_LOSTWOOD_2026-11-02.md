# Bilan de mise à jour — café Spinda, Réverie Town vivante et reprises Lost Wood

Date : 2 novembre 2026.
Base : `f69328994ca2ff15997624b68bd0881508dd394f` (release 0.3.6), branche
`destiny-unifiee`. Ce document est versionné avec la mise à jour qu'il décrit.

## 1. Café Spinda (maps town02)

- Source retenue : les trois `.rsground` du dépôt, strictement identiques aux
  bonnes versions Drive déjà intégrées, sans les régressions d'un remplacement.
- Fenêtres retirées à l'étage et dans la salle de spectacle (les deux visibles
  dans chacune) par `tools/retirer_fenetres_cafe.py` : seuls 32 `TexLoc.X`
  changent par carte, sérialisation PMDO reproduite à l'octet près hors ces
  valeurs. Empreintes résultantes : étage `4f5c8768…`, salle `5830da67…`.
  La fenêtre centrale masquée par la scène est laissée en place.
- Les trois salles passent de la zone `archives` à `town02_waterfallvillage`
  (indices 2, 3, 4) ; `game/Data/Zone/index.idx` est synchronisé dans le même
  format.
- Dépendances : seules les ressources réellement absentes à la fois de `game/`
  et de `base/` sont ajoutées depuis town02 — 8 affichages d'objets (baies et
  méga-gemmes) et 7 particules (cendre, feuilles, sakura, neige, Slugma,
  émoticône « manger »). Les Tilesheets café du dépôt sont conservées : mêmes
  dimensions que town02, avec parfois plus de frames d'animation ; les Chara
  et Portraits town02 existent déjà dans `base/`.
- Raccordements jouables, sans modifier les cartes (elles ne sérialisent
  aucune sortie) : porte invisible sur le tapis rouge du bâtiment café à
  Réverie Town, sortie sud à l'accueil avec retour devant la porte en ville,
  escalier sud à l'étage, porte ouest dans la salle, et circulation guidée
  par le personnel entre les trois salles. Les habitants du café déambulent
  localement et ont des dialogues Destiny, y compris des conversations à
  plusieurs locuteurs.
- Sieste proposée par Spinda à l'accueil : avance `SV.Destiny.JourneeVille`
  et renouvelle les étals Kecleon.

## 2. Réverie Town vivante

- Les 25 habitants sérialisés reçoivent une zone de déambulation autour de
  leur position d'origine (`COMMON.CreateWalkArea`, rayon réduit pour les
  comptoirs), activée quand le joueur reprend la main.
- Dialogues originaux Destiny pour tous les habitants ; conversations à deux
  locuteurs (Lombre/Ludicolo, Luxray/Luxio) lors des interactions.
- Kangourex : **dépôt et retrait d'objets uniquement**
  (`UI:StorageMenu` / `UI:WithdrawMenu`). L'ancien menu combiné qui ouvrait
  aussi la banque est retiré.
- Gimmighoul (ambulant) : seule banque de la ville (`UI:BankMenu`).
- Kecleon vert et violet : vrai menu boutique natif (`UI:ShopMenu`, icônes
  des objets), assortiments distincts qui tournent sur trois journées,
  stocks limités et persistés dans `SV.Destiny.StocksKecleon`.
- Alakazam : réapprendre une capacité oubliée pour 250 Poké
  (`SkillSelectMenu.runRelearnMenu` + `COMMON.LearnMoveFlow`) et oublier une
  capacité gratuitement (`UI:ForgetMenu`).
- Tinkaton : ouvrir les boîtes au trésor pour 150 Poké pièce
  (`UI:AppraiseMenu` + `UI:SpoilsMenu`).

## 3. Lost Wood — reprises après KO ou abandon

- Le segment de sortie distingue la cause (`ko` / `abandon`), pose
  `LostWoodRetry` et compte les échecs aller/retour ; les réussites
  nettoient ces drapeaux.
- Aller (partenaire en solo, falaise de nuit) : après la scène d'échec, le
  joueur est libre en `pause_aller`. En se rapprochant de l'entrée est, un
  dialogue demande « Souhaitez-vous retourner dans Lost Wood ? » — Oui
  relance le segment 0, Non fait reculer le personnage hors du seuil et
  rend le contrôle. Plus de relance automatique au contact du bord.
- Retour (en duo, prairie du réveil) : même principe en `pause_retour`, avec
  le partenaire en suiveur, un réarmement de l'invite seulement après
  éloignement, et une réplique adaptée à la cause (KO ou abandon).
- Pensées d'ouverture du héros enrichies et confirmées sans locuteur
  (voix intérieure sur fond noir : où suis-je, qui suis-je, la lumière, la
  chute, l'appel, le sommeil) ; `PenseesReveilVues` est désormais posé.

## 4. Contrôles effectués

- `tools/test_cafe_lostwood.py` : empreintes des cartes, zones et index,
  ressources présentes, invariants Lua (Kangourex sans banque, menus natifs,
  questions de reprise), analyse syntaxique Lua via Lupa.
- `tools/retirer_fenetres_cafe.py --check` : les deux cartes sont dans
  l'état corrigé attendu.
- `tools/preview_maps.py` sur les trois salles du café : aucune tuile
  manquante.
- `tools/validate.py` n'a pas pu aller au bout dans l'environnement
  d'intégration (mémoire insuffisante lors du contrôle global, après
  restauration de la carte de la ville) : à relancer en CI ou en local.

## 5. Reste à valider au runtime PMDO (Windows)

- Ouverture réelle des trois salles du café, exactitude de la porte en ville
  (coordonnées relevées sur le rendu de la carte) et allers-retours complets
  ville ↔ accueil ↔ étage ↔ salle.
- Menus natifs en jeu : stockage/retrait Kangourex, banque Gimmighoul,
  boutiques Kecleon (rotation après sieste), réapprentissage/oubli
  Alakazam, ouverture de boîtes Tinkaton.
- Déambulation des habitants (collisions, chemins) et conversations.
- Séquences complètes aller/retour Lost Wood avec KO et abandon dans les
  deux sens, sauvegarde/rechargement pendant les pauses.

## 6. Volontairement hors de cette tranche

- Services avancés du café (jus de Spinda, recyclage Wynaut/Wobbuffet) :
  dialogues en place, menus natifs non branchés — leurs flux d'origine
  dépendent d'un état de ville et de catalogues qui demandent une tranche
  dédiée.
- Liaison de capacités chez Alakazam : aucune API du moteur n'expose les
  capacités liées ; seuls réapprendre et oublier sont branchés.
- Conversations d'ambiance entièrement autonomes entre PNJ : le moteur
  n'offre pas de système de bavardage ambiant prêt à l'emploi ; les
  discussions sont déclenchées par interaction.
- La carte restaurée localement de Réverie Town n'est pas versionnée : le
  payload compressé de la 0.3.6 reste la référence.
