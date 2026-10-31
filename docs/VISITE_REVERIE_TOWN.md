# Retour à Réverie Town et visite de la ville

Après les retrouvailles et le retour à deux dans Lost Wood, le partenaire invite
le héros à le suivre. Ils quittent le croisement nocturne ; à l'aube ils
arrivent dans la carte existante `WaterfallVillageCapital`, qui reste une
carte distincte de celles des falaises et du donjon. La visite est déclenchée
une seule fois par `SV.Destiny.VisiteVille` : une transition interrompue reste
reprenable ; la visite n'est marquée `terminee` qu'après le dernier dialogue.

Le partenaire guide le héros à pied vers la place. La caméra présente ensuite
la boutique Kecleon, le stockage Kangourex, les étals colorés, les autres
comptoirs, les maisons au sud, les ponts et cascades, puis le grand bâtiment
au nord. Elle revient au héros et son suivi est rétabli. La scène utilise les
façades et la topographie de la carte native ; elle ne prétend pas que les
autres bâtiments ont déjà des services jouables.

Deux habitants sont créés à l'exécution, sans éditer le ground source :
Kecleon propose un petit assortiment de départ (Pomme, Baie Oran, Baie Mepo)
et Kangourex ouvre le stockage commun de l'équipe. Les autres commerces et
bâtiments ne sont pas encore raccordés. La statue Kangourex plaçable est un
objet séparé, documenté dans `TUTORIEL_LOST_WOOD_ET_STATUE.md`.

## Carte native et copie de jeu

Le fichier d'origine de 233 727 831 octets reste conservé sans modification
sous `payload/WaterfallVillageCapital.rsground.gz` et est restauré par
`tools/unpack_payload.py`. Son empreinte reste
`afc5081f7348b2afed306953bf5e66a358e442cb00f93fa139ec239cf94c98ee`.
La carte native possède 200 × 500 cases et 28 calques, sans entités ni
collisions bloquantes placées par son auteur ; ces propriétés ne sont pas
réinventées. Les dépendances et les limites sont dans `UNIFICATION_DESTINY.md`.

Le chargement de la sérialisation originale a dépassé la mémoire disponible du
banc Linux. Pour le paquet de jeu uniquement, `tools/compacter_ville.py`
convertit **uniquement** les objets `AutoTile` aux quatre valeurs par défaut
vers `{}` ; le constructeur natif PMDO 0.8.12 recrée ces mêmes valeurs. La
copie conserve les dimensions, l'ordre et le contenu des calques, les tuiles,
leurs références et les animations. La source est vérifiée par SHA-256 avant
conversion ; une version éditée différente est refusée, jamais écrasée.
La restauration du payload refuse elle aussi d'écraser une carte existante
différente : comparez-la ou déplacez-la avant de reconstituer l'original.

La copie destinée au jeu fait 45 877 096 octets, SHA-256
`2d755a510cb2fb923cc7acdb7803d4b9a6a10d2908dcba13a0114466d69187e9`.
Le constructeur Windows l'installe après la fusion ; pour l'essayer
manuellement, utiliser deux chemins différents :

```text
python tools/unpack_payload.py
python tools/compacter_ville.py game/Data/Ground/WaterfallVillageCapital.rsground COPIE_DE_JEU/Data/Ground/WaterfallVillageCapital.rsground
```

Cette opération ne remplace pas la carte native dans le dépôt. La copie compacte
est toujours un `.rsground` PMDO, pas une image ni une carte recréée. En moteur
Linux PMDO 0.8.12, la visite a été parcourue jusqu'au retour de la caméra et du
contrôle ; un achat chez Kecleon ainsi qu'un dépôt et un retrait chez Kangourex
ont également été vérifiés. Les tests utilisaient une équipe et des positions
de départ préparées pour l'essai. Un essai Windows reste nécessaire. La carte
reste exigeante en mémoire, même compactée. Ses collisions natives sont vides :
le joueur peut traverser des éléments du décor. Les intérieurs et sorties de
ville ne sont pas raccordés ; ces limites préexistantes sont conservées plutôt
que corrigées à l'aveugle.
