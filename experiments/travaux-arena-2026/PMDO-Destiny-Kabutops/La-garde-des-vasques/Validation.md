# La garde des vasques

[Extrait de l’encerclement (10 s)](Kabuto-encerclent-le-duo.mp4) · [Cinématique complète (1 min 29 s)](Cinematique-La-garde-des-vasques.mp4) · [Plans fixes](Preuves/Encerclement-et-raccord.png)

**1 min 25 s avant le combat**, de l’entrée dans la salle au contrôle rendu dans l’arène, sur une lecture posée (85,10 s logiques). Les confirmations restent manuelles. La carte agrandie, les deux avertissements anonymes et la fausse accusation de Nilo ne changent pas.

## La nouvelle séquence

Dans la vidéo complète, Kabutops surgit à **00:37** et repousse le duo comme auparavant. Vers **00:38**, les premiers Kabuto sortent du sol sur les flancs, puis deux autres jaillissent à l’arrière. Les quatre avancent en deux temps avec la pose d’attaque de leur sprite. Les traces de Griffe ponctuent le dernier pas ; le héros et le partenaire se tournent vers les flancs, puis vers l’arrière. La séquence laisse un bref temps pour lire le cercle avant que Kabutops reprenne la parole.

Le woosh commence vers **01:21**. Les figurants disparaissent sous le noir et leurs équivalents combattants reprennent la même formation au 9e étage. Ce ne sont pas des effets visuels en combat : ils se déplacent, prennent des tours, utilisent [Griffe et Armure](Preuves/Kabuto-utilise-Griffe.png) et peuvent être mis K.O.

| Emplacement à l’ouverture | Ennemi | Niveau | PV de départ |
|---|---|---:|---:|
| Devant le duo | Kabutops (inchangé) | 14 | 162 |
| Flanc gauche et flanc droit | 2 Kabuto | 4 chacun | 16 chacun |
| Arrière gauche et arrière droit | 2 Kabuto | 3 chacun | 14 chacun |

Les quatre départs de l’équipe de secours restent libres, même avec des recrues. Nilo tremble toujours sur la terrasse derrière Kabutops, sans tour ni cible. [Ouverture du combat](Preuves/Arriere-et-flancs-dans-larene.png).

## Vérification locale

- **Première confrontation, données normales** : quatre émergences distinctes, huit pas en pose d’attaque et quatre traces visibles. Positions, niveaux et PV confirmés par le moteur. Premiers tours joués avec Évoli et Salamèche au niveau 14 ; cet essai ne mesure pas la difficulté jusqu’à la victoire. [Trace PMDO](Preuves/Trace-PMDO.txt) · [Chrono](Preuves/Raccord-et-rythme.txt) · [Contrôle audio](Preuves/Audio.txt).
- **Revanche et victoire** : la garde est déjà en place en revanche, sans rejouer le Tunnel, et Kabutops n’a qu’une réplique. Contrôle de victoire dans un profil privé (duo niveau 50, Kabutops à 1 PV ; quatre Kabuto d’origine) : [Kabutops est tombé sans mettre fin au combat](Preuves/Kabutops-KO-le-duel-continue.png). Les quatre Kabuto ont ensuite été mis K.O. Le jeu a rendu la main aux retrouvailles après le dernier. [Bilan natif](Preuves/Bilan-du-duel.png) et retour au centre de Réverie confirmés. [Trace](Preuves/Trace-revanche-et-victoire.txt).
- **Régressions** : l’arène n’a changé que sur son effectif et son commentaire. Géométrie, 42 cases praticables, palette, tuiles, réglages de Kabutops, huit étages précédents et moteur sont identiques au commit parent. Le test des capacités vérifie les quatre emplacements requis par le moteur au K.O. : Griffe, Armure et deux emplacements vides. [Tests](Preuves/Tests.txt).

## Intégrer

Commit local `0403d9c79a51979ac5265f6723e883e96e9dfa96` sur `wip/reverie-integration-kingambit-cafe`. Pas de push ni de publication.

- [Patch de cette retouche](Garde-des-vasques.patch) : `git am` sur `a349c316bf60447b64d87263cc9ece4b31e4bd1a`.
- [Bundle du chantier](Garde-des-vasques-complete.bundle) : import dans un dépôt qui contient `37138a7ca93be920e9c47963fea21441b153ec65`.
- [Sommes SHA-256](SHA256SUMS.txt). Ni build privé, ni instrumentation, ni sauvegarde, ni capture brute ne sont livrés.
