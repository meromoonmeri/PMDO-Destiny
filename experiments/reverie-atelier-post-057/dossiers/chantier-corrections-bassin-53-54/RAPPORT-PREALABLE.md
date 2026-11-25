# Rapport préalable — bassin, captures 53–54

Base : branche Destiny `wip/reverie-integration-kingambit-cafe`, commit `ee39156a24f350b67e81740478be8505f4ff1a05` v0.5.7. Le payload jeu et Dev sont récupérés séparément et vérifiés contre les blobs Git. Une ancienne copie de `chantier-edition-couches/sources` n’est pas la dernière version et ne sera pas utilisée comme base d’écriture.

Captures 53–54 et audit précédent : troncs/ombres tronqués, ombres masquant des rebords de falaise, raccords haut de bassin, trait dans l’eau et chemins suspects. Les repères rouges identifient des régions ; il faut retrouver les couches réelles et les phases avant intervention. Un arbre masqué par un autre n’est pas forcément un arbre coupé.

Sauvegarde : conserver intacts les deux payloads originaux et leur SHA Git ; travailler sur des copies locales, avec un journal des cases modifiées et leur valeur précédente. Ne modifier ni collisions, ni entités, ni scripts, ni coordonnées du doyen, ni d’autres cartes. Préserver les phases animées et contrôler la correspondance des versions jeu/Dev. Vérifier les résultats sur toutes les phases disponibles ; l’absence de test moteur et d’ancienne sauvegarde devra être signalée.

Risques : une ombre ou un décor peut être intégrée dans une tuile composite, une suppression par rectangle peut effacer falaise, herbe, chemin, bâtiment ou animation. On ne supprime ni ne copie une zone sans examiner sa source et les couches et comparer avant/après. Les points 1G/1D/2/6/7 antérieurs restent à déterminer si la correction n’est pas démontrée sûre.
