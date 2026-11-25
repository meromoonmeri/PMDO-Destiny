# Dojo Kingambit · Les wooshes PMD

**Pour voir :** ouvre `Voir-les-18-wooshes-PMD.html`, puis choisis un type. Le bouton **Woosh PMDO par défaut** montre la référence sur la scène de Drattak. Les repères **Balayage**, **Blanc** et **Combat** permettent de comparer les moments. `Wooshes-PMD-par-type.zip` contient les 18 MP4 individuels et la référence, avec le son capturé dans le jeu. Les clips contiennent de brefs éclairs blancs.

## Ce qui a changé

Le woosh est désormais bâti sur le **rythme natif PMDO** : deux impulsions lumineuses, puis neuf traînées fines lancées en cinq vagues alternées. Chaque type a sa géométrie de ligne, sa matière et sa vitesse de balayage. Pas de sceau ni de panneau au milieu de l'écran. Le son `EVT_Battle_Transition` d'origine accompagne tous les types.

Les bandes restent visibles pendant que `GAME:FadeOut(true, 30)` tire le plateau vers le blanc. Le blanc est plein pendant 10 ticks ; les bandes expirent sous ce blanc. `GAME:FadeIn(12)` rend la même arène visible, puis l'événement de combat natif prend la main. **Le montage ne rajoute ni le blanc ni les traînées.**

Dix nouvelles générations d'image ont été possibles sur ce tour. Dragon et Acier utilisent les découpes des deux essais générés au tour précédent, soit douze sources dédiées. Les six autres (`Vol`, `Psy`, `Insecte`, `Roche`, `Spectre`, `Ténèbres`) sont des adaptations de cette matière, avec des silhouettes et des vitesses distinctes. `Provenance-des-textures.json` note précisément les sources et leurs empreintes. Les grandes illustrations Dragon/Acier n'apparaissent pas à l'écran : seulement de petites découpes de leur tracé.

## Vérifier la référence

`PMDO 0.8.12` — `Data/Script/origin/common.lua`, fonctions `COMMON.MakeWhoosh` et `COMMON.BossTransition` : sprite `Content/BG/Pre_Battle.dir` (quatre tiers 256 × 64), mouvement d'origine ±360 px/s, groupes espacés de cinq ticks, 40 ticks après le dernier groupe, puis `FadeOut(true, 30)`. La version native maintient ensuite le blanc pour le changement de carte. On retrouve cet appel notamment dans `ground/end_treacherous_mountain/init.lua`, `ground/end_ambush_forest/init.lua` et `ground/end_moonlit_temple/init.lua`. Le clip de référence appelle **exactement la fonction native**, sur le décor de Drattak, sans jouer les dialogues ni le combat d'origine ; la vidéo est coupée sur le blanc. Pour Kingambit il n'y a pas de changement de salle.

## Essayer sans remplacer le lot validé

La variante est **séparée** ; aucune modification du dépôt existant ou de la scène Dazzling. En cas de validation, sur une **copie** de Destiny ayant déjà le lot prébatailles (base locale `7fcd0610402958c2d2262c2d1093e459097d13af`), superposer le dossier `Variante-PMD/game/` à `game/`. Il contient les 18 banques `Kingambit_Prebataille_PMD_<type>.dir` et le module `dojo_kingambit_prebatailles.lua`. L'appel déjà présent dans `destiny/event.lua` reste identique. Ni les banques précédentes, ni les cartes, ni les apparitions météo, ni les événements Méga ne sont remplacés par cette opération. Pour revenir au lot précédent, restaurer son module Lua. En l'absence d'une banque de type, le module se replie sur les bandes vanilla ; il quitte le blanc en cas d'erreur de raccord.

Le banc Linux PMDO ouvre directement les finales. Il vérifie les 18 retours au combat (`BeginBattleEvent`, `map_clear_check`, trois Pokémon aux mêmes cases et en forme de base), la présence d'un blanc réel sur la vidéo et le son opéré par PMDO. Il ne remplace pas un essai de tout le mod depuis le hall. `Contrôles/` contient les mesures, le journal des finales et le test Lua.

### Sources

Le générateur d'atlas `Sources/texturer_wooshes_pmd.py --pmdo /chemin/PMDO --out /chemin/banques` attend les images dans `Sources/Images` et l'asset vanilla `Content/BG/Pre_Battle.dir` dans l'installation PMDO. Dépendances : Python, Pillow, NumPy, SciPy ; FFmpeg pour les clips. Les scripts de capture nécessitent le banc du lot précédent. Les tuiles, sprites et sons PMDO proviennent de l'installation d'origine et conservent leurs crédits. Les nouveaux détails de traînée proviennent des images générées et retaillées pour cet essai.
