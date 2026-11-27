# Inventaire des capacités Z — Destiny / PMDO

## Périmètre

- **18 attaques génériques** (une par type), **17 capacités signatures distinctes** : 35 capacités nommées au total. Neuf pour Un est une capacité signature de statut, pas une attaque infligeant des dégâts. Certaines signatures sont partagées par plusieurs formes ou Pokémon.
- La source liste aussi **239 variantes de capacités de statut Z**. Elles figurent toutes dans `239-capacites-statut-z.csv`, avec type, capacité de base, effet Z et cristal. Ce nombre est celui du tableau de Poképédia consulté, pas une preuve que Destiny les gère.
- Ce sont des règles des jeux principaux de génération VII : la conversion en donjon PMDO et ses conditions (une fois par combat, étage ou expédition, objets, rang, cibles, portée, bonus) restent à concevoir et à tester.

## 18 capacités génériques

| Type | Capacité Z | Cristal | ID PMDO |
| --- | --- | --- | --- |
| Acier | Vrille Maximum | Métallozélite | corkscrew_crash |
| Combat | Combo Hyper-Furie | Combazélite | all_out_pummeling |
| Dragon | Chaos Draconique | Dracozélite | devastating_drake |
| Eau | Super Tourbillon Abyssal | Aquazélite | hydro_vortex |
| Électrik | Fulguro-Lance Gigavolt | Voltazélite | gigavolt_havoc |
| Fée | Impact Choupinova | Nymphézélite | twinkle_tackle |
| Feu | Pyro-Explosion Cataclysmique | Pyrozélite | inferno_overdrive |
| Glace | Laser Cryogénique | Cryozélite | subzero_slammer |
| Insecte | Cocon Fatal | Insectozélite | savage_spin_out |
| Normal | Turbo-Charge Bulldozer | Normazélite | breakneck_blitz |
| Plante | Pétalexplosion Éblouissante | Florazélite | bloom_doom |
| Poison | Déluge Causti-Toxique | Toxizélite | acid_downpour |
| Psy | Psycho-Pulvérisation EX | Psychézélite | shattered_psyche |
| Roche | Apocalypse Gigalithique | Rocazélite | continental_crush |
| Sol | Éruption Géo-Sismique | Terrazélite | tectonic_rage |
| Spectre | Appel des Ombres Éternelles | Spectrozélite | never_ending_nightmare |
| Ténèbres | Trou Noir des Ombres | Ténébrozélite | black_hole_eclipse |
| Vol | Piqué Supersonique | Aérozélite | supersonic_skystrike |

## 17 capacités signatures

| Type | Capacité Z | Porteurs | Capacité requise | Cristal | ID PMDO |
| --- | --- | --- | --- | --- | --- |
| Électrik | Pikachute Foudroyante | Pikachu | Électacle | Pikazélite | catastropika |
| Électrik | Giga-Tonnerre | Pikachu à Casquette | Tonnerre | Pikachazélite | ten_million_volt_thunderbolt |
| Électrik | Électro-Surf Survolté | Raichu d'Alola | Tonnerre | Aloraïzélite | stoked_sparksurfer |
| Normal | Neuf pour Un | Évoli | Dernier Recours | Évolizélite | extreme_evoboost |
| Normal | Gare au Ronflex | Ronflex | Giga Impact | Ronflézélite | pulverizing_pancake |
| Psy | Supernova Originelle | Mew | Psyko | Mewzélite | genesis_supernova |
| Spectre | Fureur des Plumes Spectrales | Archéduc | Tisse Ombre | Archézélite | sinister_arrow_raid |
| Ténèbres | Dark Body Press | Félinferno | Dark Lariat | Félinozélite | malicious_moonsault |
| Eau | Symphonie des Ondines | Oratoria | Aria de l'Écume | Oratozélite | oceanic_operetta |
| Roche | Hurlement des Roches-Lames | Lougaroc | Lame de Roc | Lougarozélite | splintered_stormshards |
| Fée | Patati-Patattrape | Mimiqui | Câlinerie | Mimiquizélite | lets_snuggle_forever |
| Dragon | Dracacophonie Flamboyante | Ékaïser | Vibrécaille | Ékaïzélite | clangorous_soulblaze |
| Fée | Colère du Gardien d'Alola | Tokorico / Tokopiyon / Tokotoro / Tokopisco | Ire de la Nature | Tokozélite | guardian_of_alola |
| Acier | Hélio-Choc Dévastateur | Solgaleo / Necrozma Crinière du Couchant | Choc Météore | Solgazélite | searing_sunraze_smash |
| Spectre | Rayons Séléno-Explosifs | Lunala / Necrozma Ailes de l'Aurore | Rayon Spectral | Lunazélite | menacing_moonraze_maelstrom |
| Psy | Apocalypsis Luminis | Ultra-Necrozma | Photo-Geyser | Ultranécrozélite | light_that_burns_the_sky |
| Spectre | Fauche-Âme des Sept Étoiles | Marshadow | Clepto-Mânes | Marshadozélite | soul_stealing_7_star_strike |

