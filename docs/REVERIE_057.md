# Rapport préalable — météo quotidienne de Réverie

Base : 0.5.6, commit `76bd58157d72f20bc01231704121834b89e7cdcd`, branche utilisateur vérifiée. Scripts et sources moteur concernés sauvegardés dans `sauvegarde-avant-meteo-056.zip` ; empreintes des fichiers du mod vérifiées sur Git et CRC de l’archive contrôlée. Les autres projets PMDO et les sauvegardes de partie ne sont pas modifiés.

## Constat

- Le jeu possède déjà `SV.Destiny.JourneeVille` : la sieste chez Spinda l’incrémente et renouvelle les stocks. Il n’existe pas encore d’horloge météo ni de changement automatique au temps réel. Les anciennes sauvegardes peuvent ne pas avoir ce compteur.
- Les variantes du centre, nord, étang et résidentiel partagent le script de la ville ; il pose actuellement l’effet natif `clouds_overhead`. Le carrefour dispose de son propre script extérieur ; les maisons et le café sont séparés.
- Dans `ScriptGroundMisc.cs`, `GROUND:AddMapStatus` applique un effet esthétique en Ground. `GSceneMap.cs` montre que `RemoveMapStatus` arrête son émetteur et qu’ajouter un statut déjà présent est sans doublon. Les données natives `rain`, `sunny` et `cloudy` possèdent respectivement des émetteurs de pluie, de lumière et de nuages ; `heavy_rain` ne produit pas de pluie et ne sera pas utilisé. Les cartes de ville et de carrefour inspectées ont un dictionnaire de statuts initialement vide.

## Projet et risques

Tirer une météo lors du premier accès à chaque journée de jeu : temps clair, ensoleillé, couvert ou pluvieux, pondérés. Enregistrer le résultat et le numéro du jour dans `SV.Destiny` : tous les quartiers et le carrefour conservent la même météo pendant cette journée, y compris après changement de carte ou chargement ; deux jours peuvent avoir la même météo. Une ancienne sauvegarde sans champ météo reçoit une valeur au premier accès, sans réinitialiser son compteur ni ses états. La sieste indique le temps du lendemain sans appliquer de pluie à l’intérieur du café.

Conserver l’effet `clouds_overhead` de la ville, n’appliquer les nouveaux statuts qu’aux cartes extérieures explicitement concernées, et ne pas altérer les cinématiques fixes de la falaise ni les donjons. Ne pas ajouter de boucle sonore susceptible de couvrir la musique ou les effets de scène. Remplacer les seuls statuts météo gérés par ce module à l’entrée/chargement, pas à chaque frame.

Vérifier tirage, sauvegarde/rechargement, passage de jour, mêmes météo sur les cartes et carrefour, anciennes sauvegardes, interruption/fallback et absence d’effet intérieur sur doublures, puis CI. Le rendu, le son ambiant, la compatibilité avec une sauvegarde réelle et la lisibilité des portraits sous la pluie devront être vérifiés en jeu : une simulation ne les certifie pas.

## Mise en œuvre et vérification locale

La météo est enregistrée dans `SV.Destiny.MeteoReverie` et reliée à `JourneeVille`. Répartition : clair 35 %, soleil 20 %, couvert 20 %, pluie 25 %. La météo annoncée après la sieste est celle du nouveau jour. Le ciel est synchronisé sur les quartiers (y compris variantes `_Dev`) et le carrefour. Aucune carte ni cinématique n'a été retouchée ; les effets Ground sont visuels, pas une simulation climatique, et ne changent pas les donjons.

Les tests avec doublures vérifient les bornes des tirages, les anciennes sauvegardes simulées, les changements de carte, la sieste, le carrefour, les intérieurs exclus et les dialogues existants. Ils sont appelés par le contrôle existant de la CI Windows. Ils ne remplacent pas un test dans le moteur réel. L'audit graphique des captures 26–45 reste ouvert.
