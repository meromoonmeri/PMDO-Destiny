# Pokémon Mystery Dungeon: Destiny — Mise à jour 0.7.5

Depuis la [`v0.7.4`](https://github.com/meromoonmeri/PMDO-Destiny/releases/tag/v0.7.4), cette mise à jour reprend et finalise la mise en scène du sauvetage de Nilo dans la Fosse Cascade Fond.

## Fosse Cascade Fond : sauvetage de Nilo et Kabutops

- Nilo se trouve sur la terrasse supérieure des vasques et avertit le duo avant de tomber dans la salle. Le souffle de Kabutops repousse ensuite les trois personnages sur des trajectoires distinctes, vers des points libres de la carte.
- La découverte du boss conserve ses éclairs et sa voix hors champ sans effet ni son d’eau. L’état de la scène est enregistré avant sa séquence afin qu’une interruption suivie d’une réentrée ne rejoue pas la révélation.
- Avant le duel, Nilo et le partenaire échangent quelques répliques sur la peur et la protection du groupe. Le fondu sonore et visuel précède la transition au combat.
- Après la victoire, Kabutops refuse encore de changer d’avis puis s’enfuit en courant vers le sud. Nilo rejoint le duo et Lyra entre dans le cadre avant de l’appeler; les retrouvailles se poursuivent avant le retour de fin d’expédition.
- Les changements préexistants de la WIP Kingambit — notamment Nilo sur la terrasse et le souffle qui repousse le duo — sont conservés. Aucun changement de carte ou de tuiles n’est inclus dans cette mise à jour.

## Vérifications et limites

- Les contrôles automatisés de la CI couvrent les états de la scène, les déplacements et la transition de fin; la validation doit être exécutée sur le commit de cette version.
- Les points d’arrivée et certains trajets ont été contrôlés statiquement sur la carte WIP. Cela ne remplace pas un essai en jeu : aucune validation manuelle PMDO, audio ou sauvegarde réelle n’est annoncée ici.
- Par précaution, sauvegarder ses parties avant la mise à jour.
