# Cliff — quatre ambiances, ciel et mer animés

Quatre boucles de 480 × 520, **120 phases** chacune (16 s à 60 i/s, 83 ms par image). Ce sont exactement les images de l’aperçu.

| Ambiance | Contenu | Octets | SHA-256 |
|---|---|---:|---|
| Jour | ciel T00P04A, 5 nuages entiers, mer EoS 12 phases | 1469060 | `bbfbde0ec2f5d677838ed55ce0c0d056b6ec5dcc039147eefad456c8b764c12f` |
| Aube | adaptation de l’ancien agent (ciels jour et crépuscule mélangés) | 1144076 | `4d386d0497ce214e154ddc9f9f70f526ac0ca345703dd9ef52bc92aef8d564ff` |
| Crepuscule | ciel et nuages V02P01A, mer V22P01A, 9 étoiles natives animées | 932754 | `995aa9d76e4d6e25e65f3ef192af67fc75313c05b6ad797e75f65761b7899a1c` |
| Nuit | ciel Réveil, lune, 10 groupes d’étoiles natives scintillantes, mer EoS | 956484 | `4994635b78c8b9a460dbc239418e73c0e942983926c6fdb1e3641989d14bf968` |

## Portée

Ce sont des **aperçus animés autonomes**, pas des cartes PMDO. Aucun fichier de `game/` n’est modifié : ni `cliffdaytest`, ni `cliffdaytest_nuit`, ni aucune autre carte existante. Aucune collision, transition ni sauvegarde ici.

## Origine honnête des quatre

- **Jour** : ciel T00P04A et mer EoS natives ; cinq nuages entiers extraits de la référence.
- **Nuit** : ciel et lune de la zone Réveil (Destiny v0.5.7), dix groupes d’étoiles natives qui scintillent, mer EoS native, nuages PMD.
- **Crépuscule** : ciel et nuages EoS V02P01A, mer V22P01A, neuf étoiles natives animées. Le fond exact de la guilde n’est pas établi : c’est une adaptation de deux vrais fonds EoS.
- **Aube** : **adaptation** des ciels crépuscule et jour, aucune source canonique identifiée.

Détail complet dans `verifications-nuit.json` et `verifications-jour-crepuscule.json` de la chaîne de construction.
