# Méga-Évolution — trois propositions sans colonnes

| Version | Durée | Changement de sprite masqué | Révélation | Composition |
|---|---:|---:|---:|---|
| 01 · Résonance violette | 3,50 s | 1,700 s | 1,800 s | Anneaux rentrants, orbe blanc Deeshura, éclat radial aplati et emblème Guildhouse. |
| 02 · Prisme fendu | 4,40 s | 1,933 s | 2,633 s | Charge à la Deeshura, vraie spirale et vraie coque Guildhouse ; l'éclat bleu souligne les éclats de la coque. |
| 03 · Éclipse X | 3,90 s | 2,033 s | 2,167 s | Deux orbites croisées, spirale Guildhouse teintée bleu nuit, lumière Deeshura en iris et ouverture latérale. |

Les trois rendus présentent **Dracaufeu → Méga-Dracaufeu X**, à la même échelle et dans la même orientation. Aucun atlas des colonnes Guildhouse ni l'émetteur `Lightning` de Mega Stones n'est chargé. Les longues pointes verticales des flashes radiaux sont supprimées et les étoiles sont aplaties ; restent des impacts courts, des anneaux bas et des particules. Le décor est un plateau de comparaison, pas une capture d'une carte PMDO. Le son `Mega_Evolution.ogg` a été recalé pour garder son impact au moment de la révélation.

## Sources et crédits

- **Guilde Treehouse PMD** : [V2, commit `63f1e48`](https://github.com/meromoonmeri/guilde-treehouse-pmd/tree/63f1e4806f1e382ca6e00b984a5730d5cd1553d6/renders/mega_evolution_v2). Cycles de la sphère, de la coque et de l'emblème issus de `renders/mega_evolution_v2/cycles/`. L'emblème est le visuel custom de la V2, pas une icône officielle.
- **[Mega Stones — Deeshura](https://github.com/Deeshura/Mega_Stones/tree/31a26eb9ed3030b6b51ef7a6f2b70bc09ad3ec3a)** : référence de mise en scène de `mega_charizardite_x.json`, anneaux convergents, orbe lumineux, révélation radiale, `Mega_Evolution.ogg`. Licence MIT du mod conservée dans `Sources/Matieres/Mega-Stones/LICENSE-Mod.txt` (ne couvre pas automatiquement l'ensemble des ressources amont).
- **[PMDCollab/RawAsset](https://github.com/PMDCollab/RawAsset/tree/0b88bbd7dec6f3373d5ec2b0f40bbdc3f44ce90c/Particle)** : planches `Circle_Small_Purple_In`, `Light_Ball_Purple`, `Mega_Background_White`, `Mega_Background_Light_Blue`, les particules appelées par la mise en scène Mega Stones et ses variantes. Les planches sont conservées non modifiées ; géométrie et opacité sont adaptées au rendu.
- **[PMDCollab/SpriteCollab](https://github.com/PMDCollab/SpriteCollab/tree/3609a86be2a4c8ad7cf255bd2255f044daafe24f/sprite/0006)** : Dracaufeu 0006 et Méga-Dracaufeu X 0006/0001, feuilles Idle et Charge à leurs pixels natifs. Crédits détaillés et conditions par contributeur dans les `credits.txt` copiés sous `Sources/Matieres`. Nintendo / Creatures / GAME FREAK : Pokémon et designs ; CHUNSOFT et auteurs SpriteCollab pour les sprites selon les registres. Aperçu fan non commercial.

## Portée et reconstruction

- Ce sont **des propositions hors moteur** : ni fichiers `.dir` prêts à importer, ni événement de donjon, ni modification/push du dépôt. Les pierres, le changement de forme réel et le gameplay des dojos n'ont pas été modifiés.
- Les MP4 sont à 30 i/s (896×576, pixels de la composition native agrandis ×4, H.264 + AAC). Le comparateur HTML embarque les trois vidéos et ses miniatures ; aucun chargement réseau requis.
- Depuis ce dossier : `python Sources/rendre.py` (Pillow, NumPy, FFmpeg) puis `python Sources/galerie.py`. Option `--direction` de `rendre.py` pour rendre un autre angle natif, `--out` pour travailler en dehors de ce dossier. Le contrôle automatisé mesure l'opacité du cache au changement de forme, avant et après, sur les poses Idle des deux formes et Charge de départ dans les huit directions (288 contrôles par variante). C'est un contrôle de compositing, pas un test moteur.

## 04 · Éclipse X — Prisme fendu

Fusion de 4,80 s, sur le même plateau et avec les mêmes sprites. Les deux orbites d'Éclipse X précèdent la sphère bleu nuit ; l'iris se résorbe pendant que la couleur gagne la spirale, de l'intérieur vers la périphérie, entre 1,43 s et 2,47 s. Au terme de la transition, le calque de la sphère est identique au cycle Prisme fendu (pixels, opacité, dimensions et ancrage). Le raccord utilise la phase 0 de la spirale et la première image de la coque V2, réalignée. Le changement de sprite est caché à 2,07 s, la coque s’ouvre à 3,33 s avec l’éclat latéral de Deeshura, les orbites et les éclats repartent ensemble. Aucun calque de colonnes ou d’éclairs verticaux.

Reconstruction : `python Sources/fusion_eclipse_prisme.py`. Sortie `04-Eclipse-X-Prisme.mp4` ; les trois propositions du comparateur initial sont conservées. Même statut : proposition visuelle hors moteur, sans intégration ni modification du dépôt.
