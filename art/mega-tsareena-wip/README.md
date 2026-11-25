# Méga-Sucreine — travail en cours exclusif à Destiny

**Brouillon artistique et technique, non jouable et non intégré. Ne pas importer ni distribuer comme une forme terminée.** Ce dossier est hors des ressources chargées par le jeu. Il ne modifie ni la forme Sucreine normale, ni les données runtime, ni la release.

## Contenu

- `references/` : deux modèles avant approuvés et crédits de la référence d'animation.
- `marche/` : essai de marche 8 directions × 4 images, 32 × 56 pixels par cellule pour la taille native ; palette expérimentale de 15 couleurs. XML partiel à titre de repère uniquement.
- `brouillon-forme/` : proposition de forme séparée temporaire et non publiée à partir des données de Sucreine ; toutes les caractéristiques et capacités copiées sont des **valeurs provisoires**, pas une conception d'équilibrage. Ce JSON n'est pas dans `base/Data` et n'est pas chargé par le jeu.
- `apercu-marche.html` : aperçu autonome sur une carte simulée avec atelier, ce n'est pas PMDO.

## À terminer avant intégration

Six vues sont provisoires, le mouvement des bras est partiel et la marche n'est pas validée. Il manque les offsets et les ombres adaptés, le repos, l'attaque et toutes les autres animations, la transformation, les choix de caractéristiques et l'intégration du sprite. Tester l'import et toutes les animations dans PMDO ; ne pas remplacer Sucreine normale. Les durées de marche de la référence sont 8/10/8/10 ticks.

La structure de la forme reste à adapter à l'état du dépôt au moment de l'intégration ; aucun système de transformation n'est implémenté. La version de référence des données utilisée pour le brouillon vient du commit `57105372209587ee2805327170bc116c335545f9`, et doit être revérifiée avant utilisation.

Référence d'animation : [Tsareena, SpriteCollab](https://github.com/PMDCollab/SpriteCollab/tree/master/sprite/0763), attribution et conditions dans `references/credits-spritecollab.txt`. Le personnage Méga est une création non officielle, propre au projet Destiny.

Attribution de la référence Tsareena SpriteCollab : **baronessfaron / PMDCollab_1**, selon les crédits du projet. Ressources SpriteCollab sous licence [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/). Les modèles Méga et essais du présent dossier ne sont pas des ressources officielles de Pokémon.
