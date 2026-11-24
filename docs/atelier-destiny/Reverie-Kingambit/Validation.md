# Kabutops — Fosse Cascade Fond

**Correctif local** : `79a2534fbbb17d0dcaf421539ed9284e493cf84c`, sur `37138a7ca93be920e9c47963fea21441b153ec65` (WIP Réverie). Aucun push ni tag.

## Voir la scène

- [Première rencontre, avec le son de PMDO](Cinematique-Kabutops.mp4) — woosh vers **0:28**.
- [Revanche, avec le son de PMDO](Revanche-Kabutops.mp4) — woosh vers **0:07**.
- [Correctif Git](Retouche-Kabutops.patch) · [Bundle Git](Retouche-Kabutops.bundle)

## Ce qui a changé

Après relecture du *Cutscene Scripting Guide*, le partenaire repère Nilo, le héros réagit par ses gestes et les regards passent de la terrasse au gardien. Un seul éclair révèle Kabutops ; l’impact de sa faux déclenche le souffle et le recul du duo. Les répliques sont resserrées jusqu’à l’ultimatum. Après le duel, Kabutops sort par le sud et les regards suivent l’arrivée de Lyra.

Le woosh utilise les bandes natives `Pre_Battle` et le vrai bruitage `EVT_Battle_Transition`. L’arène prend le relais avec `Boss Battle 2.ogg`, sans relance de cette piste par le Lua. L’étage garde son nom dans le journal, mais ne génère plus de carton à l’entrée du duel. Les autres étages, le retour paisible et les cartes restent inchangés.

## Vérification

| Contrôle | Résultat |
| --- | --- |
| Tests Fosse et Statue Kangourex, audits des dialogues et du cadrage | OK. Le générateur régénère aussi dans un répertoire isolé le même segment d’arène sans carton. |
| Première rencontre et revanche sous PMDO 0.8.12, profil dédié, entrée directe aux vasques | OK. Bandes visibles et bruitage identifié dans les deux pistes audio enregistrées. L’arène est jouable, sans carton, avec la musique et les positions prévues. |
| Défaite en arène | Bilans et replay natifs, puis chargement de l’entrée de la Fosse. La revanche a été testée séparément avec sa phase de reprise. |
| Victoire et retour | En profil de test, Kabutops est mis à 1 PV pour déclencher la fin réelle du combat. Retrouvailles jusqu’au [bilan natif](Preuves/Bilan-victoire-PMDO.png), puis sauvegarde. Le centre de Réverie, absent du premier profil partiel, a été ajouté depuis l’archive du projet ; la sauvegarde a ensuite été rechargée jusqu’au dialogue d’accueil à Réverie. |

Les vidéos conservent le son et le temps de la capture. Le rendu de la VM de test est plus lent que les 60 images/s visées par le moteur, ce qui allonge visiblement les pauses. Les essais ne constituent pas une nouvelle traversée intégrale des huit étages ni une validation Windows.
