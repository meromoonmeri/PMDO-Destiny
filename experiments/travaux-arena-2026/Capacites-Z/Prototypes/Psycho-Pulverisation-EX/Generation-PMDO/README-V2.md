# Psycho-Pulvérisation EX — V2 : distorsion visuelle

La capture `Gardevoir-Psycho-Pulverisation-EX-V2-distorsion-son.mp4` montre le prototype en donjon. La V1 est conservée séparément.

Chaque cible est entourée d'un maillage semi-transparent et d'ondulations qui se tordent et se contractent, avant un éclatement rose et violet. C'est une **illusion animée superposée**, pas une déformation des pixels du terrain ou du personnage par shader ; le dessin est ancré à la cible. Un voile de fragments et une aura de concentration accompagnent l'effet. Les impacts sont traités successivement par le moteur.

Banc scripté huit orientations : 24/24 cibles touchées, 8/8 témoins hors zone intacts, PP 1 → 0 ; voir `journal-v2-8-directions.txt`. Zone Full rayon 2, puissance 85 spéciale et PP provisoires ; alliés, immunités, obstacles et autres situations non testés. Cristal, menu, conversion et règles Z non intégrés. Les fichiers temporaires de la copie PMDO ont été restaurés/retirés après la capture.

Sources : `preparer-psycho-pulverisation-v2.py`, `psycho-ex-v2-concentration.lua`, `test-psycho-pulverisation-v2.lua`, dans `Capacites-Z/Sources`.
