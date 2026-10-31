# Reconstituer la quête complète (254 cartes) à partir de cette branche

État visé : **254 `.rsground`** dans `game/Data/Ground`, **1 164 `.tile`** dans
`game/Content/Tile`, 36 fonds parallaxe dans `game/Content/BG`.

## 1. Cartes — automatique

```bash
git checkout destiny/quete-230-cartes
python3 tools/restaurer_cartes.py .           # 230 cartes, 3,63 Go restaurés, SHA-256 vérifiés
```

Le script contrôle aussi la présence des 1 164 planches et liste les manquantes.

## 2. Planches `.tile` — depuis l'archive Drive

925 Mo, compression x1,5 seulement : elles ne sont pas versionnées. Elles viennent
de deux sources, toutes deux déjà sur le Drive « PMD Destiny Quest 247 » :

| source | planches |
|---|---|
| `PMD_Destiny_Map_Quest_247_0812.zip` (SHA-256 `45bbdce3…80216be`) | 1 090 |
| livraison d'origine de la quête (planches propres : falaise, chemins, cafés Métano…) | 142 |

Union = 1 164. Contrôle : `ressources/PLANCHES/manifest.json` donne pour chacune
son nom, sa taille et son SHA-256.

## 3. Fonds parallaxe et zones — depuis la même archive

```
destiny/Content/BG/*.dir          -> game/Content/BG/          (36 fonds)
destiny/Data/Zone/exploration_cartes.json -> game/Data/Zone/   (zone de dev « exploration des cartes »)
```

`game/Data/Zone/index.idx` doit ensuite déclarer `exploration_cartes` : recopier
l'`index.idx` de l'archive, ou supprimer le fichier pour que PMDO le reconstruise.

## 4. Résultat attendu

```
game/Data/Ground   254 fichiers   (24 d'origine + 230 restaurées)
game/Content/Tile  1 164 fichiers
game/Content/BG    36 fichiers
```

## 5. Ce qui restera cassé, et pourquoi

- **2 planches introuvables** : `InsideHut` (utilisée par `destiny_hub`) et
  `Treasure_Town_Cafe`. Absentes de l'archive 247, des branches du dépôt et de la
  livraison d'origine. Non remplacées, non inventées : ces cartes restent vides.
- **`Content/Tile/index.idx`** copié de l'archive n'indexe pas les 74 planches
  propres à la livraison d'origine ; PMDO le régénère au démarrage.
- **229 cartes sans entrée de zone** : c'est le fonctionnement de l'archive
  (rattachement à la zone de dev `exploration_cartes`), aucune zone n'a été inventée.
- `WaterfallVillageCapital.rsground` (223 Mo) dépasse la limite de 100 Mo de GitHub :
  il est fourni en `.gz` (2 Mo) et restauré par le même script.
