# Lost Wood : départ, leçons et statue Kangourex

## Départ, sommeil du héros et musique

Le quiz termine sa musique en fondu avant le passage au noir, puis bascule sur
`zrv2_zone_reveil_nuit` pour une brève scène où le héros endormi murmure ses
questions confuses (« … Où suis-je… ? », « Qui suis-je… ? », « Tout me semble
si flou… », « J'ai sommeil… ») avant un fondu au noir vers `cliffdaytest_nuit`.
Dans cette scène nocturne, le partenaire sort de la porte de sa maison, suit le
chemin vers l'est sans s'arrêter devant le croisement, hésite devant l'entrée
orientale de Lost Wood puis s'y engage seul. La cinématique ne joue pas la
musique de Lost Wood. La piste `Content/Music/Tiny Woods.ogg` est sélectionnée
à l'entrée dans le donjon et sur chacun de ses sept étages. Elle comporte des
métadonnées de boucle (`LOOPSTART=176400`, `LOOPLENGTH=1882031`, en échantillons
à 44,1 kHz).

Le tracé utilise les marqueurs de la carte existante ; aucune carte n'a été
recréée. Le calque de premier plan temporairement déplacé pour rendre le
personnage visible est restauré avant la suite. Le halo de l'introduction
n'est pas modifié : l'aperçu historique attend encore confirmation.

## Leçons neutres dans le donjon (aller solo et retour inverse)

Chaque étage de `Data/Zone/lost_wood.json` possède un `MapEffectStep` dont
`OnMapStarts` appelle `SINGLE_CHAR_SCRIPT.DestinyLostWoodLesson`. Ces encadrés
système neutres (sans nom ni portrait de personnage, `UI:ResetSpeaker()` +
`Fanfare/Note`, avec affichage dynamique des touches via `STRINGS:LocalKeyString`)
sont présentés directement au joueur :
- **Aller solo (`1F -> 7F`)** : tour par tour et attaque directe, capacités et
  gain d'expérience, sac d'objets, estomac, course/orientation/diagonales,
  altérations d'état et repli, puis dernière vérification avant la sortie.
- **Retour en duo en sens inverse (`7F -> 1F`)** : escaliers montants inversés
  (`stairs_back_up`, `SegLoc(0, -1)`), PV des coéquipiers, expérience partagée
  et montée de niveau, menu des tactiques, échange de place / poussée d'allié,
  Mode Équipe, journal / mini-carte / état de l'équipe, puis options du jeu.

`SV.Destiny.LostWoodLessonsSeen` enregistre chaque leçon après sa dernière
page (`'1'..'7'` à l'aller, `'retour_7'..'retour_1'` au retour) : si elle est
interrompue avant, elle peut être revue. `LostWoodTutorialDone` et
`LostWoodReturnTutorialDone` indiquent la fin respective des deux séries.

Le principe étage par étage est inspiré du tutoriel du projet de Palikadude,
étudié au commit `da6c2130d641507447e6386a5e47a296e8cb4c71` :
[`Data/Zone/beginner_lesson.json` et son script d'événement](https://github.com/Palikadude/%48alcyon/tree/da6c2130d641507447e6386a5e47a296e8cb4c71/Data).
Les formulations françaises de Destiny sont originales ; aucun texte anglais
n'est présenté comme une traduction officielle ou comme du contenu libre.

## Poser une statue Kangourex

Dans l'éditeur Ground de la quête Destiny, ajouter une entité de type **Object**
et choisir `Statue_Kangourex` dans les objets. Le `.dir` natif est livré dans
`Content/Object/`. Placer la statue dans un endroit accessible, puis enregistrer
la carte. Aucun script de carte ni déclencheur à configurer n'est nécessaire :
le service de la quête convertit automatiquement le déclencheur « Aucun » en
« Action » au chargement et raccorde le menu de stockage PMDO.

En jeu, se placer devant la statue et interagir : les menus permettent de
déposer, de tout déposer, de reprendre les objets et de gérer l'argent. Le
stockage appartient à l'équipe et reste celui de la sauvegarde PMDO, partagé
avec les autres accès au stockage. Un callback d'objet préexistant est conservé
et exécuté avant l'ouverture du stockage. La carte doit être chargée dans la
quête Destiny pour que le service soit actif ; le fichier visuel seul, hors
quête, ne suffit pas.

## Provenance et droits

- **Tiny Woods** : piste originale de *Pokémon Mystery Dungeon: Blue Rescue
  Team*, obtenue depuis la [bande-son archivée](https://archive.org/details/pmd-blue-rescue-team-original-soundtrack),
  fichier `07. Tiny Woods.flac` ; métadonnées de l'archive : Arata Iiyoshi.
  La bande-son du jeu est créditée à Arata Iiyoshi et Atsuhiro Ishizuna. Le
  fichier FLAC a été converti en Vorbis sans vidéo, puis des points de boucle
  ont été ajoutés. Œuvre commerciale Pokémon/Chunsoft ; **aucune licence libre
  ni autorisation de redistribution publique n'a été établie**. Vérifier les
  droits avant toute diffusion hors du projet privé.
- **Statue** : sprite 32 × 32 [Kangaskhan Rock](https://archives.bulbagarden.net/wiki/File:Kangaskhan_Rock.png),
  repris sans redessin et encapsulé dans le format d'objet PMDO. Il provient
  d'une œuvre Pokémon ; la mention d'usage équitable sur le site source ne
  constitue pas une licence libre ou une autorisation de redistribution.

## Vérifications

- `python3 tools/tests/test_lostwood_tutoriel.py` vérifie les sept raccordements
  de zone, les points de boucle et le conteneur de la statue.
- `lua tools/tests/test_lostwood_lecons_statue.lua` simule les leçons, leur
  reprise, le retour et l'installation des callbacks de statue.
- Des essais Linux PMDO 0.8.12 ont vérifié le tracé nocturne et le silence de
  la scène, l'ouverture automatique de la statue ainsi qu'un dépôt et un retrait.
  L'accès aux étages a été forcé pour vérifier leurs leçons ; cela ne certifie
  pas un parcours intégral normal. La sortie audio du banc était factice : la
  sélection du titre est contrôlée, mais l'écoute et la boucle doivent encore
  être vérifiées sur une machine avec son. L'exécution Windows reste à vérifier.
