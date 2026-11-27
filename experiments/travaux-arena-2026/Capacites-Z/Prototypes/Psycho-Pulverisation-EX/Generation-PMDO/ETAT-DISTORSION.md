# Distorsion demandée — non réalisée

L'utilisateur a rejeté la V2 à quadrillage. L'effet souhaité est une véritable déformation sans lignes ni symbole, visible sur le Pokémon et l'espace alentour. L'ancienne V2 reste une archive mais n'est pas la solution.

Le rendu courant de PMDO/RogueEssence dessine le donjon dans `BaseDungeonScene.DrawGame`, avec `gameScreen` comme cible de rendu et un `SpriteBatch` sans effet de réfraction local. Les animations et particules examinées superposent des images ; elles ne déplacent pas les pixels du décor ou des personnages sous elles. Produire la distorsion demandée nécessite un traitement du rendu existant autour de chaque cible (par exemple lecture de la cible de rendu et déformation locale, ou shader de réfraction), puis des tests ; ce travail n'a pas été implémenté ni validé. Ne pas présenter un autre overlay dessiné comme une distorsion réelle.
