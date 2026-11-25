# Cliff de guilde — bordures latérales et courbe avant

## Ce qui a changé

- La bordure extérieure suit maintenant les côtés et le haut de la silhouette du plateau. Elle utilise les pixels du rendu jour et le masque de lisière de l'ancien Grand Cap Métano. Les fragments de 8 × 8 px sont sélectionnés selon le voisinage du contour, sans miroir ni redimensionnement.
- Les deux portions quasi verticales des côtés utilisent des retours extraits des calques Base et Cliffs de Réverie (modules 16 × 16 px à l'échelle d'origine). Ces extraits incluent un peu d'herbe autour du relief ; ils sont coupés au contour du plateau.
- Le raccord herbe/falaise de l'avant a été réadapté avec la lisière du nord de Réverie. Pour arrondir très légèrement ses angles, 86 pixels du masque du plateau ont changé, avec une variation verticale maximale de 3 px : l'emprise générale et l'axe de l'escalier sont conservés. La paroi et l'escalier sont identiques aux calques précédents (test des octets RGBA).
- Les six calques et l'image recomposée sont fournis en 480 × 416 px, import cible 8 px. Une sauvegarde des précédents est dans `sauvegarde/`. `placements.json` documente les sélections des fragments de bordure ; `verifications.json` contient les comptages.

## Aperçus

Les vues jour, crépuscule et nuit réutilisent les fonds précédents avec la nouvelle falaise ; APNG 480 × 520, 120 phases. Le test compare la première image et la phase théorique de retour avant encodage : elles sont identiques pour les trois modes. Le jour est adapté de T00P04A, le crépuscule assemble deux fonds EoS authentiques sans preuve que c'est le ciel exact de l'extérieur de la guilde, et la nuit conserve le ciel de la zone Réveil. La mer nocturne exacte de Sharpedo n'a pas été identifiée avec certitude.

## Limites et suite

Le test « contour à moins de 2 pixels d'une bordure » couvre 689/689 pixels du contour concerné mais **ne prouve pas la qualité des raccords**, notamment aux changements de pente. Les fragments choisis et leurs découpes, les colonnes de paroi répétitives et la teinte de nuit doivent encore être contrôlés dans PMDO Dev, à l'échelle native, avant de considérer ce terrain comme un tileset prêt à importer. Aucune carte ni sauvegarde de jeu n'a été modifiée ; collisions, liaisons et animations en moteur non testées.

Le grand QG de guilde, organique et dans le style PMD, est prévu pour la prochaine étape. Aucun bâtiment n'a été dessiné ou installé dans ce lot afin de garder le plateau libre.
