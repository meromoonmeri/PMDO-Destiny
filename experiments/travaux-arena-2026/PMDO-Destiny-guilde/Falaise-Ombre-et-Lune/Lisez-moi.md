# La falaise de Destiny — ombre et lune

Retouche graphique de l’extérieur Cliff 0.7.7. Cette édition est séparée des livraisons précédentes et ne modifie ni jeu ni sauvegarde.

## Voir le résultat

- **Falaise-Destiny-Ombre-et-Lune.mp4** : vidéo de 21,2 s, Full HD, 30 i/s. Elle s’ouvre directement dans un lecteur vidéo ; aucun fichier HTML n’est nécessaire. Le MP4 est distribué séparément du ZIP.
- **Falaise-Destiny-Jour-Nuit.png** : les deux vues d’ensemble. Les fichiers `Plans/Cliff-*.png` restent à la taille native de 480 × 520 px.

| Temps | Vue |
| --- | --- |
| 0:00 | Falaise entière de nuit, braseros allumés |
| 0:05,2 | Avant / après, sous les marches |
| 0:10,7 | Falaise entière de jour |
| 0:15,3 | Lune et nuages au-dessus de la mer |

## Ce qui change

L’ancienne ombre finissait avec des pixels encore opaques sur sa dernière ligne, à `y=285` sous les marches. Le nouveau calque suit les pieds et les racines, se prolonge sur l’herbe et s’atténue sans bord de sprite visible. Le nettoyage des points verts est limité au plateau d’herbe. La lune est recentrée sur le repère de la capture à **(399, 117)**, à droite de la cime ; l’ancien disque et son halo ont été retirés du ciel. Deux nappes de nuages défilent derrière le feuillage, près de la cime et à l’horizon. Les trépieds et leurs quatre poses nocturnes, la lumière sur la façade, la mer en douze poses et les accès restent en place.

## Calques PNG

`Calques/{jour,aube,crepuscule,nuit}` contient le ciel fixe, les nuages de cime et d’horizon, l’ombre, le raccord d’herbe, le premier plan et les braseros. Les nuages font 576 × 152 px avec un débord de 48 px à gauche et à droite : recadrer `[48,0,528,152]` pour la position fixe, ou décaler cette fenêtre horizontalement pour animer. `nuit/Lune-et-halo.png` se pose entre le ciel fixe et les nuages. Le disque seul est également fourni en 32 × 32 px.

Pour recomposer une vue à partir de `Plans/Cliff-*-sans-braseros.png`, reprendre la pose de mer désirée dans `Mer-12-poses.png` (atlas de deux colonnes et six lignes, origine de la pose dans la carte `[0,152]`). Si le ciel doit bouger, recomposer ses 152 premières lignes : ciel fixe, lune et halo la nuit, nuages hauts, nuages bas, cime au premier plan. Poser enfin le calque de braseros choisi par-dessus le tout. La lumière nocturne est recalculée à partir du plateau corrigé : les anciens calques de lumière de la falaise ne sont pas interchangeables.

Les coordonnées, masques et vérifications sont dans `Releve-Cliff-R2.json` et `Verification.json`. Les scripts sont fournis pour le contexte d’atelier ; le rendu initial dépend des ressources Cliff 0.7.7 et de l’édition précédente disponibles dans l’espace de travail. Le MP4 et les PNG n’ont pas ces dépendances.
