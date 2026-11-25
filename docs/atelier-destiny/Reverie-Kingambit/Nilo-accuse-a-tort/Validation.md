# Fosse Cascade Fond — Nilo accusé à tort

**Version locale :** `e156041b3274723deb360f2fd99f0a16925d9d32`. La retouche porte sur la cinématique, pas sur l’équilibrage du duel. Aucune publication ni build Windows.

## Ce que montre la prise

- La caméra suit d’abord le duo dans le passage, puis découvre Nilo déjà en train de trembler, à sa place sur la terrasse.
- Kabutops parle deux fois sous `???`, sans portrait. Entre les avertissements, le duo échange un regard, le partenaire demande qui parle et Nilo explique qu’il cherchait juste la sortie. Kabutops n’a pas vu Nilo toucher les vasques : il l’accuse à cause de sa présence.
- Après le second avertissement, l’ombre précède un éclair unique. Kabutops est révélé **devant et exactement entre les deux axes** du duo : `(280,244)` face au héros `(292,268)` et au partenaire `(268,268)`. Le coup et le recul se jouent avec le retour à l’image, sans passage par la rive ; les deux héros glissent jusqu’à `y=292` en restant tournés vers lui.
- Le woosh et l’entrée sans carton se raccordent à la même arène. La revanche saute la découverte et les avertissements.

### Repères dans `Cinematique-Kabutops-Nilo-accuse-a-tort.mp4`

| Repère | À l’écran |
| --- | --- |
| 0:08 | Première réplique devant Nilo, déjà tremblant |
| 0:13 | Premier avertissement `???` |
| 0:16–0:20 | Regards du duo, question et démenti de Nilo |
| 0:22 | Second avertissement `???` |
| 0:24 | Éclair, apparition de Kabutops et recul |
| 0:34 | Début du woosh natif |
| 0:41 | Ouverture sur l’arène et sa musique, sans carton de lieu |

La vidéo de **45,13 s** vient d’une prise dans PMDO (640 × 480 à 30 i/s, H.264/AAC, sans son ajouté). Les preuves associent les plans, la trace moteur et les repères audio à cette prise. La cadence dans la VM diffère de la cadence nominale du jeu ; les repères du tableau sont ceux de la vidéo.

## Contrôles

- Tests Python et Lua : passage des colliders, deux avertissements avant l’apparition, ancre de Nilo fixe avec tremblement, recul, revanche courte, phase et route vers l’arène. Audits de cadrage et de largeur des répliques OK. Index des tuiles conforme.
- Les cartes, l’arène, les atlas et la zone 9F sont identiques à ceux du lot **Vasques agrandies**. Dans cette retouche, la prise en jeu s’arrête au lancement du duel. Le KO et la victoire vers Réverie avaient été vérifiés dans le lot précédent ; ils n’ont pas été rejoués pour cette prise. La seule modification d’après-combat est une réplique de Nilo cohérente avec la fausse accusation.

## Fichiers d’intégration

- `Correction-Nilo.patch` : retouche seule, pour la base `5bf5783dc0208cc40cf112339f65448b4698982e` du lot **Vasques agrandies**. L’application du patch reproduit exactement l’arbre livré.
- `Cinematique-Kabutops-complete.bundle` : historique incrémental du chantier sur `37138a7ca93be920e9c47963fea21441b153ec65`, avec l’extension de carte et la correction. Ce bundle nécessite la base ; il n’est pas un jeu autonome. Régénérer l’index des tuiles à l’intégration.
- `Preuves/` : plans de la prise, entrée de l’arène, trace PMDO, contrôle du son et résultats des tests.
