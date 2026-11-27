# Giga-Tonnerre — prototype en banc

La vidéo `Pikachu-Giga-Tonnerre-8-directions-son.mp4` montre le test sonore dans la copie isolée de Destiny. L’animation s’inspire de la référence USUL : charge dans une sphère électrique, éclairs multicolores et impact lumineux sur la cible. Ce n’est pas une reproduction complète de la cinématique officielle : le Pokémon ne monte pas réellement dans la sphère et la transition vers la cible est simplifiée. Les éclairs et impacts utilisent des images générées puis recomposées en banques PMDO.

## Pikachu à casquette : approximation de banc

La copie ne possède pas la forme officielle Pikachu à Casquette. Pour cette démonstration uniquement, une petite casquette rouge a été dessinée sur les cinq poses statiques du sprite natif de Pikachu, réutilisées en miroir pour couvrir huit orientations. Ce n’est **pas une forme ajoutée au jeu** : les autres animations ne sont pas équipées, et ce dessin n’est pas un sprite officiel. Le fichier `.chara` modifié sert exclusivement au banc. Le sprite d’origine a été restauré dans la copie après capture.

## Résultats et limites

- Placement et activation scriptés ; huit orientations, une cible à deux cases et un témoin latéral par orientation.
- 8/8 cibles touchées ; 8/8 témoins intacts ; PP 1 → 0 à chaque essai. Voir `journal-8-directions.txt`.
- Fiche spéciale Électrik de puissance 195, comme la référence ; portée 3 et PP de banc provisoires. L’équilibrage PMDO n’est pas validé.
- Le bonus officiel de taux de critique (+2) n’est pas implémenté ni testé. Les conditions Pikachu à Casquette, Tonnerre et Pikachazélite ne sont pas contrôlées ; pas de conversion Z, menu ni règle de limitation complète. Murs, alliés, autres distances et interruptions non testés.
- La fiche, les scripts, les sauvegardes et le sprite de la copie ont été restaurés ; les banques temporaires en ont été retirées. Le prototype n’est pas installé comme capacité jouable.

Sources de travail : `Capacites-Z/Sources/preparer-giga-tonnerre.py`, `giga-tonnerre-charge.lua`, `test-giga-tonnerre.lua` et `intro-halo-banc-pikachu.lua`. Référence : https://www.pokepedia.fr/Giga-Tonnerre.
