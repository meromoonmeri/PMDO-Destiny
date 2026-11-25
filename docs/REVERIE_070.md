# Réverie — mise à jour 0.7.0

Base : commit `b4deaa9`, branche `wip/reverie-integration-kingambit-cafe`. Cette mise à jour porte sur le réseau intérieur de la **Guilde Destiny** et sur la façade extérieure `guilde_cliff`. Aucune carte n'a été refaite de zéro : les 15 salles existantes et les 4 cartes de falaise sont conservées, seuls leurs pixels et leurs ressources ont été corrigés.

## Guilde Destiny — intérieurs

* **Version PMDO re-shadée passée au peigne fin.** Les 15 salles sont repassées au re-shade en conservant les formes de la source DS `673e05b` : plus de *mixels* sur les arêtes, plus de flancs adoucis par un flou de filtre. L'écart moyen avec la sauvegarde brute descend à 1,30 niveau RGB, la palette des salles remonte de 1 054 à 1 875 couleurs, et les amas isolés de pixels chutent de 3 105 à 759.
* **Fenêtres — 56 ressources `.dir` refaites sur 4 ambiances.** Chaque fenêtre dispose désormais de ses quatre variantes jour, aube, crépuscule et nuit, avec le jeu de lumière propre à sa salle. Les cadres ne portent plus aucun pixel bleu nuit : la vitre ressort la nuit sur 14 fenêtres déclarées sur 14.
* **Ombres de l'entrée.** Le jeu d'ombre des quatre façades `Guilde_HD_Ombre_*` est ramené à l'identique de la sauvegarde brute `c2766e5` — quatre teintes vertes, alpha maximal 224 — au lieu du gris uniforme translucide de la version PMDO précédente.
* **Bordure rocheuse de l'escalier.** Un muret de pierre courbe borde maintenant le flanc gauche de l'escalier de la façade, sur les huit variantes (quatre ambiances × porte fermée ou ouverte). L'arc est peint uniquement avec des couleurs relevées sur la façade, avec liseré sombre, joints de pierre et deux touffes de mousse.

## Façade extérieure et nettoyage

* **Pixels parasites.** 132 pixels parasites retirés des huit façades `Guilde_HD_*` (17 par ambiance). Le nettoyage ne touche qu'aux éclats isolés de 2 à 12 pixels, rejette tout pixel ayant un reflet doré voisin — les cailloux, la mousse et les liserés sont intacts — et ne répare qu'avec un voisin opaque non froid.
* **Aucune tache lumineuse, aucun halo, aucun artefact de filtre.** Détection faite sur l'ambiance jour, application aux quatre, pour éviter les fausses détections sur la nuit.
* La roche violette déjà présente dans la source `(118,94,102)`, hors de la zone de l'escalier, est conservée telle quelle.

## Outils et documents

* `tools/nettoyer_pixels_facade.py` : nettoyage de la façade, idempotent. Vérifié en le rejouant sur les ressources d'avant nettoyage : il reproduit les huit fichiers à l'octet près, et une seconde exécution ne modifie plus rien.
* `tools/bordure_rocheuse_escalier.py` : tracé paramétrique de l'arc, idempotent (ne peint que sur les pixels transparents).
* `docs/Bilan_POLISH_GUILDE_2026-11-13.md` et les trois rapports d'audit associés.
* Planches avant/après dans `art/guilde_destiny_reseau/polish/`.

## Limites

Les contrôles de cette mise à jour sont automatisés : audit des fenêtres et des ambiances (0 anomalie, 0 avertissement), tests des bâtiments et des intérieurs, reproduction à l'octet des ressources régénérées, CI Windows. **Le rendu n'a pas été vérifié manuellement en jeu ni dans l'éditeur.** Les ombres, la bordure rocheuse et le rendu des fenêtres à chaque ambiance restent à confirmer en jeu, de même que la lisibilité des scènes sous chaque ambiance. Sauvegarder ses parties avant de mettre à jour.
