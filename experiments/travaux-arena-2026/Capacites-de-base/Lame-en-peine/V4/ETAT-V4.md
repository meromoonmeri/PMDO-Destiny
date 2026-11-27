# Lame en Peine — V4 expérimentale, à valider

## Reprise de l'enchaînement
Les neuf rémanences tracent chacune une coupe ; les mêmes lignes deviennent les contours de douze facettes qui se séparent et se fissurent. Les feux follets apparaissent pendant la rupture et rejoignent la case de Malvalame. Toute cette partie utilise une unique séquence de 80 images à huit directions, plutôt que deux effets séparés. Il n'y a plus de texture de verre ajoutée en remplacement du quadrillage. Les contours et silhouettes restent néanmoins des sprites 2D : la perspective est une illusion, pas une scène ou une animation 3D.

Un crochet C# expérimental prélève réellement les pixels du rendu en douze zones pour simuler leur réfraction, mais ne crée pas de géométrie 3D ni de véritables morceaux physiques ; ses coordonnées de facettes sont approximatives et ne suivent pas exactement les contours qui s'écartent. L'interface et les personnages peuvent aussi être réfractés. Un petit saut de forme reste possible à la transition entre lignes et facettes, en raison de l'épaisseur et de la double bordure des carreaux ; l'aspect verre, le volume et le rythme demandent encore l'appréciation de l'utilisateur.

## Vérifications
Banc dans une copie isolée, avec `PliSpatial` recompilé spécifiquement pour la V4 et moteur patché expérimental. Après correction d'une première planche trop large qui produisait un carré noir, la seconde capture montre bien les coupes, les facettes et la fin sans carré noir. Huit orientations : FIN OK ; cibles 202 → 29 à 45, témoins inchangés à 202, soin égal à la moitié des dégâts arrondie vers le bas et PP 10 → 9. Journal : `journal-v4.txt`. La convergence finale est calculée dans huit directions, mais son rendu exact dans toutes les situations n'a pas été contrôlé image par image. Le contrôle des sons est limité à la présence de signal audio dans la vidéo, pas à l'identification auditive de chaque effet.

Limitations : la fiche d'origine n'est pas publiée et ne contient pas le soin, ajouté seulement pour ce banc ; les coupes ne sont pas neuf impacts de dégâts indépendants ; l'animation précède la résolution du toucher et peut apparaître même en cas d'échec. Immunités, interruptions, durée variable liée aux images rendues, performance et interface restent à vérifier avant toute intégration. Copie de test restaurée après le banc, originaux comparés et ajouts retirés.

## Vidéo
`Malvalame-Lame-en-Peine-V4-60ips-son.mp4` : 49 s, 640 × 480, H.264 60 ips et AAC non silencieux. Galerie ID `bitter_blade_base_v4`. Le téléchargement depuis le cadre d'aperçu reste non confirmé et peut être bloqué par son sandbox.
