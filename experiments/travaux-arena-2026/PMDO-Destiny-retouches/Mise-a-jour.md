# PMDO Destiny — Mise à jour prête à publier

**18 novembre 2026 · Branche `wip/reverie-integration-kingambit-cafe`**

Le [bundle Git de la mise à jour](PMDO-Destiny-Mise-a-jour.bundle) contient les deux commits, sans sauvegarde ni fichier de test moteur :

| Commit local | Contenu |
|---|---|
| `d8ac7275` | Fosse Cascade : avant-combat, eau et placement sur le sable. Réverie : raccords, arbres et gestes des habitants. [Comparatifs et captures](Retouches.html). |
| `b5639d1e` | Correctifs de l’audit : garde du partenaire, retour direct du Café, tests du Café resynchronisés, fin du repas de Guilde et compacteur aligné sur le payload publié. |

**Publication : bloquée par l’authentification GitHub.** Le `git push` a été tenté ; la branche distante pointait toujours sur `aa1430c4` après la tentative. Aucun push forcé ni changement d’une autre branche. [Vérification Git](preuves-audit/etat-git.txt).

## Ce qui a changé après l’audit

- **Falaise de nuit.** Avec un seul membre, la carte s’affiche et le joueur garde la main ; le script ne cherche pas un partenaire inexistant et ne marque pas la scène comme terminée. Un spawner indisponible rend aussi la main. Le chemin du duo garde la scène du partenaire sélectionné.
- **Café Spinda.** Après la visite de la ville, la sortie revient directement devant le Café dans `reverie_centre`. Avant la visite, le chemin d’origine est conservé. Le test protège les entrées, les capteurs et leurs raccordements, plutôt que l’empreinte des décors d’une ancienne carte. Les cartes du Café ne sont pas modifiées.
- **Repas de Guilde.** Un repas à durée positive coupe les émotes et rend **les mêmes convives** au repos. Une durée `0` laisse le contrôle de l’arrêt à `FinRepas`. Le `Eat` de Gardevoir est intégré à sa planche normale, avec l’index corrigé ; les planches des autres formes et peaux sont conservées. Le placement permanent des convives et la scène collective de la Guilde restent à faire.

**48 suites validées** après la relance du test de compactage ; le validateur du projet passe sur **17 843 fichiers**. Le compacteur produit une copie identique de la carte déjà compacte, sans assouplir le refus d’écraser une édition. [Résultats détaillés](preuves-audit/validation-audit.txt).

## Vérifications en jeu

| Essai | Ce qui est attesté |
|---|---|
| [Falaise, équipe solo](preuves-audit/falaise-solo.png) | Profil Dev, départ direct : carte visible, déplacement de `(550,468)` à `(568,468)`, pas de départ automatique. La branche duo est vérifiée avec des doublures Lua. |
| [Café : première visite](preuves-audit/cafe-accueil.png) et [retour direct](preuves-audit/cafe-direct-retour.png) | Entrée au Café par la porte de Réverie, scène d’accueil jouée sur un premier profil. Aller-retour par les portes sur un second profil ; la carte historique n’est pas chargée au retour. |
| [Escalier fermé](preuves-audit/cafe-escalier-ferme.png) et [étage ouvert en test](preuves-audit/cafe-etage.png) | Le message de travaux apparaît en jeu. Avec le drapeau de réouverture activé seulement sur le profil de test, l’escalier mène à l’étage. La salle de spectacle reste vérifiée sur la grille et dans les scripts, pas sur un trajet complet joué. |
| [Gardevoir dans le réfectoire, fixture](preuves-audit/gardevoir-fixture.png) | Un exemplaire temporaire créé pour l’essai charge bien `Eat` (index **48**, cycle de **28 ticks**). Le test natif passe de l’action animée à l’attente après `Repas`. Le réfectoire livré n’est pas peuplé par cette fixture. |

[Extrait des essais moteur](preuves-audit/essais-moteur-audit.txt). Ces essais par scènes ne valident pas une traversée complète de la quête ni l’audio.

## Publier depuis un clone déjà authentifié

Télécharger le `.bundle`, puis, depuis le clone de `meromoonmeri/PMDO-Destiny`, remplacer le chemin de l’exemple par celui du fichier téléchargé :

```bash
git fetch origin refs/heads/wip/reverie-integration-kingambit-cafe
git fetch "/chemin/PMDO-Destiny-Mise-a-jour.bundle" refs/heads/wip/reverie-integration-kingambit-cafe
git push origin FETCH_HEAD:refs/heads/wip/reverie-integration-kingambit-cafe
```

Le bundle a été vérifié et importé sans changer l’arbre de travail. Si le distant a avancé, le push normal refusera d’écraser les nouveaux commits : ne pas ajouter `--force`. Aucun jeton n’est nécessaire dans le chat.

**Intégrité du bundle (SHA-256) :** `c984fcda54be23b64d20e63c4ce22cb7662a840758c7fe6f5373d4c999da49a3`.
