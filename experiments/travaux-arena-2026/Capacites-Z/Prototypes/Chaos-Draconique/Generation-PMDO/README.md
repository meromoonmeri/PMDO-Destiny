# Chaos Draconique — prototype de zone orientée

Six images d'impact générées individuellement par IA d'après une pose de `Dragon_Pulse_Charge` dans PMDO ; réduction au plus proche voisin et suppression du fond vert. Huit lignes identiques pour l'impact radial, non pour la zone de dégâts. L'onde utilise un effet natif `Dragon_Pulse_Ball` et la hitbox `AreaAction / Cone` de `clanging_scales` (Vibrécaille), portée provisoire 2. Sons PMDO `DUN_Dragon_Pulse` et `DUN_Dragon_Rush`.

Vidéo `Chaos-Draconique-8-directions.mp4`, journal `journal-zone-8-directions.txt` : dans une copie isolée, huit orientations avec quatre cibles par essai. Dans chacune : cibles à une et deux cases devant et sur le bord du cône à 45° touchées, cible derrière indemne. 24 cibles touchées sur 24 et 8 témoins arrière indemnes ; PP consommé. La cible, l'orientation et le lancement sont scriptés, mais les dégâts et l'aire sont gérés par PMDO via `ProcessUseSkill`. Les cibles sont parfois masquées par les effets ou le panneau de dialogue.

Portée, zone, catégorie spéciale, puissance 100 et 1 PP sont des valeurs de banc, non officielles. Pas de validation des murs, des alliés, des autres espèces, de la fluidité finale ni des règles Z ou du menu. Fiche et banque testées en copie seulement ; l'original est conservé. Voir `../../Chaos-Draconique-et-Vrille-Maximum-son.mp4`.
