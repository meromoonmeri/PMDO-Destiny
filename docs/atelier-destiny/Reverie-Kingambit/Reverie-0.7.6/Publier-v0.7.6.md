# Publier la version candidate v0.7.6

La correction est prête et contrôlée en jeu, mais **ni le push, ni la CI Windows, ni la release n’ont été effectués**. Ce guide reprend le flux prévu par le dépôt, depuis un poste déjà autorisé à y écrire. Ne pas réutiliser un run de la v0.7.5, ni transmettre de jeton dans la conversation.

## 1 · Importer le bundle et pousser la WIP

Dans un clone de `meromoonmeri/PMDO-Destiny`, avec `git` et `gh` authentifiés sur votre propre poste, téléchargez [Destiny-v0.7.6.bundle](Destiny-v0.7.6.bundle). Exécutez les blocs dans la même session Bash (Git Bash sous Windows). Remplacez le chemin du bundle et vérifiez qu’`origin` pointe bien vers le dépôt du chantier.

```bash
set -euo pipefail
repo='meromoonmeri/PMDO-Destiny'
branch='wip/reverie-integration-kingambit-cafe'
ref="refs/heads/$branch"
sha='24be5673a76e06a9824102c5f106f091eb07070a'
tag='v0.7.6'
bundle='/chemin/vers/Destiny-v0.7.6.bundle'

case "$(git remote get-url --push origin)" in
  https://github.com/meromoonmeri/PMDO-Destiny|https://github.com/meromoonmeri/PMDO-Destiny.git|git@github.com:meromoonmeri/PMDO-Destiny.git) ;;
  *) echo 'Vérifier le remote origin avant de pousser.' >&2; exit 1 ;;
esac

gh auth status --hostname github.com
# Avec un remote HTTPS, si git n’utilise pas encore gh : gh auth setup-git
git fetch --no-tags origin "$ref"
ancien=$(git rev-parse FETCH_HEAD)
git bundle verify "$bundle"
git fetch --no-tags "$bundle" "$ref:refs/heads/candidat-v0.7.6"
test "$(git rev-parse refs/heads/candidat-v0.7.6)" = "$sha"
git merge-base --is-ancestor "$ancien" "$sha"
tag_distant=$(git ls-remote origin "refs/tags/$tag")
test -z "$tag_distant"
git push origin "$sha:$ref"
test "$(git ls-remote origin "$ref" | cut -f1)" = "$sha"
```

Le push est un fast-forward, jamais un `--force`. Si la WIP a divergé ou que le tag existe déjà, arrêtez-vous et revérifiez la base avant de publier.

## 2 · Construire et vérifier Windows sur le SHA candidat

```bash
gh workflow run build-windows.yml --repo "$repo" --ref "$branch" -f mode=build
gh run list --repo "$repo" --workflow build-windows.yml --branch "$branch" \
  --commit "$sha" --event workflow_dispatch --limit 5
```

Relevez l’identifiant du run qui vient de démarrer. Si la liste est momentanément vide, actualisez-la. Définissez `run` avec cet identifiant réel, puis vérifiez son résultat et son artefact (le téléchargement dépasse 1 Go).

```bash
# Définir run avec l’identifiant numérique réel du build ci-dessus.
: "${run:?Définir run avant de continuer}"
gh run watch "$run" --repo "$repo" --exit-status
attendu="Build Windows|$branch|$sha|completed|success"
observe=$(gh run view "$run" --repo "$repo" \
  --json workflowName,headBranch,headSha,status,conclusion \
  --jq '[.workflowName,.headBranch,.headSha,.status,.conclusion]|join("|")')
test "$observe" = "$attendu"
controle=$(mktemp -d)
gh run download "$run" --repo "$repo" \
  --name PMDO-Destiny-Windows-x64 --dir "$controle"
unzip -tq "$controle/PMDO-Destiny-Windows-x64.zip"
```

## 3 · Publier avec le workflow vérifié

```bash
tag_distant=$(git ls-remote origin "refs/tags/$tag")
test -z "$tag_distant"
gh workflow run publish-verified-release.yml --repo "$repo" --ref "$branch" \
  -f run_id="$run" -f target_sha="$sha" -f tag="$tag"
```

Attendez le succès de **Publish verified Windows release**. Le workflow vérifie le build, prend les notes `docs/REVERIE_076.md` du commit exact et publie la préversion avec le ZIP complet, le delta depuis la version précédente et leurs SHA-256. Contrôlez ensuite la cible du tag, le lien vers le run et les fichiers dans [`Releases`](https://github.com/meromoonmeri/PMDO-Destiny/releases). La publication n’est terminée que lorsque ces éléments sont visibles sur GitHub.
