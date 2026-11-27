# Dracacophonie Flamboyante — V1, prototype à valider

Vidéo sonore : `Ekaiser-Dracacophonie-V1-PMD-60ips-son.mp4` ; journal : `journal-v1-8-directions-immunite.txt` ; planche de charge : `Dracaco-charge-72images.png`, huit colonnes de cases 96 × 96 pixels, lecture ligne par ligne à 60 images/s.

Ékaïser charge une onde avec des écailles et des cercles animés, puis diffuse l'attaque autour de lui. Les ondes de Vibrécaille et les particules d'impact de Dracochoc servent de références natives ; une charge de 72 images les complète. La capacité est sonore, Dragon, spéciale, puissance 185 dans la fiche de banc. Elle n'applique pas la baisse de Défense de Vibrécaille.

Les cinq statistiques (Attaque, Défense, Attaque Spéciale, Défense Spéciale, Vitesse) augmentent chacune d'un niveau **une seule fois par lancement**, et seulement si au moins une cible a effectivement perdu des PV. L'effet utilise les événements natifs de modification des statistiques après la vérification des dégâts.

## Essais en copie isolée

Huit orientations : trois adversaires adjacents sont touchés à chaque lancement, soit 24 touches (270 → 245–247 PV) ; Nymphali Fée reste à 235 PV, l'adversaire hors zone et l'allié adjacent restent à 270 PV ; chaque charge est consommée et les cinq bonus sont exactement à +1, pas +3. Un essai avec Nymphali comme seul adversaire adjacent et un essai sans adversaire adjacent ne déclenchent aucun bonus. Après le banc, les fichiers originaux ont été restaurés et comparés.

La vidéo est encodée à 60 i/s et contient du son ; le moteur peut répéter certaines images s'il ralentit. Les indications du journal peuvent masquer des parties basses de la scène.

## Limites

La portée adjacente est une adaptation du banc et non une intégration au jeu. Le déclencheur utilise un état Lua local remis à zéro à chaque lancement : les actions simultanées ou imbriquées et le nettoyage après interruption n'ont pas été testés. Murs, bords, protections, talents, cibles mises K.O. et effets de substitution ne sont pas couverts. Restrictions Ékaïser/Vibrécaille/Ékaïzélite, cristal et menu Z non intégrés ; aucun push. Le rendu est à valider visuellement.

Sources : `~/Capacites-Z/Sources/preparer-dracacophonie-v1.py`, `dracacophonie-v1-effets.lua`, `banc-dracacophonie-v1-reprise.py`, `test-dracacophonie-v1.lua`, `intro-halo-banc-ekaizer.lua`.
