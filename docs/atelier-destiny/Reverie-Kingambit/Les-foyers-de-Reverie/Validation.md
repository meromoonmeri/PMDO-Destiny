# Les foyers de Réverie

**Candidat local** `e885b934a2940096df7bdb3d51758edbce761af9` · au-dessus du **Carnet des retours** `c5b067a`. Le bundle comprend les deux lots et s’importe sur la base publique v0.7.6. **Aucun push, build Windows ou changement de la préversion publique.**

## Cinq maisons désormais habitées

| Maison | Rencontre | En jeu |
| --- | --- | --- |
| **Maison de Pierre** | Maëlle, son compagnon Basalte et leur fille Miette. Une devinette, des réponses commentées et un indice de Basalte. | [Menu](Preuves/Miette-devinette.png) · [Baie Pêcha reçue](Preuves/Miette-cadeau.png) |
| **Maison plante** | Flore, Aulne et Brin partagent un panier. Le joueur peut prendre une Pomme, une Baie Oran ou refuser. Brin se souvient de ce qui a été choisi. | [Le panier](Preuves/Flore-Le-panier.png) |
| **Hutte du nord-est** | Nacre, Malo et Perle. Perle pose une autre devinette ; Malo remet une Échaporbe quand elle est résolue. | [La devinette de Perle](Preuves/Perle-devinette.png) |
| **Hutte aquatique du sud** | Yuna, la compagne de Marius, et Lino. On les aide à choisir où laisser un mot pour le pêcheur ; Yuna répond différemment selon le choix. | [Le mot de Lino](Preuves/Lino-Le-mot.png) |
| **Maison citrouille du sud** | Zélie garde la maison. Après la scène sous l’arbre, Lyra, Léo et Nilo y rentrent au prochain changement de carte. Le joueur aide Nilo à décider que faire de son dessin. | [Le choix](Preuves/Nilo-Le-dessin.png) · [La réaction de Léo](Preuves/Leo-apres-le-choix.png) |

Ces rencontres sont facultatives. Les habitants lisent les jalons du récit et ne répètent pas simplement le même dialogue chaque jour. Un cadeau n’est donné qu’une fois ; si le sac est plein, le joueur peut revenir le chercher. Une annulation ne valide pas de réponse. Le partenaire du héros, les portes, les tuiles et les services d’origine sont inchangés.

## Contrôlé dans PMDO

- Les cinq maisons et leurs nouveaux acteurs ont été chargés dans PMDO 0.8.12.0 sous Linux. Un profil isolé a été placé après l’accueil de Nilo. Les tests pilotent ensuite les dialogues et menus au clavier.
- La devinette de Miette a accepté un essai incorrect, un indice et une bonne réponse. La Baie Pêcha a été ajoutée au sac. Après écriture d’une sauvegarde, redémarrage du moteur et reprise de la partie, l’indice et le cadeau ne sont pas reproposés. Le joueur se déplace après le dialogue.
- La Baie Oran et l’Échaporbe sont entrées dans le sac. Lino se souvient du choix « Sur la table ». Nilo garde le dessin, et Léo donne la réplique correspondante. Les autres branches et le sac plein ont été contrôlés avec des doubles du moteur.
- **Sortie et rentrée à pied** par la porte de la maison de Pierre : retour devant la façade au résidentiel, sans deuxième exemplaire de la famille de Nilo dehors, puis réentrée par le seuil. [Capture du retour](Preuves/Retour-au-residentiel.png) · [Traces en jeu](Preuves/Traces-en-jeu.txt).

## Intégration et fichiers

- [Bundle Git cumulatif](Les-foyers-de-Reverie.bundle) : `v0.7.6 → Le carnet des retours → Les foyers de Réverie`.
- [Patch incrémental](Les-foyers-de-Reverie.patch) : les foyers seuls, à partir de `c5b067a`.
- [Notes du lot](Notes.md) · [Tests ciblés et audits](Preuves/Tests-locaux.txt) · [Vérification indépendante du bundle](Preuves/Integration.txt) · [Origine des cartes et modules testés](Preuves/Version-de-la-prise.txt) · [SHA-256](SHA256SUMS.txt).

Le prochain contrôle avant une publication est un **build Windows** sur ce candidat avec une sauvegarde existante. Aucun profil de test n’est livré.
