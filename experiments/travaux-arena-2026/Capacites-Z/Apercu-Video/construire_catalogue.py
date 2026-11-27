#!/usr/bin/env python3
from pathlib import Path
import subprocess,json,csv,re
H=Path('/home/user');P=H/'Capacites-Z/Prototypes';A=H/'Capacites-Z/Apercu-Video';(A/'vignettes').mkdir(parents=True,exist_ok=True)
# Vidéos retenues : essais les plus récents, sans doublons ni captures brutes.
items=[
('armor_cannon_base_v2_corrige','Canon Blindé — V2 corrigée à valider','Feu','Carmadura',H/'Capacites-de-base/Canon-Blinde/V2-corrige/Carmadura-Canon-Blinde-V2-corrige-60ips-son.mp4',12.0,'Convergence • rayon sans rectangle • Destruction de feu','Capacité de base'),
('armor_cannon_base_v1','Canon Blindé — V1 à valider','Feu','Carmadura',H/'Capacites-de-base/Canon-Blinde/Carmadura-Canon-Blinde-V1-60ips-son.mp4',14.0,'Rayon de flammes • brûlures expérimentales • impact visuel','Capacité de base'),
('bitter_blade_base_v6_calibree','Lame en Peine — V6 charge calibrée','Feu','Malvalame',H/'Capacites-de-base/Lame-en-peine/V6-charge-calibree/Malvalame-Lame-en-Peine-V6-charge-calibree-60ips-son.mp4',1.6,'Flammes recentrées • énergie sur les lames • V6 conservée','Capacité de base'),
('bitter_blade_base_v6','Lame en Peine — V6 coup d’âme à valider','Feu','Malvalame',H/'Capacites-de-base/Lame-en-peine/V6/Malvalame-Lame-en-Peine-V6-60ips-son.mp4',5.2,'Rémanences et slashs individuels • dernier coup spectral • absorption','Capacité de base'),
('bitter_blade_base_v5','Lame en Peine — V5 cage et fracture','Feu','Malvalame',H/'Capacites-de-base/Lame-en-peine/V5/Malvalame-Lame-en-Peine-V5-60ips-son.mp4',7.1,'Volume orienté • pulsation • fracture brutale • sans distorsion','Capacité de base'),
('bitter_blade_base_v4','Lame en Peine — V4 transition continue à valider','Feu','Malvalame',H/'Capacites-de-base/Lame-en-peine/V4/Malvalame-Lame-en-Peine-V4-60ips-son.mp4',5.5,'Coupes en perspective • facettes réfractées • enchaînement continu','Capacité de base'),
('bitter_blade_base_v3','Lame en Peine — V3 à valider','Feu','Malvalame',H/'Capacites-de-base/Lame-en-peine/V3/Malvalame-Lame-en-Peine-V3-60ips-son.mp4',6.0,'Neuf entailles en perspective • verre, pli spatial et feux follets','Capacité de base'),
('bitter_blade_base_v2','Lame en Peine — V2 à valider','Feu','Malvalame',H/'Capacites-de-base/Lame-en-peine/V2/Malvalame-Lame-en-Peine-V2-60ips-son.mp4',2.5,'Rémanences de Malvalame • quadrillage de lacérations • soin testé','Capacité de base'),
('bitter_blade_base_v1','Lame en Peine — V1 à valider','Feu','Malvalame',H/'Capacites-de-base/Lame-en-peine/Malvalame-Lame-en-Peine-V1-60ips-son.mp4',2.0,'Entailles en perspective • feux follets sombres • absorption testée','Capacité de base'),
('spacial_rend_base_v1','Spatio-Rift — V1 à valider','Dragon','Palkia',H/'Capacites-de-base/Spatio-Rift/Palkia-Spatio-Rift-V1-banc-60ips-son.mp4',8.0,'Capacité de base • faille animée • huit orientations • immunité Fée','Capacité de base'),
('shattered_psyche_pli_banc','Psycho-Pulvérisation EX — pli spatial en banc','Psy','Gardevoir',P/'Psycho-Pulverisation-EX/Generation-PMDO/Gardevoir-Psycho-Pli-Spatial-banc-60ips-son.mp4',8.0,'Vraie déformation du rendu en forêt • banc isolé • performances à vérifier','Générique'),
('shattered_psyche_pli_etude','Psycho-Pulvérisation EX — étude de pli transparent','Psy','Gardevoir',P/'Psycho-Pulverisation-EX/Generation-PMDO/Psycho-pli-spatial-etude-hors-jeu-60ips-son.mp4',1.2,'Étude hors jeu sur image fixe • pixels du décor déformés • non intégrée','Étude visuelle'),
('menacing_moonraze_maelstrom_v2','Rayons Séléno-Explosifs — V2 fin animée','Spectre','Lunala',P/'Rayons-Seleno-Explosifs/Generation-PMDO/V2-impacts/Lunala-Rayons-Seleno-V2-60ips-son.mp4',5.0,'Rayons convergents • croissant animé • brèche V1 conservée','Signature'),
('light_that_burns_the_sky_v2','Apocalypsis Luminis — V2 fin animée','Psy','Ultra-Necrozma',P/'Apocalypsis-Luminis/Generation-PMDO/V2-impacts/Ultra-Necrozma-Apocalypsis-V2-60ips-son.mp4',3.5,'Pilier lumineux dessiné image par image • éclats prismatiques','Signature'),
('searing_sunraze_smash_v2','Hélio-Choc Dévastateur — V2 fin animée','Acier','Solgaleo',P/'Helio-Choc-Devastateur/Generation-PMDO/V2-impacts/Solgaleo-Helio-Choc-V2-60ips-son.mp4',4.3,'Impact solaire animé • brèche V1 conservée','Signature'),
('guardian_of_alola_v2','Colère du Gardien d’Alola — V2 fin animée','Fée','Tokorico',P/'Colere-du-Gardien-d-Alola/Generation-PMDO/V2-impacts/Tokorico-Colere-V2-60ips-son.mp4',4.0,'Lances conservées • explosion PMD animée','Signature'),
('menacing_moonraze_maelstrom','Rayons Séléno-Explosifs — V1 à valider','Spectre','Lunala',P/'Rayons-Seleno-Explosifs/Generation-PMDO/Lunala-Rayons-Seleno-V1-60ips-son.mp4',4.2,'Brèche visuelle • rayons convergents • immunité Normal','Signature'),
('light_that_burns_the_sky','Apocalypsis Luminis — V1 à valider','Psy','Ultra-Necrozma',P/'Apocalypsis-Luminis/Generation-PMDO/Ultra-Necrozma-Apocalypsis-V1-60ips-son.mp4',4.0,'Pilier prismatique • catégories expérimentales • immunité Ténèbres','Signature'),
('soul_stealing_7_star_strike','Fauche-Âme des Sept Étoiles — V1 à valider','Spectre','Marshadow',P/'Fauche-Ame-des-Sept-Etoiles/Generation-PMDO/Marshadow-Fauche-Ame-V1-60ips-son.mp4',4.5,'Ruée • sept éclats visuels • un seul impact de dégâts','Signature'),
('searing_sunraze_smash','Hélio-Choc Dévastateur — V1 à valider','Acier','Solgaleo',P/'Helio-Choc-Devastateur/Generation-PMDO/Solgaleo-Helio-Choc-V1-60ips-son.mp4',4.4,'Charge solaire • ruée • brèche et impact • Garde Mystik testée','Signature'),
('guardian_of_alola','Colère du Gardien d’Alola — V1 à valider','Fée','Tokorico',P/'Colere-du-Gardien-d-Alola/Generation-PMDO/Tokorico-Colere-V1-lances-explosion-60ips-son.mp4',3.0,'Lances autour du lanceur • explosion lumineuse • 75 % des PV actuels','Signature'),
('guardian_of_alola_etude','Colère du Gardien d’Alola — étude visuelle','Fée','Tokorico',P/'Colere-du-Gardien-d-Alola/Generation-PMDO/Tokorico-Colere-etude-visuelle-lances-explosion.mp4',1.0,'Maquette hors jeu • lances de lumière • explosion • dégâts non testés','Étude visuelle'),
('clangorous_soulblaze','Dracacophonie Flamboyante — V1 à valider','Dragon','Ékaïser',P/'Dracacophonie-Flamboyante/Generation-PMDO/Ekaiser-Dracacophonie-V1-PMD-60ips-son.mp4',4.0,'Ondes Dragon • multicible • cinq bonus conditionnels','Signature'),
('lets_snuggle_forever','Patati-Patattrape — V5 sac fermé à valider','Fée','Mimiqui',P/'Patati-Patattrape/Generation-PMDO/V5/Mimiqui-Patati-V5-sac-ferme-60ips-son.mp4',4.0,'Yeux spiralés et étoiles • bond • sac fermé • cible masquée','Signature'),
('splintered_stormshards','Hurlement des Roches-Lames — V3 à valider','Roche','Lougaroc',P/'Hurlement-des-Roches-Lames/Generation-PMDO/V3/Lougaroc-Hurlement-V3-onde-fissures-pics-60ips-son.mp4',3.5,'Onde sonore • fissures • pics sortant du sol • huit directions','Signature'),
('splintered_stormshards_v2','Hurlement des Roches-Lames — V2','Roche','Lougaroc',P/'Hurlement-des-Roches-Lames/Generation-PMDO/Lougaroc-Hurlement-Roches-Lames-V2-PMDO-60ips-son.mp4',6,'Version précédente • éclats de roche','Archive'),
('oceanic_operetta','Symphonie des Ondines — V3 corrigée','Eau','Oratoria',P/'Symphonie-des-Ondines/Generation-PMDO/Oratoria-Symphonie-Ondines-V3-corrigee-60ips-son.mp4',6,'Projectile corrigé • sphère animée • huit directions','Signature'),
('malicious_moonsault','Dark Body Press — V3 explosion','Ténèbres','Félinferno',P/'Dark-Body-Press/Generation-PMDO/Felinferno-Dark-Body-Press-V3-explosion-60ips-son.mp4',5,'Ruée rémanente • explosion rouge et noire • mur au contact testé • sans ring','Signature'),
('sinister_arrow_raid','Fureur des Plumes Spectrales — V2 PMD à valider','Spectre','Archéduc',P/'Fureur-des-Plumes-Spectrales/Generation-PMDO/Archeduc-Fureur-Plumes-V2-PMD-60ips-son.mp4',5,'Séquences 40 et 44 images • flèches Spectre natives • essai à valider','Signature'),
('pulverizing_pancake','Gare au Ronflex — V1','Normal','Ronflex',P/'Gare-au-Ronflex/Generation-PMDO/Ronflex-Gare-au-Ronflex-V1-test-son.mp4',3.5,'Giga Impact natif + impact IA • huit directions • banc expérimental','Signature'),
('extreme_evoboost_v1','Neuf pour Un — premier essai','Normal','Évoli',P/'Neuf-pour-Un/Generation-PMDO/Evoli-Neuf-pour-Un-huit-evolitions-60ips-son.mp4',3,'Ancien essai sans étoile IA retenue','Archive'),
('stoked_sparksurfer_v2','Électro-Surf Survolté — V2','Électrik','Raichu d’Alola',P/'Electro-Surf-Survolte/Generation-PMDO/Raichu-Electro-Surf-V2-sphere-son.mp4',10,'Version précédente • capture saccadée','Archive'),
('stoked_sparksurfer_v1','Électro-Surf Survolté — premier essai','Électrik','Raichu d’Alola',P/'Electro-Surf-Survolte/Generation-PMDO/Raichu-Alola-Electro-Surf-Survolte-8-directions-son.mp4',4,'Ancien essai sans sphère • capture saccadée','Archive'),
('ten_million_volt_thunderbolt_v2','Giga-Tonnerre — V2','Électrik','Pikachu',P/'Giga-Tonnerre/Generation-PMDO/Pikachu-Giga-Tonnerre-V2-colonne-ciel-son.mp4',9,'Version précédente • capture saccadée','Archive'),
('ten_million_volt_thunderbolt_v1','Giga-Tonnerre — premier essai','Électrik','Pikachu',P/'Giga-Tonnerre/Generation-PMDO/Pikachu-Giga-Tonnerre-8-directions-son.mp4',3,'Ancien éclair • capture saccadée','Archive'),
('shattered_psyche_v2_rejete','Psycho-Pulvérisation EX — V2 rejetée','Psy','Gardevoir',P/'Psycho-Pulverisation-EX/Generation-PMDO/Gardevoir-Psycho-Pulverisation-EX-V2-distorsion-son.mp4',3,'Archive rejetée : quadrillage, pas une vraie distorsion','Archive'),
('mega_charizard_v1','Méga-Dracaufeu X — premier essai','Méga-évolution','Dracaufeu',H/'Mega-Evolution-in-game/Video-test/Mega-Dracaufeu-X-essai-donjon.mp4',3,'Premier banc Méga, conservé pour comparaison','Autre projet'),
('extreme_evoboost','Neuf pour Un — V2 IA','Normal','Évoli',P/'Neuf-pour-Un/Generation-PMDO/Evoli-Neuf-pour-Un-V2-IA-60ips-son.mp4',3.0,'Huit évolutions et étoile IA retenue • cinq boosts','Signature'),
('stoked_sparksurfer','Électro-Surf Survolté — V5 PMDO','Électrik','Raichu d’Alola',P/'Electro-Surf-Survolte/Generation-PMDO/Raichu-Electro-Surf-V5-PMDO-60ips-son.mp4',7,'Décharge et Boule Élek natives • sphère et charge animées • huit directions','Signature'),
('stoked_sparksurfer_v3','Électro-Surf Survolté — V3','Électrik','Raichu d’Alola',P/'Electro-Surf-Survolte/Generation-PMDO/Raichu-Electro-Surf-V3-60ips-son.mp4',10,'Version précédente • sphère dessinée','Archive'),
('ten_million_volt_thunderbolt','Giga-Tonnerre — V5 PMDO','Électrik','Pikachu à casquette approximative',P/'Giga-Tonnerre/Generation-PMDO/Pikachu-Giga-Tonnerre-V5-PMDO-60ips-son.mp4',10,'Colonne native depuis le ciel • étincelles colorées • huit directions','Signature'),
('ten_million_volt_thunderbolt_v3','Giga-Tonnerre — V3','Électrik','Pikachu à casquette approximative',P/'Giga-Tonnerre/Generation-PMDO/Pikachu-Giga-Tonnerre-V3-60ips-son.mp4',9,'Version précédente • colonne dessinée','Archive'),
('supersonic_skystrike','Piqué Supersonique — V2','Vol','Roucarnage',P/'Pique-Supersonique/Generation-PMDO/Roucarnage-Pique-Supersonique-V2-plumes-remanence-son.mp4',2.0,'Décollage avec plumes et rémanence • piqué aérien','Générique'),
('supersonic_skystrike_v1','Piqué Supersonique — premier essai','Vol','Roucarnage',P/'Pique-Supersonique/Generation-PMDO/Roucarnage-Pique-Supersonique-8-directions-son.mp4',2.0,'Ancienne version sans plumes ni rémanence','Archive'),
('shattered_psyche','Psycho-Pulvérisation EX — distorsion à refaire','Psy','Gardevoir',P/'Psycho-Pulverisation-EX/Generation-PMDO/Gardevoir-Psycho-Pulverisation-EX-8-directions-son.mp4',3.0,'Premier essai sans distorsion • réfraction demandée non réalisée','Générique'),
('acid_downpour','Déluge Causti-Toxique','Poison','Nidoking',P/'Deluge-Causti-Toxique/Generation-PMDO/Nidoking-Deluge-Causti-Toxique-8-directions-son.mp4',3,'Pluie violette • gouttes et nappe toxique sur les cibles','Générique'),
('twinkle_tackle','Impact Choupinova — V2','Fée','Nymphali',P/'Impact-Choupinova/Generation-PMDO/Nymphali-Impact-Choupinova-V2-vent-feerique-son.mp4',3.0,'Vent féerique global • cœurs étoilés centrés','Générique'),
('twinkle_tackle_v1','Impact Choupinova — premier essai','Fée','Nymphali',P/'Impact-Choupinova/Generation-PMDO/Nymphali-Impact-Choupinova-8-directions-son.mp4',3.0,'Ancienne version • cadrage à revoir','Archive'),
('tectonic_rage','Éruption Géo-Sismique — V2','Sol','Carchacrok',P/'Eruption-Geo-Sismique/Generation-PMDO/Carchacrok-Eruption-Geo-Sismique-V2-eau-8-directions-son.mp4',4,'Roches et fissures par impact • refus depuis l’eau testé','Générique'),
('tectonic_rage_v1','Éruption Géo-Sismique — premier essai','Sol','Carchacrok',P/'Eruption-Geo-Sismique/Generation-PMDO/Carchacrok-Eruption-Geo-Sismique-8-directions-son.mp4',2.3,'Ancienne version • sans restriction eau','Archive'),
('all_out_pummeling','Combo Hyper-Furie','Combat','Mackogneur',P/'Combo-Hyper-Furie/Generation-PMDO/Mackogneur-Combo-Hyper-Furie-V2-8-directions-son.mp4',2.2,'Rafale d’impacts abstraits • sans mains humaines','Générique'),
('black_hole_eclipse','Trou Noir des Ombres','Ténèbres','Absol',P/'Trou-Noir-des-Ombres/Generation-PMDO/Absol-Trou-Noir-V2-5x5-murs-son.mp4',3,'V2 • vortex 5 × 5 centré et murs cassables','Générique'),
('black_hole_eclipse_v1','Trou Noir des Ombres — premier essai','Ténèbres','Absol',P/'Trou-Noir-des-Ombres/Generation-PMDO/Absol-Trou-Noir-des-Ombres-8-directions-son.mp4',2.2,'Ancienne version sur cible unique','Archive'),
('genesis_supernova','Supernova Originelle','Psy','Mew',P/'Supernova-Originelle/Generation-PMDO/Mew-Supernova-Originelle-8-directions-son.mp4',3,'Ciel cosmique et orbites par cible • prototype','Signature'),
('catastropika','Pikachute Foudroyante','Électrik','Pikachu',P/'Pikachute-Foudroyante/Generation-PMDO/Pikachu-Pikachute-8-directions-son.mp4',3.2,'Signature de Pikachu • charge inspirée d’Électacle','Signature'),
('continental_crush','Apocalypse Gigalithique','Roche','Dracaufeu',P/'Apocalypse-Gigalithique/Generation-PMDO/Apocalypse-Gigalithique-test-8-directions.mp4',3,'Roche tombante • trois cibles testées','Générique'),
('savage_spin_out','Cocon Fatal','Insecte','Dracaufeu',P/'Cocon-Fatal/Generation-PMDO/Cocon-Fatal-test-8-directions-son.mp4',2,'Fils, cocon et déchirure','Générique'),
('never_ending_nightmare','Appel des Ombres Éternelles — immersif','Spectre','Ectoplasma',P/'Appel-des-Ombres-Eternelles/Generation-PMDO/Ectoplasma-Appel-des-Ombres-immersif-8-directions.mp4',3,'Brume spectrale custom et mains par cible','Générique'),
('ombres_ancienne','Appel des Ombres Éternelles — premier essai','Spectre','Dracaufeu',P/'Appel-des-Ombres-Eternelles/Generation-PMDO/Appel-des-Ombres-test-multicible-8-directions.mp4',3,'Version précédente • mains par cible','Archive'),
('compilation_chaos','Chaos Draconique et Vrille Maximum','Dragon / Acier','Dracaufeu',P/'Chaos-Draconique-et-Vrille-Maximum-son.mp4',3,'Compilation des deux essais en donjon','Archive'),
('compilation_zones','Pétalexplosion et Super Tourbillon','Plante / Eau','Dracaufeu',P/'Petalexplosion-et-Tourbillon-zones-multiples.mp4',3,'Compilation des deux essais multicibles','Archive'),
('compilation_fulguro','Fulguro-Lance et Laser Cryogénique','Électrik / Glace','Dracaufeu',P/'Fulguro-et-Cryo-8-directions-son-PMDO.mp4',3,'Compilation des deux essais en donjon','Archive'),
('corkscrew_crash','Vrille Maximum','Acier','Dracaufeu',P/'Vrille-Maximum/Generation-PMDO/Vrille-Maximum-8-directions.mp4',3,'Charge et collision • prototype','Générique'),
('devastating_drake','Chaos Draconique','Dragon','Dracaufeu',P/'Chaos-Draconique/Generation-PMDO/Chaos-Draconique-8-directions.mp4',3,'Zone conique • trois cibles testées','Générique'),
('bloom_doom','Pétalexplosion Éblouissante','Plante','Dracaufeu',P/'Petalexplosion-Eblouissante/Generation-PMDO/Petalexplosion-zone-8-directions.mp4',3,'Zone autour du lanceur • essai multicible','Générique'),
('hydro_vortex','Super Tourbillon Abyssal','Eau','Dracaufeu',P/'Super-Tourbillon-Abyssal/Generation-PMDO/Tourbillon-ligne-8-directions.mp4',3,'Ligne traversante • trois cibles testées','Générique'),
('subzero_slammer','Laser Cryogénique','Glace','Dracaufeu',P/'Laser-Cryogenique/Generation-PMDO/Cryo-8-directions-son-PMDO.mp4',3,'Impact glace • huit orientations','Générique'),
('gigavolt_havoc','Fulguro-Lance Gigavolt','Électrik','Dracaufeu',P/'Fulguro-Lance-Gigavolt/Generation-PMDO/Fulguro-8-directions-son-PMDO.mp4',3,'Impact électrique • huit orientations','Générique'),
('inferno_overdrive','Pyro-Explosion Cataclysmique','Feu','Dracaufeu',P/'Pyro-Tourbillon-IA-8-directions-son-PMDO.mp4',4,'Compilation Pyro + Tourbillon • Pyro en premier','Générique'),
('breakneck_blitz','Turbo-Charge Bulldozer','Normal','Dracaufeu',P/'Turbo-Charge-Bulldozer/V3-native/Turbo-v3-8-directions-capacite-native.mp4',4,'Charge native • huit orientations','Générique'),
('mega_charizard','Méga-Dracaufeu X en donjon','Méga-évolution','Dracaufeu',H/'Mega-Evolution-in-game/Video-test/Mega-Dracaufeu-X-donjon-victoire.mp4',3,'Banc Méga • Éclipse X + Prisme fendu','Autre projet'),
]
records=[]
for key,title,kind,pokemon,path,at,desc,family in items:
 if not path.is_file(): raise FileNotFoundError(path)
 duration=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(path)]))
 image=A/'vignettes'/f'{key}.jpg'
 subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-ss',str(at),'-i',str(path),'-frames:v','1','-vf','scale=640:-2','-q:v','3',str(image)],check=True)
 title=re.sub(r"\s+IA\b", "", title);desc=re.sub(r"\s+IA\b", "", desc)
 records.append(dict(id=key,title=title,type=kind,pokemon=pokemon,path=str(path),family=family,description=desc,duration=round(duration),bytes=path.stat().st_size,poster=f'/vignettes/{key}.jpg'))
