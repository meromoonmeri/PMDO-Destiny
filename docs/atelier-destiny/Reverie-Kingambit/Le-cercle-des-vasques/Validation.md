# Le cercle des vasques

Retouche de *La garde des vasques*. La confrontation se déroule au centre de la salle haute, deux cases plus au nord. Le décor, les collisions, les dimensions, les tuiles et les couleurs sont inchangés.

**[Aperçu de l’encerclement et de la fuite (25 s)](Encerclement-et-fuite.mp4)** · [Cinématique complète jusqu’à l’arène (1 min 30)](Cinematique-Le-cercle-des-vasques.mp4) · [Du dernier K.O. au bilan (43 s)](Victoire-et-retrouvailles.mp4)

## Mise en scène

- **Avant le duel.** Après le jaillissement de Kabutops, le duo recule au milieu de la clairière. Les Kabuto des flancs émergent au large, longent les bords et se rabattent. Les deux autres contournent le duo par derrière, pivotent, puis coupent le passage sud. Le duo se resserre en se couvrant ; la caméra accompagne son regard vers l’arrière. Les quatre traces de Griffe rythment la fermeture du cercle. [Plan du cercle](Preuves/Le-cercle-se-ferme.png) · [Geste de Griffe](Preuves/Griffe-des-Kabuto.png).
- **Raccord au 9e étage.** Après le woosh natif, le duel reprend les mêmes places. Les deux Kabuto de flanc sont **niveau 4**, les deux de l’arrière **niveau 3** ; ils combattent avec Griffe et Armure. Kabutops garde ses capacités et ses 162 PV de départ. Les quatre départs alliés sont libres ; Nilo reste animé sur la terrasse sans participer au combat. [Ouverture du duel](Preuves/Ouverture-du-duel.png).
- **Après le dernier K.O.** Les quatre Kabuto ont un mouvement de recul, tremblent et réagissent par des émotes. Les deux de l’arrière s’enfoncent en premier, puis les flancs, puis **Kabutops, le dernier**, avec les particules et le son de Tunnel. Nilo attend que le passage soit sûr avant de retrouver Lyra. [Frayeur](Preuves/Kabuto-en-peur.png) · [Tunnel de la garde](Preuves/Tunnel-de-la-garde.png) · [Dernier départ](Preuves/Tunnel-de-Kabutops.png).

## Vérifications en jeu

| Contrôle PMDO 0.8.12 | Résultat |
|---|---|
| Première rencontre et rythme | **87,25 s** jusqu’à l’arène en temps de jeu, avec les dialogues confirmés à un rythme de lecture posé. Deux avertissements `???`. Woosh de **3,13 s**. [Chrono](Preuves/Rythme-et-raccord.txt) · [Trace](Preuves/Trace-premiere-confrontation.txt) · [Audio natif](Preuves/Audio.txt). |
| Revanche | **7,8 s** jusqu’à l’arène, avec une réplique et la garde déjà déployée. Entrée de contrôle en phase de revanche, sans jouer une défaite préalable. |
| Victoire | [Kabutops à 0 PV n’arrête pas le duel](Preuves/Kabutops-KO-les-Kabuto-restent.png). La scène attend le K.O. des quatre Kabuto. Les cinq fuites, les [retrouvailles](Preuves/Nilo-et-Lyra.png), le [bilan natif](Preuves/Bilan-natif.png) et le retour à Réverie ont été suivis en jeu. Le retour en ville est attesté par le journal du moteur et le dialogue d’accueil ; le profil de capture n’embarquait pas toutes les planches de personnages de la ville. [Trace de contrôle](Preuves/Trace-revanche-victoire.txt). |
| Régressions | Tests Lua, contrôle des trajets libres, des 42 cases de l’arène et du rendu natif ; comparaison structurelle avec `0403d9c`. Seules les ancres ont changé dans les cartes. Ni la géométrie, ni les huit premiers étages, ni les données de combat des cinq ennemis n’ont changé. [Tests](Preuves/Tests.txt). |

La première rencontre a été filmée au niveau 14 avec les données normales. Pour atteindre la fin et contrôler son déclenchement, un profil privé utilisait le duo au niveau 50 et Kabutops à 1 PV ; les quatre Kabuto ont conservé leurs données normales. Ce n’est pas une mesure d’équilibrage. Le build, les sondes et les sauvegardes de capture ne sont pas livrés.

## Intégration locale

- [Patch](Cercle-des-vasques.patch) : `git am` sur `0403d9c79a51979ac5265f6723e883e96e9dfa96` (*La garde des vasques*).
- [Bundle du chantier](Cercle-des-vasques-complet.bundle) : nécessite la base `37138a7ca93be920e9c47963fea21441b153ec65`.
- Commit `a992df4680cc424b139b07514817adf7fdb1649d` sur `wip/reverie-integration-kingambit-cafe`. Patch réappliqué et import du bundle vérifié. [Sommes SHA-256](SHA256SUMS.txt). Aucun push ni publication.
