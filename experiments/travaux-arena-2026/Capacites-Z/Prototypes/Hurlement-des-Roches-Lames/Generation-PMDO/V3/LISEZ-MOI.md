# Hurlement des Roches-Lames — V3

## Planches d'animation

PNG RGBA à fond transparent, cases de **128 × 128 pixels**, huit colonnes, lecture de gauche à droite puis de haut en bas. Cadence cible : **60 images par seconde** (une image par tick lorsque le moteur tourne à 60 Hz).

- `01-onde-sonore-48images-128px.png` : trois fronts d'onde successifs, direction droite, 48 images (0,80 s).
- `02-fissures-48images-128px.png` : fissures qui se propagent autour de la cible, 48 images (0,80 s).
- `03-pics-roche-72images-128px.png` : pics qui émergent du sol et encerclent la cible, avec éclats de roche natifs, 72 images (1,20 s).
- `04-impact-compose-100images-128px.png` : fissures puis pics, avec chevauchement des étapes, 100 images (1,67 s). Les quatre dernières cases de la grille sont inutilisées.

Les `.dir` sont les banques utilisées par le banc PMDO : `RochesLamesV3_Onde.dir` contient les huit orientations ; `RochesLamesV3_Impact.dir` contient l'impact composé. Les PNG sont des planches de travail et ne remplacent pas automatiquement des fichiers du jeu. La fiche JSON est une fiche réservée au banc.

## Démonstration et tests

`Lougaroc-Hurlement-V3-onde-fissures-pics-60ips-son.mp4` est la capture sonore du banc en copie isolée, encodée à 60 i/s ; des images du moteur peuvent être répétées si le rendu ne tient pas cette cadence. Le journal donne les résultats.

Huit orientations : huit cibles à deux cases touchées (270 → 220–224 PV), huit témoins latéraux indemnes, une charge consommée. Les quatre Champs électrique, herbu, brumeux et psychique ont été retirés dans les essais dédiés. Les fichiers d'origine de la copie de test ont été restaurés et comparés.

## Limites

La frappe visuelle entoure la cible mais n'immobilise pas ni ne modifie les cases du sol ; les pics et fissures sont des effets, les dégâts ne sont calculés qu'une fois. Le journal de combat peut masquer une partie des effets. La portée de deux cases est une adaptation du banc, et seule la forme Diurne de Lougaroc a été essayée ; murs, alliés, bords, immunités, échec et protection restent à tester. Le retrait de Champ couvre seulement les quatre identifiants indiqués. Cristal, restrictions et menu Z ne sont pas intégrés. Ce n'est ni une intégration définitive ni un push.

Sources de préparation et de banc : `~/Capacites-Z/Sources/preparer-roches-lames-v3.py`, `roches-lames-v3-effets.lua`, `banc-roches-lames-v3.py`, `test-roches-lames.lua` et `intro-halo-banc-lougaroc.lua`.
