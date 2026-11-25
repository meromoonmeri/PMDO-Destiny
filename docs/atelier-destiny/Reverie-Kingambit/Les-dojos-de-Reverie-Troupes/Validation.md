# Dojo Kingambit — le sceau et les troupes

**Révision locale `936b5623`** · sur la base DTEF `2e003fe9`  
18 types · 2 étages procéduraux + 1 finale par type

## Ce qui change en jeu

Après avoir choisi un dédale et confirmé, le héros et son partenaire rejoignent le **sceau orange du hall**. Une seule trappe s’ouvre sous eux, au centre du sceau (`384,270` en pixels monde). Le rebord passe devant leurs sprites pendant la descente. **Kaito reste à son poste** : ni déplacement, ni chute, ni déclenchement par contact. « Pas maintenant » est toujours sélectionné par défaut et ne lance rien.

Chaque finale oppose **un Pokémon évolué et deux pré-évolutions de la même lignée**. Les arrivées et leurs whooshes sont propres aux 18 types. Alakazam, Kadabra et Abra se montrent au fond avant de se téléporter ; Magirêve et les deux Feuforêve débouchent d’ombres ; les pétales de cerisier précèdent l’apparition de Florges, Floette et Flabébé. Le trio en scène est le trio combattu : il faut vaincre les trois adversaires.

Même géométrie DTEF, mêmes tuiles, mêmes obstacles et mêmes 36 étages procéduraux que dans la livraison précédente. Les cartes du hall, de Ledian, d’Ossatueur et du duel de Liane n’ont pas été modifiées.

## Livrables

| Fichier | Contenu |
|---|---|
| [Aperçu vidéo](Apercu-Dojo-Kingambit-Troupes.mp4) | 68 s : la trappe, les 18 entrées et la fin du combat Normal, capturées dans PMDO, avec le son du jeu. |
| [Registre des 18 troupes](Registre-des-18-troupes.png) | Une capture et la composition de chaque finale. |
| [Les-dojos-Troupes.bundle](Les-dojos-Troupes.bundle) | Candidat Git `dojos-troupes`, importable sur la base `37e6b5cd`. |
| [Troupes-depuis-DTEF.patch.xz](Troupes-depuis-DTEF.patch.xz) | Différentiel pour un arbre déjà sur `2e003fe9` ; application et inversion contrôlées. |
| [Sources-des-apparitions.zip](Sources-des-apparitions.zip) | Dessins bruts et références des trois motifs, provenance, planches de travail, outils et 18 Ogg. |

## Vérification

### Parcours complet — Normal

Le refus a laissé le duo au hall sans trappe. Après confirmation, le jeu a ouvert la trappe sur le sceau et chargé le 1F. Les deux étages procéduraux ont été franchis au clavier. La finale s’est ouverte contre **Fouinar** et **deux Fouinette**, tous à leurs PV maximum, sans modification des combattants entre l’arrivée et la victoire. La partie s’est poursuivie avec deux ennemis, puis un seul ; `Cleared` n’est arrivé qu’au dernier K.O.

EXP **591 → 667 → 815** entre le hall, les deux étages et l’arrivée en finale ; **815** au retour, au niveau **19**, avec **45/45 PV** et le sac conservé. Le retour au hall, la sauvegarde, puis le redémarrage de PMDO ont été vérifiés. Le **+** de Normal était toujours affiché après la reprise.

Le candidat scellé a également été rejoué depuis les deux côtés de Kaito : départ gauche vers Normal et départ droit vers Fée. Dans les deux cas, le duo a rejoint les mêmes positions au sceau, Kaito n’a pas bougé et un seul effet d’ouverture s’est déclenché. L’abandon au 1F a rendu le sac et les 815 EXP.

### 18 finales et son natif

Pour isoler les introductions, le banc a chargé directement les finales. Cela vérifie la mise en scène et les adversaires dans le moteur, et ne constitue pas 18 parcours complets. Les whooshes ont été enregistrés depuis la sortie audio de PMDO, puis comparés aux 18 fichiers de référence. Aucun son d’intro n’a été ajouté au montage. Les 18 retours par le menu Abandonner ont conservé l’EXP et le sac. Les introductions et le combat Normal ont été testés séparément de la génération des **162 étages** (18 types × 3 étages × 3 graines).

Les preuves sont dans [`Preuves/`](Preuves/) : traces, correspondances audio des captures et du montage final, captures de la reprise, dix suites locales réussies, reproduction binaire et contrôle de l’import Git.

## Import local

Dans un clone du dépôt de jeu contenant `37e6b5cd`, remplacer `<chemin>` par le chemin du dossier livré :

```sh
git bundle verify "<chemin>/Les-dojos-Troupes.bundle"
git fetch "<chemin>/Les-dojos-Troupes.bundle" refs/heads/dojos-troupes:refs/heads/dojos-troupes
git switch dojos-troupes
```

**Ni push ni release distante.** La branche GitHub d’intégration était encore à `37e6b5cd` au dernier contrôle ; la simulation d’envoi a échoué faute d’authentification. Le bundle n’est pas un jeu autonome : il s’intègre au dépôt et utilise l’installation complète de PMDO.
