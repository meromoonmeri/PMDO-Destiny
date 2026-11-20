# Pokémon Mystery Dungeon: Destiny — Chantier 0.7.5

Après la [`v0.7.4`](https://github.com/meromoonmeri/PMDO-Destiny/releases/tag/v0.7.4), cette retouche reprend le sauvetage de Nilo et l’entrée dans l’arène de Kabutops.

## Fosse Cascade Fond

- La carte de mise en scène passe de **480 × 360 à 576 × 528 px** (72 × 66 tuiles de 8 px). Un passage rocheux éclairé par petites vasques débouche au sud de la salle haute. Deux panoramiques distincts montrent d'abord le couloir, puis Nilo sur la terrasse. Les sprites ne sont pas redimensionnés.
- Nilo tremble déjà sur la terrasse. Il demande qui sont les deux Pokémon, puis raconte qu’il cherchait sa maman et s’est perdu. Le duo se présente et le rassure avant que Kabutops ne l’accuse. **Deux avertissements** signés `???`, sans portrait ; entre les deux, le duo se regarde et Nilo dément l’accusation.
- Secousse, terre et jaillissement vertical sur l’axe médian : Kabutops surgit devant le duo, style **Tunnel**, avec les particules et le son natifs `Dig`. L’impulsion, le coup de faux et le recul des deux Pokémon se chevauchent. Pas d’arrivée depuis la rive ni d’éclair plein écran qui masque l’animation.
- Face au duo, Kabutops explique les crues, les départs de familles et le danger en aval. Il soupçonne Nilo parce qu’il l’a vu près de la source, pas parce qu’il l’a vu agir. Quand le héros constate que le gardien est trop en colère pour entendre raison, son partenaire lui répond et se prépare. Objectif de **1 min 20 à 1 min 30** avec une lecture posée ; la confirmation des dialogues reste manuelle.
- Le woosh garde ses neuf bandes natives `Pre_Battle` et le bruitage `EVT_Battle_Transition` entier. La revanche est courte et conserve le même raccord. `Boss Battle 2.ogg` démarre côté arène. Nilo reste visible et tremble sur la terrasse derrière Kabutops, au même point du décor que dans le pré-combat. Sa pose est dessinée depuis le sprite natif de Lixy ; il n’entre dans aucune équipe, n’a ni tour ni collision et ne peut pas être choisi comme cible.
- **Duel inchangé** : le générateur prélève la salle haute à `x=48` pour garder l'arène 480 × 360, ses 42 cases praticables et l'équilibrage du 9e étage. Pas de carton au lancement, mais le nom reste dans le journal. Aucun changement aux huit premiers étages.
- Après la victoire, Kabutops s'enfuit par le sud. Nilo redescend de la terrasse et retrouve Lyra. Les retrouvailles et le retour paisible suivent le décalage de la salle haute. Le bilan reste celui du moteur, sans fanfare ni journal ajouté par le script.

### Références de mise en scène

- [Val Silencieux — Équipe de Secours Rouge (GIF de l'approche et de la révélation)](https://lparchive.org/Pokmon-Mystery-Dungeon-Red-Rescue-Team/Update%2026/) : l'arrivée de Cotovol puis le déplacement vers Tengalice construisent l'espace avant l'apparition d'Électhor. Ici : seuil, terrasse, voix non identifiée puis révélation, sans reprendre les répliques ni le noir complet.
- [Searing Crucible — Halcyon, `FirstPreBossScene`](https://github.com/Palikadude/Halcyon/blob/1522c7a8b7a34d70078e11ed605b21d563b0dc51/Data/Script/halcyon/ground/searing_crucible/searing_crucible_ch_5.lua) : avance du groupe, caméra en retard, interruption de la musique et signes du décor avant l'arrivée de Magcargo. Le décor et le Lua de Destiny ne copient pas de ressource de cette scène.

## Netteté, sans retouche de la carte

Les fichiers ground, arène et planches sont inchangés. Le moteur échantillonne déjà les tuiles en `PointClamp` à une taille de fenêtre entière. Pour les aperçus, `tools/render_ground_moteur.py` conserve désormais les tuiles complètes de 8 ou 24 px et exporte les animations WebP sans perte. `--echelle 2`, `3` ou `4` duplique les pixels, sans interpolation ; le PNG par défaut reste à taille native. `--arene end_grotte_verdoyante` permet de rendre les mêmes strates de la salle haute dans l’arène 480 × 360.

## Régressions couvertes

`tools/tests/test_grotte_verdoyante.py` vérifie les dimensions du ground, tous les liens vers la planche d'extension, le passage des colliders le long des trajets et l'intégrité de l'arène et du donjon. Les doublures Lua vérifient les deux plans d’approche, l’ordre des échanges, le tremblement avant le premier plan, les deux avertissements anonymes, le mouvement vertical et le recul, la décision du héros, le raccord et le spectateur non combattant (placement, animation et nettoyage), la revanche et les phases de fin. Relancer `python tools/build_grotte_verdoyante.py` avec Pillow pour régénérer les cartes et l'index des tuiles. Le nouvel atlas est assemblé par `tools/agrandir_vasques.py` à partir du décor Destiny.
