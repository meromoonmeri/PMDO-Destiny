# Turbo-Charge Bulldozer — prototype expérimental

Prototype VFX de charge, vitesse et impact : 24 poses, huit rangées Dir8. Le PNG et le `.dir` ne contiennent pas le Pokémon : le moteur affiche son propre sprite.

`essai-8-directions-sans-son.mp4` est une vraie capture d'un banc PMDO 0.8.12, avec la banque chargée en donjon autour de Dracaufeu. Les huit directions ont été déclenchées par un script de test, pas par une capacité sélectionnée dans le menu ; le journal enregistre leur ordre. L'orientation des traits a été vérifiée sur `capture-8-directions-en-jeu.png`. Aucun test de collision, dégâts, cible, déplacement ni cristal Z n'a été réalisé. Aucun son n'a été capturé.

Ce n'est pas une copie certifiée de l'animation officielle, ni une capacité complète jouable ou un résultat artistique final. Les autres capacités Z ne sont pas créées.

## Version issue du générateur d'image

- `Source-generation-turbo.png` : dessin original généré, conservé inchangé.
- `Motif-turbo-detoure.png` : détourage et palette adaptée ; `animer_turbo_genere.py` crée 32 poses, huit orientations et deux calques (derrière/devant le Pokémon).
- `Turbo-genere-test-ingame.mp4` : capture réelle dans le donjon `ambush_forest` sur banc PMDO 0.8.12, les huit orientations du VFX déclenchées successivement par script. Le son `DUN_Giga_Impact` est émis et capturé depuis le moteur ; il sert d'essai sonore, ce n'est pas le son officiel garanti de l'attaque Z.
- Les deux banques `.dir` ont été lues par le moteur ; `journal-test-generation.txt` consigne les huit orientations ; `controle-genere-8-directions-en-jeu.png` montre des images extraites de la capture.
- **Limites :** le personnage reste immobile ; aucune cible, poussée, collision, mécanique Z, dégâts, cristal ou attaque déclenchable en jeu normal n'a été implémenté. Les 8 vues sont obtenues par rotation pixelisée du motif principal : elles n'ont pas été dessinées individuellement en perspective. C'est un prototype à valider artistiquement et à compléter, pas une animation de capacité finale certifiée conforme à l'originale.

## Combat de démonstration contre Ronflex

`Turbo-Charge-contre-Ronflex-son.mp4` est une capture du moteur PMDO 0.8.12 en donjon, avec son du jeu capturé en direct. Dans ce banc de test jetable, un Ronflex ennemi est créé et placé sur une trajectoire libre ; Dracaufeu avance d'une case, les VFX directionnels s'affichent, puis l'ennemi reçoit une réaction de coup et perd réellement des PV via `InflictDamage` : 155 → 82. L'audio utilise les sons du jeu `DUN_Giga_Impact` et `DUN_Hit_Neutral` ; ils sont des choix d'essai, pas la piste officielle certifiée.

**Limites :** il s'agit d'une scène déclenchée en console, pas d'une capacité Z sélectionnable depuis le menu. La cible, l'avancée, le choc et les 73 dégâts sont scriptés pour le test ; ni formule, ni collision automatique, ni cristal, ni contrainte d'utilisation Z n'ont été intégrés. Un seul sens de combat a été filmé ; seuls les VFX avaient été essayés dans les huit directions, pas huit combats.