## Audit local de Destiny 0.7.8 (données PMDO 0.8.12)

- Les **35 fiches JSON** existent dans `Data/Skill/` ; **0/35** sont marquées `Released: true` (les autres sont `false`). Existence d'une fiche ≠ capacité Z utilisable ou animation présente.
- Les 35 fiches examinées utilisent `AttackAction`, leurs champs `ActionFX.Sound` et `Data.HitFX.Sound` sont vides. Les dégâts ou autres événements déclarés varient : leur présence ne prouve ni un fonctionnement Z complet ni une animation correcte.
- `35-capacites-z-et-audit.csv` recense les identifiants, noms anglais, états et données de base. Seize prototypes VFX ont été testés en donjon : Turbo-Charge, Pyro-Explosion, Super Tourbillon, Fulguro-Lance, Laser Cryogénique, Pétalexplosion, Chaos Draconique, Vrille Maximum, Appel des Ombres Éternelles, Cocon Fatal, Apocalypse Gigalithique Pikachute Foudroyante Supernova Originelle Trou Noir des Ombres Combo Hyper-Furie et Éruption Géo-Sismique. Les quinze derniers comportent des éléments générés par IA ; Turbo est procédural. Tous ont été testés dans huit orientations avec cibles placées par script. Pétalexplosion a été testée en aire, Super Tourbillon en ligne traversante et Chaos Draconique en cône, chacun sur trois cibles et un témoin. Appel des Ombres expérimente une paire de mains par cible en aire, avec 0 à 3 cibles et huit orientations ; Cocon Fatal vise une case à deux cases, avec un témoin latéral ; Apocalypse Gigalithique utilise une zone décalée à trois cibles et un témoin arrière. Les règles Z et la fluidité finale restent à valider. Supernova Originelle a été testée avec Mew, trois cibles et un témoin dans chaque orientation ; son Champ Psychique reste à implémenter. La version immersive d’Appel des Ombres a été testée avec Ectoplasma. Trou Noir des Ombres V2 a été testé avec Absol dans une zone centrée de 5 × 5 cases : trois cibles et un témoin par orientation, puis destruction de murs standards et conservation d’un mur extérieur et d’un mur indestructible. Combo Hyper-Furie a été testé avec Mackogneur : impacts abstraits sans mains, une cible adjacente et un témoin par orientation. Éruption Géo-Sismique a été testée avec Carchacrok en zone autour du lanceur, trois cibles et un témoin par orientation. Dix-neuf capacités n’ont pas encore de prototype testé.

## Huit directions et production

Chaque capacité aura une fiche de suivi pour les huit orientations : bas, bas-droite, droite, haut-droite, haut, haut-gauche, gauche, bas-gauche. Pour les effets symétriques, une seule animation peut être réutilisée si son rendu est vérifié dans les huit directions ; pour les projectiles, trajectoires, attaques de contact ou cadrages asymétriques, il faut des vues adaptées. Ne pas confondre effets visuels (particules) et animation du corps du Pokémon : les signatures peuvent nécessiter des poses propres à l'espèce.

## Sources

- Poképédia : https://www.pokepedia.fr/Capacit%C3%A9_Z — tableaux génériques, signatures et statut.
- PMDO, création de capacités : https://wiki.pmdo.pmdcollab.org/Creating_Moves
- PMDO, ressources VFX directionnelles : https://wiki.pmdo.pmdcollab.org/Modding_Objects_and_VFX
- PMDO, sprites : https://wiki.pmdo.pmdcollab.org/PMD_Sprite_Format

