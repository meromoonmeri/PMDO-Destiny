# Mise à jour Kingambit — entrées, cyclones, wooshes PMD et Méga

Branche cumulative issue de `wip/reverie-integration-kingambit-cafe` au commit `37e6b5cdcfb46a064239c7c6983ef4840d27d408`. Elle conserve les précédents commits de Réverie et n’écrase pas la branche `main`.

| Élément | Contenu | Statut |
|---|---|---|
| Dojo, dédales et troupes | 18 finales, 54 combattants, mêmes salles et règles. Trappes et arènes DTEF propres à chaque biome. | Intégré dans `game/`, via `2e003fe` et `936b562` |
| Apparitions et maîtres | Troupes en forme de base, pas de Méga simultanée ni automatique. Maîtres éligibles à l’évolution. | Intégré, `be14e78` |
| Dragon, Vol, Eau, Feu | Cyclones animés pour Dragon/Vol, pluie sur les colonnes Eau, canicule et braises sur les colonnes Feu. | Intégré, `79ddccc` |
| Précombats | 18 wooshes PMD sur les bandes à contresens, fondu blanc réel et retour à l’arène. La version à sceaux reste dans l’historique `7fcd061`. | Nouvelle variante active : [notes et tests](KINGAMBIT_PREBATAILLES.md) |
| Méga-Gemmes | Addon de Deeshura adapté à Réverie, 47 Méga-Gemmes + Météorite Delta, animation et cadence retouchées, mécaniques d’origine. | [Addon facultatif](../addons/Mega_Stones_Reverie/DESTINY.md), séparé de `game/` |
| Éclipse X — Prisme fendu | Fusion validée : progression d’une seule sphère vers la vraie spirale de Prisme fendu, fracture V2, ouverture latérale, sans colonnes. | [Aperçu et sources](../art/previews/mega_eclipse_x_prisme/), **non intégré au moteur** |

**Aperçu animé :** [les 18 wooshes et l’original PMDO](../art/previews/kingambit_wooshes_pmd/Apercu-18-wooshes-PMD.mp4), un chapitre par type. La [provenance](../art/previews/kingambit_wooshes_pmd/Provenance-des-textures.json) identifie les images générées et les adaptations.

## Installation et validation

Sur le dépôt complet, valider et reconstruire Destiny selon le [README](../README.md). L’addon reste une installation facultative dans PMDO ; ses index ne remplacent jamais ceux de Destiny. La fusion Éclipse X — Prisme fendu est un fichier de référence, pas une nouvelle capacité ou une animation utilisée en combat.

Banc de prévisualisation : PMDO Linux 0.8.12 avec cartes, banques d’apparition et scripts de la branche ; capture au départ direct des 18 finales jusqu’à `BeginBattleEvent`. Les créneaux de blanc et le son ont été contrôlés. Le lot des quatre Méga-Évolutions via le sac et le chargement des 48 objets concernent l’addon précédent, pas la fusion Éclipse X. Les greffes et profils de test ne sont pas versionnés ; aucune version Windows autonome n’est revendiquée ici.

Pokémon et Donjon Mystère : propriété de leurs ayants droit. Les ressources de tiers conservent leurs crédits et licences, notamment celles de SpriteCollab, PMDO et Mega Stones. Projet de fans non commercial.
