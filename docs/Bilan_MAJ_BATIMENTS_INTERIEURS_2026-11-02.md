# Bilan — chaque bâtiment de Réverie Town avec son intérieur

Date : 2 novembre 2026. Suite de la mise à jour café Spinda / Lost Wood
(`Bilan_MAJ_CAFE_LOSTWOOD_2026-11-02.md`), sur la même branche
`destiny-unifiee`.

## Correspondances intégrées

Structure suivie à la lettre : **bâtiment Bekipan → intérieur Bekipan,
house → house, réserve → réserve, café → café…**

| Bâtiment | Intérieur |
|---|---|
| Poste Bekipan | `post_office` (deux Bekipan au comptoir) |
| Maisons citrouille (nord-ouest et sud) | `metano_fire_home` |
| Hutte nord-est | `metano_water_home` |
| Hutte sud | `metano_electric_home` |
| Maisons plante (sud et ouest) | `metano_grass_home` |
| Maison de Pierre | `metano_rock_home` |
| Maison d'Alakazam | `metano_normal_home` |
| Maison ronde du sud-ouest (maison de l'équipe) | `guild_heros_room` |
| Boutique Kecleon | `guild_storage_room` (réserve du marché) |
| Banque au coffre | `guild_storage_room` (salle des coffres) |
| Réserve Kangourex | `guild_storage_room` |
| Forge de Tinkaton | `dojo_ossatueur` (atelier provisoire) |
| Tente du centre | `metano_inn` (campement/auberge) |
| Tente de l'est | `ledian_dojo` (dojo, sensei Ledian) |
| Café Spinda | accueil + étage + salle (déjà intégré) |

## Technique

- 12 cartes d'intérieur town02 importées (fichiers LFS récupérés depuis le
  dépôt public town02) et 36 Tilesheets réellement manquantes ajoutées ;
  `game/Content/Tile/index.idx` régénéré (95 587 053 octets, sous la limite
  GitHub) et vérifié par `tools/build_tile_index.py --check`.
- Les intérieurs sont déclarés à la suite du café dans
  `town02_waterfallvillage` (indices du café inchangés) ; index des zones
  synchronisé.
- La carte de la ville ne sérialise aucune porte : un objet invisible est
  installé sur chaque seuil au chargement. La porte demande confirmation,
  mémorise le point de retour (`RetourBatimentX/Y`) et entre par le marqueur
  principal de l'intérieur. Les sorties sérialisées des intérieurs
  ramènent devant la façade utilisée.
- Scripts Destiny originaux pour les intérieurs : sorties, dialogues des
  Bekipan de la poste, du sensei Ledian et de son élève, de l'Ossatueur de
  l'atelier, journal de la maison de l'équipe. Les entrées de donjon des
  dojos sont neutralisées en attendant leur tranche.
- Contrôles : `tools/test_batiments_interieurs.py`, rendus
  `tools/preview_maps.py` des 12 intérieurs depuis le dépôt (aucune tuile
  manquante), analyse Lua.

## À valider au runtime

- Position exacte des 16 seuils en ville (coordonnées relevées sur le rendu
  de la carte étendue) et points de retour.
- Entrée/sortie de chaque intérieur, partenaire suiveur dans les maisons,
  dialogues des PNJ sérialisés (Bekipan, Ledian, Gible, Ossatueur).
- La réserve commune (boutique Kecleon / banque / Kangourex) et l'atelier
  provisoire de Tinkaton pourront recevoir des intérieurs dédiés plus tard.
