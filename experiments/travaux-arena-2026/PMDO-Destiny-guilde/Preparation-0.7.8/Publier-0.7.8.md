# Publier Destiny 0.7.8

## État actuel

**Publiée sur GitHub en préversion.** Après authentification, les sources et un correctif de compatibilité ont été envoyés. Le premier build a échoué sur un test de signature ; après correction, le second build Windows et le workflow de publication ont réussi. La note, le tag et les deux archives ont été vérifiés sur la [release v0.7.8](https://github.com/meromoonmeri/PMDO-Destiny/releases/tag/v0.7.8). Voir `Etat-publication.json` pour les identifiants de runs et les empreintes. Ne pas installer le bundle source comme s’il s’agissait du jeu.

- Dépôt : `meromoonmeri/PMDO-Destiny`
- Branche : `wip/reverie-integration-kingambit-cafe`
- Base attendue : `8f80c6e2c47e681acd334be661d601a59fed2367`
- Commit préparé : `7bd2dc104706571c91a2ea4a3c45282b94eabbb6`
- Bundle : `Destiny-0.7.8-source.bundle`, SHA-256 `1d021c33e2aef709dcbe8c6634524f16ce720d92df4fbbc40f2cb4270b946d45`
- La note de version est dans le commit sous `docs/REVERIE_078.md`, chemin que le workflow utilise pour la v0.7.8.

Le commit ajoute le patch complet d'accessoires, la note et des compléments d'atelier. La branche de base contient déjà les autres travaux de la guilde, les cartes, Kingambit et Réverie. Les 40 objets sont livrés sous forme de kits et de catalogue séparés, non intégrés au jeu ; 20 des 60 objets prévus n'ont pas été créés. Les anciennes versions des accessoires sont conservées comme archives ; leurs patches ne doivent pas être appliqués en plus. Méga-Tsareena est exclue. Les générations brutes haute définition et sources de reconstruction complètes de la série des 60 objets restent dans l'espace de travail, hors de ce bundle.

Le bundle a été vérifié et importé dans un dépôt de contrôle distinct ; le patch inverse et la concordance de la note ont été vérifiés. Les tests antérieurs des accessoires incluent une compilation Linux/FNA et des essais sur une copie isolée. Le placement des accessoires ne peut pas être garanti sur toutes les espèces ; aucun parcours complet en donjon ni build Windows de ce commit n'a été testé.

## 1. Importer et pousser le commit — déjà effectué

Les commandes ci-dessous sont conservées à titre d’archive et ne sont utiles que si la branche distante revient à la base exacte. Le commit corrigé est déjà poussé ; ne pas les relancer inutilement.

Sur une machine possédant un clone du dépôt, des droits d'écriture et les outils Git et GitHub CLI : authentifiez-vous localement avec `gh auth login --hostname github.com --web`, puis `gh auth setup-git` si nécessaire. **Ne transmettez pas de jeton ni de mot de passe dans le chat.**

Dans le clone, adaptez le chemin absolu du bundle puis exécutez :

```bash
(
  set -euo pipefail
  URL=https://github.com/meromoonmeri/PMDO-Destiny.git
  REF=refs/heads/wip/reverie-integration-kingambit-cafe
  BASE=8f80c6e2c47e681acd334be661d601a59fed2367
  CIBLE=7bd2dc104706571c91a2ea4a3c45282b94eabbb6
  BUNDLE='/chemin/absolu/Destiny-0.7.8-source.bundle'

  git fetch --no-tags "$URL" "$REF"
  DISTANT=$(git rev-parse FETCH_HEAD)
  if [ "$DISTANT" != "$BASE" ]; then
    echo "La branche distante a changé ($DISTANT). Arrêt : réintégrer les changements, sans forcer." >&2
    exit 1
  fi
  git bundle verify "$BUNDLE"
  git fetch --no-tags "$BUNDLE" refs/heads/preparation-0.7.8
  test "$(git rev-parse FETCH_HEAD)" = "$CIBLE"
  git merge-base --is-ancestor "$BASE" FETCH_HEAD
  git push "$URL" "$CIBLE:$REF"
  test "$(git ls-remote "$URL" "$REF" | cut -f1)" = "$CIBLE"
  echo "Commit présent sur GitHub : $CIBLE"
)
```

Si la branche a avancé, s'arrêter et réintégrer le travail sur la nouvelle tête ; **ne pas forcer**.

## 2. Compiler et contrôler sous Windows

Le second build a déjà réussi ; consulter `Etat-publication.json` avant de lancer une nouvelle construction.

Déclencher le workflow en mode construction :

```bash
gh workflow run build-windows.yml --repo meromoonmeri/PMDO-Destiny \
  --ref wip/reverie-integration-kingambit-cafe -f mode=build

gh run list --repo meromoonmeri/PMDO-Destiny --workflow build-windows.yml \
  --branch wip/reverie-integration-kingambit-cafe --event workflow_dispatch \
  --json databaseId,headSha,status,conclusion,url
```

Repérez le **nouveau** run dont `headSha` est exactement `7bd2dc104706571c91a2ea4a3c45282b94eabbb6`. Suivez-le avec `gh run watch <ID> --repo meromoonmeri/PMDO-Destiny --exit-status`, puis vérifiez dans GitHub Actions qu'il est terminé avec succès et qu'il contient `PMDO-Destiny-Windows-x64`. Tester le jeu et la sauvegarde sur une copie avant publication. Si le build ou ces essais échouent, ne pas publier.

## 3. Publier après validation

La publication a déjà réussi. Ne pas déclencher une seconde publication : le tag existe désormais.

Vérifiez qu'aucun tag `v0.7.8` n'existe et que le run sélectionné est bien celui du commit ci-dessus. Ensuite, dans la même session authentifiée, remplacez `<ID_DU_RUN_VALIDE>` par son identifiant numérique :

```bash
gh workflow run build-windows.yml --repo meromoonmeri/PMDO-Destiny \
  --ref wip/reverie-integration-kingambit-cafe \
  -f mode=release -f run_id=<ID_DU_RUN_VALIDE> \
  -f target_sha=7bd2dc104706571c91a2ea4a3c45282b94eabbb6 -f tag=v0.7.8
```

Suivez le nouveau run de publication et contrôlez la préversion GitHub, la note et les archives/chiffres SHA-256 effectivement générés. Le workflow prend `docs/REVERIE_078.md` et peut générer une mise à jour incrémentale depuis la précédente release. Ne pas annoncer sa présence avant vérification.
