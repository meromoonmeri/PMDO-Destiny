# Les chemins de Réverie

Ce lot prolonge [Les foyers de Réverie](REVERIE_FOYERS.md). Il ne modifie ni les cinq intérieurs, ni le recrutement, ni l’identité du partenaire de l’équipe.

## Rencontres sur les chemins

Les quatre voyageurs apparaissent après la visite guidée et laissent la place à l’alerte de Nilo. Ils marchent entre des points vérifiés sur les chemins : pas de déplacement à travers les maisons, ni de halte sur un seuil. Interagir les arrête sur place, même en pleine marche. Ils reprennent leur tour après le dialogue.

| Voyageur | Où le trouver | Rencontre |
|---|---|---|
| **Mirabelle**, Skitty | Au centre, sur le chemin sous le grand escalier, à l’ouest du café | Accueillante ; parle des vieux ponts et offre une Baie Oran. |
| **Sureau**, Grainipiot | Dans le résidentiel, sur le sentier au nord de la Maison de Pierre | Bougon, mais attentif à ses voisins. Il évoque Nilo si on insiste. |
| **Tilleul**, Phanpy | À l’est de l’étang, sur le chemin de la terrasse | Enjoué et un peu rêveur ; offre une Pomme après son récit. |
| **Liane**, Kungfouine | Dans le résidentiel, à l’est du carrefour de la maison citrouille | Propose un duel facultatif. Le refus est le choix par défaut. |

Les cadeaux sont uniques par partie. Si le sac est plein et que l’objet ne peut pas être empilé, le voyageur le garde pour une prochaine rencontre. Les textes et trajets sont dans `reverie_itinerants_recits.lua` ; `reverie_itinerants.lua` gère les tâches de marche, les actions, et l’état `SV.Destiny.ItinerantsReverie`.

### Le duel de Liane

Le choix accepté charge une vraie carte de combat PMDO (zone technique `reverie_duel`, un étage). Votre équipe affronte une seule Kungfouine dans l’arène animée du Dojo Kingambit, selon les règles habituelles du moteur. L’entraînement ne rapporte pas d’EXP et ne consomme pas durablement les objets utilisés. Victoire, K.O. ou renoncement vous ramènent au lieu de la rencontre et changent la réponse de Liane. On peut la défier à nouveau. Au cas où le jeu est fermé pendant le combat, la sauvegarde préalable reprend en ville.

La carte d’arène au sol demeure inchangée. Sa version 24 px est générée avec `python tools/build_duel_reverie.py --source . --out CHEMIN_NEUF`. Elle conserve les collisions du décor, les flammes, la lueur du sceau et les cristaux animés. Le seuil de victoire repose sur `BeginBattleEvent` / `map_clear_check` ; la restauration de l’équipe sur `DungeonStakes.None`. Il n’y a pas de combat simulé par des dialogues.

## Le café Spinda

**Bulle** (Okéoké) mène l’échange à coups de questions et se reprend devant les caisses encore fermées. **Balou** (Qulbutoké) ponctue de « Banco ! » et d’un silence. Aborder Balou d’abord ne donne pas le même début qu’aborder Bulle. La dynamique s’inspire de la [version française d’Explorateurs du Ciel](https://www.pokepedia.fr/Qulbutok%C3%A9/Pok%C3%A9mon_Donjon_Myst%C3%A8re) ; le dialogue est original Destiny. Aucune nouvelle boutique, monnaie ou mécanique de recyclage.

## Le sud, après la maison isolée

La **maison ronde au toit brun**, seule sur la rive sud à l’est du pont central, n’est pas la maison citrouille de Nilo. La rivière et ses deux ponts, l’approche de la maison ronde et les chemins vers Pierre, Plante, Citrouille et l’escalier P sont conservés. Aucun nouvel intérieur n’est attribué à la maison ronde.

- Limite à `Y = 2976` px ; la dernière rangée est solide (`Y = 2968`). Largeur conservée à 1 600 px, origine et coordonnées des entrées inchangées.
- Les dix variantes de ville perdent 128 rangées. Les quelques couronnes d’arbres de la forêt qui débordaient au-dessus de la coupe sont retirées ; les arbres de la rive et le décor des maisons restent.
- Les anciennes cartes contenues dans une sauvegarde se rechargent. Si le héros se trouvait dans la zone supprimée, le duo revient à la sortie sud du pont central, du même côté de la rivière. Les états du scénario et des foyers restent intacts.
- Le chemin scénarisé de Nilo (Fosse Cascade) et les sorties d’exploration existantes ne sont pas remaniés.

Le recadrage se reproduit avec `python tools/rogner_sud_reverie.py PAYLOAD_076 REPERTOIRE_NEUF`. Pour reconstruire les cartes du dépôt, `python tools/unpack_payload.py` vérifie les nouvelles empreintes et n’écrase jamais une carte déjà présente. Dans un arbre de compilation réutilisé, déplacer d’abord les anciennes cartes générées et l’ancien index de tuiles, ou construire depuis une copie propre. La planche de l’arène est déjà versionnée et l’index de tuiles se reconstruit comme d’habitude.

## Vérification

```sh
python -m pip install Pillow ijson lupa
python tools/tests/test_chemins_reverie.py
python tools/tests/test_quartiers_reverie.py
python tools/tests/test_polish_reverie.py
python tools/tests/test_reverie_foyers.py
```

`test_chemins_reverie.py` vérifie les voies autour des passants, les accès de la rive sud, les ressources 24 px, les deux actions du café, le sac plein, les dons uniques et le retour du combat sur trois résultats. Il complète, mais ne remplace pas, un essai dans PMDO.
