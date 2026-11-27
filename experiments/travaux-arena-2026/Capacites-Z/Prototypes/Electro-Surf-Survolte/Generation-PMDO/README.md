# Électro-Surf Survolté — prototype en banc

La vidéo `Raichu-Alola-Electro-Surf-Survolte-8-directions-son.mp4` montre le test dans la copie isolée de Destiny. Le porteur est bien la **forme 1 Raichu d’Alola** native du jeu. La référence USUL montre Raichu sur sa queue, une aura électrique, un surf aérien et une frappe dorée. L’adaptation PMDO utilise la pose native, une vague électrique, une ruée et une déflagration recomposées à partir d’images générées. Elle ne reproduit pas le décor céleste ni la chorégraphie complète ; la glissade reste très brève à l’écran.

## Résultats

- Huit orientations, placement et lancement scriptés ; une cible Ronflex à deux cases et un témoin latéral par orientation.
- **8/8 cibles touchées et paralysées**, **8/8 témoins indemnes et non paralysés** ; PP 1 → 0 dans chaque essai.
- Test supplémentaire sur Lainergie, type Électrik : PV 110 → 47 et pas de paralysie. C’est un cas testé, pas une validation exhaustive de toutes les immunités ou interactions.
- La paralysie utilise l’événement de statut natif PMDO, avec sa propre durée et ses règles. D’autres immunités et capacités ne sont pas validées.

## Mise en œuvre et limites

La fiche de banc conserve la catégorie spéciale et la puissance 175 présentes dans les données de départ. L’action utilise une `DashAction` de portée 3 avec retour au point de départ ; c’est une adaptation de banc, pas la mécanique officielle confirmée. La puissance et la portée n’ont pas été équilibrées pour PMDO. Les cases, collisions contre murs, alliés, cible immunisée aux dégâts et interruptions ne sont pas testés. Le caractère sans contact de la référence officielle n’est pas certifié avec cette action de ruée.

Pour rendre la phase de déplacement moins instantanée, les marqueurs de ruée et d’impact de l’animation native 5 de Raichu d’Alola ont été modifiés uniquement dans le fichier `.chara` de banc ; cela peut aussi affecter d’autres usages de cette animation tant qu’il est installé. La démonstration ne fournit pas une animation de surf en vol complète. La fiche et le sprite originaux, les scripts et sauvegardes de la copie ont été restaurés et comparés après l’essai ; banques temporaires retirées.

La restriction à Raichu d’Alola, Tonnerre et Aloraïzélite, la conversion Z, le menu et la limitation Z complète ne sont pas intégrés : ce n’est pas une capacité jouable finale. Sources : `Capacites-Z/Sources/preparer-electro-surf.py`, `electro-surf-charge.lua`, `test-electro-surf.lua`, `intro-halo-banc-raichu-alola.lua` et `journal-8-directions.txt`. Référence : https://www.pokepedia.fr/%C3%89lectro-Surf_Survolt%C3%A9/G%C3%A9n%C3%A9ration_7.
