> **V1 REJETÉE : retirée de l’aperçu à la demande de l’utilisateur. À refaire image par image dans le style PMD.**

# Hurlement des Roches-Lames — V1 expérimentale

Vidéo sonore : `Lougaroc-Hurlement-Roches-Lames-V1-IA-60ips-son.mp4` ; journal : `journal-v1-8-directions-champs.txt`.

Lougaroc déclenche un effet de hurlement, puis des lames de pierre apparaissent autour de la cible et convergent vers elle. Les lames proviennent d'une image générée, détourée et animée ; les éclats, l'effet et le son de Lame de Roc utilisent les ressources Roche natives de PMDO. La fiche de banc est Roche physique, puissance 190. Les six lames sont visuelles : un seul calcul de dégâts est appliqué.

## Banc en copie isolée

Huit orientations : 8/8 cibles Lokhlass touchées (270 → 221–225 PV), 8/8 témoins latéraux indemnes, une charge consommée par lancement. Test additionnel distinct : les champs Électrifié, Herbu, Brumeux et Psychique ont chacun été posés puis retirés après l'attaque (4/4). Le script ne vise que ces quatre identifiants de champ ; les effets sur d'autres statuts de terrain et sur la météo n'ont pas été vérifiés. Les originaux de la copie isolée ont été restaurés et comparés ; les ressources temporaires ont été retirées.

La vidéo dure 50 s et contient 3 000 images à 60 i/s avec son (moyenne −21,3 dB). Elle comprend les essais de direction et de retrait des champs ; certaines images peuvent être répétées selon le rendu du moteur. Le journal de combat peut masquer une partie des pierres sur les cibles du bas.

## Limites

L'action reprend le ciblage fixe de Lame de Roc à **deux cases** : les autres distances, l'absence de cible, les murs, alliés, bords de carte et interruptions n'ont pas été testés. Le retrait des champs est exécuté après l'action dans cette fiche de banc ; son comportement en cas d'échec ou de protection n'est pas vérifié. La disposition et l'envol des lames sont une adaptation 2D, pas la cinématique 3D complète. Seule la forme Diurne a été testée. Les restrictions Lougaroc / Lame de Roc / Lougarozélite, le cristal et le menu Z ne sont pas intégrés. Prototype scripté en copie isolée, pas une publication en jeu ni un push.

Sources reproductibles : `~/Capacites-Z/Sources/preparer-roches-lames.py`, `roches-lames-effets.lua`, `test-roches-lames.lua`, `intro-halo-banc-lougaroc.lua`, `banc-roches-lames.py`.

Références : https://www.pokepedia.fr/Hurlement_des_Roches-Lames/G%C3%A9n%C3%A9ration_7 ; https://www.pokebip.com/page/jeuxvideo/pokemon_ultra_soleil_ultra_lune/nouvelles_attaques.
