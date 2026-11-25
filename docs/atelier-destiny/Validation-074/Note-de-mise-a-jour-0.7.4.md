# Pokémon Mystery Dungeon: Destiny — Mise à jour 0.7.4

Depuis la [`v0.7.3`](https://github.com/meromoonmeri/PMDO-Destiny/releases/tag/v0.7.3), cette version remanie le duel de la Fosse Cascade Fond et les retours d’expédition, retouche les abords de Réverie, ouvre les comptoirs de Zig et Zag et anime les dix convives de la Guilde.

## Bois Perdus et Fosse Cascade : les bilans d’expédition

- **Bois Perdus.** « La dernière sortie », l’historique et la fanfare de résultat natifs de PMDO sont rétablis à la fin de chaque trajet enregistré. L’aller en solo réussi mène, après le bilan, à la prairie du réveil où l’équipe se reforme. Le retour réussi en duo ramène à la falaise de jour. Un échec à l’aller ramène à la falaise de nuit ; un échec au retour repasse par la prairie. En exploration libre, le bilan précède le retour à Réverie.
- **Une seule expédition à la Fosse Cascade.** Le 8ᵉ étage mène aux vasques puis à l’arène de Kabutops sans ouvrir de bilan intermédiaire. La victoire reprend la scène avec Nilo et Lyra ; le bilan et la fanfare de fin d’expédition viennent **après les retrouvailles**, avant le retour à Réverie. Une exploration libre réussie après le sauvetage se clôt aussi aux vasques. En cas de K.O. ou de repli, le retour à l’entrée et l’état de reprise du scénario sont conservés.
- **Les annonces arrivent en ville.** Après l’accueil de Nilo, Réverie annonce que la Fosse est accessible en exploration libre par la sortie est. Si une mission du tableau a été accomplie, son annonce s’affiche au retour ; la prime reste à retirer une seule fois **au tableau des missions**, pas à la sortie du donjon.

## Fosse Cascade Fond : la nouvelle mise en scène de Kabutops

- La découverte alterne un premier éclair blanc sur la clairière vide, des réactions décalées du duo, puis un grondement et une voix hors champ. Un double éclair révèle Kabutops sur le sable, **sans geyser, éclaboussures ni bruit d’eau**. Pendant le pré-combat, les reflets sont figés et le calque des bulles est masqué, puis restauré. Les vasques gardent leurs animations en visite libre.
- Nilo (Lixy) tremble visiblement. Le partenaire se place pour le couvrir ; la caméra garde le duo et les acteurs lisibles au-dessus du dialogue. La musique s’interrompt au choc, puis reprend après le retour de l’image. Le son du coup de faux est calé sur l’impact de l’animation lorsque la planche le permet. La revanche ne répète pas la scène de découverte ni des éclairs supplémentaires à l’entrée du duel.
- Le point d’apparition au sol et la position de combat concordent sous les marches : Kabutops en **`(10, 10)`** dans l’arène, équipe en **`(10, 12)`**. Les 42 cases praticables et les statistiques du boss restent inchangées. Le chargement forcé de l’arène depuis l’éditeur et la continuité de l’expédition en partie normale sont conservés.
- Après sa défaite, Kabutops fuit **en courant vers le sud** au lieu de plonger dans les vasques. Nilo rejoint l’équipe, puis Lyra arrive ; le dialogue et le retour se déroulent à la suite de cette scène.

## Réverie Town : chemins, arbres et habitants

- Quatre raccords de terrain sont repris : le chemin et le virage près de la terrasse du Café, le pied de l’escalier est du Dojo et deux coutures de teinte à l’ouest. Les transitions sable–herbe sont plus progressives ; quatre arbres tronqués retrouvent leur cime, leur tronc et leur ombre. Les tuiles d’herbe répétées sont corrigées sans changer les collisions ni les déclencheurs.
- Les dix variantes jeu/édition reçoivent les mêmes retouches de calques. Les animations des rivières et cascades, les accès, les intérieurs et les habitations existantes sont conservés. La grande refonte proposée du vert foncé et des quatorze segments de chemin n’est pas incluse.
- Les habitants proches peuvent échanger un regard ou une émote, avec une réponse décalée. Le pêcheur et la fleuriste ont des gestes à leur poste ; les services ne migrent pas pour ces animations. Le système s’efface devant les menus, les dialogues et les cinématiques, et ne laisse pas de geste en attente après le départ du quartier.

## Zig et Zag : deux étals et un stock par jour

| Comptoir | Offre au réassort |
| --- | --- |
| **Zig, le Kecleon vert** | Deux provisions et quatre soins, avec une Pomme et une Baie Oran garanties, un lot de projectiles et un équipement. |
| **Zag, le Kecleon violet** | Une CT, trois orbes et deux lots de quatre baguettes. |

- Les deux frères remplacent les noms Basil et Félix dans la visite et les dialogues. Chaque comptoir propose **Acheter**, **Vendre** et **Infos** dans les menus natifs de PMDO. Le prix et la quantité sont calculés pour le lot complet ; les Poké et la place disponible sont vérifiés avant de débiter un achat. Une vente retire la pile sélectionnée, y compris parmi les objets équipés éligibles.
- Un lot acheté disparaît de l’étal de la journée et reste épuisé après reprise de la sauvegarde. Les assortiments de Zig et Zag sont indépendants ; rouvrir les menus ne les relance pas. Une sieste au Café Spinda fait passer la ville au lendemain ; terminer la Fosse ou sa revisite réussie compte également pour le calendrier de Réverie. Joliflor conserve son propre étal.

## Guilde : dix convives au réfectoire

| Membre | Rôle |
| --- | --- |
| Gardevoir | Maîtresse de guilde |
| Canarticho | Second |
| Simisage | Cuisine |
| Mélofée | Infirmerie et tournée du réveil |
| Cizayox | Entraînement au combat |
| Noctali | Exploration et cartographie |
| Dimoret | Éclaireuse |
| Draby | Chef de la Team Star |
| Pandespiègle | Recrue à l’entraînement, Team Star |
| Capumain | Livraisons, Team Star |

- Les dix personnages prennent place dans la salle existante dès l’entrée. Chacun joue une **vraie animation de corps `Eat`** ; l’émote de miettes vient en complément. Parler à un convive interrompt son repas : il se tourne vers le joueur, présente son rôle, puis reprend son animation. Sortir, revenir ou recharger ne crée pas de doublon. La disposition de la salle, ses passages et ses portes sont inchangés.
- Huit animations de repas ont été intégrées aux conteneurs `Chara` ; celles déjà utilisables de Noctali et Capumain sont conservées. Les planches sources (`Eat`, `Wake`, `Sleep`, `Pose`), leurs aperçus, le manifeste, l’index des personnages et l’importeur documentent ce travail. Les ressources de cloche et de calot, le script de réveil et la pose de service de Mélofée sont disponibles pour les scènes : ce lot n’ajoute pas de tournée jouable dans de nouvelles salles.

## Installation et vérifications

- **Faire une copie de sa sauvegarde avant la mise à jour.** Conserver les ressources et les scripts de cette version ensemble, en particulier les `.chara` et leur index. Depuis les sources, `python tools/unpack_payload.py` restaure les dix cartes de Réverie et génère l’index des tuiles avec les ressources de cette révision ; `tools/build_windows.py` l’appelle lors du montage du ZIP complet. Le compacteur vérifie la même empreinte que le payload livré.
- **Contrôles structurels et automatisés :** payloads et raccords de Réverie, arène et enchaînements de la Fosse, routes solo/duo et échecs des Bois, annonces et prime unique, achats/ventes et réassort, dix variantes `Eat` réellement chargées par le moteur et réapparition sans doublon. Les suites exactes sont sous [`tools/tests/`](../tools/tests/), notamment `test_grotte_verdoyante`, `test_lost_wood`, `test_polish_reverie`, `test_tableaux_reverie`, `test_boutiques_kecleon`, `test_guilde_effectif` et `test_guilde_eat_runtime`.
- **Essais sous PMDO/Linux :** deux bilans et deux replays distincts pour l’aller et le retour des Bois ; un bilan et un replay uniques du 8ᵉ étage de la Fosse au retour en ville ; achat et vente chez les Kecleon, sauvegarde au Café et réassort après la sieste ; dix convives encore présents après rechargement et reprise du repas après dialogue. Les sorties de donjon ont été déclenchées par une fixture de test : ces essais ne représentent ni une traversée intégrale à la manette, ni un duel joué de bout en bout, ni une vérification audio.
- **Windows :** [Build Windows](https://github.com/meromoonmeri/PMDO-Destiny/actions/workflows/build-windows.yml) en mode `build` valide et assemble le ZIP. Seule une exécution réussie **sur la révision qui porte cette note** valide ce candidat Windows ; un ancien run vert ne suffit pas.

Détails techniques : [Fosse Cascade et raccords de Réverie](POLISH_FOSSE_REVERIE.md) · [Effectif et ressources de la Guilde](GUILDE_EFFECTIF_075.md) · [Comparaison du code depuis la v0.7.3](https://github.com/meromoonmeri/PMDO-Destiny/compare/v0.7.3...45082b7f5c08b4b909f685e8256d4fb324ab036b).
