# PMDO Destiny — Rapport intermédiaire d’audit

**18 novembre 2026 · Phase 1 : état des lieux avant correction**  
Branche : `wip/reverie-integration-kingambit-cafe` · Révision : [`aa1430c4e8953e486b82691731fbbcbce8e4c57e`](https://github.com/meromoonmeri/PMDO-Destiny/commit/aa1430c4e8953e486b82691731fbbcbce8e4c57e)  
Moteur : **PMDO 0.8.12.0**, Linux, quête Destiny chargée séparément, profils joueur et Dev isolés.

## Résultat

**Une nouvelle partie en français atteint le premier étage des Bois Perdus**, du halo d’introduction au premier message de tutoriel du donjon. Je n’ai pas constaté de blocage sur ce parcours. Ce résultat ne valide ni la deuxième traversée des Bois Perdus ni la progression jusqu’à Réverie ou à la Fosse.

**46 suites sur 47 réussissent**, en comptant le succès de la suite Ambiances à sa relance isolée. Le seul échec restant est l’empreinte attendue de l’accueil du Café Spinda. **Deux points à traiter séparément du parcours joueur** : l’accès direct à la falaise de nuit peut faire planter le Dev si l’équipe de test ne contient qu’un membre ; le réfectoire de la Guilde est présent, mais le repas animé de Gardevoir n’est pas intégré à l’état jouable vérifié.

**Aucun correctif appliqué, aucun commit, aucune fusion et aucun push.** L’arbre de travail audité est propre ; `git diff --check` ne signale rien.

## 1. État de la branche et des données

- Le HEAD est **16 commits devant et 0 derrière** le tag `v0.7.3` (`30dc4447`). La branche d’audit divergente n’a pas été fusionnée.
- Le dernier commit, **« Eat de Gardevoir calque sur celui de Kirlia »**, fournit les sources et l’aperçu de l’animation (huit directions, cadence 6/8/6/8). Il ne modifie ni le Lua, ni une carte, ni la planche `.chara` du jeu. Depuis le tag, pas de diff net sous `game/Data/{Ground,Map,Zone}`. Les trois éclairs de la Fosse introduits par `7665fff43a` relèvent du script, et non d’une nouvelle arène.
- Comparaison avec l’arbre Git : **14 403 fichiers** suivis sous `base/` et `game/` contrôlés en taille ; **88 grounds, 8 maps et 14 zones** comparés à l’octet. Les **10 grounds du payload** et l’index de **2 282 planches** ont été contrôlés séparément dans la quête préparée. La documentation qui présente certaines salles de la Guilde comme absentes n’est pas une référence fiable à ce HEAD.

## 2. Ce qui a réellement été testé

| Contrôle | Résultat | Limite |
|---|---|---|
| Validation de la quête préparée | **17 835 fichiers, 3 903,5 Mio**, `VALIDATION OK` | Préparation Linux, pas installation du paquet Windows. |
| Tests du dépôt | **45/47** au premier passage, **46/47** après relance Ambiances | L’interruption initiale d’Ambiances (`-9`, journal vide) n’a pas de cause établie. La suite passe seule en ~3,7 s. |
| Lua et guide | **132 Lua** compilent ; les deux audits heuristiques de dialogue et cadrage passent | Compilation et heuristiques ne vérifient ni le jeu d’acteur à l’écran, ni le son, ni chaque branche de scénario. |
| Lecture par PMDO | **98 grounds, 8 maps, 14 zones** désérialisés | Désérialiser ne joue pas `Enter` et ne déclenche pas un passage de porte. |
| Chargements Dev par sonde moteur | **6 ouvertures** : quiz, Réverie Dev, falaise nuit, parvis Guilde, entrée de la Fosse, fond de la Fosse | Ne vaut pas validation des cinématiques ou de leurs sorties. |
| Génération de donjons par PMDO | **34 étages × 2 graines = 68 générations avec entrée** : Grotte 9, Dazzling 1, Bois Perdus 14, Passage Aquatique 10 | Graines `20261118` et `20261119`. Ni combat ni traversée complète. Un premier essai sans état de sauvegarde est exclu : il ne produisait que des maps de repli. |
| Partie neuve en français | **Titre → halo → quiz → Bulbizarre / Caninos de Kanto (« Aube ») → littoral de nuit → falaise de nuit → Bois Perdus, étage 1** | Une seule combinaison héros/partenaire ; pas de reprise, K.O. ou victoire joués. Audio désactivé dans l’environnement de test. |
| Dev graphique | Falaise de nuit affichée avec l’équipe Dev par défaut ; plantage à l’entrée avec un seul Pokémon imposé | Essai forcé, distinct du passage réussi en mode joueur. Pas de validation graphique des autres scènes Dev. |

Le journal joueur donne l’ordre `intro_halo` → `personality_test` → `zrv2_zone_reveil_nuit` → `cliffdaytest_nuit` → `lost_wood`. La [capture du premier étage](preuves/bois-perdus-etage-1.png) montre Caninos seul, 19/19 PV, devant la première leçon « Repère d’exploration ». Le chemin de progression a donc bien franchi la scène de la falaise ; cela ne permet pas de noter chaque réplique ou chaque mouvement de Pichu.

## 3. Constats à traiter

### A. Falaise de nuit — plantage Dev reproduit avec un seul Pokémon

**Reproduction observée :** dans un profil Dev isolé, ouvrir `cliffdaytest_nuit`, ramener l’équipe de test à un seul Pokémon, réinitialiser l’état Destiny puis revenir directement sur la carte. La carte est lue, puis le processus s’arrête avec `NLua.Exceptions.LuaException: Argument number 2 is invalid` (code 134). Avec l’équipe Dev par défaut, la carte s’affiche. En partie neuve, le partenaire existe et la progression atteint les Bois Perdus.

**Point de code à vérifier :** `ground/cliffdaytest_nuit/init.lua:420–435` masque le héros, prend `GAME:GetPlayerPartyMember(1)` puis appelle `GROUND:SpawnerSetSpawn('Adagio', partenaire)` sans garde. Le deuxième argument de l’API est un `CharData`. C’est cohérent avec le plantage, mais la trace native ne désigne pas elle-même la ligne Lua. Prévoir un test Dev à un membre et un test à deux membres avant de choisir un comportement de repli. Ne pas confondre ce plantage avec le message de démarrage Linux `socket.core` manquant, après lequel l’initialisation continue.

### B. Café Spinda — test et carte de référence désalignés

`tools/test_cafe_lostwood.py:24,79` attend `182e0a465947db903fb48fd00d70538c` pour `game/Data/Ground/caféspindaaccueil.rsground`. Le fichier exact du HEAD **et du tag v0.7.3** donne `729111e96de0ac1589fab583385061a9`. Le test s’arrête sur cette première assertion ; il ne conclut donc rien sur les contrôles suivants ni sur l’accès au Café en jeu. La grille est connectée entre l’entrée, le comptoir et la sortie réellement utilisée ; ce n’est pas encore un aller-retour avec les PNJ et les déclencheurs actifs.

**Suite proposée :** vérifier l’aller-retour ville ↔ Café, l’escalier et la salle du fond avant de resynchroniser le test avec la carte voulue. Ne pas restaurer une ancienne carte uniquement pour faire passer son hash.

### C. Guilde — trois vérifications distinctes pour le repas

1. **Placement :** `guilde_destiny_refectoire.rsground` existe, mais ne définit pas de `MapChars` ni de `Spawners`. Dans `ground/guilde_destiny_refectoire/init.lua:17,26,33`, `RepasImmediat` anime les acteurs trouvés ; il ne les installe pas. La présence de la salle ne suffit pas à prouver un repas peuplé.
2. **Animation :** ni la feuille Gardevoir de base ni `game/Content/Chara/282.chara` n’exposent d’action `Eat` native d’après la lecture des feuilles. L’aperçu et les sources du dernier commit ne remplacent pas la feuille compilée attendue par `guilde_effectif.lua:209–230`.
3. **Fin du repas :** le test Lua isolé montre que `Repas(nil, 5)` peut laisser l’état `eating` après son retour, alors que `FinRepas({"Gardevoir"})` nettoie l’état et demande `CharEndAnim`. Dans `guilde_effectif.lua:184–203,309–346`, `Repas` passe des paires `{membre, acteur}` à `FinRepas`, qui les repasse à un résolveur attendant des identifiants. C’est un défaut du helper reproduit avec des doublures, **pas** un repas bloqué observé en jeu. Aucun appel actif à ce `Repas` ni à la tournée de réveil n’a été identifié dans les scripts parcourus.

**Suite proposée :** vérifier l’installation des acteurs et la feuille compilée, puis jouer entrée → début → fin de repas → sortie/réentrée. Tester séparément le nettoyage du helper pour éviter qu’un changement d’asset masque le défaut Lua.

## 4. Guide, chorégraphie et déplacements

Le corps du *Cutscene Scripting Guide* a été lu jusqu’à la ligne **1 418** et ses **70 placements illustrés** ont été parcourus. Quelques légendes ne sont pas lisibles à cette taille ; les pages liées ne sont pas comptées comme lues. Les repères retenus sont : cadrer les pieds et portraits pendant la réplique ; ne pas devancer une animation que la scène doit attendre ; laisser des respirations entre les réactions ; coordonner émotes, sons et fondus ; joindre explicitement les mouvements parallèles quand la scène en dépend. Les exemples SkyTemple ont été distingués des règles du moteur PMDO.

Le relevé AST compte **8 062 appels**, dont **117 méthodes directes distinctes** dans les interfaces suivies et **157 appels de transition**. Il repère des sites à inspecter, pas 157 liaisons validées en jeu : les cibles calculées, helpers, callbacks et états sauvegardés demandent une lecture ou un essai en situation. Le moteur confirme la boîte standard de deux lignes ; `cinematique.lua:11–14` fixe les portraits en `(8,132)` et `(256,132)` miroir. Un portrait bien ancré ne garantit pas que le personnage reste visible après un panoramique.

**Trajets :** 100 segments simulés, dont 9 recoupent des tags solides et 5 franchissent les limites de carte ; 10/10 couples départ–objectif sont connectés en grille. La [liste des segments](preuves/trajets.csv) isole notamment l’approche de la Fosse, le départ depuis la porte de Pichu, la sortie de Kabutops et les sorties de la troupe Dazzling. Ce ne sont pas 14 collisions de jeu : le moteur ignore certaines collisions en cinématique (`GroundChar.cs:347–358`) ; la simulation ignore l’altitude, les PNJ, le déclenchement et la caméra. Le marqueur `boss (392,368)` dépasse le fond de la Fosse (480×360) ; Kabutops est positionné en `(240,232)`, et aucun usage bloquant de ce marqueur n’est établi.

## 5. Reste à jouer avant de conclure sur les cinématiques

| Scène / parcours | Vérification restante |
|---|---|
| Bois Perdus, ZRV2 et falaise jour | Jouer la fin du solo, les retrouvailles et le retour en duo ; contrôler qu’une leçon de tutoriel ne se rejoue pas au mauvais moment. Puis jouer Dazzling en victoire et en échec et vérifier où le duo revient, son état et le retour du contrôle. |
| Réverie, Café, Dojo et Guilde | Vérifier les capteurs dans les deux sens, en progression réelle puis sur rechargement. Comparer la météo du carrefour et des quartiers avec les variantes et le changement de jour du Café. Observer le cadrage des interlocuteurs et les acteurs présents. |
| Passage Aquatique | Jouer le refus, l’entrée, la victoire jusqu’à la crique et le retour à la plage. Contrôler les sorties et le changement d’ambiance sans présumer que le chargement de la zone valide l’accès. |
| Fosse : alerte → grotte → Kabutops → retour | Vérifier la position des témoins de l’alerte, le seuil et le repli, les **trois éclairs**, l’arrivée de Kabutops, le placement en arène et la fuite. Comparer K.O., repli et victoire : présence de Lyra, duo allongé/réveil, destination et contrôle restitué. |
| Guilde : repas et réveil | Relever les acteurs posés et les animations effectivement chargées, la sortie de boucle et la reprise des états à la réentrée. Distinguer helpers accessibles et scènes réellement branchées. |

Reprendre ces contrôles sur des profils séparés (joueur et Dev), avec les acteurs attendus déjà présents quand on ouvre une scène directement. Pour chaque variante, consigner l’état d’entrée, la destination et l’état de sortie, les acteurs visibles, le retour du contrôle, et un éventuel blocage reproductible. Les séquences sonores devront être jugées avec une sortie audio réelle.

**Annexes :** [empreintes des 110 objets cartographiques suivis](preuves/empreintes-cartes.tsv) · [résultat des suites et relance Ambiances](preuves/resultats-tests.txt) · [extrait de la progression joueur](preuves/parcours-joueur.txt). Les observations de ce rapport ne couvrent pas un parcours complet de la quête.
