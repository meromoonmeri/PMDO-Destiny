# Lame en Peine V2 — lacérations spatiales

Prototype à valider, inspiré d'une chorégraphie de coupes fulgurantes : les feux follets sombres précèdent des rémanences de Malvalame qui apparaissent successivement autour de la cible. Dix entailles diagonales se croisent en quadrillage, puis l'énergie spatiale éclate et se dissipe. Les 96 images de l'impact comprennent de vraies poses du sprite PMDO de Malvalame.

Les déplacements multiples sont une **illusion visuelle** : ce sont des copies et rémanences 2D du sprite ; le lanceur ne se téléporte pas réellement. Les entailles et l'impact sont des effets superposés au décor, non une déformation réelle de ses pixels. Le quadrillage ne constitue pas plusieurs coups : la capacité conserve une seule attaque adjacente et le soin expérimental de la V1.

La capture `Malvalame-Lame-en-Peine-V2-60ips-son.mp4` est issue du banc en donjon, avec son et encodage à 60 images par seconde ; le nombre d'images de jeu réellement distinctes par seconde n'a pas été mesuré.

## Vérifications

Banc réussi dans huit directions : cible blessée et témoin latéral intact à chaque fois, PP 10 → 9. Malvalame commence à 1 PV : les huit soins correspondent à la moitié des dégâts arrondie vers le bas, par exemple 169 dégâts et 84 PV récupérés. Voir `journal-v2.txt`.

La fiche d'origine demeure non publiée et le prototype n'est installé que pour le banc ; les fichiers et sauvegardes de la copie isolée ont été restaurés et comparés. Immunités, talents, protections, interruptions, effets de soin particuliers et cas de bord restent à vérifier avant toute intégration. Les flammes spectrales sont visuelles et n'ajoutent pas de brûlure.
