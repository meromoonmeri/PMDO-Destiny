# Contrôle de reprise — marche en lévitation

## Références et verrouillage
- Modèle approuvé avant-droite : `../revision-corpulence/repos-trois-quart-01.png`, SHA-256 : bb569d6190170b4553aa46c79cedab3b7eaeeb647567b80727934e70333bebf4.
- Le fichier d’origine n’a pas été modifié ; deux copies expérimentales ont servi à l’essai.
- La marche de référence SpriteCollab utilise 4 images de 8, 10, 8 et 10 ticks (à 60 Hz) ; la lévitation est un choix demandé pour la Méga, pas une donnée de la source.
- Jambe 1 : 21212 pixels modifiés ; rectangle des modifications x=412–529, y=792–1073 ; pixels modifiés au-dessus de y=790 : 0.
- Jambe 2 : 18522 pixels modifiés ; rectangle des modifications x=531–649, y=792–1044 ; pixels modifiés au-dessus de y=790 : 0.

## Contrôle visuel
- Un fragment noir résiduel sous la première jambe a été effacé. Des raccords de couleur et de contour restent visibles.
- Les poses de jambes sont obtenues par compression verticale, non par une articulation fidèle : effet raide et proportions temporaires. Elles ne sont pas validées.
- Un essai de mouvement de bras a créé des contours flous et abîmé le bord de la robe. Il est écarté (`essai-bras-non-valide.png`) et ne figure pas dans la boucle.
- Bras fixes, aucune action finalisée, autres directions manquantes. L’aperçu ne représente pas un sprite PMDO intégrable.
- La vue de dos validée est absente ; pas de remplacement inventé.
