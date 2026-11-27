# Méthodes PMDO étudiées pour les capacités Z

## Ce que les références documentent

- Les animations de Pokémon PMD sont des sprites, pas les mêmes fichiers que les effets d'attaque. `AnimData.xml` précise le nom, les dimensions, la durée de chaque pose en unités de 1/60 s et, selon le mouvement, les repères `RushFrame`, `HitFrame` et `ReturnFrame`. Les fichiers `Anim.png`, `Offsets.png` et `Shadow.png` ont les mêmes dimensions ; les poses sont en colonnes et les directions en lignes. Voir [PMD Sprite Format](https://wiki.pmdo.pmdcollab.org/PMD_Sprite_Format) et [Sprite Tool](https://wiki.pmdo.pmdcollab.org/Sprite_Tool).
- Exemple réellement consulté : [SpriteCollab / Dracaufeu / AnimData.xml](https://raw.githubusercontent.com/PMDCollab/SpriteCollab/master/sprite/0006/AnimData.xml). Walk : 40×48, 4 poses de durées 8,10,8,10 ; Attack : 80×88, 14 poses de durées 2,2,2,2,4,1,1,2,2,2,2,2,2,2, repères rush 2 / hit 5 / return 8 ; Shoot : 56×56, 11 poses, hit 2 / return 6. Ces valeurs sont propres au sprite examiné, pas une règle universelle pour tous les Pokémon.
- Pour les effets, [Modding Objects and VFX](https://wiki.pmdo.pmdcollab.org/Modding_Objects_and_VFX) décrit les fichiers d'import `[Nom].Dir8.png` : huit directions empilées, poses en colonnes, cellules carrées. `Dir5` peut utiliser une symétrie, `None` peut convenir à un effet véritablement radial. Les effets sont importés comme banques `.dir`, indépendamment des sprites des Pokémon.
- L'[éditeur de capacités PMDO](https://wiki.pmdo.pmdcollab.org/Creating_Moves) associe mouvement (`HitboxAction`), animation du personnage (`CharAnim`), projectiles et leur vitesse, portées, collisions, VFX d'action, VFX de contact, sons et dégâts. `FrameTime` règle la durée de chaque image d'un effet donné, tandis que les durées du sprite personnage sont dans `AnimData.xml`.
- Comparaison locale : Giga Impact utilise `DashAction`, arrêt au mur et à la cible ; Ball'Ombre utilise `ProjectileAction` ; Hydro-Queue/attaques eau varient selon leur portée. Ces capacités servent d'exemples techniques, pas de preuve de fidélité aux Z-Moves des jeux officiels.

## Appliqué aux tests en cours

- Réutilisation des animations et repères des Pokémon réellement fournis par le moteur plutôt que d'inventer un sprite unique pour tous les Pokémon.
- Turbo-Charge V3 : charge et impact en calques avant/arrière, puis déplacement et collision par `DashAction`.
- Pyro V2 : projectile `Dir8` de 8 poses, impact de 16 poses. Tourbillon V2 : 16 poses au contact en couches avant/arrière ; son projectile bleu est un effet PMDO existant. Chaque image des nouveaux effets a été dessinée par programme, et non générée indépendamment par un modèle d'image ; les résultats restent à retoucher manuellement si nécessaire.
- Les trois prototypes ont été appelés par `ProcessUseSkill` contre un ennemi replacé et restauré pour chaque direction. Le moteur calcule les dégâts et consomme les PP. Le test est assisté par script et ne prouve pas l'accès en partie normale.
- Les catégories et la puissance de base sont des valeurs temporaires de test ; les Z-Cristaux, l'adaptation de puissance et catégorie selon la capacité d'origine, l'accès depuis le menu et les limites d'utilisation restent à construire et vérifier. 32 des 35 animations n'ont pas encore été produites. Les 239 variantes de statut ne sont pas 239 signatures supplémentaires.
