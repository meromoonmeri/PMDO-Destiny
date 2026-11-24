# Destiny — Bourgeons, lumière PMD

Le premier panneau de l’aperçu montre aussi **le seuil de l’Accueil**, avec le halo fixe de `G01P02A` et le tapis PMU adaptés. Cet habillage est indépendant de la lumière des bourgeons ; le détail est dans [`Accueil-PMD/Lisez-moi.md`](../Accueil-PMD/Lisez-moi.md).

Dans **`Guilde-Destiny-Bourgeons-PMD.html`**, clique sur **Visiter de nuit** au-dessus des cartes pour entrer au Carrefour. Suis ensuite les boutons de passage : l’ambiance Nuit et les reflets restent actifs de salle en salle. Si le navigateur préfère les mouvements réduits, la lueur reste visible mais fixe. Clique sur **Animations : en pause** pour relancer la variation.

**Lire la vidéo** montre la falaise d’origine à gauche et le Grand Salon de Destiny à droite. À 4 s, un gros plan montre le calage des lianes et la ronce au pied du poteau ouest. **Voir les lianes ajustées dans le Grand Salon** ouvre directement cette salle en Nuit.

## Verdure ajustée

Les cartes portant la mention **Verdure ajustée** signalent les 11 salles reprises sur les poteaux. Quinze enroulements ont été recentrés sur le fût ; les lianes passent derrière les anneaux et les chapiteaux restent lisibles. Les six petits rameaux de ronce sont cantonnés à quelques pieds de poteau, notamment au Salon et dans les couloirs. Ils ne sont pas lumineux. Voir `Verdure/Index-ajustements.json`.

Les **rives courbes** des 15 salles ont aussi été contrôlées. 27 lianes de rive ont été recalées sur la lèvre du bois, dont les deux côtés du Bureau du maître, du Carrefour, des quatre dortoirs et de la Chambre du héros. Les enroulements des poteaux, les ronces et les points lumineux existants sont conservés. Les feuilles peuvent dépasser la tige, mais ni les seuils ni le vitrage ni le fond ne reçoivent de verdure. Le plan large du Salon dans la vidéo reprend les nouvelles rives. Voir `Verdure/Index-raccords.json` et `Verdure/Verification-raccords.json`.

En haut de l’aperçu, **Lever la grille** montre le retrait ombré de l’escalier nord de l’Accueil. Les marches basses et le bois de l’arche restent intacts. Pour reconstruire les raccords depuis une version avec la grille et le seuil déjà montés, utiliser `python Bourgeons-PMD/Sources/Assembler-raccords.py --source /chemin/vers/avant-raccords.html` depuis le dossier de la guilde.

## La référence exacte

C’est l’entrée extérieure de la guilde de Grodoudou au sommet de la falaise, **[G01P01C](https://projectpokemon.org/home/gallery/image/77577-g01p01cpng/)**, la nuit dans *Explorateurs du Ciel*. L’APNG d’origine, extrait par MegaMinerd et publié par evandixon sur Project Pokémon, comporte quatre images d’environ 167 ms chacune. Les flammes et certains pixels des pierres et de la façade changent ; les zones témoins du ciel et du chemin éloigné restent fixes. Voir `Releve-Falaise.json` et la boucle originale dans **Référence Grodoudou**.

## Adaptation dans la guilde

Les **bourgeons de Destiny**, et non des braseros, éclairent les poteaux et les premières planches. Les 30 points d’origine sont conservés ; un bourgeon s’ajoute sur chacune des deux ronces enroulées aux montants du passage nord du Carrefour. Elles ne débordent pas sur le passage. La texture de diffusion générée est projetée de la végétation vers le bois, à faible opacité (21 % au maximum pour les reflets). Les quatre images suivent la cadence de la référence de Grodoudou ; le feuillage atténue le reflet par endroits. La lueur ne s’active qu’en Nuit et se masque avec les lianes.

Le **fond hors du décor** reprend les bleus des cartes de Grodoudou. En Jour : `#1f1f3f` pour l’Accueil (`G01P02A`), `#17173f` pour les autres salles. En Nuit : `#0f0f2f` pour les salles communes et `#07071f` pour les dortoirs et la Chambre du héros, d’après leurs cartes de référence. Les deux ambiances intermédiaires interpolent ces teintes. Les fonds sont appliqués par masque, pas en recolorant le bois ni les vitres.

L’option **Ornements : sans/avec** montre, séparément, des frises en bois et des écussons peu saillants qui épousent les courbes de plusieurs murs. Ils n’émettent aucune lumière et ne sont pas ajoutés aux objets de l’atelier. Les plans, les passages, la grille, le tapis et le halo du seuil sud ainsi que les étoffes restent en place. Les fichiers du jeu ne sont pas modifiés.

Pour reconstruire cette étape depuis l’aperçu des raccords de rives, utiliser `python Bourgeons-PMD/Sources/Assembler-balade.py --source /chemin/vers/avant-balade.html`. Les prélèvements, ancrages et mesures sont dans `Verdure/Index-balade-nuit.json` ; le contrôle navigateur est dans `Verdure/Verification-balade-nuit.json`.
