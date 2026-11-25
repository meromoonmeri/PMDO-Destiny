# Publier la mise à jour Kingambit et Réverie

- **Dépôt :** `meromoonmeri/PMDO-Destiny`
- **Branche à publier :** `dojos-kingambit-pmd`
- **Dernier commit :** `36630860da1afb433dafb971a6dd9890fbb11ca9`
- **Prérequis du bundle cumulatif :** `37e6b5cdcfb46a064239c7c6983ef4840d27d408`, historique de `wip/reverie-integration-kingambit-cafe`.

**[Préversion v0.7.7 publiée](https://github.com/meromoonmeri/PMDO-Destiny/releases/tag/v0.7.7).** Le [build Windows #44937172432](https://github.com/meromoonmeri/PMDO-Destiny/actions/runs/44937172432) et la [publication #44938062280](https://github.com/meromoonmeri/PMDO-Destiny/actions/runs/44938062280) ont réussi sur `3d86bd8`, dans la branche `wip/reverie-integration-kingambit-cafe`. La release contient le ZIP Windows x64 complet et le ZIP de mise à jour depuis `v0.7.6` avec leurs sommes SHA-256. `main` et `dojos-kingambit-pmd` n’ont pas bougé.

Le premier build sur la révision originale `3663086` a échoué. `Correctif-CI-trames-Reverie.patch` corrige le contrôle des trames transparentes ; `Correctif-Packaging-Reverie.patch` synchronise le compacteur avec le payload officiel. Ces deux correctifs sont dans le commit publié. Voir `Etat-du-push.txt` et `Suivi-v0.7.7.json` pour les détails.

La procédure ci-dessous documente le push de la révision originale. Elle **n’est pas nécessaire** pour installer la préversion publiée.

## Pousser et lancer la CI en une commande

Installer [GitHub CLI](https://cli.github.com/) si nécessaire, puis ouvrir le terminal dans le clone de Destiny (Git Bash sous Windows). Télécharger `Publier-et-lancer-la-CI.sh` et `Destiny-Kingambit-PMD.bundle`, puis lancer :

```sh
bash /chemin/vers/Publier-et-lancer-la-CI.sh /chemin/vers/Destiny-Kingambit-PMD.bundle
```

Le lanceur utilise ta session GitHub CLI ou ouvre la connexion dans le navigateur en demandant la portée `workflow`. Si cette portée manque dans une session OAuth existante, il demande son autorisation. L’équivalent manuel pour une session GitHub CLI déjà ouverte est `gh auth refresh --hostname github.com --scopes workflow`.

Il vérifie le bundle, pousse `3663086` uniquement sur `dojos-kingambit-pmd`, contrôle la ref distante, puis envoie la demande **Build Windows**. Ce workflow est manuel : un push seul ne le démarre pas. Le build produit un ZIP Windows en artefact ; il ne modifie pas `main`, ne crée pas de tag et ne publie pas de Release.

## Depuis un clone Destiny dont le compte a le droit d’écrire : méthode manuelle

Télécharger `Destiny-Kingambit-PMD.bundle`, puis remplacer le chemin ci-dessous. La procédure ne change pas la branche locale courante et ne publie que la révision vérifiée sur la branche Kingambit, **sans force**.

```sh
(
  set -e
  bundle=/chemin/vers/Destiny-Kingambit-PMD.bundle
  git fetch origin wip/reverie-integration-kingambit-cafe
  git bundle verify "$bundle"
  git fetch "$bundle" refs/heads/dojos-kingambit-pmd
  test "$(git rev-parse FETCH_HEAD)" = 36630860da1afb433dafb971a6dd9890fbb11ca9
  git push origin FETCH_HEAD:refs/heads/dojos-kingambit-pmd
)
```

Si la vérification signale une base absente dans un clone superficiel, récupérer l’historique complet de la branche d’intégration avant de réessayer. Si la branche locale ou distante diverge, ne pas forcer : vérifier ses commits avant de la mettre à jour. Utiliser la session Git habituelle du compte ou s’authentifier via GitHub CLI sur son propre terminal ; ne pas transmettre de jeton dans la conversation.

## Ce qui est inclus

- Les dojos, le casting et les **18 wooshes PMD** contrôlés, avec le blanc natif en fin de transition. Dazzling reste intacte. Cyclones Dragon/Vol, pluie Eau et canicule Feu.
- L’addon facultatif `Mega_Stones_Reverie` avec les **48 émoticônes et sprites d’objets**, dont les quatre X/Y, et **48 descriptions françaises**. Les effets et les textes par défaut ne changent pas.
- Les icônes et sprites raccordés aux six baies de Destiny, dont la récompense Pêcha. Ce correctif est indépendant de l’addon.
- Les aperçus Méga sans colonnes et **Éclipse X — Prisme fendu**, qui reste un aperçu hors moteur.

Le pack Git a été vérifié, déballé dans un dépôt isolé et les objets du lot sont présents. Les cinq tests Lua Kingambit avaient réussi. Les descriptions ont été contrôlées dans le vrai menu du sac de PMDO Linux 0.8.12 en français, avec un contrôle du texte anglais par défaut. Ce n’est pas une validation Windows complète.

L’aperçu `Apercu-18-wooshes-PMD.mp4` est inchangé. `SHA256SUMS.txt` vérifie le film et le bundle.
