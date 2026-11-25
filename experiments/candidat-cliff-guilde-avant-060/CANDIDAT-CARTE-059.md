# Carte de guilde — candidat isolé, non installable

Une première conversion réelle des pixels de la maquette en données Ground et tileset PMDO est préparée dans `candidat-isole/`. Elle ne remplace aucune carte du jeu. Identifiants autonomes `guilde_cliff_essai_jour` et `Destiny_GuildeCliff_Essai_Jour_059` ; Ground 480×520, grille 60×65 cases de 8 pixels, trois calques de terrain, QG et porte fermée.

Le QG est remonté à (128,120) pour laisser un passage devant les marches. La guilde est fermée dans le candidat. Test statique : les deux positions de départ 16×16 sont libres, la porte est atteignable depuis l'entrée et le parcours atteint les deux côtés de la pelouse. Recomposition de 4 581 cellules à partir de l'archive tileset vérifiée pixel par pixel contre l'aperçu hors moteur. Images et collisions : `rapports/apercu-candidat-jour.png`, `rapports/atteignabilite-candidat.png`.

**Limites bloquantes :** environnement fixe de jour uniquement, pas d'étoiles/nuages/mer animés, pas d'objet-porte piloté par interaction, aucun raccord à Réverie, aucun index ajouté, aucune entrée de zone ou script de transition, aucun test de chargement ou déplacement PMDO, aucun test partenaire, sauvegarde, Windows ou CI. Le pack n'est donc pas installable tel quel et n'est pas une v0.5.9 jouable. Les images du QG générées ne sont pas des ressources natives certifiées. Les collisions sont une approximation à examiner dans le moteur.

Reconstruction : `construire-carte-essai.py` (garde anti-écrasement), contrôles de recomposition : `tester-carte-essai.py`. Ces scripts utilisent les ressources et outils locaux mentionnés par leurs chemins et ne sont pas un installateur.
