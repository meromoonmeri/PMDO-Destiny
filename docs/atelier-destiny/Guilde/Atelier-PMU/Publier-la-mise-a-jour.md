# Publier le cadrage et l’atelier de la guilde

**État : préparé et vérifié localement, non poussé.** Le contrôle de push HTTPS a été refusé faute d’authentification (`unable to get password from user`). Le dépôt n’a pas été modifié. Aucun build, tag ou release n’a été déclenché.

| Élément | Valeur |
|---|---|
| Dépôt | `meromoonmeri/PMDO-Destiny` |
| Branche de travail | `wip/reverie-integration-kingambit-cafe` |
| Pointe distante vérifiée | `0c0a13f75e13ab95132b66b282dae1b369ef885b` |
| Commit cadrage sud | `0ebeba87d885f5c3381dfa35e27c7fed47cbb20d` |
| Commit atelier HTML | `355d1f3d3e45544b43260f812997d462afbc715a` |
| Bundle | `Guilde-Destiny-0.7.7-Mise-a-jour.bundle` |
| SHA-256 du bundle | `ba25c47330bfcad0bc87c519ec76298871794dd28f0d9e1b600ba51549b075bf` |

Le premier commit ne modifie que les sept scripts de salle et le module commun de caméra. Le second ajoute la page autonome `docs/guilde/Guilde-Destiny.html` et ses sources. Aucune carte ni texture du jeu n’est remplacée par ces deux commits ; aucun meuble n’est posé automatiquement. Ce bundle est indépendant de l’ancienne refonte et de la rallonge rejetée.

## Depuis un clone authentifié de Destiny

Utilise Bash ou Git Bash avec les droits d’écriture sur la branche. Si nécessaire, authentifie Git **sur ta machine**, par exemple avec `gh auth login --hostname github.com --web` puis `gh auth setup-git`. Ne partage pas d’identifiants ni de jeton.

Dans le clone, remplace la valeur de `BUNDLE` par son chemin absolu, puis lance :

```bash
(
  set -euo pipefail
  URL=https://github.com/meromoonmeri/PMDO-Destiny.git
  BRANCHE=wip/reverie-integration-kingambit-cafe
  TETE=355d1f3d3e45544b43260f812997d462afbc715a
  BUNDLE='/chemin/absolu/Guilde-Destiny-0.7.7-Mise-a-jour.bundle'
  git fetch --no-tags "$URL" "refs/heads/$BRANCHE"
  DISTANT=$(git rev-parse FETCH_HEAD)
  git bundle verify "$BUNDLE"
  git fetch --no-tags "$BUNDLE" refs/heads/arena-guilde-atelier
  test "$(git rev-parse FETCH_HEAD)" = "$TETE"
  if ! git merge-base --is-ancestor "$DISTANT" "$TETE"; then
    echo 'La branche a avancé autrement : ne pas forcer le push.' >&2
    exit 1
  fi
  git push "$URL" "$TETE:refs/heads/$BRANCHE"
  test "$(git ls-remote "$URL" "refs/heads/$BRANCHE" | cut -f1)" = "$TETE"
  echo "Commit vérifié sur GitHub : $TETE"
)
```

Ces commandes ne changent pas les fichiers de travail de ton clone. En cas de nouvel ajout sur la branche, intègre les commits à jour au lieu de forcer.
