# Zones et portées des capacités : relevé PMDO

Ce document distingue les exemples **natifs PMDO** des adaptations **expérimentales** des capacités Z. Le CSV `Audit-zones-attaques-PMDO.csv` est un audit statique des fiches de la copie Destiny/PMDO : le type de hitbox et ses paramètres ne suffisent pas à certifier un résultat en jeu. Les 35 fiches Z d'origine sont inactives, pas des références de comportement final.

## Références vérifiées dans les données et le moteur

- **Hydrocanon (`hydro_pump`)** : `ProjectileAction`, portée 8, `StopAtHit=false`, `StopAtWall=true`. C'est une **ligne qui peut traverser plusieurs cibles**, pas une zone circulaire ; l'effet d'eau utilise un émetteur de flux.
- **Vent Mauvais (`ominous_wind`)** et **Tempête Florale (`petal_blizzard`)** : `AreaAction`, `HitArea=Full`, portée 4. L'aire part du lanceur, et le moteur remplit les cases accessibles jusqu'à la limite ; elle n'est pas un projectile directionnel. L'overlay de Vent Mauvais/Petal Blizzard habille l'écran mais n'est pas lui-même la hitbox.
- Le moteur `Hitbox.AreaLimit` distingue `Full`, `Cone`, `Cross` et `Sides`, et `OffsetAction` peut viser une zone centrée à distance. `DashAction` réalise une charge ; `ProjectileAction` peut s'arrêter ou non sur la première cible et au mur. Les paramètres d'alignement contrôlent quels camps peuvent être atteints. Les paramètres `Range` n'ont pas forcément le même sens pour toutes ces actions.
- Pour l'`AreaAction` **Full** actuelle, le moteur délimite les cases dans un carré de rayon `Range` autour du lanceur, puis propage la hitbox sur les cases accessibles. Ainsi « rayon 2 » dans ce prototype signifie jusqu'à deux cases sur chaque axe, diagonales comprises, et pas un cercle euclidien strict. Ne pas supposer le même fonctionnement pour un autre moteur ou une autre forme.

## Nouveaux essais Z, choix provisoires

### Pétalexplosion Éblouissante — zone autour du lanceur

Fiche expérimentale dérivée de Tempête Florale : `AreaAction`, `HitArea=Full`, `Range=2`, uniquement ennemis. Cinq poses IA d'impact par cible, plus l'overlay et le son PMDO de Tempête Florale. Dans chacun des huit essais, trois Ronflex se trouvaient respectivement à deux cases devant, une derrière et une sur le côté ; un quatrième était à trois cases devant, hors du carré de rayon 2. Résultat du journal : **24 cibles dans l'aire touchées sur 24, huit contrôles hors portée intacts sur huit**, une charge de PP consommée à chaque fois. L'aire étant symétrique, le dessin d'impact est identique pour chaque orientation ; les huit orientations du lanceur ont bien été lancées.

### Super Tourbillon Abyssal — ligne traversante

Variante expérimentale dérivée de Hydrocanon : `ProjectileAction`, portée 4, ne s'arrête pas sur le premier ennemi, s'arrête théoriquement aux murs, ne cible que les ennemis ; impact IA de Tourbillon. À chaque orientation, trois ennemis alignés aux distances 1, 2 et 3 ont tous été touchés et le témoin sur le côté n'a pas subi de dégâts : **24 cibles sur 24 et huit témoins sur huit**. La configuration d'arrêt au mur a été vérifiée dans la fiche, mais le comportement face à un mur n'a pas encore été testé. La boîte de dialogue peut masquer la cible la plus basse dans la vidéo ; le journal conserve les quatre valeurs de PV.

Dans ces deux essais, placement des cibles, orientation, attribution et déclenchement de la capacité sont scriptés. Les dégâts et les charges PP sont gérés par `ProcessUseSkill`. Terrain dégagé, une espèce de lanceur et de cible ; distances ciblées seulement. Le rayon 2 et la portée 4 sont des propositions d'adaptation PMDO, non des règles Z officielles ou définitives. Le ciblage des alliés, murs, couloirs, bords de carte, autres tailles, variations de puissance et règles des cristaux restent à vérifier avant intégration jouable. Les autres Z-Moves ne sont pas encore implémentés avec leurs zones.

### Chaos Draconique — cône orienté

Variante expérimentale dérivée de `clanging_scales` (Vibrécaille) : `AreaAction`, `HitArea=Cone`, rayon 2. Pour chacune des huit orientations, deux ennemis devant à 1 et 2 cases et un ennemi sur le bord à 45 degrés sont touchés, un témoin à une case derrière reste intact : 24 cibles touchées et huit témoins indemnes. Ce sont les placements testés, pas une preuve exhaustive de toutes les cases, des murs ou des alliés.

### Vrille Maximum — charge

Variante expérimentale de `gyro_ball` : `DashAction`, portée 3, arrêt configuré à la cible et au mur. Une cible à deux cases touchée dans chacune des huit directions, avec déplacement et collision par le moteur. Les murs ne sont pas encore testés.

### Essai complémentaire : Apocalypse Gigalithique

Prototype provisoire fondé sur `rock_slide` : `OffsetAction`, `HitArea:1` (Sides), centre décalé de deux cases. Dans chacune des huit directions, trois cibles disposées au centre et sur deux cases de la zone ont subi des dégâts ; un témoin arrière est resté intact (24/24 et 8/8). En diagonale le moteur traite les côtés selon `Hitbox.IsInSquareHitbox` : le test place les ailes sur deux cases cardinales adjacentes au centre, pas sur une diagonale calculée par simple rotation. Cet échantillon ne constitue pas une cartographie exhaustive ; murs, alliés et autres cases n'ont pas été testés. Effets visuels par cible, déclenchement et placement scriptés, pas de règles Z.
