# Audit pixel et raccords — avant la nouvelle passe

Base publiée : v0.5.5, commit `97847f618dd16d99f9475e75b74242c247146631`. Base et 93 banques re-téléchargées et contrôlées par empreintes Git ; les 10 cartes et 93 banques ont été sauvegardées avec CRC ZIP. Références Métano authentifiées à `Palikadude/Halcyon@1522c7a8b7a34d70078e11ed605b21d563b0dc51`.

Les corrections locales antérieures ont été reconstituées depuis les fichiers du commit exact et leurs scripts, puis contrôlées de nouveau sur les 10 cartes. Leur état cumulé est la base de cette passe ; aucune nouvelle publication n'a eu lieu.

## Stratégie d’audit

1. Compter chaque pixel des rendus de données, sans rééchantillonnage, en tenant compte de l’alpha ; documenter les couleurs, la provenance et les classes visuelles observables.
2. Scanner les onze couches, les coordonnées valides, les séquences, cadres et durées des dix cartes ; repérer des changements, trous et transitions à vérifier, sans confondre ombres, superpositions, transparence intentionnelle, limites et défauts.
3. Comparer pixels et modules aux ressources Métano authentifiées, mais ne pas exiger l’égalité géographique de deux layouts différents. Isoler les composants suspects et les inspecter, notamment autour des zones annotées.
4. Retoucher seulement les cas suffisamment démontrés avec des motifs natifs complets ou des séquences originales, sans effacer personnages, objets, événements, collisions ou animations. Pour toute surimpression, vérifier toutes les images et les autres couches.
5. Vérifier le delta et les dix variantes, puis test moteur/éditeur et CI si disponibles. Ne pas déclarer exhaustive une validation esthétique sur la seule base d'un scan automatique.

## Risques et limites

Un pixel de couleur rare n'est pas forcément incorrect : mélange alpha, ombre, objet, personnage ou effet légitime. Une ligne droite peut être voulue ; une animation peut être cachée ou fonctionner à une période différente. Un rendu de ressources ne reproduit pas forcément le gameplay et les effets moteur. Les animations ayant des durées et périodes différentes, quatre images générales ne suffisent pas à couvrir toutes les combinaisons de temps. Il ne faut ni recolorer globalement ni modifier la géographie pour satisfaire une métrique.
