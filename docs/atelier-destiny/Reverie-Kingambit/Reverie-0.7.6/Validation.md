# Fosse Cascade Fond — version candidate 0.7.6

[Voir les deux corrections en jeu (18 s, avec son)](Sable-et-apres-duel.mp4) · [Notes de version](Notes-v0.7.6.md) · [Procédure de publication](Publier-v0.7.6.md)

## Ce qui change

- **Les deux Kabuto arrière surgissent du sable, pas de la berge.** Le cadre descend avant le premier nuage de terre. Les deux Kabuto remontent le passage et rejoignent leurs places d’origine dans le cercle, puis en arène. [Surgissement gauche](Preuves/Surgissement-arriere-gauche.png) · [Surgissement droit](Preuves/Surgissement-arriere-droit.png) · [Raccord à l’arène](Preuves/Raccord-arene.png).
- **Kabutops est au milieu dès le fondu d’après-combat.** Partenaire à gauche, héros à droite, trois ombres sur la même ligne à 32 px d’intervalle. Le cadre reste lisible avec les portraits. Les regards et les réactions sont décalés selon le *Cutscene Scripting Guide*. [Premier plan](Preuves/Trio-au-fondu.png) · [Réplique de Kabutops](Preuves/Kabutops-au-centre.png).
- Les quatre Kabuto s’enfouissent, l’arrière avant les flancs. Kabutops ne change pas de place : il part le dernier par Tunnel. Le duo libère l’axe de la descente de Nilo et de l’arrivée de Lyra, qui s’arrête devant lui sans le traverser. [Dernier Tunnel](Preuves/Tunnel-du-chef.png) · [Retrouvailles](Preuves/Nilo-et-Lyra.png).

## Vérifications

| Contrôle | Résultat |
|---|---|
| Première confrontation | Première rencontre au niveau 14, avec les PV normaux des cinq ennemis. Les deux nuages et les pieds des Kabuto arrière sont dans le sable visible. Même placement de départ dans l’arène ; approche complète en 87,32 s de jeu, dont 3,13 s de woosh. [Trace](Preuves/Premiere-confrontation.txt) · [Audio](Preuves/Audio-et-reperes.txt). |
| Revanche et victoire | Revanche courte à une réplique (7,82 s de jeu). Le [K.O. de Kabutops seul](Preuves/Kabutops-KO-garde-debout.png) ne termine pas le combat. La scène se déclenche après le cinquième K.O. Les cinq fuites, les retrouvailles et le [bilan natif](Preuves/Bilan-natif.png) ont été vus en jeu. La sauvegarde, le retour au centre de Réverie et le dialogue d’accueil sont confirmés. [Trace](Preuves/Victoire-et-retour.txt) · [Journal](Preuves/Journal-retour.txt). |
| Tests locaux | Tests Lua et Python de Fosse Cascade, échantillonnage du sable rendu et collisions, K.O., retour E2, générateur de ZIP différentiel et audits de cadrage. Aucun changement de carte, de tuiles, de statistiques du duel ou du moteur par rapport à `a992df4`. [Tests](Preuves/Tests-locaux.txt) · [Contrôles de la prise](Preuves/Raccord-et-coordonnees.txt). |

Prises faites dans PMDO 0.8.12 avec un profil local. Pour vérifier le déclenchement de la victoire, le duo était au niveau 50 et Kabutops partait à 1 PV ; les quatre Kabuto n’ont pas été affaiblis. Ce n’est pas un test d’équilibrage ou de défaite/reprise naturelle. Le rendu du retour en ville n’a pas été validé dans son intégralité : le profil réduit de capture affiche des ressources de remplacement dans le hub. Les sondes, les sauvegardes et ce profil ne font pas partie du commit.

## Livraison et état GitHub

- Candidat : `24be5673a76e06a9824102c5f106f091eb07070a` sur `wip/reverie-integration-kingambit-cafe`.
- [Bundle des sept commits](Destiny-v0.7.6.bundle) : import vérifié dans un dépôt de contrôle à partir de la base publique `37138a7ca93be920e9c47963fea21441b153ec65`.
- [Patch de la dernière retouche](Retouche-vasques-0.7.6.patch) : à appliquer sur `a992df4680cc424b139b07514817adf7fdb1649d` (*Le cercle des vasques*). Arbre réappliqué vérifié. [Sommes SHA-256](SHA256SUMS.txt).

**Non publié.** Le push tenté sans session GitHub disposant des droits d’écriture a échoué. La branche distante n’a pas bougé ; le build Windows n’a pas été lancé, et aucun tag ni ZIP de release 0.7.6 n’a été publié. [Résultat du push](Preuves/Publication.txt) · [Reprendre la publication sur le SHA exact](Publier-v0.7.6.md).