**État : inventaire et audit statique terminés ; 16 prototypes VFX sur 35 testés dans les huit directions, pas de capacité complète jouable ; 19 capacités restent sans prototype testé.**

## Mise à jour des prototypes

22 capacités Z disposent désormais d’un prototype de banc testé dans huit orientations ; 13 restent sans prototype testé. Giga-Tonnerre utilise un Pikachu ordinaire dont les poses statiques ont reçu une casquette approximative, et non une forme officielle intégrée. Voir `../Prototypes/Giga-Tonnerre/Generation-PMDO/README.md`. Les chiffres précédents de cette page correspondent à un état antérieur. Psycho-Pulvérisation EX attend toujours une véritable distorsion, sans quadrillage. Aucune règle Z complète n’est installée.

Électro-Surf Survolté : Raichu d’Alola testé dans huit directions, avec paralysie des huit cibles normales et témoin latéral intact ; un Lainergie de type Électrik touché sans paralysie. Animation et restrictions Z encore incomplètes. Voir `../Prototypes/Electro-Surf-Survolte/Generation-PMDO/README.md`.

## Mise à jour — Neuf pour Un

23 capacités Z disposent maintenant de prototypes testés dans huit orientations ; 12 restent sans prototype testé. Neuf pour Un : Évoli, huit évolitions visuelles et cinq statistiques de PMDO à +2 ; voir `../Prototypes/Neuf-pour-Un/Generation-PMDO/README.md`. Les règles complètes, objets et menu Z ne sont toujours pas intégrés. Psycho-Pulvérisation EX attend toujours une véritable distorsion.

Neuf pour Un V2 : étoile et rayons issus de la seconde image générée, retenue par l’utilisateur ; huit sprites PMDO autour d’Évoli. Les huit orientations et cinq boosts ont été retestés. Voir `../Prototypes/Neuf-pour-Un/Generation-PMDO/README-V2.md`.


## Mise à jour — Gare au Ronflex V1

24 capacités Z ont un prototype testé en huit orientations ; 11 restent sans prototype testé. Gare au Ronflex combine les textures natives de Giga Impact, de type Normal, avec un impact généré par IA. Huit cibles touchées, huit témoins latéraux indemnes et une charge consommée dans le banc isolé. Vidéo et limites dans `../Prototypes/Gare-au-Ronflex/Generation-PMDO/ETAT.md` ; ce n’est pas une intégration complète.


## Mise à jour — Foudre V4 IA

Électro-Surf Survolté : sphère générée et animée ; 24 cibles touchées et paralysées, 16 témoins intacts, immunité à la paralysie électrique vérifiée. Giga-Tonnerre : colonne enrichie par une image générée, huit cibles touchées et huit témoins intacts. Les versions précédentes sont conservées. Voir les fichiers `README-V4-IA.md` des deux prototypes pour les limites des bancs.


## Mise à jour — Fureur des Plumes Spectrales V1

25 capacités Z ont un prototype testé dans huit orientations ; 10 restent sans prototype testé. Fureur des Plumes Spectrales combine les flèches et particules Spectre natives de Tisse Ombre avec un impact IA. Huit cibles touchées, huit témoins indemnes, une charge consommée par test. Envol et volée adaptés ; limites et vidéo dans `../Prototypes/Fureur-des-Plumes-Spectrales/Generation-PMDO/ETAT.md`.

## Mise à jour — Dark Body Press V1

26 capacités Z ont un prototype testé sur huit orientations ; 9 restent sans prototype testé. Dark Body Press : charge et impact IA, textures Ténèbres natives, ruée avec rémanence ; un mur ordinaire au contact est détruit dans un essai vers la droite, mur latéral et mur incassable conservés. Huit cibles touchées et huit témoins indemnes. Prototype de banc, non intégré ; détails dans `../Prototypes/Dark-Body-Press/Generation-PMDO/ETAT.md`.

## Mise à jour — Symphonie des Ondines V1

27 capacités Z ont un prototype testé sur huit orientations ; 8 restent sans prototype testé. Symphonie des Ondines : sphère d’eau générée, bulles et cercles natifs d’Aria de l’Écume, projectile et éclatement ; 8 cibles touchées et 8 témoins indemnes. Prototype en copie isolée, non intégré ; détails dans `../Prototypes/Symphonie-des-Ondines/Generation-PMDO/ETAT.md`.

