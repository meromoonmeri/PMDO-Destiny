# Intégrer Les chemins de Réverie en local

Choisir **une seule** des deux méthodes ci-dessous, dans le **dépôt source** de PMDO-Destiny. Ni le bundle ni le patch n’est un ZIP à extraire dans un jeu déjà installé. Garder une copie du dossier `SAVE` avant d’essayer le jeu construit à partir du candidat.

## Depuis la source de la v0.7.6 : prendre le bundle

Base : `37e6b5cdcfb46a064239c7c6983ef4840d27d408` (`v0.7.6`). Le bundle reprend les trois lots : *Le carnet des retours*, *Les foyers de Réverie*, puis *Les chemins de Réverie*. Il ne faut pas réappliquer les deux premiers après l’import.

Depuis une copie complète du dépôt qui possède cette base, remplacer le chemin du fichier ci-dessous par celui du bundle téléchargé :

```sh
bundle="/chemin/vers/Les-chemins-de-Reverie.bundle"
git bundle verify "$bundle"
git fetch "$bundle" refs/heads/work/reverie-chemins:refs/heads/essai/reverie-chemins
git worktree add ../Destiny-essai-chemins essai/reverie-chemins
cd ../Destiny-essai-chemins
python tools/unpack_payload.py
```

Aucune commande ci-dessus ne publie quoi que ce soit. La dernière restaure les dix cartes et génère l’index de tuiles dans l’arbre d’essai.

## Depuis les Foyers : prendre le patch

Le patch suppose le commit `e885b934a2940096df7bdb3d51758edbce761af9`. Dans un arbre propre à ce commit, décompresser `Les-chemins-de-Reverie.patch.xz` avec 7-Zip ou `xz -dk`, puis :

```sh
git apply --check /chemin/vers/Les-chemins-de-Reverie.patch
git apply /chemin/vers/Les-chemins-de-Reverie.patch
python tools/unpack_payload.py
```

Sur un arbre **déjà utilisé pour compiler** une autre variante, utiliser de préférence une copie neuve. Les `.rsground` générés et `game/Content/Tile/index.idx` d’un ancien lot peuvent faire diverger les empreintes ; l’extracteur les refuse plutôt que de les écraser. Ne pas déplacer les cartes originales versionnées ni le dossier `SAVE`.

## Pour refaire les contrôles

Les détails des voyageurs, du recadrage et de l’arène figurent dans `docs/REVERIE_CHEMINS.md` après import. Le bilan et les captures des essais sont dans [Validation.md](Validation.md). Les empreintes de cette remise sont dans `SHA256SUMS.txt`. Aucun installateur Windows n’a été produit pour ce candidat.
