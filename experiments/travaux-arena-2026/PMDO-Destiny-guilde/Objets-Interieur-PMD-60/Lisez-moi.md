# Objets d’intérieur de guilde PMD

**40 / 60 livrés.** Chaque objet livré a son propre brut généré, puis un sprite transparent à l’échelle 1×. Les six lots sont indépendants.

Ouvrez [le catalogue hors ligne](Catalogue-Objets-de-Guilde.html) pour voir chaque objet sur parquet, sur fond sombre ou sur damier. Les kits ZIP contiennent les PNG, la planche et l’index par lot.

| Lot | Thème | État |
| --- | --- | --- |
| 01 | Accueil et missions | [Kit (10 PNG)](Kit-Objets-Guilde-PMD-01-Accueil.zip) · [aperçu](Lots/01-Accueil/Apercu-du-lot.png) |
| 02 | Cuisine et réfectoire | [Kit (10 PNG)](Kit-Objets-Guilde-PMD-02-Cuisine.zip) · [aperçu](Lots/02-Cuisine/Apercu-du-lot.png) |
| 03 | Dortoirs et chambres | [Kit (10 PNG)](Kit-Objets-Guilde-PMD-03-Dortoirs.zip) · [aperçu](Lots/03-Dortoirs/Apercu-du-lot.png) |
| 04 | Bureau et bibliothèque | [Kit (10 PNG)](Kit-Objets-Guilde-PMD-04-Bureau.zip) · [aperçu](Lots/04-Bureau/Apercu-du-lot.png) |
| 05 | Réserve et atelier | À générer |
| 06 | Infirmerie et salle commune | À générer |

## Sources

- `Generations/` contient les bruts individuels sur fond magenta. Ils ne sont pas dupliqués dans les kits ZIP.
- `Sources/Programme.json` contient les 60 objets prévus ; l’inventaire de chaque lot ne compte que les PNG réellement produits. `Sources/Palette.json` fixe les rampes communes. Le repère de style est le rondin nº 003 de l’ancienne planche PMU, et non un des 60 objets.
- Depuis ce dossier, `python Sources/Construire.py --lot 01-Accueil` reconstruit un lot déjà généré (Pillow, NumPy, SciPy). Sans argument, reconstruit tous les lots dont les dix bruts existent.
- PNG transparents, une orientation. Aucun fichier du jeu, commit GitHub, ni ROM n’a été modifié.
