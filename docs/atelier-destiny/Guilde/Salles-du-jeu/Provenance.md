# Guilde Treehouse de Pokémon Mystery Dungeon: Destiny — salles du jeu

Les 15 cartes proviennent de la zone jouable `guilde_destiny_interieur`. Les fichiers ont été extraits directement de l’archive Windows 0.7.3 (CRC du ZIP vérifié). Le script de la falaise distribué avec ce jeu envoie bien vers `guilde_destiny_accueil`, premier étage de cette zone.

- [Préversion Windows 0.7.3](https://github.com/meromoonmeri/PMDO-Destiny/releases/tag/v0.7.3) et [registre des salles](https://github.com/meromoonmeri/PMDO-Destiny/blob/v0.7.3/game/Data/Zone/guilde_destiny_interieur.json).
- `v0.7.3` : `30dc4447f23cf077483d3048db3ada2c72218ce5`.
- Les 90 fichiers d’images, planches et cartes comparés ont les mêmes octets dans la distribution 0.7.3 et le tag. Leurs identifiants de fichiers Git correspondent dans les tags 0.7.6, 0.7.7 et la branche de travail au commit `0c0a13f`. Les scripts de scène, eux, peuvent différer.
- Repères visuels : la porte du maître est **au centre** du Grand Salon. Le bureau du maître n’a **qu’une fenêtre, centrale**. Les racines et les lianes du jeu sont présentes. Ce n’est pas la refonte locale `9feecc8`.

## Contenu

- `PNG/Jour` et `PNG/Nuit` : cartes complètes à leur définition native, recomposées avec les tuiles, les fenêtres et les états de porte d’origine, sans retouche. Aucun PNJ, HUD ni caméra de scène : ce sont des rendus de cartes et non des captures d’une partie. Le Grand Salon a aussi son état porte ouverte.
- `Sources/` : les 108 ressources géométriques, graphiques et scripts associés extraits du ZIP Windows, sans changement. Ce n’est pas un mod à installer.
- `Provenance.json` : chemins d’archive, SHA-256 et comparaison avec les sources. `Salles.json` : inventaire des 15 pièces et de leurs dimensions.
