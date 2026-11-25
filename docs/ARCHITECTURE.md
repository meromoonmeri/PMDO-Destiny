# Architecture autonome de Destiny

## Principe

Le projet sépare le **moteur**, les **données PMDO de base** et le **jeu Destiny**, tout en les distribuant dans un seul dépôt.

```text
PMDO-Destiny/
├── engine/                 # Code C# complet du moteur
├── base/                   # Runtime PMDO 0.8.12
├── game/                   # Quest Destiny
│   ├── Content/
│   ├── Data/
│   │   ├── Ground/
│   │   ├── Map/
│   │   ├── Zone/
│   │   └── Script/destiny/
│   ├── Strings/
│   └── Mod.xml
├── art/
├── tools/
└── docs/
```

Les Grounds, les maps de donjons, les zones, les ressources et les scripts sont séparés. Le dépôt contient aussi le moteur et les données runtime nécessaires.

## Pourquoi aucun sous-module ?

PMDC utilise normalement RogueEssence, FNA, NLua et d'autres dépendances comme sous-modules. Leur contenu a été matérialisé dans `engine/` aux commits enregistrés dans `SOURCE_LOCK.json`. Un clone ou un ZIP GitHub contient donc directement le code attendu, sans `git submodule update`.

## Pourquoi aucun Git LFS ?

Tous les fichiers source sont inférieurs à la limite GitHub de 100 Mio. Aucun pointeur LFS n'est utilisé. Le ZIP Windows compilé est distribué comme artefact/release et non comme objet LFS.

## Lancement dédié

Pendant la construction, PMDO exécute `-quest Destiny -build`. Cette commande native fusionne les données de base et la quest dans une installation standalone.

Le paquet Windows contient alors :

- `Destiny.exe`, produit depuis PMDC ;
- les données PMDO et Destiny déjà fusionnées ;
- les scripts des namespaces `origin` et `destiny` ;
- `JOUER_A_DESTINY.bat`, qui exécute simplement `Destiny.exe`.

Le paquet final n'a plus besoin de `MODS/` ni du paramètre `-quest`. L'utilisateur n'a ni à installer un PMDO générique ni à sélectionner manuellement un épisode spécial.

## Écran-titre

PMDO dessine `Content/UI/Title.png` au-dessus du fond de titre. Destiny utilise une image opaque de 320 × 240 pixels, couvrant toute la surface interne du jeu. Le fichier source haute définition est conservé dans `art/`.

## Point de départ

`game/Data/StartParams.xml` dirige la nouvelle partie vers :

- zone : `destiny_hub` ;
- segment : `-1`, donc un Ground fixe ;
- ID : `0`, première entrée de `GroundMaps` ;
- entrée : `0`, premier marqueur de la map.

`destiny_hub.json` déclare `GroundMaps: ["destiny_hub"]`, et `index.idx` rend cette zone visible par le moteur.

## Scripts et sauvegarde

Les scripts Destiny se trouvent sous `Data/Script/destiny/`. Ils peuvent utiliser les modules PMDO de base, notamment `origin.common`.

`scriptvars.lua` ajoute seulement les valeurs propres à Destiny et replace le checkpoint sur la clairière. Il ne réinitialise pas la table `SV` de la base.

## Limite actuelle

La clairière est un socle technique sans issue de donjon ni chapitre. Les futures maps devront être ajoutées avec leurs zones, transitions, scripts et ressources. La première version vérifie le pipeline autonome ; elle ne prétend pas encore fournir une campagne complète.
