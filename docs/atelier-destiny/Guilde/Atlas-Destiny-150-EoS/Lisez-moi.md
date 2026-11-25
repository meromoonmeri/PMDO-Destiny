# Atlas Destiny — 150 lieux sur le fond EoS

Ouvrir l’aperçu serveur **Atlas Destiny · 150 lieux — fond EoS** (port 4191).

- **Monde entier** montre les 150 vignettes sur le continent d’*Explorateurs du Ciel*. **Fond EoS** masque les vignettes et les repères pour montrer la planche seule.
- **Départ Réverie** cadre le village, la Fosse Cascade, le Passage Aquatique, les Bois Perdus et la falaise de la guilde. Leurs petits chemins sont un calque affiché seulement pendant le départ.
- **Dévoiler** enchaîne les huit vues de la planche, sans utiliser les vues à points jaunes. Les fondus et le recul de la caméra sont ajoutés entre ces vues ; la texture et les contours des nuages proviennent de la planche elle-même.
- Zoomer, déplacer la carte ou chercher un lieu dans le carnet. Les noms restent hors du dessin.

## Fond et calques

La base est la planche DS / DSi d’*Explorateurs du Ciel* fournie avec la demande (`Sources/Reference-EoS.png`). Le fond sans ajouts est recadré pixel pour pixel en 504 × 336 ; aucun changement de contour, de palette, de grain, de relief, de grille marine ni de bordure. Les 150 miniatures de l’index sont les mêmes que dans la version précédente. Leurs petites vignettes cartographiques sont replacées sur le continent original, dans des secteurs adaptés à sa forme ; ce ne sont pas des coordonnées officielles. Eddy’s Lab reste une référence pour les noms, pas le fond de cette édition.

| Fichier | Contenu |
|---|---|
| `Apercu/` | Site statique complet et ses calques. |
| `Atlas-Destiny-EoS-Hors-Ligne.html` | Même atlas interactif, autonome et sans réseau. |
| `Fond-EoS-Original-504x336.png` | Fond de la planche seul, à la taille native. |
| `Monde-Destiny-EoS-6048x4032.png` | Atlas des 150 lieux sans texte, agrandi en pixels nets. |
| `Verification-carte.json`, `Verification-navigateur.json` | Concordance des 8 vues, séparation du fond et des vignettes, vérifications ordinateur/mobile/hors ligne. |

Le site se sert avec `python -m http.server 4191 --bind 0.0.0.0 --directory Apercu` depuis ce dossier. `Sources/ConstruireEoS.py` reconstruit les calques avec Pillow, NumPy et SciPy à partir de la planche fournie et des miniatures du dossier voisin `Atlas-Destiny-150`. `Sources/Autonome.py` assemble la version hors ligne. L’ancienne édition existe toujours à part. Aucun fichier du jeu n’a été modifié.
