# Hurlement des Roches-Lames — V2, prototype à valider

Vidéo sonore : `Lougaroc-Hurlement-Roches-Lames-V2-PMDO-60ips-son.mp4`. Journal : `journal-v2-8-directions-champs.txt`.

Lougaroc prépare une attaque Roche puis des éclats successifs convergent et se dispersent sur la cible. La nouvelle animation d'impact comporte 64 images, avec fragments de pierre et ressources Roche natives. Il s'agit d'un effet sur cible, et non d'une cinématique complète. Le rendu reste à valider par le joueur ; le journal de combat peut masquer une partie de l'effet.

## Banc isolé

Huit orientations : les huit cibles placées à deux cases sont touchées (270 → 221–225 PV), les témoins latéraux restent à 270 PV et chaque charge est consommée. Les quatre Champs électrique, herbu, brumeux et psychique ont chacun été absents après le lancement. Les fichiers originaux de la copie de test ont été restaurés et comparés.

## Limites

Le retrait est limité aux quatre identifiants testés ; météo et autres statuts, protection et échec ne sont pas vérifiés. La portée de deux cases est celle du banc ; seule la forme Diurne a été essayée. Alliés, murs, bords et immunités ne sont pas couverts. Ce prototype scripté n'intègre ni cristal ni menu Z ni restrictions d'utilisation et n'a pas été poussé dans le dépôt.

Sources : `preparer-roches-lames-v2-pmd.py`, `banc-roches-lames-v2-pmd.py`, `roches-lames-effets.lua` et `test-roches-lames.lua` dans `~/Capacites-Z/Sources/`.
