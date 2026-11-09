# Destiny : ressources PMU et cadence en mode développeur

## Ce qui existe déjà dans la branche distante

Les 40 banques `PMU_00_partie_01` … `PMU_10_partie_01` de l'instantané PMU 2014 sont présentes dans le dépôt Destiny v0.5.7 (`ee39156a24f350b67e81740478be8505f4ff1a05`). Les 40 fichiers distants ont été téléchargés et vérifiés par SHA-256 contre le manifeste : 40/40, 41 665 401 octets au total. Ces banques contiennent des tuiles de 8×8, pas une bibliothèque de tous les objets complets. Deux objets PMU individuels sont visibles dans `game/Content/Object` du dépôt : lampe et table. Présence dans le dépôt ne constitue pas un test d'affichage dans l'éditeur ni une vérification du package final.

## Travail supplémentaire local : objets complets et fleurs

- Cinq objets statiques PMU entiers préalablement extraits (cheminée/tableau, canapé, bibliothèque, piano, épée décorative) sont ajoutés au dossier local `travail/game/Content/Object/`, avec leurs PNG `.1.png` d'import dans `travail/art/pmu/objets-source/`.
- Dix fleurs et bouquets animés ont été ajoutés comme `PMU_Fleurs_*.dir`, chacun en 2 trames 32×32, avec les PNG `.2.png` d'import. Leur correspondance avec des couples réellement utilisés par les cartes historiques est vérifiée dans la base des 2 000 cartes. La sélection a été regardée graphiquement, mais n'est qu'un échantillon : aucune affirmation d'exhaustivité.
- Une carte Ground distincte `pmu_fleurs_animees_dev.rsground` place ces fleurs en décorations séparées ; leur `FrameTime` est réglé à 15. Elle ne change aucune carte existante et n'est pas raccordée à un lieu jouable. Les feuilles et la carte se trouvent dans le chantier local, pas dans le dépôt.
- `apercu-fleurs-250ms.gif` est une recomposition des images originales, pas un rendu du moteur ou de l'éditeur.

## Cadence et accès dev

Le code PMU historique `MapViewer.OnTick` inverse la phase globale quand l'horloge dépasse 250 ms. Le `MapRenderer` choisit la tuile ordinaire ou sa variante animée selon cette phase. La cadence est donc globale dans cet instantané, pas une durée indépendante découverte pour chaque objet. Une durée de 15 frames PMDO correspond approximativement à 250 ms à 60 FPS ; elle figure sur chaque décoration de la carte locale, sans être une cadence par objet extraite des cartes PMU. Attention au comportement exact à vérifier en moteur.

Dans le code Destiny, `GroundTabDecorationsViewModel` expose le choix d'animation d'objet, `StartFrame`, `EndFrame` et `FrameLength`, qui lit/écrit `ObjectAnim.FrameTime` et actualise l'aperçu. Une feuille `.dir` identifie les images ; la cadence est un attribut de la décoration placée, pas un réglage magique automatiquement conservé dans la feuille. On doit encore vérifier en ouvrant la carte dans l'éditeur Windows : comportement de l'interface, index, rendu et sauvegarde réels.

## Ce qui reste et limites

La demande d'intégration complète n'est pas satisfaite : inventaire historique de 2 000 cartes donne 4 080 couples différents, 293 742 occurrences dans 962 cartes, dont 22 couples avec une référence introuvable ; ces chiffres comptent les cellules, pas les objets complets. Il faut reconstruire les objets multicases sans découpage, traiter les banques d'animation manquantes, vérifier les ressources d'autres versions PMU, indexer et tester en jeu/dev. Le code MIT ne prouve pas les droits de chaque image tierce. Les 10 fleurs et cinq objets supplémentaires sont locaux et non publiés.

Les tests statiques vérifient les pixels source, les conteneurs `.dir`, les durées et le Ground ; les tests Lua existants passent sur doublures. Aucun test d'interface dev, moteur, ancienne sauvegarde ni CI pour ces ajouts. L'autorisation Device a été confirmée par l'utilisateur, mais le processus qui portait l'accès temporaire a disparu au retour de cette étape : aucun push, tag, release ou CI. Le dépôt reste sur 0.5.7. Ne pas traiter cette sauvegarde locale comme une release complète.
