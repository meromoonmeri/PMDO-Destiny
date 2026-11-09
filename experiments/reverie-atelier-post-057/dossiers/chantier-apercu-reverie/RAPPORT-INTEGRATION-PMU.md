# Intégration PMU — état local, non publiée

Base : Destiny v0.5.7 `ee39156a24f350b67e81740478be8505f4ff1a05`. Les 19 cartes et scripts concernés, et quatre variantes sud/historiques, ont été récupérés selon l'arbre Git puis sauvegardés dans `sauvegarde-cartes-interieurs-bassin-057.zip` (CRC valide). Les scripts locaux précédents ont été restaurés de leur archive CRC valide. Le rapport préalable `RAPPORT-PREALABLE-PMU-MAISONS-DRACO.md` reste applicable.

## Réalisation locale : maison d'équipe de la falaise

`travail/game/Data/Ground/maison_equipe_falaise.rsground` contient désormais un décor PMU **Tanren Traveller's Inn s1506** (serveur PMU 8fb424a / client c25c01f). Ses cinq calques sont reconstruits en tuiles PMDO 8×8 sans mise à l'échelle : 80 × 60 cases ; les cinq banques PMU effectivement utilisées sont déjà présentes dans l'arbre v0.5.7. Aucune référence graphique ne manque sur cette carte. Les animations de deux états comportent une cadence indicative de 15 frames, pas une cadence PMU authentifiée.

La carte conserve son identité, sa musique, les entités `LitEquipe`, `LitPartenaire`, `SortieMaison` et le marqueur `entree`. Lit d'équipe et lit partenaire restent des objets interactifs avec sauvegarde ; leur ancienne animation Hay_Bed est gardée et positionnée sur les deux zones de foin. L'entrée, les lits et la sortie sont déplacés dans la nouvelle géométrie. Les tuiles ayant le type PMU `Blocked = 1` sont bloquées ; les autres types, notamment `Scripted`, restent praticables mais leurs scripts ne sont pas convertis. Le contrôle de chemin statique atteint sortie et deux zones de lits ; les collisions fines avec les objets ne sont pas encore validées.

Dans le script local de la maison, une ancienne sauvegarde chargée à l'intérieur est déplacée une seule fois vers le nouveau seuil pour éviter une position désormais bloquée, avec le partenaire s'il est présent ; les chargements suivants conservent leur position. L'entrée normale marque le nouveau format. Ces protections ne constituent pas un test d'une vraie sauvegarde. La sortie revient encore sur `cliffdaytest` comme l'original : le parcours complet de nuit n'est pas raccordé et aucun éclairage nocturne n'a été intégré.

`integrer-maison-equipe-pmu.py` génère cette carte depuis les originaux vérifiés, la base standard PMU et `types-cartes-pmu.json` ; `test-maison-equipe-pmu.py` vérifie structure, références, seuils, migration simulée, sortie et lit sur doublures. Les tests précédents des scripts locaux restent PASS. Pas de test du moteur, de la sérialisation native, des transitions de nuit, de la musique réelle, du positionnement ou des collisions en jeu. Ne pas considérer la maison comme prête à publier.

## Six maisons de Réverie — reconstruction locale

Six cartes ont également été remplacées dans `travail/game/Data/Ground` par des cartes PMU standard, sans toucher aux données du dépôt distant : pierre `s1142`, feu `s1143`, plante `s1144`, normale `s1145`, eau `s1146`, électrique `s1373`. Chacune utilise ses cinq calques PMU et ne présente pas de référence manquante au contrôle. L'identité et la musique de chaque carte, les noms des entités, porte, marqueurs et partenaire sont conservés ; seuils repositionnés. La collision reprend uniquement les cases PMU `Blocked = 1`, sans convertir les scripts/types spéciaux PMU. Une migration locale sur chargement replace une seule fois au nouveau seuil le héros et le partenaire d'une ancienne sauvegarde. Les scripts d'origine continuent d'assurer les sorties et la continuité musicale.

`integrer-maisons-reverie-pmu.py` génère les cartes à partir des copies originelles et `test-maisons-reverie-pmu.py` vérifie références, dimensions, entités, sorties et migration sur doublures. Ce sont des **candidats intégrés au répertoire local**, pas des résultats testés en jeu : collisions d'objets, personnages dynamiques, transition et ancienne sauvegarde restent à vérifier. Les propositions de carte source sont visibles dans `maisons-pmu-candidates.png` ; la validation artistique au zoom jeu reste à faire.

## Encore à intégrer

- Hutte aquatique et auberge de Réverie (ainsi que le poste, qui n'est pas une habitation) : non remplacés. Tous les intérieurs : **mode nuit non réalisé** ; portes / sauvegardes / collisions restent à tester en moteur.
- L'auberge de la maison d'équipe en vraie variante nuit cohérente et retour correct vers l'extérieur jour/nuit : **non réalisés**. Aucune horloge jour/nuit générale n'a été identifiée dans les scripts Réverie examinés ; `JourneeVille` n'indique pas l'heure.
- Fusion physique et logique des deux secteurs et découpe sud de Réverie : **non réalisées**.
- Bassin et doyen Draco : **non réalisés**. La proposition de bassin sud antérieure était uniquement une maquette non intégrée et recouvrait des cases praticables ; l'ombre et l'effet de nage demandés doivent être localisés et reconstruits sans effacer un personnage ou des événements. Le Relicanth du bassin d'Halcyon est posé sur une rivière à quatre trames, mais aucun effet séparé de nage n'a encore été identifié.
- Intégration exhaustive des personnages/objets/animations PMU et correction des captures, ainsi que validation réelle des prototypes ACT / café / suivi et musique : **non réalisées**.

Aucune modification du dépôt distant, CI ou nouvelle release. Avant publication vérifier les droits des images PMU et les sorties d'intérieurs, compatibilité anciennes sauvegardes et rendu/sons dans PMDO 0.8.12, puis CI Windows.
