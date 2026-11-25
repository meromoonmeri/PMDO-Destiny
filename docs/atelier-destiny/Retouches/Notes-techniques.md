# Fosse Cascade & Réverie — première passe de polish

Base de travail : `aa1430c4e8953e486b82691731fbbcbce8e4c57e`, `wip/reverie-integration-kingambit-cafe`.

## Fosse Cascade : faire entendre le danger avant de le montrer

Référence de rythme : le [secours de Cotovol et l’arrivée d’Électhor](https://lparchive.org/Pokmon-Mystery-Dungeon-Red-Rescue-Team/Update%2026/) dans *Équipe de Secours Rouge* (à ne pas confondre avec le duel au Mont Foudre). L’avertissement du témoin et la voix entendue dans le noir précèdent la révélation d’Électhor. Ici, le ton et les répliques sont propres à Nilo et Kabutops.

- `fgv1_fin_grotte_vasques/init.lua` fige les reflets par `TileLayer.FrameLength = 0` et masque le calque des bulles pour le pré-combat et la revanche. Les valeurs sont remises sous le dernier fondu noir. La visite libre et le post-combat ne passent pas par cette suspension. Pas de VFX ni de bruit d’eau ajouté à l’apparition.
- La montée du duo révèle Nilo sans que les personnages traversent les marches. Un éclair sur la clairière vide, réactions décalées, grondement et réplique hors champ dans le noir, puis un double éclat dont le dernier dévoile le boss. Le coup de faux est joué avec `Attack` ; le SE utilise l’instant d’impact de la planche si disponible. Le partenaire se décale pour couvrir le côté où Nilo s’est réfugié. La revanche ne rejoue pas la découverte et le fondu d’entrée en combat ne rajoute pas les éclairs du helper générique.
- Le problème existait aussi **dans le duel** : `(10,8)` correspondait au milieu des marches visibles. Le centre de la nouvelle case `(10,10)` vaut `(252,252)` px ; le collider du ground et le marqueur `boss` commencent tous deux à `(244,244)` (16×16 px). L’équipe commence en `(10,12)` ; les quatre emplacements d’entrée sont libres. Les stats du boss, les 42 cases praticables, les conditions de victoire et le retour ne changent pas.

## Réverie : reprendre les raccords, pas refaire la ville

Référence visuelle : [la carte native `metano_town.rsground` de Halcyon](https://github.com/Palikadude/Halcyon/blob/da6c2130d641507447e6386a5e47a296e8cb4c71/Data/Ground/metano_town.rsground) (Palikadude, commit `da6c2130`). Le sable et l’herbe se rejoignent avec quelques pixels de transition ; les sentiers conservent un noyau lisible dans les virages et au pied des marches. Le lot utilise uniquement les ressources Réverie déjà présentes et un atlas de retouches, pas d’import supplémentaire de Halcyon.

- Les retouches `.tile` des versions `0.5.1` à `0.5.6` déjà en place sont conservées. Le lot « vert foncé + 14 segments », mentionné mais non livré dans `REVERIE_074.md`, n’a pas été fusionné. Le générateur réutilise l’identifiant d’herbe `(39,218)` relevé dans cette note et traite les quatre raccords vérifiés sur la carte actuelle.
- Chemin de la terrasse du Café et virage, raccord au pied de l’escalier est du Dojo, deux coutures de teinte à l’ouest. Les bordures du sable sont progressives, sans changer les sols que le moteur autorise à traverser.
- Quatre arbres coupés en bord de la carte sont repris à partir du tampon d’un arbre entier de Réverie (cime, tronc, ombre), sans déplacer les déclencheurs. L’herbe répétée est reprise sur le calque `Base` avec la texture native contiguë. Les dix variantes jeu/Dev ont les mêmes calques ; tous leurs octets **hors `Layers`** sont conservés. Les rivières et cascades de Réverie gardent leurs animations.
- Les habitudes des habitants déjà en place restent actives. Au lieu d’attendre une paire qui peut être absente du quartier, la ville choisit un échange silencieux près du joueur : un regard et une émote, puis la réponse différée. Les services ne quittent pas leur poste ; le pêcheur et la fleuriste ont des gestes locaux. Les menus, scènes et dialogues ont la priorité. Aucun geste en attente ne survit au départ de la carte.

## Reproduire le lot visuel

Conserver une copie du `payload/` de la révision de départ. `python tools/polish_reverie_raccords.py --source-payload /copie/payload --out /copie/retouches` écrit les dix archives, l’atlas `.tile` et PNG et le manifeste, sans écraser la source. Son entrée attend le décor de `aa1430c4` et refuse un jeu de calques divergent. Les empreintes et les zones retouchées sont renseignées dans `tools/reverie_polish_manifest.json`.

Les grounds volumineux et `game/Content/Tile/index.idx` ne sont pas à versionner. Si une copie de tests contient les anciens grounds générés, les conserver à part avant `python tools/unpack_payload.py`. Régénérer l’index avec `python tools/build_tile_index.py` s’il existait déjà. Ne pas remplacer directement les cartes d’une installation ni le profil de sauvegarde.

## Contrôles effectués (PMDO 0.8.12, FR)

- Payloads reconstitués (10/10), index des tuiles régénéré (2 283 planches), `validate.py` OK. 15 suites ciblées passent, notamment Fosse Cascade, nouveaux raccords, variantes ville, ambiances, tableaux et liaisons. La compilation Dev → jeu reste exacte avec la nouvelle banque : 203 pistes statiques sont regroupées dans le calque `Base`, et les arbres complets ajoutent 67 pistes nettes à `Objects`. Les cascades et le nombre de pistes des autres calques sont inchangés. La campagne entière du pré-audit n’a pas été rejouée.
- Réverie : `reverie_centre` en contrôle libre. Les tests ont repositionné le joueur, pas les PNJ. Les émotes de Lombre/Ludicolo, Roserade et Goinfrex sont passées dans le moteur (Lombre/Ludicolo et Roserade en images). Deux arrêts d’Ophélie donnent un déplacement réel `528,1337 → 506,1344 → 518,1341` sans ordre console : c’est **sa promenade préexistante**, pas un nouveau trajet scénarisé. Goinfrex reste à son poste `1012,1404` dans les six relevés. Les autres gestes et l’arbitrage avec les menus sont couverts par des doubles d’API, sans les donner tous pour observés.
- Fosse : en zone réelle (`InDevZone=false`, accès console sans refaire les 8 étages), premier pré-combat joué jusqu’au fondu et 605 reflets figés / bulles masquées mesurés. L’arène a été chargée via la version Dev de la scène, puis via `ContinueDungeon` après la revanche en zone réelle. Mesure dans l’arène : Kabutops `(10,10)`, leader `(10,12)`. L’essai normal du premier fondu a été interrompu par un talent invalide du partenaire de test (surnom passé au mauvais emplacement de l’API) ; l’équipe de test a été corrigée avant la revanche. Aucun changement d’équilibrage n’a été fait pour cet essai.

À poursuivre : l’enchaînement des huit étages jusqu’à la scène (le premier fondu nominal avec une équipe de partie ordinaire en fait partie), victoire/retour après K.O. et écoute (sortie audio factice), ainsi que les autres lisières. Les quatre arbres et quatre raccords ne constituent pas un audit exhaustif de la carte.
