# Pokémon Mystery Dungeon: Destiny — Chantier 0.7.5

Après la [`v0.7.4`](https://github.com/meromoonmeri/PMDO-Destiny/releases/tag/v0.7.4), cette retouche reprend le sauvetage de Nilo et l’entrée dans l’arène de Kabutops.

## Fosse Cascade Fond

- Le partenaire repère Nilo sur la terrasse. Nilo avoue avoir dérèglé le courant, sans descendre ni trembler. Un seul éclair révèle Kabutops. Son coup de faux déclenche le souffle : le duo recule sans lui tourner le dos, puis le partenaire tente de désamorcer le conflit.
- L’ultimatum de Kabutops enchaîne sur le woosh de boss : neuf bandes natives `Pre_Battle`, le bruitage `EVT_Battle_Transition` entier, puis le fondu vers l’arène et le démarrage de `Boss Battle 2.ogg` par le moteur. En revanche, un bref défi remplace la rencontre, avec le même woosh.
- Le carton « Fosse Cascade Fond » ne s’affiche plus à l’entrée du duel. Le segment nomme toujours l’étage pour le journal et conserve ses événements de placement, de combat et de sauvegarde. Les cartons des huit étages et de la visite libre restent inchangés.
- Après la victoire, Kabutops s’enfuit par le sud. Lyra rejoint Nilo : les regards et les répliques suivent son arrivée. Le bilan reste celui du moteur, sans fanfare ou journal ajouté par le script.

La scène conserve les phases de sauvegarde et de revanche. Les cartes, collisions, tuiles et statistiques de combat n’ont pas changé.

## Régressions couvertes

`tools/tests/test_grotte_verdoyante.py` vérifie la structure du donjon et le nom de l’arène sans carton. Les doublures Lua vérifient l’ordre aveu/éclair/souffle, la synchronisation des bandes et du son, la reprise sans rejouer la découverte, la revanche et le retour après la victoire.
