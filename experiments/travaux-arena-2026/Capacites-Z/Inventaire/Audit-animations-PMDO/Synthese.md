# Audit des animations des capacités de base PMDO

Source : fiches de la copie isolée PMDO-Destiny, état restauré, 883 fiches JSON. Empreinte SHA-256 de l'archive source : `60e065050f205bbb9cbe4c0089cac98eda347a3333183b5914594bc9342b0a09`.

Périmètre principal : 642 capacités publiées (`Released=true`), hors 35 capacités Z et hors action interne `attack`. Les 205 autres fiches hors Z et action interne ne sont pas publiées et figurent à part dans le tableau.

## Résultats de l’audit statique

- 591 capacités ont au moins une référence directe à une ressource d'effet graphique dans leur fiche.
- 2 autres ont une rémanence procédurale explicite sans référence directe à un fichier d'effet : Acrobatie, Vive-Attaque.
- 49 n'ont ni référence directe à une ressource d'effet ni rémanence procédurale détectée ; ce sont des **candidates à vérifier**, pas des absences d’animation prouvées.
- 0 ont un script explicite ou une ressource attendue introuvable et demandent une vérification complémentaire.

Ces catégories portent sur les effets, pas sur la pose du Pokémon. Les fiches peuvent également déclencher des animations indirectes par les statuts ou le code natif. Les ressources sont vérifiées selon leur type attendu (particule, fond, rayon), mais leur rendu et leur qualité n’ont pas été testés dans le jeu. Une ressource partagée ou une simple image compte comme référence, sans présumer d’une animation unique ou fidèle.

## Candidates sans effet graphique directement référencé

- Allègement (`autotomize`)
- Ampleur (`magnitude`)
- Après Vous (`after_you`)
- Blabla Dodo (`sleep_talk`)
- Bélier (`take_down`)
- Camouflage (`camouflage`)
- Charge (`tackle`)
- Chatouille (`tickle`)
- Chgt Vitesse (`shift_gear`)
- Chute Libre (`sky_drop`)
- Copie (`mimic`)
- Copie Type (`reflect_type`)
- Corps Perdu (`vital_throw`)
- Cotogarde (`cotton_guard`)
- Coup d'Boule (`headbutt`)
- Crève-Cœur (`heart_stamp`)
- Danse-Folle (`teeter_dance`)
- Draco-Queue (`dragon_tail`)
- Encornebois (`horn_leech`)
- Force Cachée (`secret_power`)
- Frappe Atlas (`seismic_toss`)
- Frappe Psy (`psystrike`)
- Hurle-Temps (`roar_of_time`)
- Hâte (`agility`)
- Interversion (`ally_switch`)
- Lumi-Éclat (`luster_purge`)
- Lutte (`struggle`)
- Maléfice Sylvain (`forests_curse`)
- Mimi-Queue (`tail_whip`)
- Picpic (`peck`)
- Plaquage (`body_slam`)
- Plumo-Queue (`tail_slap`)
- Projection (`circle_throw`)
- Puissance (`focus_energy`)
- Ravage Rampant (`skitter_smack`)
- Rebond (`bounce`)
- Reflet (`double_team`)
- Rengorgement (`work_up`)
- Repos (`rest`)
- Retenue (`hold_back`)
- Shelter (`shelter`)
- Souplesse (`slam`)
- Spatio-Rift (`spacial_rend`)
- Tout ou Rien (`final_gambit`)
- Trempette (`splash`)
- Yama Arashi (`storm_throw`)
- Ère Glaciaire (`glaciate`)
- Écras'Face (`pound`)
- Évo-Dynamo (`buzzy_buzz`)

## Fichiers

- `audit-complet.xlsx` : résultats, candidates, effets référencés et fiches non publiées.
- `audit-complet.csv` : une ligne par capacité hors Z et action interne.
- `fiches-source-PMDO.zip` : instantané des fiches utilisées.
- `Capacites-Z/Sources/audit-animations-capacites.py` : méthode reproductible.
