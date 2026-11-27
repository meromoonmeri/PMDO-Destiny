# Lame en Peine — V3 expérimentale

## Animation
Neuf gestes de Malvalame et neuf entailles individuelles apparaissent progressivement sur un quadrillage incliné en perspective. Les silhouettes sont des sprites 2D superposés : il ne s'agit ni de déplacements réels du personnage ni de géométrie 3D. La fin montre une fracture transparente en éclats de verre et six feux follets qui convergent vers la case du lanceur. Un crochet C# expérimental déforme les pixels du rendu autour de la cible en parallèle. La transition comporte un court intervalle où les lignes ont disparu avant l'apparition de la fracture ; l'effet et son rythme restent à valider visuellement.

## Banc
Lancement dans une copie isolée avec runtime patché PliSpatial, pas d'intégration définitive. Les huit directions ont été exécutées jusqu'à FIN OK. Pour chaque direction : un appel de l'animation et du pli, cible blessée (202 → 29 à 38 PV), témoin intact (202 → 202), lanceur soigné de la moitié des dégâts arrondie vers le bas (départ 1 PV), PP 10 → 9. Le journal contient les chiffres individuels. La capture montre la fracture ; les calculs de destination des feux utilisent la direction du lanceur. Le résultat visuel de la convergence dans toutes les directions et la qualité de la déformation restent à examiner en détail, ainsi que les performances, les immunités et interruptions. Les entailles sont visuelles : elles ne créent pas neuf frappes de dégâts indépendantes.

La fiche d'origine est non publiée et ne contient pas le soin ; celui-ci est ajouté uniquement pour le prototype. L'effet Lua précède la résolution du toucher, donc peut s'exécuter même en cas d'échec : cas non testé, à corriger pour une intégration. Le hook de rendu peut également déformer l'interface, dépend du rythme de rendu et doit être durci. Le banc a été restauré, originaux comparés et ajouts retirés.

## Vidéo
`Malvalame-Lame-en-Peine-V3-60ips-son.mp4` : 56 secondes, 640 × 480, H.264 à 60 images/s et audio AAC non silencieux. Capture du banc, pas de montage de simulation. Disponible également dans la galerie (identifiant `bitter_blade_base_v3`). Le téléchargement depuis le cadre d'aperçu reste non confirmé et peut être bloqué par son sandbox.
