# Destiny / Réverie — récapitulatif et état de la prochaine mise à jour

## Publication : état vérifié

- La dernière release disponible est **[v0.5.7](https://github.com/meromoonmeri/PMDO-Destiny/releases/tag/v0.5.7)**, une prérelease Windows complète, sur la branche `wip/reverie-integration-kingambit-cafe` au commit `ee39156a24f350b67e81740478be8505f4ff1a05`. La branche et le tag pointent toujours sur ce commit au contrôle de cette session. Ce n’est pas une publication sur `main`.
- La [CI Windows de la v0.5.7](https://github.com/meromoonmeri/PMDO-Destiny/actions/runs/42425754568) a réussi. Cela ne remplace pas un essai de jeu réel ou d’ancienne sauvegarde.
- **Aucun nouveau push, tag ou release n’a été effectué pour les travaux locaux ci-dessous.** La session d’accès GitHub précédente a disparu ; aucun jeton ni session active n’a été trouvé et le connecteur GitHub n’est pas disponible. Une nouvelle authentification sécurisée sera nécessaire.
- Plusieurs éléments demandés sont incomplets ou encore non validés dans PMDO. Les publier tous en les présentant comme une version complète serait trompeur et pourrait casser des cartes ou des sauvegardes. Les travaux locaux n’ont pas été appliqués au dépôt distant.

## Déjà publiés jusqu’à la v0.5.7

- Cinématiques Dazzling et rythme : retrait ciblé des moqueries `Special0` d’Aria et Adagio, conservation de `Special0` de Sonata et des émotes `glowing`, répliques et réactions ajoutées (v0.4.8).
- Carrefour, liaison de l’escalier vers `cliffdaytest`, chemin vers Réverie et compléments musicaux de la sauvegarde ; renommage actif de Métano en Réverie tout en préservant la provenance historique (v0.4.9–0.4.10). Les destinations non établies n’ont pas été inventées.
- Système de banques et de calques Réverie : carte de jeu à 11 calques et version d’édition plus détaillée. Les 37 couches de l’édition ne sont pas toutes activables séparément dans le composite à 11 couches.
- Versions successives de la visite, des scènes et des ressources, notamment l’accueil vivant de la place et la scène autour de Lyra/Nilo. En v0.5.6 : échanges Rose–Lombre, accueil de Ludicolo, réactions des habitants et gestes ; certaines marches sont conditionnées par la disponibilité du trajet. Le café comprend également des réactions lors de sa scène d’accueil.
- Corrections graphiques ciblées cumulées, notamment certaines phases d’eau, pierres et raccords : **elles ne constituent pas une correction exhaustive de toutes les captures**.
- Quarante banques de tuiles PMU historiques sont déjà dans la branche v0.5.7 ; leur présence ne signifie pas que tous les objets et animations sont convertis ou intégrés comme objets complets.
- Météo quotidienne de Réverie (v0.5.7) : clair, soleil, couvert ou pluie, choix conservé sur la journée, nouvelle journée après la sieste au café ; intérieurs et donjons exclus. Tests simulés et CI réussis, effets et anciennes sauvegardes réelles à vérifier en jeu.

## Travaux locaux après v0.5.7 — non publiés

### Carte, bassin et raccords

- Corrections candidates des captures 53–55 ; quatre arbres proches de la falaise ont été déplacés avec leurs ombres plutôt que simplement masqués. Les retouches associées, une touffe animée et certaines collisions sont conservées dans les copies candidates.
- Chemins : 134 cases de l’escalier de la capture 51 et 13 cases de la capture 27 ont reçu une reprise issue de modules Métano. Vérifications des données non concernées et rendu indépendant des quatre phases pour ces zones : réussis.
- Une vue globale du candidat `reverie_etang` a été préparée. Elle est statique et ne montre pas les PNJ ; l’ancienne partie sud est encore présente.
- **Restent ouverts :** rive de la capture 52 dans ce candidat, raccords des falaises et courbes mauves, autres chemins, herbes, ombres et anomalies ; possibles obstacles invisibles à l’ouest des arbres déplacés. Aucun test en jeu ni avec une sauvegarde réelle.

### Scène de Lyra, ACT et déplacements

- Proposition locale : fin de scène sans panoramique final vers l’entrée ; marche échelonnée du trio et scène ACT après son départ, avec restauration des positions des trois membres. Tests sur doublures réussis. Cadrage, rythme et collisions restent à vérifier en jeu. La surveillance et le rapport à la Fédération sont évoqués, pas implémentés dans un donjon.
- Prototype local de suivi du partenaire dans les intérieurs, retour aux positions antérieures quand elles sont sûres et maintien de la musique à travers certaines transitions. Les doublures passent ; pas de validation des sons, collisions dynamiques ou anciennes sauvegardes dans PMDO. Le retour exact a un repli lorsque nécessaire.

### Café Spinda

- Enquête sur l’écran noir : une piste de chargement des noms accentués sous Windows et un défaut distinct de nettoyage des modules Lua ont été identifiés. Correctifs préparés localement, tests isolés et sur doublures réussis.
- **La cause exacte de l’écran noir n’a pas été reproduite** ; le correctif moteur C# n’a pas été compilé ou testé sous Windows et ne doit pas être considéré validé en jeu.

### Intérieurs PMU et doyen Draco

- Candidats locaux : maison d’équipe sur la falaise depuis la carte PMU historique `s1506` et six maisons de Réverie (`s1142` à `s1146`, `s1373`). Identifiants et éléments essentiels préservés, migrations et accès contrôlés sur doublures ; aucune validation des collisions fines, des déplacements ou d’une vraie sauvegarde.
- Nuit, continuité jour/nuit de la maison d’équipe, hutte aquatique, auberge et poste restent à réaliser ou raccorder correctement.
- Proposition de Draco nageur devant la pierre : aperçu animé seulement. Il n’est pas installé dans le jeu et l’effet de nage exact d’Halcyon n’est pas confirmé.

### Deux sections de Réverie

- Une maquette de ville en deux sections a été montrée et validée visuellement : nord/centre et sud regroupé, en retirant la grande extension sud au-delà de la dernière maison isolée. La ligne de séparation est indicative.
- La fusion réelle des Ground, des portes, des capteurs, des positions des PNJ et la migration des sauvegardes ne sont pas faites.

### Ressources PMU et poste Bekipan

- Inventaire historique : 11 planches, 52 486 cases de 32 px, 40 bandes au format PMDO ; catalogue visuel et inventaires consultables localement. Les cases comprennent du sol et des fragments, et ne correspondent pas chacune à un objet complet.
- Quinze objets complets ont été préparés localement : cinq statiques et dix fleurs animées. Un autre ensemble de 4 058 paires animées correspond à des **fragments de deux cases**, pas à des objets multicases assemblés ; 22 paires comportent une référence manquante. L’intégration exhaustive des objets, décors, cascades et écumes reste à faire. Aucun personnage PMU n’est destiné à l’intégration.
- Aperçu serveur de cinq intérieurs historiques : `s70` et `s168` sont nommés bureaux de poste ; `s1000`, `s450` et `s1377` sont des lieux de logement ou mairie associés à des PNJ Bekipan. Aucun ne peut être affirmé comme Poste Bekipan sur ces seules preuves. Les PNJ mobiles et scripts ne sont pas rendus.
- Les droits de redistribution des différents graphismes restent à vérifier indépendamment.

### Lost Wood et autres recherches

- Lost Wood : première maquette refusée, non livrée. Une reprise DTEF conserve les décors et utilise les ressources demandées, mais ses raccords et couleurs sont visuellement douteux ; elle n’est ni complète ni validée en moteur. **Ne pas l’installer en l’état.**
- Recherche de Lush Hollow / Marvelous Cave dans le backup Drive : pas de correspondance trouvée par nom ; cela ne prouve pas leur absence dans les contenus binaires.

## Sauvegardes et validation avant une vraie prochaine release

1. Reconstituer proprement les travaux locaux depuis leurs scripts et sauvegardes : certains dossiers temporaires ont disparu entre sessions ; vérifier les empreintes et la compatibilité des modifications cumulées.
2. Terminer les points encore ouverts ci-dessus, en conservant les événements, animations, cartes et sauvegardes ; ne pas installer en bloc les fragments PMU comme objets finis.
3. Tester en PMDO 0.8.12 / Windows les scènes, entrées, sorties, collisions, musique, rendu, animations et anciennes sauvegardes. Les tests statiques et les doublures ne suffisent pas.
4. Authentifier à nouveau l’accès GitHub de façon sécurisée, puis pousser la branche voulue sans écrasement, lancer et vérifier la CI Windows, créer le tag et la release et contrôler l’archive complète. Ne jamais transmettre ou enregistrer de jeton dans le récapitulatif. Si un ancien jeton a été exposé, le révoquer.

## Documents locaux utiles

- `chantier-raccords-et-pmu/ETAT-RACCORDS-PMU.md` — détail des raccords, sauvegardes et limites.
- `chantier-deplacement-arbres-bassin/ETAT-DEPLACEMENT.md` — arbres et collisions.
- `chantier-apercu-reverie/RAPPORT-ETAT.md` et `RAPPORT-INTEGRATION-PMU.md` — deux sections, scène, intérieurs et suivi.
- `chantier-cafe-ecran-noir/RAPPORT-AUDIT-CAFE.md` — hypothèse et correctif café.
- `chantier-ressources-pmu/RAPPORT-RESSOURCES-PMU.md` — banques et objets ; la situation des 40 banques publiées y est explicitée.
- `chantier-lostwood-amapola/ETAT-REPRISE-DTEF.md` — état de la reprise non prête à installer.
- `apercu-poste-pmu/index.html` — aperçu des intérieurs de postes et lieux liés aux Bekipan.

Les rapports plus anciens peuvent décrire un état antérieur : se référer en priorité au statut indiqué ici et aux rapports les plus récents de chaque chantier.
