# Atelier de Destiny

Livrables, sources et vérifications de la Guilde, de Réverie et des cartes du monde, rassemblés sur la branche `wip/reverie-integration-kingambit-cafe`.

## Points d’entrée

- [Carte Miracle : Destiny 4 — Grand Large](Guilde/Carte-Miracle-Destiny-4-Grand-Large/Carte-Miracle-Destiny-4.html) · [Carnet des 50 lieux](Guilde/Carte-Miracle-Destiny-4-Grand-Large/Carnet-des-50-lieux.html) · [Animation des nuages](Guilde/Carte-Miracle-Destiny-4-Grand-Large/Destiny-4-Levee-des-nuages.mp4).
- [Atelier de la Guilde](../guilde/Guilde-Destiny.html) · [Toutes les salles](Guilde/Guilde-Destiny-Toutes-les-Salles.html) · [Mobilier](Guilde/Guilde-Destiny-Mobilier-Halcyon-IA.html).
- [Réverie, Kingambit et les quêtes](Reverie-Kingambit/) · [Fosse Cascade](Fosse-Cascade/) · [Bilan de Réverie](Bilan-Reverie/Bilan-Reverie-Town.html) · [Systèmes](Systemes/).

Télécharger les HTML pour les ouvrir dans un navigateur : GitHub affiche leur code source. La Carte Miracle est autonome et jouable hors ligne.

## Dans le jeu, sur cette branche

- **Guilde** : cadrage des sept sorties sud, vitrage R2 des huit fenêtres et retouche de l’Accueil et du Grand Salon sans prolonger les chemins. Les cartes natives, les seuils, les offsets de tuiles et les collisions n’ont pas été remplacés. Le mobilier est disponible dans l’atelier PMU ; il n’est pas placé dans le jeu par ces correctifs.
- **Réverie, Fosse Cascade et Kingambit** : les cinématiques, les systèmes et les dojos étaient déjà intégrés à la branche. Le portage conserve les scènes et dialogues les plus récents. Les correctifs ciblés rendent la main à la Falaise en solo, rétablissent le retour direct du Café après la visite et arrêtent le repas pour les mêmes convives.

**Grand Large est un atlas autonome**, pas un remplacement de la carte en jeu. Il reprend les poses et la cadence de la levée des nuages EoS et garde la carte entière fermée jusqu’à la dernière levée. [Sources et contrôles](Guilde/Carte-Miracle-Destiny-4-Grand-Large/Lisez-moi.md) · [Bilan illustré de Réverie](Bilan-Reverie/Bilan_REVERIE_TOWN.md) · [Vérifications d’intégration](Verification-integration.json).

## Inventaire de publication

| Dossier | Fichiers |
| --- | ---: |
| [Apercus-valides](Apercus-valides/) | 5 |
| [Arbre-ancien](Arbre-ancien/) | 2 |
| [Audit](Audit/) | 6 |
| [Bilan-Reverie](Bilan-Reverie/) | 8 |
| [Fosse-Cascade](Fosse-Cascade/) | 3 |
| [Guilde](Guilde/) | 2291 |
| [Retouches](Retouches/) | 27 |
| [Reverie-Kingambit](Reverie-Kingambit/) | 403 |
| [Systemes](Systemes/) | 30 |
| [Validation-074](Validation-074/) | 7 |

[Inventaire détaillé des livrables](Inventaire.tsv) (taille et identifiant du blob Git). Les ZIP redondants sont remplacés par les fichiers qu’ils contenaient ; les kits qui ont des fichiers uniques sont conservés. Les archives servent de référence : elles ne remplacent pas automatiquement les données natives, et certaines correspondent à des versions antérieures. Les essais écartés, caches, copies de programme et identifiants n’ont pas été publiés.

Les rapports `État`, notes de publication et bundles archivés conservent leur état d’origine. N’appliquez pas l’ancienne refonte de la guilde ni le paquet d’extension des sols par-dessus ces correctifs. Aucun nouveau build Windows ni release n’a été lancé pour cette publication.
