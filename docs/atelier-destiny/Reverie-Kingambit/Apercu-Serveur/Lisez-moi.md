# Aperçu serveur · Réverie v0.7.7

Vitrine interactive en français de la préversion Kingambit/Réverie : MP4 chapitré, 54 objets consultables, captures de PMDO et liens vers la [préversion Windows](https://github.com/meromoonmeri/PMDO-Destiny/releases/tag/v0.7.7). Ce serveur ne lance pas le jeu lui-même.

## Démarrer

```sh
node serveur.mjs
```

Node 20+, aucune dépendance. Le serveur démarre sur `0.0.0.0:4173` ; `PORT` change le port si nécessaire. L’aperçu est embarquable dans Arena. La navigation, le catalogue, les images, les polices et la lecture vidéo utilisent le même serveur. Les liens de téléchargement pointent vers la publication officielle et s’ouvrent à part.

`public/` est le seul dossier publié. Le montage `../Kingambit-Mise-a-jour/Apercu-18-wooshes-PMD.mp4` est publié sur une route explicite avec lecture par plages d’octets, sans exposer les autres fichiers de livraison. Les sources de la vitrine et les fichiers du workspace restent privés au serveur.

## Reconstruction des données

```sh
python preparer_media.py
```

Requiert Pillow et FFmpeg/FFprobe. Le script réutilise les captures natives et le registre des icônes ; les descriptions ne sont pas réécrites. Il faut conserver les dossiers de captures et de livraison à côté de `Apercu-Serveur`. Les polices Manrope et Fraunces sont intégrées avec leurs licences OFL dans `public/fonts/`.
