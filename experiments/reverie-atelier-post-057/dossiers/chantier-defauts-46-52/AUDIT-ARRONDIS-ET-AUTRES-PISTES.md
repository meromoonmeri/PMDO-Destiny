# Chemins, raccords et nouvelles pistes — audit local

Base v0.5.7 `ee39156a24f350b67e81740478be8505f4ff1a05`. Source Métano : carte de référence de Halcyon au commit `1522c7a8b7a34d70078e11ed605b21d563b0dc51`, rendu conservé dans `chantier-chemins-reverie/metano-reference-sol-falaises.png`.

## Reprise de la capture 51

La version antérieure, trop rectangulaire aux deux côtés du croisement, est remplacée : le chemin conserve toute la largeur de la marche et les deux retours d’herbe/sable utilisent des modules de carrefour Métano sans redimensionnement, rotation ou recoloration. La reprise part de la base d’origine, pas d’une carte déjà transformée. La rive 52 et ses quatre phases à 10 frames sont conservées dans la même reprise. Résultat : `reprise-arrondie-51-52/escalier51-avant-apres.png`.

Les dix cartes d’origine ont été comparées aux références ; 134 cellules `Base` et 46 cellules `Objects Over` ont reçu les ajouts, sans toucher aux autres cellules, données ou collisions. La banque de correction contient 269 images de 8×8. Un rendu indépendant des zones 51 et 52 sur `reverie_centre` est identique aux quatre phases attendues ; empreintes des dix sorties vérifiées. Aucun contrôle moteur ni jugement esthétique exhaustif : les très petites ruptures de texture en bordure et la qualité à l’échelle native doivent encore être inspectées en jeu.

## Pistes supplémentaires repérées

Recherche ciblée de contacts directs sable/herbe rectilignes d’au moins 10 pixels, hors objets : 6 segments regroupés en 5 sites sur le rendu initial. Ces critères ne repèrent pas toutes les coupures et peuvent signaler des motifs normaux ; ne pas faire de remplacement automatique. Visualisations `audit-nouveaux-candidats.png` et `audit-candidat-*.png`.

- **(1447, 599)** : raccord sous l’escalier, déjà signalé capture 51 et repris localement ici.
- **(279, 1176)** : bord coupé entre chemin et rivière, capture 48 déjà signalée. L’eau est animée ; la zone reste à reprendre sans masquer les séquences.
- **(151, 743)** : petite zone de terre à bord inférieur plat sous un arbre, non clairement reliée à une annotation antérieure. **Suspect à examiner**, pas défaut confirmé : peut être un motif de sol/ombre volontaire ou partiellement masqué par l’arbre.
- **(413, 583)** : ligne sous une porte ; semble correspondre au seuil du bâtiment plutôt qu’à une coupure à effacer. À vérifier en contexte.
- **(583, 2738)** : zone en partie masquée par un arbre ; résultat de recherche ambigu, à ne pas corriger sans isoler les couches.

La capture 27 comporte aussi des excroissances de sable sur les deux bords. Les essais de remplacement directs `prototype-chemin27-*` créent d’autres ruptures et sont **écartés**, pas appliqués. Les captures 27–29, 31, 33–39, 42, 44–50 et la zone restante de 30 restent à examiner ou corriger, avec l’ancien audit et les ressources PMU. Les résultats publiés précédemment sont conservés ; aucun push, nouvelle CI ni release n’a été fait pour cette reprise. Ne pas présenter le chantier comme terminé.
