# Le carnet des retours — validation du candidat

**Candidat local** `c5b067a20e6c13de83d848dfd18ab3a4fda26bc8` · **Base** `37e6b5cdcfb46a064239c7c6983ef4840d27d408` (v0.7.6 publique).

Ce lot ne fait pas partie de la v0.7.6. Il n’a été ni poussé, ni empaqueté pour Windows, ni publié.

## Les habitants réagissent à l’histoire

| Jalon | Habitants avec une réplique propre | Saynètes disponibles |
| --- | ---: | ---: |
| Retour des Bois Perdus / première visite, hors scène principale | 33 | 21 |
| Alerte de Lyra | 33 | 22 |
| Après l’accueil de Nilo | 34 | 21 |
| Première expédition réussie au Passage Aquatique | 34 après l’accueil de Nilo | 22 |

La visite, l’alerte et l’accueil gardent leur priorité. Les habitants à poste fixe réagissent sans fermer leur service. Après l’accueil, Pip et Ondine quittent le centre pour l’étang, sans être présents dans les deux quartiers à la fois. Les saynètes se déclenchent quand on vient parler aux habitants, pas en entrant dans la ville. La crique apporte une chronique distincte, qui n’annonce pas le sort de Nilo si on la découvre plus tôt.

## Essais avec le moteur

PMDO 0.8.12.0 sous Linux, sur un profil de test isolé. Les commandes ont placé l’équipe et appelé les actions et passages de la carte dans un état **après l’accueil**. Ce n’est pas une partie jouée depuis le début. Les cartes utilisées correspondent, octet pour octet après décompression, aux cartes de la base publique.

| Contrôle | Résultat observé |
| --- | --- |
| **Zig et Zag, au centre** | Le dialogue s’achève et le menu **Produits** s’ouvre. Fermeture du menu, retour au jeu. [Dialogue](Preuves/Zag-apres-le-retour.png) · [Menu](Preuves/Etal-vert.png) |
| **Le dessin de Nilo, au résidentiel** | Échange complet entre Léo, Lyra et Nilo. Le marqueur de scène vue est écrit et le mode cinématique désactivé. [Capture](Preuves/Le-dessin-de-Nilo.png) |
| **Le carnet, à l’étang** | Échange complet de Pip et Ondine. Après la scène, la flèche bas déplace le héros de 46 px ; la caméra n’est plus fixée sur les PNJ. [Capture](Preuves/Le-carnet-de-Pip.png) |
| **Escaliers** | Le moteur a exécuté Centre → Résidentiel, puis, sur une autre prise, Résidentiel → Étang via les callbacks du jeu. |
| **Sauvegarde à l’étang** | Écriture d’un `SAVE.rssv` de 95 962 231 octets après le carnet. Le retour de l’appel Lua seul n’a pas été compté comme preuve. |
| **Rechargement à l’étang** | Après redémarrage de PMDO, reprise sur la même carte, sans scène automatique. En parlant cette fois à Ondine, seule sa réplique individuelle s’affiche : la scène à deux n’est pas rejouée. [Capture](Preuves/Ondine-apres-rechargement.png) |

Les [traces des prises](Preuves/Traces-en-jeu.txt) distinguent les essais de passage, la restitution du contrôle et le rechargement de la sauvegarde. Les premiers essais de sauvegarde ont buté sur la mémoire disponible dans le bac à sable. L’écriture sur disque a abouti avec de la mémoire d’appoint temporaire et un plafond du tas .NET relevé, sans changer le moteur ou les cartes. Ni profil ni sauvegarde de test ne sont livrés.

## Tests automatisés et intégrité

- [Rapport des tests locaux](Preuves/Tests-locaux.txt) : couverture des quatre jalons, accessibilité des ancres sur les tuiles réelles, services, persistance avec doubles du moteur, interruption de scène, priorités de l’intrigue et retour réussi du Passage Aquatique. Onze suites de régression, le runner autonome de la règle de K.O. et les deux audits de cadrage passent.
- [Preuve d’intégration](Preuves/Integration.txt) : import du bundle dans un dépôt indépendant ; patch inverse puis direct reproduisant les deux arbres exacts. Aucune carte ni donnée C# dans le changement.
- [Version et ressources de l’essai](Preuves/Version-de-la-prise.txt) · [Sommes SHA-256 du lot](SHA256SUMS.txt).

## Livrables et suite

Le [bundle Git](Le-carnet-des-retours.bundle) contient la branche locale `work/reverie-ville-reactive`. Il s’importe sur un clone possédant déjà le commit public de la v0.7.6. Le [patch](Le-carnet-des-retours.patch) a la même base. Les [notes](Notes.md) décrivent les dialogues, positions et règles de priorité.

Avant de publier ce lot : lancer un **nouveau build Windows** sur ce candidat et le tester sur une installation de la 0.7.6 avec une sauvegarde existante. Le tag et les paquets publics de la 0.7.6 restent inchangés.
