# Quest Destiny

Ce dossier est temporairement copié dans `MODS/Destiny/` pendant la construction, puis la commande native `-build` de PMDO le fusionne avec la base pour produire le jeu standalone.

- `Mod.xml` : identité, UUID et namespace `destiny`.
- `Data/StartParams.xml` : héros de départ et map initiale.
- `Data/Ground/` : Grounds fixes — 24 cartes importées plus `destiny_hub`.
- `Data/Map/` : futures maps de donjons (aucune pour l'instant : le périmètre importé ne contient que des Grounds fixes).
- `Data/Zone/` : une zone par Ground, plus `index.idx` (25 entrées).
- `Data/Script/destiny/` : scripts Lua de la quest, un `init.lua` par Ground.
- `Content/Tile/` : 142 tilesets (`.tile` autonomes, PNG embarqués).
- `Content/Object/` : 7 animations d'objets référencées par les cartes.
- `Content/UI/Title.png` : écran-titre interne PMDO.
- `Strings/` : titre du jeu et futures traductions.

## Cartes présentes

| Groupe | Cartes |
|---|---|
| Guilde (14) | `guild_first_floor`, `guild_second_floor`, `guild_third_floor_lobby`, `guild_bedroom_hallway`, `guild_heros_room`, `guild_dining_room`, `guild_guildmasters_room`, `guild_storage_hallway`, `guild_storage_room`, `guild_top_left_bedroom`, `guild_top_right_bedroom`, `guild_bottom_left_bedroom`, `guild_bottom_right_bedroom`, `guilde_parvis` |
| Entrées (5) | `crooked_cavern_entrance`, `Brine_Cave_Entrance`, `drenched_bluff_entrance`, `vast_steppe_entrance`, `altere_pond` |
| Donjons (2) | `ledian_dojo`, `luminous_spring` |
| Bourg (2) | `spinda_cafe`, `metano_cafe` |
| Capitale (1) | `WaterfallVillageCapital` |
| Socle (1) | `destiny_hub` |

## Avant de lancer le jeu

`WaterfallVillageCapital.rsground` pèse 228 Mio et dépasse la limite GitHub de
100 Mio par fichier. Il est versionné compressé sans perte dans
`ressources/WaterfallVillageCapital.rsground.gz`. Restaure-le une fois :

```bash
python tools/restaurer_waterfall.py
```

Le script vérifie la taille (233 727 831 octets) et l'empreinte SHA-256 du
fichier d'origine publié dans `town02`.

## Documentation

- `docs/QUEST_DESTINY_AUDIT.md` — inventaire des sources et périmètre retenu.
- `docs/QUEST_DESTINY_ORGANISATION.md` — conventions PMDO déduites de Halcyon et structure retenue.
- `docs/QUEST_DESTINY_MANQUANTS.md` — ressources manquantes, références cassées, hors-périmètre.
