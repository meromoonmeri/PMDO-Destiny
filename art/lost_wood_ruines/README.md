# Ruines, galets et sentiers de Lost Wood

Sources graphiques à l'échelle native : cases de 24 × 24 px sur fond transparent. Les six ruines et les galets sont issus d'images originales générées pour Destiny, inspirées de références de ruines et de rivière ; ce ne sont pas des dessins canoniques. La colonne brisée et les débris dérivent des mêmes créations ; les deux colonnes tombées sont en miroir. Les 16 raccords de sentier sont dessinés procéduralement, dans l'ordre du masque Nord, Est, Sud, Ouest (bits 1, 2, 4, 8).

Les équivalents `.tile` dans `game/Content/Tile` contiennent les cellules PMDO avec alpha prémultiplié. Les six fragments sous `game/Data/Map` utilisent ces feuilles et leurs propres collisions rectangulaires ; aucun des fragments de référence étudiés n'est redistribué. Les galets sont décoratifs sur l'eau ; les chemins au sol restent praticables.
