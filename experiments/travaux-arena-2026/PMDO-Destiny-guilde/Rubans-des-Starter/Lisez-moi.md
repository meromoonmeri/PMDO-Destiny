# Destiny — Rubans des starters

**86 choix de départ (81 espèces), 9 teintes et « Sans ruban ».** Toutes les formes du vrai quiz sont incluses, notamment Miaouss, Goupix d’Alola, Caninos de Hisui, les deux Farfuret, les deux Zorua et les deux Axoloto. Ni objet tenu ni bonus de combat : le ruban est un accessoire purement visuel.

## Essayer sans rien installer

Ouvrez **`Vestiaire-des-Starters.html`**. Choisissez le héros ou le partenaire, la forme et la couleur. Les flèches font le tour des huit directions ; **Marche** et **Nuit** montrent le mouvement et l’éclairage. Les sprites d’attente et de marche proviennent des `.chara` de Destiny. L’aperçu fonctionne sans réseau et ne modifie pas une sauvegarde.

Le fichier **`Rubans-en-jeu.png`** montre le menu et deux rubans effectivement portés dans le réfectoire de la guilde, en jour et en nuit.

## Porter le ruban dans le jeu recompilé

1. Sur une carte au sol, ouvrir **Équipe → Pokémon → Ruban**.
2. **Haut/Bas** change la teinte surlignée ; **Gauche/Droite** tourne le sprite. Le surlignage ne change pas la tenue tant que le choix n’est pas validé.
3. Valider une teinte ou choisir **Sans ruban**. L’annulation ne change rien. Il est possible d’habiller séparément les deux membres du duo.
4. Sauvegarder normalement. Le ruban reste affiché au sol et en donjon ; le changement de couleur se fait hors donjon.

Les fondateurs gardent l’accès après évolution. Un starter recruté qui a déjà porté un ruban le garde aussi. Une sauvegarde sans champ de ruban démarre sans coloris imposé ; aucun paquet d’objets ni fichier `.chara` à remplacer.

## Intégrer aux sources de Destiny

Le patch a été construit sur **`8f80c6e2c47e681acd334be661d601a59fed2367`**, branche `wip/reverie-integration-kingambit-cafe`. À la racine d’une copie de travail propre de Destiny, après avoir sauvegardé vos données de jeu :

```sh
git apply --check /chemin/vers/Rubans-Destiny.patch
git apply /chemin/vers/Rubans-Destiny.patch
```

Puis reconstruire Destiny avec la procédure de build du projet (.NET 8 ; `build_windows.bat` pour la distribution Windows). Le patch contient à la fois le moteur C# et les scripts Lua. Il **ne s’installe pas par-dessus le seul `Destiny.exe`**. Le moteur a été compilé et essayé sur un banc Linux/FNA ; aucun exécutable Windows fourni, aucune publication GitHub ni modification de votre installation.

## Fonctionnement

- **Un seul roster.** Le quiz et l’enregistrement de l’éligibilité partagent la même fonction Lua. L’ordre et l’interdiction de reprendre l’espèce du héros dans le choix du partenaire restent inchangés.
- **Le vrai sprite.** Pose au col, sous le col ou attache courte à l’épaule suivant le corps du Pokémon. Le calque utilise la tuile, le miroir, les décalages, la hauteur et les repères du sprite réellement en cours d’affichage. Le nœud doit toucher un pixel visible de la silhouette.
- **Respect du rendu.** Le ruban suit la teinte ambiante, reçoit le filtre nocturne natif et disparaît avec une animation invisible. La forme de camouflage n’affiche pas le ruban du Pokémon caché.
- **Persistance indépendante.** Un identifiant de teinte est stocké dans `CharData`, pas dans le sac et pas dans un index d’équipe. Le jeu sans couleur choisie conserve le rendu d’origine. Les options du scénario ne sont pas ajoutées au mode Rogue ni aux reprises de replay.

## Vérifications et fichiers

- **`Starters-eligibles.tsv`** : liste complète espèce, forme, génération et profil d’attache.
- **`Verification-rendu.json`** : contrôle sur les banques `.chara` exactes du commit, au repos et en marche. 774 combinaisons genre/skin (replis compris), 28 168 nœuds contrôlés, 1 232 images rendues dans le banc FNA, dont 336 via les actions de donjon.
- **`Verification-integration.json`** : essai réel au réfectoire avec Pikachu et Goupix d’Alola, choix distincts dans le menu, objet tenu préservé, déplacement, sauvegarde et reprise après redémarrage.
- **`Verification-vestiaire.json`** : interface hors ligne, rendu des 86 choix, navigation, retrait, rendu mobile et lecteur isolé.
- **`Sources/` et `Tests/`** : sources du patch, de l’aperçu et du banc. Le script de test `Banc-jeu.lua` est réservé au banc isolé ; **ne pas l’intégrer au jeu final**.

### Crédits

Les sprites restent ceux de [Destiny, crédits des sprites et du moteur](https://github.com/meromoonmeri/PMDO-Destiny/blob/8f80c6e2c47e681acd334be661d601a59fed2367/CREDITS.md) et de leurs auteurs respectifs (dont SpriteCollab). Les masques de ruban et les rampes de teinte sont propres à cet atelier. Aucun sprite de ruban de Halcyon n’a été utilisé.
