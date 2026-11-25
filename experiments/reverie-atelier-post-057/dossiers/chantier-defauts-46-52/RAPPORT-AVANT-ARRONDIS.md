# Audit préalable — bords de sable arrondis

La reprise locale de l’escalier 51 a rétabli toute la largeur de la marche, mais présente encore des coupures rectangulaires de sable foncé aux jonctions avec le chemin horizontal. Elle n’a pas été publiée. Les deux zones entourées de la même capture constituent un cas précis à corriger.

Comparer les retours aux chemins natifs de Métano et utiliser des modules de bordure complets, sans interpolation ni rotation et sans changer la géographie, les falaises, les collisions ou les couches supérieures. Vérifier chaque point de jonction plutôt que juxtaposer deux rectangles sans contrôler leur contour. Les quatre phases de la rive 52 et leurs durées doivent rester intactes. Restaurer les cartes 0.5.7 originales vérifiées et reconstruire une nouvelle version cumulée, plutôt qu’appliquer le raccord à une carte déjà modifiée. Conserver et vérifier les sauvegardes des sources et les changements locaux avant d’aller plus loin.

L’audit d’autres raccords et captures continue : un échantillon corrigé ne prouve pas que tous les chemins de la ville sont homogènes. Le rendu hors moteur ne remplace pas une inspection en jeu. Les corrections de café sont suivies dans le chantier séparé `chantier-cafe-ecran-noir`.
