# Pousser le retour de Nilo

**Push effectué et vérifié.** La [branche WIP](https://github.com/meromoonmeri/PMDO-Destiny/tree/wip/reverie-integration-kingambit-cafe) est passée de `37138a7` à `37e6b5cdcfb46a064239c7c6983ef4840d27d408`, sans réécriture d’historique. Voir le [journal du push](Preuves/Publication.txt). Il n’est pas nécessaire de relancer l’envoi.

Le bloc suivant est conservé pour reproduire l’import du [bundle](Destiny-v0.7.6-Retour-Nilo.bundle) dans un clone autorisé de `meromoonmeri/PMDO-Destiny`. Pour HTTPS, si nécessaire, authentifiez Git sur votre propre poste avec `gh auth login --web` puis `gh auth setup-git`. Ne transmettez aucun jeton dans la conversation.

```bash
set -euo pipefail
branch='wip/reverie-integration-kingambit-cafe'
ref="refs/heads/$branch"
sha='37e6b5cdcfb46a064239c7c6983ef4840d27d408'
bundle='/chemin/vers/Destiny-v0.7.6-Retour-Nilo.bundle'

case "$(git remote get-url --push origin)" in
  https://github.com/meromoonmeri/PMDO-Destiny|https://github.com/meromoonmeri/PMDO-Destiny.git|git@github.com:meromoonmeri/PMDO-Destiny.git) ;;
  *) echo 'Vérifier le remote origin.' >&2; exit 1 ;;
esac

git fetch --no-tags origin "$ref"
ancien=$(git rev-parse FETCH_HEAD)
git bundle verify "$bundle"
git fetch --no-tags "$bundle" "$ref"
test "$(git rev-parse FETCH_HEAD)" = "$sha"
git merge-base --is-ancestor "$ancien" "$sha"
git push origin "$sha:$ref"
test "$(git ls-remote origin "$ref" | cut -f1)" = "$sha"
```

C’est un push sans réécriture d’historique. Si la vérification d’ascendance échoue, il faut intégrer les nouveaux changements distants avant de pousser. Ce bloc ne crée ni tag ni release. Le build Windows a depuis réussi sur ce SHA et la [préversion v0.7.6](https://github.com/meromoonmeri/PMDO-Destiny/releases/tag/v0.7.6) est publiée. Le run 0.7.5 n’a pas été réutilisé.
