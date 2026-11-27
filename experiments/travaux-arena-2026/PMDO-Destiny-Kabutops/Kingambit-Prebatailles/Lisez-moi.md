# Dojo Kingambit — les 18 prébatailles

Un woosh différent pour chaque finale, dans l'esprit du **Fight Woosh étoilé de la Team Dazzling**. Les bandes se croisent, portent un signe propre au type et s'effacent. La scène Fée rend hommage aux étoiles de Dazzling ; les autres signatures changent aussi de trajectoire, de motif et d'accent sonore. Aucun pixel ni son de Dazzling n'est repris.

## Voir et entendre

`Les-18-prebatailles-dans-PMDO.mp4` (à côté de l'archive) montre les dix-huit wooshes, avec un chapitre par maître et le **son enregistré dans le jeu**. `Preuves/Planche-des-18-dans-PMDO.jpg` réunit un instant de chaque capture. Le registre des signatures se trouve dans `docs/KINGAMBIT_PREBATAILLES.md`.

Le woosh suit l'apparition du maître et des deux cadets. Il dure **1,40 s** à 60 i/s et disparaît avant le lancement natif du combat. Il ne remplace pas les entrées : cyclones Dragon/Vol, pluie Eau, canicule Feu et autres apparitions restent en place. Les cartes, équipes, mécaniques, musiques et événements Dazzling sont inchangés. La fusion **Éclipse X — Prisme fendu** validée est conservée séparément comme aperçu ; ce lot n'installe pas de nouvel effet Méga.

## Intégrer au dépôt

**Base :** branche `dojos-cyclones-meteo`, commit `79ddccca57331787d145eda262773fb50fd944e0`. **Delta :** `dojos-prebatailles`, commit `7fcd0610402958c2d2262c2d1093e459097d13af`. Aucun push.

Sur une copie propre à cette base, choisir **une** des deux voies :

```sh
# A. Récupérer le commit scellé (chemin absolu de l’archive extraite)
git fetch /chemin/Integration/Prebatailles.bundle dojos-prebatailles:dojos-prebatailles
git switch dojos-prebatailles

# B. Depuis la base Cyclones–Météo, appliquer le patch binaire
xz -dc /chemin/Integration/Prebatailles-depuis-Cyclones-Meteo.patch.xz | git apply --index
```

`game/` contient aussi les 36 ressources et les deux Lua du delta pour intégration à la main dans un checkout correspondant. Ne pas écraser `event.lua` sur une autre base : reprendre seulement l'enveloppe du callback `DestinyDojoTroupeJouer`. Pour une autre version du jeu, préserver l'ordre apparition → prébataille → `BeginBattleEvent` et valider `DungeonScene.ViewRect`. L'archive n'est pas un build Windows autonome.

## Contrôles

Le **banc PMDO Linux 0.8.12** ouvre directement les dix-huit finales avec les vrais scripts, cartes, sprites et BG. Les étapes en amont sont sautées par le banc, pas les événements des finales. Chacune est filmée : position de l'overlay sur le décor, image attendue, Ogg entendu, puis `map_clear_check` actif et trois combattants à leurs positions d’origine après `BeginBattleEvent`. `Preuves/` contient le journal, les mesures image-son, le contrôle des banques, les vérifications Lua et le test d'aller-retour du patch. Aucun test de parcours depuis le hall ou de build Windows n'est revendiqué ici.

Sources de dessin, synthèse, capture et montage sous `Sources/`. `Index-Prebatailles.json` identifie les paires de banques `Kingambit_Prebataille_<type>`. Le fichier `MANIFESTE-SHA256.txt` dans le ZIP permet de les vérifier.

## Crédits

- Référence de rythme et de superposition : `Pre_Battle_Dazzling_Etoiles` et `jouer_woosh_dazzling` dans la scène `cliffdaytest` de PMDO-Destiny. La version d'origine reste intacte.
- Rendus : dessins pixel et synthèse construits pour ce lot, sans image ni échantillon pris au woosh Dazzling. Moteur de capture : PMDC/RogueEssence ; tuiles et sprites d'arène déjà présents dans Destiny/PMDO, avec leurs crédits d'origine. Pokémon appartient à Nintendo, Creatures et GAME FREAK.
