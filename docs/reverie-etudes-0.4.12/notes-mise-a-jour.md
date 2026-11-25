# Réverie Town — notes de mise à jour et état réel

**Publication de travail 0.4.12-dev : documents et propositions isolées uniquement.** Les fichiers dans `experiments/` ne sont pas intégrés au jeu. Les sauvegardes, la 0.4.11 et les anciens tags restent inchangés.

## Déjà publié sur GitHub

### 0.4.8 — cinématiques Dazzling

- Améliorations de déplacement et de rythme des cinématiques concernées, notamment autour d'Aria, Adagio, Lopunny et Mawile.
- Retrait ciblé des animations `Special0` de moquerie d'Aria et d'Adagio ; la pose `Special0` de Sonata et les émotes `glowing` ont été conservées.
- Ajouts de répliques et d'une goutte de sueur après la bousculade et le départ des Dazzling, suivant l'autorisation donnée ; les dialogues et événements préexistants restent préservés.
- CI Windows corrigée et réussie pour la publication.

[Prérelease 0.4.8](https://github.com/meromoonmeri/PMDO-Destiny/releases/tag/v0.4.8-dev-cinematiques-dazzling)

### 0.4.9 — carrefour et musiques

- L'escalier du carrefour mène à `cliffdaytest` ; le chemin de Ronflex mène vers Réverie Town. Les deux autres destinations restent indéterminées.
- 213 morceaux présents dans la sauvegarde ont été inventoriés ; 151 fichiers manquants ont été ajoutés.
- CI réussie.

[Prérelease 0.4.9](https://github.com/meromoonmeri/PMDO-Destiny/releases/tag/v0.4.9-dev-carrefour-reverie)

### 0.4.10 — renommage Réverie Town

- Renommage des mentions actives Metano concernées, y compris ressources et références, pour Réverie Town ; les crédits et archives historiques conservent leur provenance.
- Index des tuiles vérifié et CI réussie.

[Prérelease 0.4.10](https://github.com/meromoonmeri/PMDO-Destiny/releases/tag/v0.4.10-dev-reverie-town)

### 0.4.11 — système expérimental de calques

- Système autonome en 14 banques, avec carte de jeu de 11 calques et carte d'édition séparée de 37 calques. Le regroupement conserve l'ordre visuel, mais la carte à 11 calques ne permet pas de basculer indépendamment les 37 couches d'édition.
- Cadence des cascades ajustée sans modifier les images ; aperçu local statique et animé.
- Sources et index contrôlés ; CI réussie. **Aucun test de rendu ou gameplay dans PMDO 0.8.12 n'est revendiqué.**

[Prérelease 0.4.11](https://github.com/meromoonmeri/PMDO-Destiny/releases/tag/v0.4.11-dev-reverie-calques) · [CI système réussie](https://github.com/meromoonmeri/PMDO-Destiny/actions/runs/42140848725)

### Plan des zones — documentation publiée

Le plan statique des zones et de leurs liaisons a été poussé sur la branche d'audit au commit [`7b7194e`](https://github.com/meromoonmeri/PMDO-Destiny/commit/7b7194e1ce45e3175c02919a8352732a91058800). La [CI documentaire](https://github.com/meromoonmeri/PMDO-Destiny/actions/runs/42147696224) est réussie. Ce commit est documentaire : il ne découpe pas encore la ville en cartes jouables et n'installe pas les corrections d'entrées.

## Préparé localement, non intégré au jeu

### Café Spinda

Trois salles ont été récupérées depuis la sauvegarde `town02-main_BACKUP`, avec leurs dix banques d'origine vérifiées. Les copies gardent géométrie, fenêtres, entités et données de la sauvegarde ; seules les références de banques ont été renommées pour isoler les ressources.

Avant installation, il faut vérifier les objets d'entrée/sortie, le placement des PNJ, les scripts, les retours, les sauvegardes et l'index de tuiles. En particulier, les objets attendus par certains scripts Destiny ne correspondent pas tous à ceux présents dans les cartes sauvegardées. Le paquet actuel n'est pas une mise à jour prête à installer.

### Dojo et extérieur

- La salle carrefour du réseau Ledian existant a été choisie comme futur intérieur du grand dojo nord-est ; ses quatre ouvertures sont graphiques et ne définissent pas encore leurs destinations.
- Le tapis rouge, sa fine ombre et la bande noire sous l'entrée ont été retirés **sur des copies locales**. Les autres parties visibles du bâtiment et l'ouverture noire de la porte sont conservées.
- Les deux cartes de ville et la banque concernée ont été sauvegardées ; les références modifiées sont uniques et les anciennes tuiles préservées. L'index global n'a pas été régénéré.
- La salle carrefour doit encore être adaptée en carte Ground : sortie de grotte noire demandée, collisions, accès, retours, PNJ et tests PMDO.

### Réseau souterrain et casino

- Réseau Ledian retrouvé : trois couloirs et trois salles, 46 calques et 15 accès graphiques. Ce sont des modules PNG existants ; ils ne sont pas encore reliés dans le jeu.
- Casino des braises retrouvé dans une branche de Guilde Treehouse PMD : quatre secteurs, décors séparés et quatre poses de flammes documentées dans son pack. Ce pack ne contient pas de carte Ground jouable.
- Le raccordement réel entre le dojo, les modules, le casino et la grotte de Réverie reste à définir et tester ; les destinations non confirmées ne sont pas inventées.

### Hutte aquatique

Un aperçu de variation de palette a été préparé à partir de l'image fournie, mais **les ondulations autour du rocher demandées ensuite ne sont pas encore produites**. L'animation n'est pas intégrée au jeu ; les droits des graphismes issus de PMD Red Rescue Team doivent être vérifiés avant distribution.

### Entrées, guildes, tableaux et découpage

- L'audit a repéré des seuils noirs potentiellement inaccessibles à cause des collisions. Les retraits de la liaison d'Arcanine et du faux marqueur de maison d'équipe sont demandés mais **pas appliqués**.
- Le retrait des intérieurs de guilde appartenant à Halcyon reste à appliquer après analyse des références et des sauvegardes : certaines ressources sont aussi utilisées ailleurs.
- Les deux emplacements des tableaux sont repérés ; leur attribution individuelle entre quêtes et gazette n'est pas confirmée. Renouvellement quotidien et filtrage des donjons débloqués ne sont pas encore opérationnels.
- E2 est prévu pour une sélection des donjons, avec indicateurs d'histoire et de missions ; E1 reste indéterminée. Les changements de cartes, les débords de décor et les liaisons doivent encore être implémentés et testés.

## Précautions pour cette publication

Ce commit ajoute les aperçus et copies d'étude dans des dossiers séparés. **Il ne modifie aucune carte active ni aucun script de jeu.** Les archives ne constituent pas une mise à jour installable et ne doivent pas être copiées directement dans PMDO. L'intégration demande la reconstruction de l'index, l'audit des sauvegardes, des collisions et des transitions, puis des tests en jeu. La planche Mudkip n'est pas incluse dans cette publication, ses droits de distribution restant à vérifier.
