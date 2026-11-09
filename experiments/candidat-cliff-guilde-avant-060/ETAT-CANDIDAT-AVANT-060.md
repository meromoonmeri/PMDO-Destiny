# État Cliff guilde avant v0.6.0

La carte Cliff guilde n'est pas disponible comme carte jouable raccordée à Réverie. Cette sauvegarde d'atelier ne constitue ni une mise à jour installable, ni une release v0.6.0.

## Éléments reconstruits et sauvegardés

- `candidat-isole/Data/Ground/guilde_cliff_essai_jour.rsground` : candidat Ground 480 × 520, guilde fermée, décor fixe de jour.
- `candidat-isole/Content/Tile/Destiny_GuildeCliff_Essai_Jour_059.tile` : tileset autonome de ce candidat.
- Rapport `rapports/candidat-carte-essai.json` et scripts de reconstruction et vérification.

La vérification locale a recomposé 4 581 cellules identiques octet pour octet à l'aperçu ; une recherche statique donne 327 positions accessibles et atteint le seuil. Cela ne démontre ni le chargement dans PMDO ni une partie jouable.

## Travail indispensable avant une 0.6.0 jouable

Raccorder aller/retour à l'escalier nord de Réverie sans modifier le Carrefour ; intégrer et indexer les ressources dans le jeu ; régler et vérifier les collisions et le partenaire ; conserver scènes et sauvegardes ; intégrer les ambiances et animations nécessaires ; tester le trajet et la sauvegarde dans le moteur puis vérifier le build Windows et la CI. Le candidat ne doit pas être installé en l'état.

Le dernier jeu publié est la prérelease v0.5.8, qui n'intègre pas la nouvelle carte Cliff. Aucune v0.6.0 ni v6.0 n'a été créée ici.
