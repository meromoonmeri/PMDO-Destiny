# Pokémon Mystery Dungeon: Destiny — Chantier 0.7.5

Après la [`v0.7.4`](https://github.com/meromoonmeri/PMDO-Destiny/releases/tag/v0.7.4), cette retouche reprend le sauvetage de Nilo et l’entrée dans l’arène de Kabutops.

## Fosse Cascade Fond

- La carte de mise en scène passe de **480 × 360 à 576 × 528 px** (72 × 66 tuiles de 8 px). Un passage rocheux éclairé par petites vasques débouche au sud de la salle haute. Deux panoramiques distincts montrent d'abord le couloir, puis Nilo sur la terrasse. Les sprites ne sont pas redimensionnés.
- Nilo tremble déjà sur la terrasse, sans bouger de place. Il n'a rien touché : Kabutops l'accuse parce qu'il l'a vu près des vasques. Après la coupure de musique, **deux avertissements** sont signés `???`, sans portrait. Entre les deux, les protagonistes se regardent, cherchent qui parle et entendent Nilo se défendre.
- Juste après le second avertissement, le plateau s'assombrit. Un seul éclair révèle Kabutops déjà devant et à mi-distance du héros et du partenaire. La faux et le recul s'enchaînent pendant le retour à l'image : les deux glissent en arrière sans tourner le dos. Pas de détour par la rive ni de geyser.
- Après le face-à-face, le cadre et l'alignement du duo rejoignent ceux de l'arène. Le woosh garde ses neuf bandes natives `Pre_Battle` et le bruitage `EVT_Battle_Transition` entier. La revanche saute le couloir et la révélation, mais conserve le même raccord. `Boss Battle 2.ogg` démarre côté arène.
- **Duel inchangé** : le générateur prélève la salle haute à `x=48` pour garder l'arène 480 × 360, ses 42 cases praticables et l'équilibrage du 9e étage. Pas de carton au lancement, mais le nom reste dans le journal. Aucun changement aux huit premiers étages.
- Après la victoire, Kabutops s'enfuit par le sud et Lyra rejoint Nilo. Les retrouvailles et le retour paisible suivent le décalage de la salle haute. Le bilan reste celui du moteur, sans fanfare ni journal ajouté par le script.

### Références de mise en scène

- [Val Silencieux — Équipe de Secours Rouge (GIF de l'approche et de la révélation)](https://lparchive.org/Pokmon-Mystery-Dungeon-Red-Rescue-Team/Update%2026/) : l'arrivée de Cotovol puis le déplacement vers Tengalice construisent l'espace avant l'apparition d'Électhor. Ici : seuil, terrasse, voix non identifiée puis révélation, sans reprendre les répliques ni le noir complet.
- [Searing Crucible — Halcyon, `FirstPreBossScene`](https://github.com/Palikadude/Halcyon/blob/1522c7a8b7a34d70078e11ed605b21d563b0dc51/Data/Script/halcyon/ground/searing_crucible/searing_crucible_ch_5.lua) : avance du groupe, caméra en retard, interruption de la musique et signes du décor avant l'arrivée de Magcargo. Le décor et le Lua de Destiny ne copient pas de ressource de cette scène.

## Régressions couvertes

`tools/tests/test_grotte_verdoyante.py` vérifie les dimensions du ground, tous les liens vers la planche d'extension, le passage des colliders le long des trajets et l'intégrité de l'arène et du donjon. Les doublures Lua vérifient les deux plans d'approche, le tremblement avant le premier plan, les deux avertissements anonymes, l'innocence de Nilo et le recul à la révélation, le raccord sans carton, la revanche et les phases de fin. Relancer `python tools/build_grotte_verdoyante.py` avec Pillow pour régénérer les cartes et l'index des tuiles. Le nouvel atlas est assemblé par `tools/agrandir_vasques.py` à partir du décor Destiny.
