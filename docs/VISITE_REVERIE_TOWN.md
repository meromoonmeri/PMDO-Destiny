# Retour à Réverie Town et visite de la ville

Après les retrouvailles, le retour à deux emprunte le segment inverse de
Lost Wood (générateurs 7 → 1). Le duo débouche sur `cliffdaytest` au lever
du jour. Devant sa maison, le partenaire explique au héros qu’il n’a pas
connu ses parents et que tatie Kangourex l’a recueilli ; il présente ensuite
Réverie Town, les équipes de secours et d’exploration, puis le rôle des
guildes à travers le monde. Le héros répond par gestes, sans parler.

Au moment où le partenaire formule son rêve de guilde, la Team Dazzling
remonte le chemin du sud vers une mission à l’est. Adagio, Aria et Sonata
se présentent sous les sparkles et raillent les deux novices ; le héros
répond par une posture déterminée et le partenaire refuse de renoncer.
Après leur départ vers l’est seulement, le duo prend la route de la ville.

Ils gagnent ensuite la carte existante `WaterfallVillageCapital`, qui reste
une carte distincte de celles des falaises et du donjon. La visite est
déclenchée une seule fois par `SV.Destiny.VisiteVille` : une transition
interrompue reste reprenable ; la visite n'est marquée `terminee` qu'après
le dernier dialogue.

Le partenaire guide le héros à pied vers la place. La caméra présente ensuite
la boutique Kecleon, le stockage Kangourex, les étals colorés, les autres
comptoirs, les maisons au sud, les ponts et cascades, puis le grand bâtiment
au nord. Elle revient au héros et son suivi est rétabli. La scène utilise les
façades et la topographie de la carte native ; elle ne prétend pas que les
autres bâtiments ont déjà des services jouables.

La version town02 étendue contient 25 habitants, 7 objets au sol, 3
décorations animées et 2 marqueurs d'entrée. Le script réutilise les
Kecleon et Kangourex sérialisés (création en repli uniquement s'ils sont
absents) : Kecleon propose un petit assortiment de départ (Pomme, Baie Oran,
Baie Mepo) et Kangourex ouvre le stockage commun de l'équipe. Les autres
commerces et bâtiments ne sont pas encore raccordés. La statue Kangourex
plaçable est un objet séparé, documenté dans
`TUTORIEL_LOST_WOOD_ET_STATUE.md`.

## Carte native et copie de jeu

La source récupérée dans `town02-main_BACKUP` est
`WaterfallVillageCapital (1).rsground` (330 293 103 octets, MD5
`e5dc1889005b0d0ac39cf87d29ec3fa2`). Pour l'intégrer sous l'asset existant,
seuls les fins de ligne CRLF ont été normalisées en LF, `AssetName` a été
renommé `WaterfallVillageCapital`, et les entités de service/entrée ont reçu
des noms explicites (`Kecleon`, `Kecleon_Violet`, `Kangourex`, `Drifloon`,
`entrance`, `entrance_partner`). Le fichier intégré de 304 752 270 octets
(SHA-256 `3710d542711bb98f384e8b63748e994d0a0240131a62ac09790a9b8947b02952`)
reste conservé sous `payload/WaterfallVillageCapital.rsground.gz` et est
restauré par `tools/unpack_payload.py`. La carte possède 200 × 500 cases,
37 calques, 43 Tilesheets référencées, 25 habitants, 7 objets au sol et
2 marqueurs. Les dépendances et les limites sont dans
`UNIFICATION_DESTINY.md`.

Le chargement de la sérialisation originale a dépassé la mémoire disponible du
banc Linux. Pour le paquet de jeu uniquement, `tools/compacter_ville.py`
convertit **uniquement** les objets `AutoTile` aux quatre valeurs par défaut
vers `{}` ; le constructeur natif PMDO 0.8.12 recrée ces mêmes valeurs. La
copie conserve les dimensions, l'ordre et le contenu des calques, les tuiles,
leurs références et les animations. La source est vérifiée par SHA-256 avant
conversion ; une version éditée différente est refusée, jamais écrasée.
La restauration du payload refuse elle aussi d'écraser une carte existante
différente : comparez-la ou déplacez-la avant de reconstituer l'original.

La copie destinée au jeu fait 54 622 678 octets, SHA-256
`ff5b28e1c29bccb2e5c8a51b04c658df9de028e938f755dfaaa7a4f344442782`.
Le constructeur Windows l'installe après la fusion ; pour l'essayer
manuellement, utiliser deux chemins différents :

```text
python tools/unpack_payload.py
python tools/compacter_ville.py game/Data/Ground/WaterfallVillageCapital.rsground COPIE_DE_JEU/Data/Ground/WaterfallVillageCapital.rsground
```

Cette opération ne remplace pas la carte intégrée dans le dépôt. La copie
compacte est toujours un `.rsground` PMDO, pas une image ni une carte
recréée. La version étendue doit encore être parcourue en moteur réel pour
valider ses 37 calques, ses habitants sérialisés, ses marqueurs et la charge
mémoire. Sa grille d'obstacles contient 37 417 cases marquées `Tags: 1`,
mais les intérieurs et sorties de ville ne sont pas raccordés ; ces limites
préexistantes sont conservées plutôt que corrigées à l'aveugle.
