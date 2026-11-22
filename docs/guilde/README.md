# Atelier de la Guilde · PMD Destiny 0.7.7

Ouvre `Guilde-Destiny.html` dans ton navigateur. La page est autonome : aucun serveur, compte ou téléchargement d’images n’est nécessaire. Les 15 salles utilisent le décor de la publication Windows 0.7.7, avec le vitrage R2 et le liseré sans rallonge. Aucun meuble n’est posé au départ.

## Visiter et aménager

1. Choisis une salle. Les boutons **Jour**, **Aube**, **Crépuscule** et **Nuit** changent les vitres et la lumière d’après les ressources du jeu. **Comparer les 4** affiche ton plan aux quatre moments à la fois.
2. Dans **Plan**, sélectionne l’un des 33 objets **Mobilier PMU** et clique à l’endroit voulu. Tu peux glisser les meubles, les dupliquer ou les retirer. L’aimant utilise la grille native de 8 px ; désactive-le pour poser au pixel près. Les flèches déplacent l’objet sélectionné ; `Maj` + flèche avance d’un pixel.
3. **Cadre sud** est une vue de 320 × 240 px calée sur le seuil. **Avant** permet de retrouver la caméra d’origine. La carte et les coordonnées des meubles ne sont pas modifiées par ce bouton.
4. **Exporter → Plan de l’atelier** enregistre tout le projet en JSON. **Ouvrir un plan** recharge un export. La copie automatique du navigateur est un confort : garde un JSON à part. Depuis un aperçu intégré, ouvre la page téléchargée dans ton navigateur si les téléchargements sont bloqués.

## Utiliser un aménagement dans le jeu (facultatif)

Installe d’abord le correctif de cadrage 0.7.7 (les scripts du premier commit de cette mise à jour), avant que tes cartes ne soient personnalisées.

1. Choisis la salle aménagée, puis **Exporter → Copie de carte pour Destiny**.
2. Sélectionne le `.rsground` d’origine de cette salle dans `Data/Ground`. L’atelier vérifie sa correspondance exacte avec la publication Windows 0.7.7. Si la carte est déjà modifiée, réutilise ta copie originale intacte.
3. Le navigateur télécharge une **nouvelle copie du même nom**, sans écrire dans le jeu. Ferme Destiny, sauvegarde l’original ailleurs, puis remplace la carte de cette salle. Pour revenir en arrière, remets simplement l’original. Conserve le JSON et les originaux si tu veux modifier ton aménagement plus tard.

Cette opération ajoute seulement un calque décoratif qui référence les sprites `.dir` PMU déjà fournis avec Destiny. Le mobilier est **traversable** : ni collisions, ni seuils, ni marqueurs, ni textures du sol, ni scripts, ni sauvegardes ne sont modifiés. L’outil garde libres les seuils et leur arrivée, et ne prolonge pas les chemins.

## Sources

Plan 0.7.7 : publication Windows `v0.7.7`, commit `3d86bd838698d9de699c76f6f715c8eef35562e5`. Les 33 meubles sont les objets natifs `Content/Object/Guilde_Imm_pmu_*.dir` de cette publication (adaptations PMU historiques, voir `BANQUES_PMU.md` du jeu). Les images de fenêtre n’ont pas été remplacées par une coloration générique. Le HTML ne contient ni service externe ni suivi.

`Sources/Assembler.py` permet de reconstruire le HTML après modification de son gabarit, de sa feuille de style ou de son JavaScript ; il réutilise les données intégrées au fichier existant.
