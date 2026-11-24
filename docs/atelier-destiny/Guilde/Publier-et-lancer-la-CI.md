# Archive — ancienne refonte de la Guilde

**Ne pas utiliser ce bundle pour la 0.7.7.** La [procédure actuelle](Atelier-PMU/Publier-la-mise-a-jour.md) concerne le cadrage des sorties sud sans rallonge et le nouvel atelier PMU.

**État : non publié.** L’autorisation a été confirmée dans le navigateur, mais la connexion a été réinitialisée pendant l’échange OAuth. Aucune session GitHub utilisable n’en a résulté. La branche distante est toujours à `aa1430c4e8953e486b82691731fbbcbce8e4c57e`, et aucun run Windows n’a été lancé.

| Élément | Valeur |
|---|---|
| Dépôt | `meromoonmeri/PMDO-Destiny` |
| Branche | `wip/reverie-integration-kingambit-cafe` |
| Commit à publier | `9feecc86355a9e7346e07f6bb2f80ec5102f2bcd` |
| Bundle | `PMDO-Destiny-Guilde.bundle` |
| SHA-256 du bundle | `4f0a796317edd9407acb0101e24a72f6423fcbc8afde800e2b4627ae6ad1adce` |

Le bundle contient la **refonte sans mobilier**, le polish Fosse Cascade/Réverie et les corrections d’audit. L’aménagement rejeté n’est pas dans son historique. `git bundle verify` et l’import ont été vérifiés localement.

## 1. Importer et pousser sans force

Dans un clone du dépôt, depuis Bash ou Git Bash, avec une session GitHub possédant les droits d’écriture. Utiliser le chemin **absolu** du bundle téléchargé. Vérifier la session avec `gh auth status --hostname github.com`. Si nécessaire, s’authentifier sur sa machine avec `gh auth login --web`, puis installer le gestionnaire d’identifiants avec `gh auth setup-git`. Ne pas envoyer de jeton dans le chat.

```bash
(
  set -euo pipefail
  URL=https://github.com/meromoonmeri/PMDO-Destiny.git
  BRANCHE=wip/reverie-integration-kingambit-cafe
  REF="refs/heads/$BRANCHE"
  SHA=9feecc86355a9e7346e07f6bb2f80ec5102f2bcd
  BUNDLE='/chemin/absolu/PMDO-Destiny-Guilde.bundle'

  git bundle verify "$BUNDLE"
  git fetch --no-tags "$BUNDLE" "$REF"
  test "$(git rev-parse FETCH_HEAD)" = "$SHA"

  # S’arrêter si une autre mise à jour de la branche n’est pas dans le bundle.
  git fetch --no-tags "$URL" "$REF"
  DISTANT=$(git rev-parse FETCH_HEAD)
  git merge-base --is-ancestor "$DISTANT" "$SHA" || {
    echo 'La branche distante a divergé ; ne pas forcer.' >&2
    exit 1
  }

  git push "$URL" "$SHA:$REF"
  test "$(git ls-remote "$URL" "$REF" | cut -f1)" = "$SHA"
  printf 'Commit confirmé sur GitHub : %s\n' "$SHA"
)
```

L’import n’écrase ni le checkout ni les fichiers de travail du clone. Il faut que ce clone contienne l’ancêtre `aa1430c4…`, comme dans l’historique de la branche WIP.

## 2. Déclencher le build et contrôler le run

Après confirmation du SHA distant :

```bash
gh workflow run build-windows.yml \
  --repo meromoonmeri/PMDO-Destiny \
  --ref wip/reverie-integration-kingambit-cafe -f mode=build

gh run list --repo meromoonmeri/PMDO-Destiny \
  --workflow build-windows.yml --branch wip/reverie-integration-kingambit-cafe \
  --commit 9feecc86355a9e7346e07f6bb2f80ec5102f2bcd --event workflow_dispatch \
  --json databaseId,headSha,createdAt,status,conclusion,url
```

Si le run vient d’être déclenché et n’est pas encore listé, relancer la commande de liste après quelques secondes. Prendre l’ID du nouveau run dont le `headSha` correspond au SHA attendu :

```bash
gh run watch ID_DU_RUN --repo meromoonmeri/PMDO-Destiny --exit-status
gh run view ID_DU_RUN --repo meromoonmeri/PMDO-Destiny \
  --json databaseId,headSha,status,conclusion,url,jobs
```

Un build vérifié doit avoir ce SHA, `status: completed`, `conclusion: success` et l’artefact **PMDO-Destiny-Windows-x64**. Les contrôles sous Linux n’ont pas produit ce ZIP. Ne pas lancer `mode=release` et ne pas créer de tag.
