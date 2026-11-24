# Destiny — Nuit vivante

Ouvre **`Guilde-Destiny-Nuit-Vivante.html`**. L’atelier est autonome et s’ouvre en **Nuit**, sur les 15 salles. Les **42 poteaux habillés** portent deux motifs de lianes générés dans l’esprit de Reverie et ajustés au plan de chaque salle. Les spires laissent apparaître le bois entre leurs tours. Les quatre ambiances de Grodoudou restent disponibles.

- **Nuit** : les bourgeons n’oscillent pas tous au même rythme. Quatre groupes par salle modulent doucement la lumière sur les boiseries et le sol. Deux projections de feuillage se fondent l’une dans l’autre pour faire varier les ombres, sans flash.
- **Animations : actives / en pause** fige ou relance les étoffes et les effets de Nuit. Avec le réglage système « réduire les animations », l’atelier démarre en pause.
- **Lianes : avec / sans** masque aussi leurs halos et leurs ombres. Les 15 plans nus, les 29 passages et les 7 cadrages sud restent identiques.
- **Aménager → Drapeaux et tentures** : les drapeaux sur hampe, les gonfanons et les guirlandes de fanions portent le badge **Animé**. Seules les étoffes bougent, de quelques pixels ; le bois et les attaches restent fixes. Les bannières murales, les tentures et les écus restent fixes. Rien n’est placé d’avance.

Les collections de 100 variantes PMU/Halcyon et de 33 objets d’origine restent accessibles. Tu peux ouvrir un plan JSON de l’atelier précédent. La sauvegarde automatique de cette édition est séparée. L’export **Image de la salle** saisit un instant fixe ; le JSON garde le placement.

## Fichiers du kit

`Etoffes-animees/` contient **12 variantes** (3 modèles × 4 palettes) en deux formats : APNG en boucle et planches de 16 images agencées en 4 × 4. `Index-etoffes.json` indique les rectangles, ancres et durées. Les frames restent dans la taille exacte de chaque sprite statique à l’échelle 1×, sans changement du point de placement.

`Lianes-de-poteaux/` contient les deux motifs transparents. `Calques-nuit/` donne, pour chaque salle, les lianes et les dix calques lumineux ou ombrés à la taille du plan natif. Applique les halos en mode **Écran**, les ombres en mode **Produit**, puis les cœurs des bourgeons en mode **Normal**, en modulant leur opacité. `Index-nuit-et-poteaux.json` donne les coordonnées, les cadences moyennes et les contrôles de géométrie.

`Extrait-Nuit-Vivante.mp4` montre le détail du Grand Salon et les trois animations textiles à part, sans placer de mobilier dans la salle.

**Aperçu et ressources graphiques, pas un installateur.** Les précédents atlas et planches ne sont pas modifiés. La lumière animée, les nouvelles lianes et les étoffes ne sont pas installées dans le jeu ; l’export natif reste réservé aux objets d’origine.
