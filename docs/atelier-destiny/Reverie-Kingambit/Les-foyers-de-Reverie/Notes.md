# Les foyers de Réverie

Extension locale du **Carnet des retours**. Les cinq habitations déjà raccordées ont des habitants ; ni la Guilde, le café, l’auberge ni les services ne sont remplacés. Aucune modification de l’équipe du joueur, des tuiles ou du tracé des portes.

| Lieu | Rencontre | Ce qui reste après une visite |
| --- | --- | --- |
| **Maison de Pierre** | Maëlle et Basalte, compagnons, et leur fille Miette. Une devinette avec indice de Basalte et réaction à la réponse. | Une Baie Pêcha à la résolution. Maëlle la garde de côté si le sac est plein. |
| **Maison plante** | Flore, Aulne et Brin. Flore propose l’un des deux en-cas préparés en famille. | Une Pomme **ou** une Baie Oran, une fois. Brin se souvient de ce qui a été pris. |
| **Hutte du nord-est** | Nacre, Malo et Perle. Une autre devinette, sur la rivière, avec un indice et une réplique de Malo qui remet le lot. | Une Échaporbe à la résolution, sans retrait si l’inventaire est plein. |
| **Hutte aquatique du sud** | Yuna, la compagne du pêcheur Marius, et Lino. Lino hésite sur l’endroit où laisser un mot à son père. | Deux réponses différentes de Yuna, puis un retour sur le choix à la visite suivante. Marius reste au bord de l’eau. |
| **Maison citrouille du sud** | Zélie accueille les visiteurs tant que le trio n’est pas rentré. Après leur saynète sous l’arbre, Lyra, Léo et Nilo rentrent au prochain changement de carte. | Un choix sur ce que Nilo fait de son dessin, avec une réponse de Lyra et une suite différente de Léo. Pas de deuxième Nilo dehors. |

## Intégration

- `reverie_foyers_recits.lua` définit les habitants (genre du moteur, sprite déjà présent, prénom, poste, répliques) et les menus. Les répliques lisent les jalons du Carnet : Bois Perdus, alerte, retour de Nilo et retour de la crique. Certaines positions varient elles aussi, sans rotation au hasard.
- `reverie_foyers.lua` mutualise les entrées/sorties et les échanges. Les acteurs sont créés après l’installation du partenaire ou réutilisés à la reprise. Les colliders, repères et objets existants sont protégés ; le repli déplace le PNJ, jamais l’équipe. Les regards, pauses et portraits utilisent les aides cinématiques de Destiny. Pas de scène imposée à l’entrée et pas de changement de caméra.
- Les résultats des décisions et les cadeaux réellement reçus sont mémorisés dans `SV.Destiny.FoyersReverie`. L’annulation ne choisit pas à la place du joueur ; une mauvaise réponse n’épuise pas la devinette. Le marqueur de résolution reste vrai si le cadeau ne rentre pas dans le sac. Une sieste ou une réentrée ne recharge pas le panier de cadeaux.
- `recit.FamilleAuFoyer` ne s’active qu’au jalon de Nilo, après la scène extérieure complète. La famille n’est pas retirée au milieu de l’échange ; les états de visite, d’alerte et d’accueil gardent la priorité. Les anciennes sauvegardes sans la nouvelle table commencent les rencontres normalement.

## Contrôles à rejouer

```sh
python -m pip install lupa Pillow ijson
python tools/tests/test_reverie_foyers.py
python tools/tests/test_reverie_recit.py
python tools/tests/test_entrees_reverie.py
python tools/tests/test_hutte_aquatique.py
python tools/tests/test_suivi_interieurs.py
```

Le test des foyers utilise les cinq cartes natives, y compris les marqueurs d’anciennes entrées et les capteurs de sortie. Il vérifie la circulation en 16 × 16, les genres, les répliques par jalon, les deux devinettes, le sac plein et la reprise des branches. Les tests Lua utilisent des doubles du moteur : le rendu, les menus et l’écriture de la sauvegarde se contrôlent aussi dans PMDO.
