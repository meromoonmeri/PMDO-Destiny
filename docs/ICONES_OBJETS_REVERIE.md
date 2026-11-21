# Icônes d’objets de Réverie

Ce lot relie **47 Méga-Gemmes et la Météorite Delta** à des dessins uniques en pixel art. Les 48 objets concernent 46 Pokémon ; Dracaufeu et Mewtwo ont chacun deux pierres X/Y distinctes. Les dessins se lisent en [planche](../art/previews/icones_objets_reverie/Planche-54-icones.png).

## Ressources natives PMDO 0.8.12

| Affichage | Liaison | Taille |
| --- | --- | --- |
| Sac, messages, dialogue de récompense | `Icon` de la fiche et de son résumé dans `Data/Item/index.idx` | 11 × 11 px |
| Objet posé au sol | `Sprite` de la fiche vers `Content/Item/*.dir` | 14 × 14 px pour les pierres |

Les `Icon` **672–719** correspondent à `U+E340`–`U+E36F`. Les `Icon` **720–725** (`U+E370`–`U+E375`) couvrent **Willia, Ceriz, Maron, Pêcha, Kika et Fraive**. Pêcha garde l’ID `berry_pecha` et est toujours donnée par la devinette du foyer de pierre. Pour les six baies, les sprites Destiny existants sont raccordés et la description vide est remplacée par l’effet actuel (+3 points de satiété). Le champ `Released`, les événements d’usage et les spawns ne changent pas. Oran, Sitrus et les autres objets ne sont pas modifiés.

L’addon [`Mega_Stones_Reverie`](../addons/Mega_Stones_Reverie/DESTINY.md) est toujours facultatif. Les scénarios et effets des Méga-Gemmes, y compris les formes X/Y, ne sont pas modifiés. Les versions de `text.font` et `text.zh-hans.font` sont **identiques dans `game/` et dans l’addon** : quand celui-ci a priorité, son atlas contient aussi les baies. Un mod tiers remplaçant ces polices complètes peut nécessiter une fusion ; le moteur ne combine pas les glyphes. Les atlas PMDO d’origine, sauf la zone ajoutée, et toutes leurs métriques sont conservés.

`game/Data/Item/index.idx` conserve ses résumés de gelées. C’est un overlay de **quête**, pas l’index global d’un jeu autonome. Pour un build compilé, laisser la fusion d’index à PMDO ; ne pas écraser l’index compilé avec ce fichier partiel.

## Reproduire les banques générées

Depuis un checkout complet, avec Python 3, `Pillow` et `numpy` :

```sh
python tools/icones_mega/generer_icones_mega.py --destiny . --out /tmp/icones-reverie
```

La source des palettes et gravures est `tools/icones_mega/Modeles-des-gemmes.tsv`. Le programme charge les deux polices et les fiches de baies stock **0.8.12** depuis `base/` (ou `--stock /chemin/vers/PMDO`). Il produit `Destiny/`, `AddOn/`, les PNG, un registre de correspondances et un alias d’éditeur optionnel, sans modifier le dépôt. L’éditeur lit cet alias dans `Editor/Aliases/Item_Icon.json` de l’installation de base, pas dans le dossier de l’addon. Fusionner les nouvelles clés si un alias personnalisé existe.

Le banc de contrôle utilise un profil temporaire PMDO Linux 0.8.12 et une carte d’essai. Pour le rendre reproductible, les scripts de capture sont dans `tools/icones_mega/`. Ils vérifient la résolution de chaque `.dir` et la présence du dessin dans le vrai `ItemMenu` en comparant les pixels opaques des captures. Le test Pêcha appelle le script de foyer inchangé et répond « Un trou » via le menu ; il contrôle l’émoticône de « Reçu : … » et l’ajout unique de la baie. Ce banc ne remplace pas un test du build Windows complet de Destiny.
