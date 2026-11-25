# Audit des cinématiques — préparation 0.4.2

Date : 4 novembre 2026.

Cet audit relit les scènes principales de Destiny avec la même grille que le
helper `game/Data/Script/destiny/cinematique.lua` :

- locuteur et portrait explicites pour chaque réplique ;
- portrait du partenaire à droite lorsqu'il s'adresse au héros ;
- personnages tournés vers leur interlocuteur pour dialoguer ;
- regard dans la direction ou vers le lieu montré ;
- une seule source sonore pour une réaction de groupe ;
- rotations à la vitesse 4, avec de courtes désynchronisations ;
- respirations de 10, 20 ou 30 frames selon le moment ;
- coroutines rejointes avant le dialogue suivant ;
- caméra et contrôle rendus au joueur en fin de scène.

## Résultats par scène

### Test de personnalité

La scène est une voix et des choix, sans acteur visible à orienter. Aucune
ambiguïté de locuteur n'a été relevée.

### Réveil et Champs des Rêves

La scène principale distingue déjà les pensées du héros (portrait standard)
des répliques du partenaire (portrait de droite), et ses gestes sont à la
vitesse 4.

Deux reprises ont été corrigées :

- avant de proposer de repartir dans les Bois Perdus, le duo regarde
  maintenant l'entrée au sud ; après le choix, les deux personnages se font
  face et le partenaire répond en portrait de droite ;
- après un retour manqué, le duo se fait face après l'ouverture sur la
  montagne, au lieu de dialoguer en regardant tous les deux vers le nord.

### Falaise de nuit — partenaire seul

Le locuteur est explicite. Dans la reprise après échec, le partenaire regarde
désormais vers l'est avant de dire que l'entrée se trouve à l'est.

La variante historique Dazzling de nuit, non requise par la scène active,
n'est pas réactivée ni réécrite.

### Falaise de jour — retour et Team Dazzling

La réplique « Ne me dis pas que… » appartient au partenaire. La réaction qui
la précède a été réordonnée pour que cette attribution soit lisible en jeu :

1. le partenaire réagit en premier avec « ! » et le son unique de la
   réaction ;
2. le héros répond par « ? » cinq frames plus tard ;
3. les deux se font face ;
4. le partenaire dit « Ne me dis pas que… ».

La Pose de la Team Dazzling a aussi été corrigée à la racine. Les vraies
frames existaient dans les `.chara`, mais sous la clé 13. Or 13 est seulement
l'`InternalIndex` SpriteCollab de ces sources ; le moteur cherche Pose sous
le FrameType global 50. Il retombait donc sur l'Idle pendant que les étoiles
jouaient. Les groupes Pose de Mawile (303), Lopunny (428) et Tsareena (763)
sont déplacés de la clé 13 vers la clé 50, en conservant
`InternalIndex = 13`, les huit directions et toutes les durées.

### Visite de Réverie Town

La visite ne passait pas encore par `destiny.cinematique` :

- les répliques du partenaire-guide utilisent le portrait de droite ;
- le duo se fait face à l'accueil et pour la conclusion ;
- les gestes du héros regardent le partenaire au lieu d'une direction codée
  en dur ;
- toutes les rotations passent à la vitesse 4 ;
- avant chaque lieu présenté, le duo regarde dans sa direction ;
- Kecleon et tatie Kangourex se tournent vers les visiteurs avant de parler.

## Contrôles effectués

- syntaxe Lua des quatre scripts de scène modifiés ;
- audit statique des vitesses de rotation sur les cinq scènes principales :
  aucune rotation autre que 4 après correction ;
- ordre partenaire « ! » → héros « ? » → réplique du partenaire ;
- lecture des trois conteneurs `.chara` : groupe 50 présent, huit
  séquences, `InternalIndex = 13`, durées attendues ;
- positions des payloads dans les `.chara` inchangées, donc index toujours
  cohérent.

Ces contrôles ne remplacent pas un visionnage complet dans PMDO sous
Windows ; ils établissent la cohérence des scripts et des données livrées.
