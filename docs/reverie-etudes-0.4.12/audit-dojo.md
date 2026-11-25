# Rapport avant modification — dojo de Réverie

## Décisions confirmées

- Le grand dojo nord-est utilisera la salle carrefour Ledian existante comme intérieur. Son image de référence est `salle_carrefour/composition.png` dans le lot `ledian_dojo_v1` ; quatre accès graphiques N/S/E/O. Leur affectation et leur connexion aux souterrains ne sont pas établies, à l'exception de la volonté générale d'accéder au réseau par la grotte indiquée. Ne pas inventer les destinations ou la liaison au casino.
- Retirer uniquement le tapis rouge posé devant l'entrée du grand dojo nord-est, pas les tentures rouges ni le reste du bâtiment, et pas le tapis du café Spinda.

## Audit et risques avant intervention

- Carte de référence : 0.4.11, `WaterfallVillageCapital` (11 calques de jeu) et `WaterfallVillageCapital_Dev` (37 calques d'édition), dans `Reverie-systeme-11-jeu-37-edition-EXPERIMENTAL.zip`. Ce n'est pas nécessairement l'état d'un projet téléchargé depuis lors.
- Le tapis est dessiné dans la même banque et le même sprite que l'édifice : `Reverie_WV_14_Trimmed_Decor`, calque d'édition 28 (index 27), composite jeu 08 (index 7). Un masquage global de la banque, ou une suppression de tuiles entières, risquerait d'enlever aussi le seuil et les murs.
- Préparer uniquement une copie : 40 tuiles partiellement masquées, ajoutées à des positions inutilisées de la même banque ; conserver tous les anciens pixels et toutes les autres tuiles, et pointer seulement les 40 références uniques concernées dans chacune des deux cartes vers les nouvelles tuiles. Le tapis est limité au rectangle x=[1437,1491[ et y=[380,416[, avec deux très fins bords d'ombre x=1436 et x=1491 (seuls les pixels sombres semi-transparents sont masqués). La carte est en pixels natifs. Hors rectangle, pixels identiques. Le masque révèle le calque existant sous le tapis ; le pied du bâtiment peut nécessiter une retouche esthétique.
- Sauvegarder d'abord les deux cartes et la banque, vérifier les nouveaux indices et la recomposition avant d'envisager toute installation. Ne pas modifier les collisions ni les événements. Le moteur teste l'interaction à un pixel de la hitbox ; supprimer le visuel ne rend pas le seuil automatiquement accessible.
- La salle carrefour est une composition graphique générée issue du lot Ledian, non une `.rsground` jouable. Il faudra reconstruire une carte et son index, définir géométrie/collisions, une sortie visible noire conforme à la demande antérieure, l'entrée et le retour, préserver les personnages/dialogues du dojo, puis tester dans PMDO 0.8.12. Ses quatre accès visibles n'établissent pas des destinations. Ce travail de raccordement n'est pas compris dans l'aperçu.
- Aucune application au dépôt ni publication sans compléter l'audit de références/sauvegardes et les tests. La 0.4.11 et ses tags restent inchangés.
