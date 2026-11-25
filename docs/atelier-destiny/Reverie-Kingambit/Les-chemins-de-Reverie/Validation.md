# Les chemins de Réverie — candidat local

**Testé dans PMDO 0.8.12.0 sous Linux.** La ligne de coupe proposée reste à valider visuellement. Aucun push, aucun nouveau build Windows, aucune publication. Le Carnet et le lot déjà validé des Foyers restent intacts.

## La rive sud

[Plan avant modification](Repere-coupe-sud.png) · [Ancienne forêt en jeu](Preuves/Ancienne-foret.png) · [Maison ronde après la coupe](Preuves/Maison-ronde-apres-la-coupe.png) · [Pont ouest](Preuves/Pont-ouest.png)

La carte reste large de **1 600 px** et passe de **4 000 à 2 976 px** de haut. La coupe s’arrête après la maison ronde isolée, **à droite du pont central**. Ce n’est pas la maison citrouille de Nilo. La rive, les deux ponts et les accès à Pierre, Plante, la Citrouille et l’escalier P sont conservés. Aucun intérieur n’a été ajouté à la maison ronde.

- **Ancienne sauvegarde reprise** : le même profil, enregistré dans la forêt en `(688, 3056)`, revient côté sud du pont central en `(688, 2896)`, le partenaire en `(688, 2920)`. L’équipe et l’état narratif restent intacts.
- **À pied dans le moteur** : traversée du pont central jusque sur la rive nord, retour au bord solide (`Y = 2952` pour le héros), puis arrivée devant la maison ronde. Le pont ouest a aussi été traversé dans les deux sens au clavier, après placement du héros à son débouché sud.
- **Contrôles de carte** : dix variantes jeu/édition synchronisées, onze calques, empreintes vérifiées lors de l’extraction. Les seuils et les routes ont été contrôlés avec le collider 16 × 16. Les tests de régression des intérieurs et de la Fosse Cascade passent.

## Les rencontres et le café

| En jeu | Constat |
|---|---|
| [Sureau](Preuves/Sureau.png) et Liane | Positions différentes au fil du temps ; un échange arrête le passant sans le déplacer. |
| [Mirabelle](Preuves/Mirabelle.png) et [Tilleul](Preuves/Tilleul.png) | Une Baie Oran et une Pomme reçues. Après sauvegarde, redémarrage et nouvelle visite, chacune reste à un exemplaire. |
| [Bulle](Preuves/Bulle-au-cafe.png) et [Balou](Preuves/Balou-au-cafe.png) | Cinq pages par échange, avec une ouverture distincte selon l’interlocuteur. Bulle mène la conversation, Balou répond « Banco ! ». La [Bourse d’échange reste fermée](Preuves/Caisses-fermees.png). |

La visibilité pendant l’alerte et le report d’un cadeau quand le sac est plein sont vérifiés par des doubles Lua. Les changements de quartier et les placements à proximité des interlocuteurs ont été assistés dans le banc privé ; les dialogues et menus ont été déclenchés au clavier.

## Le duel de Liane

[Arène animée](Preuves/Arene-du-dojo.png) · [Capacités en combat](Preuves/Combat-de-Liane.png) · [Réplique de victoire après redémarrage](Preuves/Victoire-apres-reprise.png)

Le menu laisse **« Pas maintenant »** sélectionné par défaut. Accepter ouvre un véritable combat PMDO contre une seule Kungfouine de niveau 10 au Dojo Kingambit, sans gain d’EXP ni perte durable de sac. Aucun résultat n’a été forcé par le banc d’essai.

| Issue native | Retour constaté |
|---|---|
| [K.O.](Preuves/KO-journal-natif.png) (`Failed`) | Résidentiel, même emplacement du héros et du partenaire, même Baie Oran et même Pomme, mêmes niveaux et PV qu’avant la manche. |
| [Abandon depuis le menu](Preuves/Abandon-menu-natif.png) (`GaveUp`) | Retour sur le lieu du défi, sac et équipe inchangés. La réplique d’abandon est conservée après enregistrement et redémarrage. |
| [Victoire](Preuves/Retour-victoire.png) (`Cleared`) | La version finale, à **52/52 PV** pour Liane, a été battue au clavier avec le duo d’essai de niveau 16. Le héros revient exactement en `(920, 2592)` ; le partenaire est replacé sur une case praticable, son point mémorisé empiétant sur un obstacle. Sac, niveaux, PV et marqueur de victoire sont conservés au redémarrage. |

K.O. et abandon ont été joués avec le duo au niveau 8, avant l’alignement du maximum de PV de Liane sur ses 52 PV initiaux. Les scripts de retour n’ont pas changé. Les trois issues sont également retestées par doubles sur le candidat final. Ces essais ne constituent pas un équilibrage pour toutes les équipes.

## Remise locale

- **Commit `785ecef7e385a77270bcf931419c47e42526d5d3`**, branche `work/reverie-chemins`, parent `e885b934a2940096df7bdb3d51758edbce761af9` (*Les foyers de Réverie*).
- [Bundle cumulatif depuis `v0.7.6`](Les-chemins-de-Reverie.bundle) ou [patch compressé à partir des Foyers](Les-chemins-de-Reverie.patch.xz). L’import du bundle et l’application puis l’inversion du patch ont été contrôlés dans un dépôt séparé.
- [Instructions d’intégration](Notes.md) · [Tests locaux](Preuves/Tests-locaux.txt) · [Trace du moteur](Preuves/Trace-PMDO.txt) · [Empreintes](SHA256SUMS.txt).

Aucun profil ni outil de pilotage privé n’est fourni dans le lot.
