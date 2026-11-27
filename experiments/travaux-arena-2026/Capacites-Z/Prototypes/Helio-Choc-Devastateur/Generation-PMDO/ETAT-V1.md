# Hélio-Choc Dévastateur — V1 à valider

## Rendu

Solgaleo charge de l'énergie solaire et des éclats Acier, se rue sur l'adversaire, puis une brèche violette apparaît sur la cible avant l'impact solaire. L'animation combine trois banques : charge (64 images), brèche (54 images) et impact (56 images), avec des textures natives de Lance-Soleil, Luminocanon, Boutefeu et Poing Météore. `Solgaleo-Helio-Choc-V1-60ips-son.mp4` est une capture sonore du banc, encodée à 60 images/s.

C'est une adaptation : la brèche est un effet superposé, pas une véritable aspiration dans une autre carte ; Solgaleo reste sous forme de sprite et ne roule pas dans une sphère. Dans ce banc, la ruée précède visuellement la brèche. À valider avant toute intégration.

## Essais

Fiche de banc : Acier physique, puissance 200, une charge, cible unique, ruée jusqu'à deux cases. Huit orientations : huit Lapras passent de 270 à 230–234 PV, les huit témoins latéraux restent à 270 PV, charge consommée. Le drapeau de suspension est revenu à son état initial après chaque action.

Un contrôle séparé place Garde Mystik sur un Lapras : Griffe Acier ne lui retire aucun PV (270→270), tandis qu'Hélio-Choc le blesse (270→232) ; Garde Mystik est toujours présente et active après le coup. Journaux : `journal-v1-8-directions-talent.txt` et `journal-v1-controle-garde-mystik.txt`. Les copies isolées ont été restaurées et les originaux comparés.

## Limites importantes

Le contournement expérimental suspend temporairement **tous** les talents de la cible via un drapeau, puis le rétablit en fin d'action. Il n'est pas prêt pour le jeu : il faut gérer les talents non contournables, les interruptions, l'échec, les actions simultanées ou imbriquées, les K.O. et les effets à proximité sans laisser le talent suspendu. Seule Garde Mystik a été vérifiée. Protection, autres talents, immunités, alliés, murs, bords et autres cas ne sont pas testés. L'activation par Solgaleo ou Necrozma Crinière du Couchant, Choc Météore, Solgazélite et les menus Z ne sont pas intégrés. Aucun push effectué.

Sources : `~/Capacites-Z/Sources/{preparer-helio-v1.py,helio-v1-effets.lua,test-helio-v1.lua,test-helio-controle-talent.lua,banc-helio-v1.py,banc-helio-v1-controle.py,intro-halo-banc-solgaleo.lua}`.
