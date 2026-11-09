# Forêt aux lucioles — source DTEF de Lost Wood

Source : atelier Treehouse de l'utilisateur, dossier `RAW/TileDtef/foret_lucioles` de la version 1 du lot. Les 27 PNG sont conservés tels quels : trois variantes de 432 × 192 px et deux couches de douze phases d'eau, aux durées 17 et 9 ticks. L'enveloppe XML indique la taille standard de 24 px.

La feuille active `game/Content/Tile/LostWoodLucioles.tile` a été importée avec l'outil PMDO 0.8.12 ; les trois définitions `lost_wood_{wall,floor,secondary}` lui font référence. Les matières générées sont des interprétations sur une géométrie native et ne sont pas présentées comme des sprites officiels. Les droits des ressources de tiers demeurent applicables.

`python tools/tests/test_lost_wood_dtef.py` compare les raccords, variantes et images des deux animations aux ressources importées, en tenant compte de l'alpha prémultiplié par le moteur. L'ancien dossier `art/dtef/LostWoodDestiny` est conservé pour les données et tests historiques.
