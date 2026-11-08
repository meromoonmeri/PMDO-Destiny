# Audit global des chemins de Réverie — travail en cours

Base : v0.5.7, commit `ee39156a24f350b67e81740478be8505f4ff1a05`. Le rapport préalable est `RAPPORT-PREALABLE-AUDIT-CHEMINS-COMPLETS.md`. Les travaux ci-dessous sont **locaux, non publiés et non validés en jeu**.

## Couverture et variantes

Les dix planches `audit-chemins-global/vue-{0..4}-{0..1}.png` couvrent les 1 600 × 4 000 pixels de la carte à l'échelle native, phase 0, et ont fait l'objet d'un examen visuel d'ensemble. Le dernier secteur au sud (y 3200–3999) est essentiellement boisé, sans chemin principal visible. L'examen à cette échelle et sur une seule phase n'est pas une vérification exhaustive de chaque pixel, ni des zones sous les décors.

Les cellules des 11 couches ont été comparées par empreinte SHA-256 de leur représentation JSON canonique, couche par couche : les 10 cartes jeu et développement ont exactement les mêmes cellules et noms de couches. Résultat reproductible : `audit-chemins-global/comparaison-couches-variantes.json`, script `audit-chemins-global/comparer-variantes.py`. Cela ne signifie pas que les événements, collisions ou autres métadonnées de cartes sont identiques : ils n'ont pas été comparés par ce test.

## Raccords constatés et état

- Escalier de la capture 51, secteur nord-est, autour de (1447, 599) : reprise locale antérieure conservée, avec chemin rejoignant les deux extrémités et retours d'herbe/sable en modules Métano. `reprise-arrondie-27-51-52/escalier51-avant-apres.png`.
- Chemin de la capture 27, vers (672, 1765) : saillie de bordure coupée, confirmée. Un module complet du sol Métano (584, 640)–(616, 672) a été copié sans rotation, changement d'échelle, interpolation ni recoloration vers (664, 1752)–(696, 1784). Ajout local sur 13 cellules, 568 pixels réellement modifiés. Aucune couche supérieure ne recouvre les pixels modifiés. Avant/après : `reprise-arrondie-27-51-52/chemin27-avant-apres.png`. C'est une correction locale du bord gauche, pas une correction intégrale de la capture 27.
- Autres bordures de la capture 27 vers (728, 1800) à droite et (672, 1816) à gauche : transitions suspectes à revoir. Les essais de remplacement plus étendus créent des coutures ou excroissances et ont été écartés, y compris `audit-chemins-global/27-deux-bords-candidat.png` et `27-trois-candidat.png` ; ils ne figurent pas dans les cartes modifiées.
- Chemin contre l'eau vers (279, 1176), capture 48 : coupure déjà connue ; encore ouverte, doit être traitée sans recouvrir les animations d'eau.
- (151, 743), sous un arbre : zone de terre plate suspecte, partiellement masquée ; pas assez de preuve pour la modifier. (413, 583) semble être le seuil d'une porte et (583, 2738) est masqué/ambigu ; non modifiés.
- La rive capture 52 fait partie du même paquet local : déplacement irrégulier du bord, quatre phases conservées ; elle doit encore être regardée dans le moteur.

Les autres chemins ont été parcourus dans les vues d'ensemble, mais certains détails et bords masqués restent à inspecter en zoom et en couches séparées ; les captures 28–29, 31, 33–39, 42, 44–50 et le reste de 30 restent ouverts selon les audits précédents. **Ne pas conclure que toutes les coupures du monde sont corrigées.**

## Vérifications et sauvegarde

`preparer-arrondis-27-51-52.py` repart des dix cartes d'origine, ne modifie que les cellules concernées de `Base` et `Objects Over`, conserve les données de chaque cellule, et teste que les nouveaux pixels du sol ne recouvrent pas les couches supérieures. `verifier-arrondis-27-51-52.py` recompose indépendamment les trois zones 27, 51 et 52, compare les pixels aux sources attendues et vérifie quatre phases, banque, durées et empreintes des dix sorties : PASS. Les empreintes des cartes ne constituent pas un test de rendu complet de chaque carte en jeu ; l'identité des cellules des couches d'origine complète ce contrôle.

Reprise locale : `reprise-arrondie-27-51-52/`. Sauvegarde CRC vérifiée : `sauvegarde-reprise-arrondie-27-51-52-local.zip`, SHA-256 `794e16ec7a8e854bb725967abb52323e73675724645a1b0e932fcf7a49aa782b`. Elle n'est ni une release ni une publication et ne remplace pas la sauvegarde d'origine `sauvegarde-057-avant.zip`.

## Autres chantiers encore ouverts

Écran noir du café : correctif local préparé, mais cause Windows UTF-8/ANSI et réparation non confirmées en moteur Windows. Voir `../chantier-cafe-ecran-noir/RAPPORT-AUDIT-CAFE.md`. Catalogue PMU : cinq objets locaux seulement ; conversion et disponibilité exhaustive des ressources et Char Display non établies. Aucun push, aucune CI ou nouvelle release pour ces modifications. Validation en jeu et avec sauvegardes réelles indispensable avant publication.
