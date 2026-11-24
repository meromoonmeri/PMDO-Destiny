# Destiny — 100 objets PMU / Halcyon et lianes de Reverie

## La planche transparente

**`Tilesheet-PMU-Halcyon-100.png`** : 1 920 × 1 280 px, 10 × 10 cases de 192 × 128 px, à l’échelle 1× du jeu (la tuile logique fait 8 px). Les objets sont centrés dans leurs cases et n’empiètent pas les uns sur les autres. La transparence est conservée jusque dans les détails des silhouettes.

- **20 modèles PMU** conservés à leur taille native : tables, banc, sièges, couchages, rangements, objets de cuisine et ornements.
- **5 grands tapis inspirés de Halcyon**, réalisés avec le générateur d’image, détourés et ramenés à l’échelle pixel du jeu : salon, passage, médaillon, tresse et missions.
- **4 palettes pour chaque modèle** : **Chêne & miel**, **Noyer & grenat**, **Châtaigne & sauge**, **Bois fumé & ardoise**. Chaque bloc 2 × 2 suit cet ordre : miel / grenat en haut, sauge / ardoise en bas.

`PNG/` dans le ZIP contient les **100 sprites détourés individuellement**. Les fichiers `Index-100.json` et `Index-100.csv` associent chaque sprite à sa case et à son rectangle exact dans la planche. Les coordonnées commencent en haut à gauche et les rectangles sont `[x, y, largeur, hauteur]` en pixels. L’index JSON comprend aussi des ancres indicatives, les dimensions sources, les rampes de couleur et les empreintes SHA-256.

## Dans les 15 salles

Ouvre **`Guilde-Destiny-Lianes-et-PMU-100.html`** dans ton navigateur. Il fonctionne hors ligne. Sur **Les 15 salles**, sélectionne **Nuit** pour voir les bourgeons allumés et la lumière chaude qu’ils projettent sur le bois. **Lianes : avec / sans** permet de retrouver à tout moment les plans sans végétation. Jour, Aube, Crépuscule et Nuit conservent les couleurs de Grodoudou comme base. Les **29 passages** restent dégagés et les **7 cadres sud** conservent le cadrage sans rallonge.

Dans **Aménager**, les 100 variantes sont disponibles par palette et catégorie. Rien n’est posé d’avance. Le sélecteur **Collection** permet de retrouver les 33 objets d’origine. Utilise **Exporter → Image de la salle** pour une vue PNG ou **Plan de l’atelier** pour conserver et reprendre ton placement dans ce nouvel aperçu. La sauvegarde automatique de cet aperçu est distincte de celle de l’atlas précédent.

## Calques de lianes

Les quatre motifs de lianes sont des créations du générateur d’image inspirées des boiseries de **Reverie Normal Home** et du **Reverie Inn**. Les trajets sont ajustés à la corniche, aux poteaux et aux rives de chaque salle ; ils ne réutilisent pas l’ancienne verdure. `Lianes-par-salle/` donne les calques en PNG transparents à la taille exacte des 15 plans. Pour les recomposer manuellement :

1. Poser `Lianes.png` sur le plan natif. L’aperçu applique à ce calque la palette de l’heure choisie.
2. **De nuit seulement**, superposer `Lumiere-Nuit-Ecran.png` en mode de fusion **Écran** à 100 %.
3. Toujours de nuit, ajouter `Bourgeons-Nuit.png` en mode **Normal** au-dessus des halos.

`Index-lianes.json` donne les trajets et les points lumineux. Les halos éclairent le décor au-delà du contour des sprites. Il ne s’agit pas d’une simple recoloration des fleurs.

**C’est un kit graphique et un aperçu d’atelier, pas un installateur.** Rien n’a été modifié dans le jeu ni dans l’atlas sans verdure. L’export natif de l’aperçu reste limité aux objets d’origine et n’inclut pas les nouvelles lianes, les lumières ou les 100 variantes.

### Provenance

Silhouettes : banque PMU de la guilde Destiny 0.7.7, dérivée des banques graphiques historiques PMU-Client. Les références précises aux fichiers source sont dans l’index. Tapis et motifs des lianes : créations originales de cette série avec le générateur d’image ; Halcyon et Reverie servent de références visuelles.
