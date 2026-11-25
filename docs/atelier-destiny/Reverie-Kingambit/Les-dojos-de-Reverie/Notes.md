> **Ancien prototype, remplacé.** Le candidat actuel (arènes DTEF, trappes de biome, Ledian et Ossatueur intacts) est dans [Les-dojos-de-Reverie-Magenta](../Les-dojos-de-Reverie-Magenta/Validation.md). Ne pas pousser ce premier colis.

# Les dojos de Réverie — intégration locale

**Candidat :** `704da0d86e2cd30c2cabdb482c5a073d304caf38`  
**Parent validé :** Les chemins de Réverie, `785ecef7e385a77270bcf931419c47e42526d5d3`

Parler à **Kaito** dans l’accueil du Dojo Kingambit. Sur les trois pages, choisir un des 18 types, puis **Descendre**. La trappe s’ouvre à l’endroit de l’interaction, et le duo tombe dans le dédale. Les deux premiers étages sont à explorer ; le troisième se termine en battant le maître du type. L’EXP reste acquise au retour. Les objets du sac restent utilisables et les consommables utilisés ne sont pas remboursés. Le refus est proposé par défaut. Un **+** dans la liste signale un dédale réussi.

La retouche concerne uniquement les intérieurs : accueil, arène et reliques de Kingambit, salle d’Ossatueur, salle de Ledian. Les façades et le duel de Liane sont inchangés. Si une ancienne sauvegarde reprend à l’intérieur d’un dojo, ressortir et y rentrer pour recharger le décor corrigé.

## Deux façons d’intégrer le code

**Depuis la branche des Chemins, sur une copie de travail propre :**

```sh
xz -dc /chemin/Les-dojos-de-Reverie.patch.xz | git apply --index -
python tools/build_tile_index.py
python tools/unpack_payload.py
```

Le patch est le seul delta depuis les Chemins ; ne pas l’appliquer directement à la v0.7.6.

**Depuis le dépôt source qui contient la base publique `37e6b5c` :**

```sh
BUNDLE=/chemin/Les-dojos-de-Reverie.bundle
git bundle verify "$BUNDLE"
git fetch "$BUNDLE" refs/heads/work/dojo-kingambit-dedales:refs/heads/apercu/les-dojos
git switch apercu/les-dojos
python tools/build_tile_index.py
python tools/unpack_payload.py
```

Le bundle est cumulatif : Carnet, Foyers, Chemins et Dojos. Le dernier appel régénère notamment l’index des tuiles. Le document `docs/REVERIE_DOJOS.md` du dépôt décrit les 18 dédales et les outils de reconstruction. **Ni publication ni nouvel exécutable Windows** ; aucun fichier de sauvegarde n’est livré ni à remplacer.

Voir aussi [la capture de la trappe](La-trappe-de-Kingambit.mp4), [le comparatif avant/après](Comparatif-des-dojos.png) et [les vérifications](Validation.md).
