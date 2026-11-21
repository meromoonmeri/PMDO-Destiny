# Réverie Town — Le carnet des retours

Lot suivant la 0.7.6, développé à part depuis le commit `37e6b5c`. Il concerne les habitants **extérieurs des cartes de Réverie Town**, depuis le nord fusionné jusqu’à l’étang. Les intérieurs, la Guilde et les donjons gardent leur scénario et leurs services.

## Ce qui change dans la ville

| Moment | Transformations visibles et quelques rencontres |
| --- | --- |
| **Retour des Bois Perdus** | Le retour des Bois et l’épisode des Dazzling conduisent à la visite guidée, qui reste intacte. Une fois ce jalon atteint, Pip descend du côté des étals, Céleste change de poste et Azur et Ondine inventent leur façon de compter les retours. Sur le parcours principal, l’alerte déclenchée à la fin de la visite prend la priorité immédiatement. |
| **Alerte de Lyra** | Azur guette à l’est, Ondine attend près de la hutte, Gustave libère la petite allée. À la place, Rose, Nino et Marcel défont les rubans pour dégager le passage. Au café, Suzie, Capucine et Moka préparent une part à emporter, pas une fête. Lyra reste joignable à la place puis à la sortie E2 avec son menu d’origine. |
| **Après l’accueil de Nilo** | Léo, Lyra et Nilo se retrouvent dans le résidentiel, où le dessin de Nilo devient une petite scène. Pip et Ondine se donnent rendez-vous à l’étang et quittent le centre sans double. Sur la place, le dernier nœud de la guirlande, le bol de Margot et l’ardoise de Zig et Zag racontent le retour chacun à leur manière. |
| **Première sortie réussie du Passage Aquatique** | Un épisode indépendant, sans spoiler si la crique est visitée plus tôt. Pip et Ondine changent de berge à l’étang ; les habitants parlent du sel dans les sacs, des nouveaux repères ou des cartes mouillées. Une alerte active retarde cette chronique, mais ne l’efface pas. |

Les 26 habitants natifs et les 7 habitués ajoutés par script ont chacun une réplique par jalon (y compris Nuage, dont l’identifiant natif est vide). Nilo rejoint la liste après le sauvetage. Les comptoirs, le pêcheur et le garde ne déménagent pas : ils participent aux saynètes ou répondent sur place. Lyra est une seule habitante, même lorsque le scénario emploie son instance d’alerte. Aucune récompense supplémentaire ni condition de quête n’est ajoutée.

## Intégration

- `destiny/reverie_recit.lua` contient les répliques, les saynètes et les postes narratifs. Le moment de la chronique est dérivé de `RetourAccompli`, `CombatDazzling`, `VisiteVille`, `AlerteShinx` et des flags de l’accueil/sauvetage déjà présents. Sieste, mission libre, abandon et K.O. ne changent pas ces chapitres. Les anciennes sauvegardes reprennent au bon jalon sans rejouer la visite ou l’accueil pour remplir un nouveau compteur.
- `destiny/reverie_saynetes.lua` lance les échanges à l’interaction, **pas au chargement**. Cadrage sur les habitants réellement présents, regards décalés, pauses, émotes et pas court de Pip si le terrain est libre. Réplique seule si un voisin est absent ou hors champ ; caméra, regards et IA rendus au jeu. `SV.Destiny.SaynetesReverieVues` empêche le rejeu au même jalon, y compris via l’autre interlocuteur d’un duo. Un échec de mise en scène ne consomme pas la scène.
- `WaterfallVillageCapital/init.lua` applique les postes après la visite/l’accueil ou avant le fondu d’entrée. Les deux habitants qui changent de quartier sont réutilisés ou créés par le script, avec un seul propriétaire à chaque jalon. Le test de pose garde les 16 px de collision, respecte les seuils et cherche un poste voisin si le joueur ou le partenaire occupe l’ancre. Aucun asset de carte/tuiles, comptoir, choix d’achat ou sortie ne change.
- `PassageAquatiqueTermine` est enregistré seulement au retour d’une vraie expédition réussie depuis la crique, avant le bilan natif. Une ancienne partie dont le jeu n’avait pas conservé ce jalon le récupère à la prochaine sortie réussie.

Références : `Base Camp` de PMDO pour la lecture des états `SV` à la pose des habitants ; *Cutscene Scripting Guide* pour les regards, les temps de réponse et les portraits placés selon le cadre. Les aides Destiny gardent leur rendu à 320 × 240.

## Contrôles reproductibles

```sh
python -m pip install lupa ijson Pillow
python tools/tests/test_reverie_recit.py
python tools/tests/test_visite_marchands.py
python tools/tests/test_habitants_quartiers.py
python tools/tests/test_plage_sablefin_integration.py
```

Le premier contrôle charge les obstacles des cartes publiées puis exécute les scripts de ville avec des doubles de PMDO. Il vérifie les répliques pour les quatre jalons, les postes et leurs chemins, l’absence de doublons, la persistance, les comptoirs, un passage à l’étang, le vrai choix de phase et le retour de caméra après une interruption simulée. Il ne remplace pas un essai avec les sprites, la caméra et les menus du moteur.
