# Le gardien des vasques — validation locale

**Précombat : 1 min 22 s, de l’entrée dans la Fosse Cascade Fond au contrôle rendu dans l’arène.** La prise jouée mesure 81,80 s (81,93 s en temps logique). Les dialogues avancent à la confirmation : ce n’est pas une durée imposée au joueur. Le [MP4](Cinematique-Le-gardien-des-vasques.mp4) dure 1 min 26 s et montre également les premières secondes du duel.

| Dans la vidéo | Ce qu’on voit |
|---:|---|
| **00:05** | Nilo tremble déjà sur la terrasse. Il demande qui sont les deux Pokémon et parle de sa maman ; le partenaire présente l’équipe de secours. |
| **00:26** et **00:35** | Deux avertissements de `???`, sans portrait. Le duo cherche d’où vient la voix ; Nilo dit qu’il n’a rien touché. |
| **00:36–00:38** | Secousse, terre, Kabutops jaillit **devant et entre** les deux Pokémon. Le mouvement des faux les repousse avant que le gardien prenne sa place de combat. |
| **00:39–01:04** | Kabutops évoque les crues, les familles parties et les villages en aval. Il soupçonne Nilo à cause de sa présence près de la source ; la scène ne valide pas l’accusation. |
| **01:08–01:17** | Le héros regarde Kabutops, puis le partenaire : « Ce Pokémon est beaucoup trop en colère pour entendre raison... Nous n'avons pas le choix. » Le partenaire se retourne vers le boss, prêt à se battre. |
| **01:18–01:22** | Woosh natif complet, environ 3,15 s dans la prise. Raccord vers l’arène et `Boss Battle 2`, sans carton de titre. |

[Plans en jeu](Preuves/Plans-en-jeu.png) · [Tunnel image par image](Preuves/Tunnel-image-par-image.png) · [Repères audio](Preuves/Audio-et-rythme.txt)

## Nilo et les issues du duel

- Lixy est sur la terrasse, derrière et légèrement à droite de Kabutops. Il conserve sa pose native, animée, et oscille sur 4 px. Ni allié, ni monstre de donjon, ni obstacle : il ne prend pas de tour et n’est pas une cible. Le court message natif « Mode équipe activé » peut le recouvrir au tout premier instant de l’arène ; il ne gêne ensuite ni la lecture des coups ni celle du registre.
- [Extrait animé pendant les tours](Nilo-pendant-le-duel.webp) et [capture pendant Groz’Yeux](Preuves/Nilo-pendant-Groz-Yeux.png). Vérifié pendant six tours avec l’équilibrage normal ; cet essai s’arrête en arène, sans KO ni victoire.
- **Revanche et victoire :** une seule réplique d’introduction en revanche, woosh, puis vrai combat moteur. Un point de contrôle privé avec Kabutops à 1 PV a permis de vérifier le retour au ground en phase 3, la descente de Nilo, les retrouvailles avec Lyra et le [bilan natif](Preuves/Bilan-natif-controle.png). La sauvegarde issue du bilan a été relue : passage par `WaterfallVillageCapital` et arrivée à [Réverie](Preuves/Retour-a-Reverie.png), où Léo accueille Nilo et Lyra. Ce point de contrôle ne teste pas la difficulté ; le boss livré n’a pas été modifié.
- **KO et reprise :** le chemin d’échec moteur avait été joué sur la version précédente. Il n’a pas été rejoué jusqu’au KO sur ce commit. La réentrée, la reconstruction de la pose de Nilo et son nettoyage sont vérifiés par le test Lua du service, pas par un rechargement de sauvegarde en plein duel.

## Carte et netteté

Ouvrir [l’inspecteur autonome](Carte-pixel-a-pixel.html), basculer entre **Vasques** et **Arène**, puis choisir **1× à 4×**. Aucun réseau nécessaire. À 1×, les [vasques et leur antichambre](Fosse-Cascade-Fond-576x528.png) mesurent **576 × 528 px**, l’[arène](Arene-Fosse-Cascade-480x360.png) **480 × 360 px**. L’eau et les strates sont plus faciles à examiner au zoom entier ; le jeu garde les mêmes tuiles, teintes, proportions et contrastes. Aucune retouche, aucun lissage.

Les PNG proviennent des couches du moteur ; le rectangle de la salle haute correspond pixel pour pixel à l’arène à la phase d’eau de référence. Un [comparatif](Preuves/Nettete-comparaison.png) isole le même pan de roche et de vasque : la nouvelle capture RGB correspond à **100 %** au PNG sur ce pan, alors que l’ancien export vidéo avait déjà altéré les contours et les nuances. Le MP4 est un aperçu compressé ; les PNG et l’inspecteur sont les références pour lire le pixel art. Les cinq fichiers carte/tuiles/zone sont identiques à la version précédente (SHA vérifiés) ; la Fosse reste à **9 étages**, avec la même arène et le même équilibre.

## Intégration

Commit local `a349c316bf60447b64d87263cc9ece4b31e4bd1a` sur `wip/reverie-integration-kingambit-cafe`. Aucune publication ni push.

- [Patch](Gardien-des-vasques.patch) à appliquer sur `e156041b3274723deb360f2fd99f0a16925d9d32` avec `git am`.
- [Bundle complet du chantier](Gardien-des-vasques-complet.bundle) à importer dans un dépôt contenant `37138a7ca93be920e9c47963fea21441b153ec65`. Ref transportée : `refs/heads/wip/reverie-integration-kingambit-cafe`.
- [Journal des tests](Preuves/Tests.txt) : tests de Fosse Cascade, du témoin et du stockage Kangourex ; audits des cadrages et des répliques, index de tuiles et import hors ligne du bundle. Patch rejoué jusqu’au même arbre Git. [Sommes SHA-256](SHA256SUMS.txt).

La vidéo est capturée dans PMDO à 30 images/s (pistes vidéo RGB et audio prises séparément, synchronisées par horodatage, échelle entière 4×). Le build privé utilisé pour chronométrer découple l’horloge de jeu des ralentissements du rendu logiciel ; il n’y a pas d’accélération au montage. Ni instrumentation, ni C# modifié, ni sauvegarde, ni capture brute ne sont inclus dans les fichiers d’intégration.
