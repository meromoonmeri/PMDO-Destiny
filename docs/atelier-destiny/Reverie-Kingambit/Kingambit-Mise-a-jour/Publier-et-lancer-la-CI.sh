#!/usr/bin/env bash
# À exécuter sur son ordinateur, depuis un clone de PMDO-Destiny.
# Usage : bash Publier-et-lancer-la-CI.sh [chemin/vers/Destiny-Kingambit-PMD.bundle]
# Aucun jeton à saisir dans ce script ou à donner dans la conversation.
set +x
set -euo pipefail

repo=meromoonmeri/PMDO-Destiny
branch=dojos-kingambit-pmd
ref="refs/heads/$branch"
base_branch=wip/reverie-integration-kingambit-cafe
base=37e6b5cdcfb46a064239c7c6983ef4840d27d408
commit=36630860da1afb433dafb971a6dd9890fbb11ca9
bundle_sha256=b93168b6b11e722ede5dd3129cee7479ac15e2f35278efb3e9f0547ed16af6a4
workflow=build-windows.yml
bundle=${1:-"$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)/Destiny-Kingambit-PMD.bundle"}

die() { printf 'Arrêt : %s\n' "$*" >&2; exit 1; }
command -v git >/dev/null || die 'Git est requis.'
command -v gh >/dev/null || die 'Installe GitHub CLI depuis https://cli.github.com/.'
git rev-parse --git-dir >/dev/null 2>&1 || die 'Ouvre un terminal dans ton clone de PMDO-Destiny.'
[[ -f "$bundle" ]] || die 'Donne le chemin du bundle cumulatif en premier argument.'

approved_url() {
  case "$1" in
    "https://github.com/$repo"|"https://github.com/$repo.git"|\
    "git@github.com:$repo"|"git@github.com:$repo.git"|\
    "ssh://git@github.com/$repo"|"ssh://git@github.com/$repo.git") return 0 ;;
    *) return 1 ;;
  esac
}
fetch_url=$(git remote get-url origin) || die 'Le distant origin est absent.'
push_url=$(git remote get-url --push --all origin) || die 'Le distant de publication est absent.'
approved_url "$fetch_url" && approved_url "$push_url" || die "origin doit pointer uniquement vers github.com/$repo."
if command -v sha256sum >/dev/null; then
  actual_sha256=$(sha256sum < "$bundle")
elif command -v shasum >/dev/null; then
  actual_sha256=$(shasum -a 256 < "$bundle")
else
  die 'Il faut sha256sum ou shasum pour vérifier le bundle.'
fi
[[ "${actual_sha256%% *}" == "$bundle_sha256" ]] || die 'Le bundle ne correspond pas à la livraison vérifiée.'

# Ce lanceur n’accepte aucun jeton transmis en variable ; il utilise seulement
# la session GitHub CLI locale ou une authentification GitHub dans le navigateur.
unset GH_TOKEN GITHUB_TOKEN GH_ENTERPRISE_TOKEN GITHUB_ENTERPRISE_TOKEN
export GH_HOST=github.com GIT_TERMINAL_PROMPT=0
if ! gh auth status --hostname github.com >/dev/null 2>&1; then
  gh auth login --hostname github.com --git-protocol https --web --scopes workflow || die 'Connexion GitHub non terminée.'
elif [[ "$push_url" == https://* ]]; then
  # Sans cette portée, GitHub rejette les commits qui modifient un workflow.
  if scopes=$(gh api --hostname github.com --include "repos/$repo" 2>/dev/null |
      awk 'tolower($0) ~ /^x-oauth-scopes:/ { sub(/^[^:]*:/, ""); gsub(/[[:space:]]/, ""); print }'); then
    if [[ -n "$scopes" && ",$scopes," != *',workflow,'* ]]; then
      gh auth refresh --hostname github.com --scopes workflow || die 'Autorise la portée workflow dans le navigateur, puis réessaie.'
    fi
  fi
fi
repo_git() { git -c credential.helper= -c 'credential.helper=!gh auth git-credential' "$@"; }

if ! git cat-file -e "$base^{commit}" 2>/dev/null; then
  repo_git fetch origin "refs/heads/$base_branch"
fi
git bundle verify "$bundle" || die "Récupère l’historique de $base_branch dans ton clone, puis réessaie."
git fetch --no-tags "$bundle" "$ref"
[[ "$(git rev-parse FETCH_HEAD)" == "$commit" ]] || die 'Le commit du bundle n’est pas celui prévu.'

# Pas de force, pas de tag, pas de changement de branche locale.
repo_git push origin "$commit:$ref"
remote=$(repo_git ls-remote --exit-code --refs origin "$ref")
[[ "${remote%%$'\t'*}" == "$commit" ]] || die 'Le distant ne pointe pas sur le commit attendu ; CI non lancée.'
printf 'Push vérifié : %s (%s).\n' "$branch" "${commit:0:7}"

# Le workflow n’a pas de déclencheur push. Le mode normal par défaut est
# build (Windows + contrôles + ZIP), sans publication de release.
if ! gh workflow run "$workflow" --repo "$repo" --ref "$branch" --json <<< '{}'; then
  die "Push confirmé, mais la demande de CI a échoué. Vérifie les droits Actions : https://github.com/$repo/actions/workflows/$workflow"
fi
printf '\nDemande de build envoyée, résultat à vérifier dans Actions.\n'
printf 'https://github.com/%s/actions/workflows/%s?query=branch%%3A%s\n' "$repo" "$workflow" "$branch"
