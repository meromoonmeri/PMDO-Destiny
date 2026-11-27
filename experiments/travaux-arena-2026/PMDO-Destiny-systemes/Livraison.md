# Destiny — Bilans d’expédition, Zig et Zag, réfectoire

**Lot poussé et vérifié sur `wip/reverie-integration-kingambit-cafe`** : [commit `45082b7`](https://github.com/meromoonmeri/PMDO-Destiny/commit/45082b7f5c08b4b909f685e8256d4fb324ab036b), basé sur `d5d44d7edbca8ad39406db10257df20fac845d40`. Aucun tag ni release n’a été créé, et aucun build Windows n’a été déclenché manuellement. Le correctif contient les scripts, les ressources `Chara` et leur index, les tests et la documentation. Il ne contient ni profil de test ni modification des cartes, des décors, des salles ou des passages.

## Ce qui change en jeu

- **Bilans PMDO.** « La dernière sortie » et la fanfare natives s’affichent à la fin d’un trajet des Bois Perdus. La Fosse Cascade garde une seule expédition jusqu’à la fin : pas de bilan à la sortie du huitième étage, bilan après les retrouvailles, puis retour à Réverie. L’annonce d’ouverture est faite en ville, après l’accueil de Nilo. Une mission terminée est annoncée au retour ; sa récompense reste à réclamer au tableau.
- **Comptoirs de Réverie.** Zig, en vert, propose des provisions, des soins, des projectiles et de l’équipement. Zag, en violet, propose une CT, trois orbes et deux lots de baguettes. Les deux utilisent les menus natifs d’achat et de vente. Un article acheté disparaît de l’étal du jour. Une sieste chez Spinda fait passer au lendemain et renouvelle les deux stocks. Joliflor conserve son fonctionnement.
- **Réfectoire.** Gardevoir, Canarticho, Simisage, Mélofée, Cizayox, Noctali, Dimoret, Draby, Pandespiègle et Capumain prennent place dans la salle existante. Chacun joue un vrai `Eat` de corps : les miettes sont un complément. En dialogue, le convive se tourne vers le joueur, présente son rôle, puis reprend son repas.

## Vérifications

| Point | Résultat |
| --- | --- |
| Fosse Cascade, bilan et retour | Même expédition enregistrée du 8F à l’arène de Kabutops, sans bilan entre les deux. Après les retrouvailles de Nilo et Lyra : **un bilan natif et un seul enregistrement**. Retour à Réverie, accueil de Nilo et annonce d’ouverture également vérifiés. |
| Bois Perdus | Deux bilans et deux enregistrements distincts : aller solo → prairie du réveil, retrouvailles et retour en duo → falaise de jour. Équipe de 1 à l’aller et de 2 au retour, sans héros restant en réserve après la réunion. Les échecs, reprises et paiements uniques sont couverts par les tests Lua. |
| Achats, ventes et calendrier | Lot de quatre baguettes acheté chez Zag pour 100 Poké et revendu chez Zig pour 20. Autre essai : CT Façade achetée pour 2 500 Poké, sauvegarde au Café, arrêt et reprise du jeu. CT toujours dans le sac, étal de Zag toujours amputé d’une offre. Après la sieste, Zig et Zag proposent de nouveaux étals, pour un total de 8 et 6 offres. |
| Réfectoire | Dix convives en jeu, reprise du repas après le dialogue de Draby, sortie et retour par le carrefour conservé, puis dix convives à nouveau après rechargement, sans doublon. |

Les captures et traces sont dans `Preuves/`. Les tests moteur ont été effectués sous PMDC/Linux avec une fixture locale : les entrées de donjon et issues ciblées ont été accélérées, pas les menus de résultat ni les transactions. Ces essais ne certifient pas une traversée manuelle de tous les étages, un combat joué intégralement ou un build Windows. Le son était dirigé vers une sortie muette pendant ces captures ; le raccord aux fanfares natives est couvert par les appels et les ressources du moteur.

## Appliquer et rejouer les tests

Depuis le dépôt Destiny, sur la révision de base et avec un arbre propre :

```sh
git apply --check /chemin/vers/Destiny-systemes.patch
git apply /chemin/vers/Destiny-systemes.patch
```

**Appliquer le patch dans son ensemble** : les `.chara` et `game/Content/Chara/index.idx` doivent rester synchronisés. Le patch n’est pas un jeu autonome. Les cartes de la ville restent dans le payload existant et se reconstruisent avec `tools/unpack_payload.py` comme avant.

```sh
python -m pip install Pillow lupa
python tools/tests/test_boutiques_kecleon.py
python tools/tests/test_guilde_eat_runtime.py
python tools/tests/test_guilde_effectif.py
python tools/tests/test_grotte_verdoyante.py
python tools/tests/test_tableaux_reverie.py
```

La liste exacte des chemins figure dans `Fichiers-modifies.txt` ; les résultats des autres régressions locales sont dans `Preuves/Tests-automatisés.txt`.
