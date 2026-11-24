# Les gemmes de Réverie — kit pour Destiny

**48 objets Méga, pour 46 Pokémon :** 47 Méga-Gemmes et la Météorite Delta de Rayquaza. Chaque objet a sa silhouette, sa palette et sa gravure. Les Dracaufites X/Y et les Mewtwoïtes X/Y ont chacune leur propre dessin. Un glyphe de **11 × 11** apparaît dans le sac et les dialogues ; un sprite distinct de **14 × 14** s’affiche lorsque la pierre est au sol. Les noms, effets, coûts, formes et IDs de l’addon ne changent pas.

**Textes en français :** avec la langue du jeu réglée sur Français, les 48 objets Méga ont une description française. Les variantes X/Y précisent la forme obtenue ; la Météorite Delta mentionne ses sept couleurs. Les textes par défaut sont conservés pour les autres langues.

**Baies :** Pêcha, Willia, Ceriz, Maron, Kika et Fraive utilisent désormais leurs propres dessins dans les menus et au sol. Les six sprites Destiny déjà présents ont été réutilisés à l’identique. Les anciennes descriptions vides indiquent maintenant l’effet déjà en place, soit +3 points de satiété ; aucune guérison d’état ni nouvelle apparition en donjon n’a été ajoutée. Pêcha reste la récompense de la devinette de Miette. Le correctif fait partie de **Destiny**, pas de l’addon Méga.

## Voir les dessins

- `Les-gemmes-de-Reverie.html` : galerie hors ligne, comparaison émoticône/sprite et descriptions françaises sous « Description FR ».
- `Planche-54-icones.png` : les 54 dessins de menu réunis sur une page.
- `Captures/` : sac, descriptions X/Y et message « Reçu : Baie Pêcha ! » capturés dans PMDO Linux 0.8.12, en banc isolé.

## Installer les fichiers du kit ZIP

1. **Dans le dépôt Destiny :** superposer `game/` et `addons/` à la révision `2a216fbee07421f0c0b06bca45afe0fb73d2d7ab` ou appliquer le bundle additionnel, si la révision est déjà présente. `game/Data/Item/index.idx` est un **index d’overlay de quête** ; il conserve les 19 gelées de Destiny et ajoute les résumés des six baies. Ne jamais le copier sur l’index complet `Data/Item/index.idx` d’un exécutable compilé. Pour un exécutable Destiny autonome, appliquer le lot au dépôt, puis régénérer le build selon sa procédure habituelle.
2. **Pour la quête PMDO 0.8.12 déjà installée comme mod :** superposer le contenu de `game/` à `MODS/Destiny/` si son overlay objet vient de la même révision. Ne pas modifier `Data/Item/` de la base PMDO. Si votre quête possède d’autres objets custom dans `index.idx`, fusionner uniquement les six entrées `berry_*` de ce lot au lieu de remplacer son index.
3. **Addon facultatif :** placer le dossier complet `addons/Mega_Stones_Reverie/` dans `MODS/` et l’activer. Ne pas laisser activés à la fois Mega Stones original et cette variante : UUID et namespace communs. Tester Pêcha est possible sans cet addon.
4. **Éditeur seulement :** `Editeur/Item_Icon.json` est la liste d’alias stock étendue. On peut l’installer dans `Editor/Aliases/` d’un PMDO stock, ou intégrer ses 54 nouvelles clés à sa propre liste. Aucun alias n’est nécessaire pour jouer.

### Mise à jour Git (au lieu de la copie ZIP)

Le bundle `Destiny-Icones-Mega.bundle` ajoute les icônes (`1d4b7a8`) et la traduction française (`3663086`) à la livraison Kingambit précédente `2a216fb`. Depuis une copie propre de la branche `dojos-kingambit-pmd` qui contient déjà `2a216fb` :

```sh
git bundle verify /chemin/vers/Destiny-Icones-Mega.bundle
git fetch /chemin/vers/Destiny-Icones-Mega.bundle refs/heads/dojos-kingambit-pmd
git merge --ff-only FETCH_HEAD
```

C’est une mise à jour locale ; elle n’a pas été publiée sur GitHub faute d’accès en écriture dans cette session. Le bundle `Destiny-Kingambit-PMD.bundle` de la livraison Kingambit est aussi à jour et contient l’ensemble des commits, à partir de la base d’intégration de Réverie.

### Compatibilité des polices

PMDO charge **une banque de police entière**, pas des glyphes répartis entre mods. Les deux dossiers contiennent donc les mêmes `Content/Font/text.font` et `text.zh-hans.font`, étendus à partir du stock 0.8.12. Les pixels, caractères et métriques de tous les glyphes préexistants sont conservés. Si un autre mod remplace la police de texte, fusionner les glyphes plutôt que de superposer deux polices incompatibles. Plage réservée par le kit : `U+E340`–`U+E375`, soit `Icon=672`–`725`.

## Sources

`Sources/Modeles-des-gemmes.tsv` : palette, silhouette et motif dessinés pour chaque objet. `Registre-icones.json` associe chaque ID aux deux visuels et aux deux polices. Les PNG à taille native sont dans `Dessins/` du ZIP. `Sources/generer_icones_mega.py` les convertit en `.dir` et en glyphes natifs tout en préservant les données non visuelles. `Sources/localiser_descriptions_fr.py` génère ou vérifie les 48 traductions sans modifier les autres champs. `Sources/banc_icones_*` documente le banc isolé (aucune instrumentation dans les scripts jouables). Les crédits de Mega Stones sont dans l’addon ; les baies conservent leurs crédits Destiny et SpriteCollab.
