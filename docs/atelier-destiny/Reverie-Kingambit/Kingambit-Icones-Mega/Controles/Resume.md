# Contrôles — icônes de Réverie

Banc PMDO Linux **0.8.12.0** ; profil et carte d’essai isolés. Les captures montrent les menus natifs du moteur, pas une reconstitution. La comparaison porte sur tous les pixels opaques de chaque émoticône. Pour chaque objet, le moteur a aussi chargé le `.dir` nommé dans sa fiche et confirmé ses dimensions et sa trame.

| Scénario | Banque sélectionnée | Résultat |
| --- | --- | --- |
| Destiny + addon, français | Addon / `text.font` | 48 objets Méga + 6 baies, 7 pages du sac ; 54 descriptions FR conformes |
| Destiny + addon, anglais | Addon / `text.font` | 54 textes d’origine retrouvés, glyphes inchangés |
| Destiny + addon, chinois simplifié | Addon / `text.zh-hans.font` | 48 objets Méga + 6 baies, contrôle initial des glyphes |
| Addon seul, français | Addon / `text.font` | 48 objets Méga, 6 pages du sac ; les fiches de baies stock restent inchangées |
| Destiny seul, français | Destiny / `text.font` | 6 baies dans le sac ; icône Pêcha reconnue aussi dans « Reçu : … » |
| Destiny seul, chinois simplifié | Destiny / `text.zh-hans.font` | 6 baies dans le sac |

**Récompense Pêcha :** test du script de production du foyer avec « Un trou » sélectionné au clavier, sans addon. Le sac passe de 0 à 1 baie ; un second échange ne redonne rien. Le dessin de la récompense est identique au glyphe du sac.

**Régression :** 5 tests Lua Kingambit réussis. Les index gardent leurs autres entrées, et les fiches gardent les effets et les statuts de disponibilité d’origine. Aucun changement de carte, de script jouable ou de transformation Méga dans ce lot.

Ces contrôles ne constituent pas un build Windows complet ni un test de chaque transformation depuis le début du jeu.