rows=list(csv.DictReader(open(H/'Capacites-Z/Inventaire/35-capacites-z-et-audit.csv',encoding='utf-8-sig')))
tested={x['id'] for x in records};pending=[dict(title=x['nom'],type=x['type'],family=x['famille'],pokemon=x['pokemon']) for x in rows if x['id_pmdo'] not in tested]
assert len(pending)==0
(A/'catalogue.json').write_text(json.dumps({'videos':records,'pending':pending},ensure_ascii=False,indent=2))
# Documents publics harmonisés, sans modifier les originaux de travail.
def public_text(s):
 s=s.replace('README-V4-IA.md','rapports V4')
 for a,b in [('générées par IA','personnalisées'),('générés par IA','personnalisés'),('généré par IA','personnalisé'),('générée par IA','personnalisée')]:s=s.replace(a,b)
 return re.sub(r'\bIA\b','personnalisé',s)
(A/'inventaire-public.md').write_text(public_text((H/'Capacites-Z/Inventaire/Inventaire-complet.md').read_text()))
(A/'capacites-public.csv').write_text(public_text((H/'Capacites-Z/Inventaire/35-capacites-z-et-audit.csv').read_text(encoding='utf-8-sig')),encoding='utf-8-sig')
print('catalogue :',len(records),'vidéos ;',35-len(pending),'capacités Z avec prototype,',len(pending),'sans prototype filmé')