## Mise à jour — Hurlement des Roches-Lames V1

28 capacités Z ont un prototype testé sur huit orientations ; 7 restent sans prototype testé. Hurlement des Roches-Lames : lames IA convergentes et textures de Lame de Roc ; 8 cibles touchées, 8 témoins intacts et 4 champs retirés dans des essais séparés. Prototype isolé non intégré ; détails dans `../Prototypes/Hurlement-des-Roches-Lames/Generation-PMDO/ETAT.md`.

## Mise à jour — Patati-Patattrape V1

29 capacités Z ont un prototype testé sur huit orientations ; 6 restent sans prototype testé. Patati-Patattrape : bond, pose de Mimiqui native agrandie, effets Fée natifs et nuage IA ; huit cibles touchées et huit témoins intacts. Le déguisement est une superposition visuelle, non un vrai enveloppement ; prototype non intégré. Détails dans `../Prototypes/Patati-Patattrape/Generation-PMDO/ETAT.md`.

## Correction — cinq signatures à refaire

Fureur des Plumes Spectrales, Dark Body Press, Symphonie des Ondines, Hurlement des Roches-Lames et Patati-Patattrape : les V1 ont été rejetées et retirées de la galerie. Les essais techniques historiques ci-dessus restent documentés, mais ne valent pas validation artistique. Les fichiers sont conservés hors galerie pour référence, sans constituer des livrables retenus. 24 Z ont encore une vidéo de prototype affichée ; 11 sont à créer ou à refaire (dont ces cinq). Reprise image par image adaptée à PMD, ressources natives par type, tests et vidéo sonore ; pas d’intégration ni de push à ce stade.

## Reprise PMD — Fureur des Plumes Spectrales V2

La V2 est affichée dans la galerie pour validation artistique : 40 images de préparation, 44 images d’impact, flèches Spectre natives, plume IA pixelisée. Huit cibles touchées et témoins indemnes dans le banc, copie restaurée ; limites dans `../Prototypes/Fureur-des-Plumes-Spectrales/Generation-PMDO/ETAT-V2-PMD.md`. La V2 n’est pas intégrée. Quatre autres versions rejetées restent à refaire. La galerie affiche 25 capacités avec vidéo et 10 à créer ou refaire ; ce décompte ne signifie pas une validation utilisateur.

## Reprise électrique — V5 PMDO

Giga-Tonnerre : colonne de foudre native et étincelles colorées, huit cibles touchées et huit témoins intacts. Électro-Surf : charge inspirée de Décharge et sphère utilisant les images de Boule Élek, 24 cibles paralysées et 16 témoins indemnes ; Lainergie non paralysée. Bancs isolés restaurés. Les deux vidéos V5 sont dans l'aperçu ; limites et résultats détaillés dans les fichiers `ETAT-V5.md` des prototypes. Ces essais ne constituent pas une intégration Z complète.

## Reprise PMD — Dark Body Press V2

Charge et impact image par image, ruée avec image rémanente et fumée sur les cases touchées, sans ring. Huit cibles touchées et témoins intacts ; un mur au contact détruit vers la droite, mur latéral et mur incassable préservés. Prototype de banc à valider, non intégré ; limites dans `../Prototypes/Dark-Body-Press/Generation-PMDO/ETAT-V2-PMD.md`. Symphonie des Ondines, Hurlement des Roches-Lames et Patati-Patattrape restent à refaire.

## Reprise PMD — Symphonie des Ondines V2

Bulles natives, sphère animée et jaillissement d'eau : huit cibles touchées et huit témoins intacts, copie restaurée. Prototype de banc à valider, non intégré ; limites dans `../Prototypes/Symphonie-des-Ondines/Generation-PMDO/ETAT-V2-PMD.md`. Hurlement des Roches-Lames et Patati-Patattrape restent à refaire.

## Corrections — Symphonie V3 et Dark Body Press V3

Symphonie : projectile corrigé et retesté, huit directions ; ancienne vidéo retirée de la galerie. Dark Body Press : explosion rouge et noire au coup final, d'après Destruction, sans zone de dégâts supplémentaire ; huit directions et mur au contact vers la droite testés. Les deux bancs ont été restaurés ; limites détaillées dans leurs fichiers `ETAT-V3.md`. Pas d'intégration complète ni de push.
