#!/usr/bin/env python3
"""Assemble la Quest unique `destiny` (PMDO 0.8.12) dans PMDO-Destiny/game à partir
des éléments récupérés et vérifiés dans destiny_work/stage/*.

Principes : aucune carte n'est modifiée, sauf le champ AssetName des anciennes versions
renommées pour coexister (remplacement ciblé de la première occurrence). Les tuiles /
fonds existants ne sont jamais écrasés : un conflit de contenu est consigné.
"""
import json, os, re, shutil, struct, sys, hashlib, io
from pathlib import Path

W = Path('/home/user/destiny_work')
GAME = W / 'PMDO-Destiny/game'
GROUND = GAME / 'Data/Ground'
TILE = GAME / 'Content/Tile'
BG = GAME / 'Content/BG'
OBJ = GAME / 'Content/Object'
SCRIPT = GAME / 'Data/Script/destiny'
ZONE = GAME / 'Data/Zone'

report = {'grounds': [], 'tiles_added': [], 'bg_added': [], 'conflicts': [], 'skipped_identical': [], 'notes': []}

def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for ch in iter(lambda: f.read(1 << 20), b''):
            h.update(ch)
    return h.hexdigest()

def copy_asset(src, dstdir, kind):
    src = Path(src); dst = Path(dstdir) / src.name
    if dst.exists():
        if sha(src) == sha(dst):
            report['skipped_identical'].append(str(dst.relative_to(GAME)))
            return 'identical'
        report['conflicts'].append({'kind': kind, 'name': src.name, 'src': str(src.relative_to(W)), 'existing': str(dst.relative_to(GAME))})
        return 'conflict'
    shutil.copy2(src, dst)
    (report['tiles_added'] if kind == 'tile' else report['bg_added']).append(str(dst.relative_to(GAME)))
    return 'added'

def ground_asset_name(path):
    size = os.path.getsize(path)
    with open(path, 'rb') as f:
        head = f.read(400000)
        if size > 400000:
            f.seek(max(0, size - 400000)); head += b'\n' + f.read()
    m = re.search(rb'"AssetName":\s*"((?:[^"\\]|\\.)*)"', head)
    return m.group(1).decode('utf-8') if m else None

def add_ground(src, zone, new_name=None, source_note='', script=None, script_src=None, flags=None):
    """Copie une carte ; new_name => renommage + réécriture ciblée d'AssetName."""
    src = Path(src)
    orig = ground_asset_name(src)
    name = new_name or src.stem
    dst = GROUND / f'{name}.rsground'
    renamed = bool(new_name and orig != new_name)
    data = None
    if renamed:
        data = src.read_bytes()
        pat = ('"AssetName": "%s"' % orig).encode('utf-8')
        pat2 = ('"AssetName":"%s"' % orig).encode('utf-8')
        if pat in data:
            data = data.replace(pat, ('"AssetName": "%s"' % new_name).encode('utf-8'), 1)
        elif pat2 in data:
            data = data.replace(pat2, ('"AssetName":"%s"' % new_name).encode('utf-8'), 1)
        else:
            raise SystemExit(f'AssetName introuvable dans {src}')
    elif orig != name:
        raise SystemExit(f'AssetName {orig!r} != {name!r} pour {src}')
    if dst.exists():
        same = (hashlib.sha256(data).hexdigest() == sha(dst)) if renamed else (sha(src) == sha(dst))
        if same:
            report['notes'].append(f'{name}: déjà présent, identique')
        else:
            report['conflicts'].append({'kind': 'ground', 'name': name, 'src': str(src.relative_to(W))})
            return
    else:
        if renamed:
            dst.write_bytes(data)
        else:
            shutil.copy2(src, dst)
    # script
    sdir = SCRIPT / 'ground' / name
    sdir.mkdir(parents=True, exist_ok=True)
    if script_src is not None:
        shutil.copy2(script_src, sdir / 'init.lua')
    elif script is not None:
        (sdir / 'init.lua').write_text(script, encoding='utf-8')
    elif not (sdir / 'init.lua').exists():
        (sdir / 'init.lua').write_text(skeleton(name), encoding='utf-8')
    zones.setdefault(zone, [])
    if name not in zones[zone]:
        zones[zone].append(name)
    report['grounds'].append({'name': name, 'zone': zone, 'original_name': orig, 'src': str(src.relative_to(W)), 'sha256': sha(dst), 'bytes': dst.stat().st_size, 'note': source_note, 'flags': flags or []})

def skeleton(name):
    return f"""-- Squelette de script Destiny (carte importée sans script propre).
-- Simple fondu d'entrée ; cinématiques et raccordements : à écrire.
require 'origin.common'

local {name} = {{}}

function {name}.Init(map)
end

function {name}.Enter(map)
  GAME:FadeIn(30)
end

function {name}.GameLoad(map)
  GAME:FadeIn(30)
end

function {name}.Update(map, time)
end

return {name}
"""

def copy_content_dir(root, tiles=True, bgs=True):
    root = Path(root)
    if tiles and (root / 'Content/Tile').is_dir():
        for p in sorted((root / 'Content/Tile').iterdir()):
            if p.suffix == '.tile':
                copy_asset(p, TILE, 'tile')
    if bgs and (root / 'Content/BG').is_dir():
        for p in sorted((root / 'Content/BG').iterdir()):
            if p.suffix == '.dir':
                copy_asset(p, BG, 'bg')

# ---------------------------------------------------------------- zones existantes
zones = {}
zone_meta = {}
for zp in sorted(ZONE.glob('*.json')):
    z = json.loads(zp.read_text(encoding='utf-8-sig'))
    zones[zp.stem] = list(z['Object']['GroundMaps'])
    zone_meta[zp.stem] = z

# ================================================================ 1. SCÉNARIO (64113588)
S = W / 'stage/scenario'
copy_content_dir(S)
for extra in ['Content/Music', 'Content/UI']:
    srcd = S / extra
    if srcd.is_dir():
        for p in srcd.rglob('*'):
            if p.is_file():
                d = GAME / p.relative_to(S)
                d.parent.mkdir(parents=True, exist_ok=True)
                if not d.exists():
                    shutil.copy2(p, d)
for f in ['Data/quiz_personnalite_config.json', 'Data/quiz_personnalite_natures.json']:
    shutil.copy2(S / f, GAME / f)
(GAME / 'Data/AutoTile').mkdir(exist_ok=True)
for p in (S / 'Data/AutoTile').glob('*.json'):
    shutil.copy2(p, GAME / 'Data/AutoTile' / p.name)

def fix_script(text, fixes):
    for old, new in fixes:
        if old not in text:
            raise SystemExit(f'correctif introuvable: {old!r}')
        text = text.replace(old, new)
    return text

COMMON_FIX = ("require 'common'", "require 'origin.common'")
scen_scripts = {
    'intro_halo': [COMMON_FIX, ("GROUND:EnterGroundMap('personality_test', 'Main_Entrance_Marker')", "GAME:EnterGroundMap('personality_test', 'Main_Entrance_Marker')")],
    'personality_test': [COMMON_FIX, ("require 'ground.personality_test.quiz_data'", "require 'destiny.ground.personality_test.quiz_data'"), ("GROUND:EnterGroundMap('cliffdaytest_nuit', 'Pichu_Crossroads')", "GAME:EnterGroundMap('destiny_cliff_tests', 'cliffdaytest_nuit', 'Pichu_Crossroads')")],
    'reveil_nuit': [COMMON_FIX],
    'cliffdaytest_nuit': [COMMON_FIX, ("GROUND:Hide(hero)", "GROUND:Hide('PLAYER')")],
}
scripts_fixed = {}
for m, fixes in scen_scripts.items():
    t = (S / f'Data/Script/destiny/ground/{m}/init.lua').read_text(encoding='utf-8')
    scripts_fixed[m] = fix_script(t, fixes)
zone_script = (S / 'Data/Script/destiny/zone/lost_wood/init.lua').read_text(encoding='utf-8')
zone_script = fix_script(zone_script, [COMMON_FIX])

# grounds du scénario
for m in ['personality_test', 'intro_halo', 'reveil_nuit']:
    add_ground(S / f'Data/Ground/{m}.rsground', 'personality_test', source_note='projet-creation-pmdo arena/64113588 quest_pmd_destiny', script=scripts_fixed[m])
# ordre voulu par le scénario : personality_test(0), intro_halo(1), reveil_nuit(2)
zones['personality_test'] = ['personality_test', 'intro_halo', 'reveil_nuit']
(SCRIPT / 'ground/personality_test').mkdir(parents=True, exist_ok=True)
shutil.copy2(S / 'Data/Script/ground/personality_test/quiz_data.lua', SCRIPT / 'ground/personality_test/quiz_data.lua')
(SCRIPT / 'zone/lost_wood').mkdir(parents=True, exist_ok=True)

# cliffdaytest_nuit : carte déjà dans le socle (identique au zip cinématique) ; script scénario
(SCRIPT / 'ground/cliffdaytest_nuit').mkdir(parents=True, exist_ok=True)
(SCRIPT / 'ground/cliffdaytest_nuit/init.lua').write_text(scripts_fixed['cliffdaytest_nuit'], encoding='utf-8')
# variante nocturne de la cinématique Dazzling conservée telle quelle (non chargée automatiquement)
C = W / 'stage/cutscene/mod_pmdo'
daz_nuit = (C / 'Data/Script/\u0068alcyon/ground/cliffdaytest_nuit/init.lua').read_text(encoding='utf-8')
(SCRIPT / 'ground/cliffdaytest_nuit/cinematique_dazzling_nuit.lua').write_text(
    "-- Variante nocturne originale de la cinématique « Pichu × Team Dazzling »\n"
    "-- (MOD_CUTSCENE_PICHU_DAZZLING_PMDO.zip, branche arena/e39626d2). Conservée intacte ;\n"
    "-- la carte cliffdaytest_nuit est pilotée par init.lua (scénario arena/64113588).\n"
    "-- Pour la rejouer : remplacer init.lua par ce fichier (et require 'origin.common').\n" + daz_nuit, encoding='utf-8')

# ================================================================ 2. CINÉMATIQUE DAZZLING (cliffdaytest, jour)
daz = (C / 'Data/Script/\u0068alcyon/ground/cliffdaytest/init.lua').read_text(encoding='utf-8')
daz = fix_script(daz, [COMMON_FIX])
(SCRIPT / 'ground/cliffdaytest').mkdir(parents=True, exist_ok=True)
(SCRIPT / 'ground/cliffdaytest/init.lua').write_text(daz, encoding='utf-8')
copy_content_dir(C)   # tuiles/BG identiques au socle (vérification)

# zone destiny_cliff_tests (scénario) : cartes réellement disponibles
# cliffdaytest, cliffdaytest_nuit déjà dans le socle (zone reverie) -> déplacées ici
for zname in list(zones):
    for g in ['cliffdaytest', 'cliffdaytest_nuit']:
        if g in zones[zname] and zname != 'destiny_cliff_tests':
            zones[zname].remove(g)
zones['destiny_cliff_tests'] = ['cliffdaytest']
# cliffdaytest_source : original sans entités (projet-pmdo main cliffdaytest.rsground cd276dab)
add_ground(W / 'stage/extra/ppmdo/Data/Ground/cliffdaytest.rsground', 'destiny_cliff_tests', new_name='cliffdaytest_source',
           source_note='projet-pmdo main cliffdaytest.rsground (blob cd276dab) = source canonique de la cinématique (nom attendu par la zone du scénario)')
# cliffnordouesttest1 canonique (racine de projet-creation-pmdo main, blob 51e9dd3b)
add_ground(W / 'stage/candidates/cliffnordouesttest1__51e9dd3b.rsground', 'destiny_cliff_tests', new_name='cliffnordouesttest1',
           source_note='projet-creation-pmdo main cliffnordouesttest1.rsground (blob 51e9dd3b)',
           flags=['INCOMPLETE: planches v2_promontoire_jour_03, terrain, terrain (2), terrain (3), terrain (4) introuvables dans tous les dépôts'])
for t in ['00_ciel', 'Altere_Pond_Cliffs', 'INVERSEPATHWAY']:
    copy_asset(W / f'stage/extra/town02/Content/Tile/{t}.tile', TILE, 'tile')
copy_asset(W / 'stage/wfc/Content/Tile/Metano_Altere_Transition_Base.tile', TILE, 'tile')
# cliffnordouesttest1_nuit : dernière itération (compat town02, commit e6c22020)
add_ground(W / 'stage/extra/nuit_compat/Data/Ground/cliffnordouesttest1_nuit.rsground', 'destiny_cliff_tests',
           source_note='projet-creation-pmdo commit e6c22020 (2026-10-21 21:44) livrables_cliff_nord_nuit_pmdo — version « compatible town02 »')
zones['destiny_cliff_tests'].append('cliffdaytest_nuit')
# le script de zone lost_wood renvoie vers l'index 8 de destiny_cliff_tests (= cliffdaytest_nuit dans la zone d'origine à 9 entrées)
new_idx = zones['destiny_cliff_tests'].index('cliffdaytest_nuit')
if "'destiny_cliff_tests', -1, 8, 0" in zone_script:
    zone_script = zone_script.replace("'destiny_cliff_tests', -1, 8, 0", f"'destiny_cliff_tests', -1, {new_idx}, 0")
else:
    m = re.search(r"destiny_cliff_tests'?,\s*-1,\s*8,\s*0", zone_script)
    if not m:
        raise SystemExit('appel EnterZone destiny_cliff_tests index 8 introuvable')
    zone_script = zone_script[:m.start()] + m.group(0).replace('8, 0', f'{new_idx}, 0').replace('8,0', f'{new_idx},0') + zone_script[m.end():]
(SCRIPT / 'zone/lost_wood/init.lua').write_text(zone_script, encoding='utf-8')
report['notes'].append(f'lost_wood/init.lua : index cliffdaytest_nuit dans destiny_cliff_tests 8 -> {new_idx}')

# ================================================================ 3. WATERFALL VILLAGE (town02)
WFC = W / 'stage/wfc'
copy_content_dir(WFC)
copy_asset(W / 'stage/extra/town02/Content/Tile/D06p11a_Base.tile', TILE, 'tile')
add_ground(W / 'extract/town02/WaterfallVillageCapital.full.rsground', 'town02_waterfallvillage', new_name='WaterfallVillageCapital',
           source_note='meromoonmeri/town02 main Data/Ground/WaterfallVillageCapital.rsground (Git LFS, 233 727 831 o)')
add_ground(WFC / 'Data/Ground/waterfall_cave_1.rsground', 'town02_waterfallvillage',
           source_note='meromoonmeri/town02 main Data/Ground/waterfall_cave_1.rsground (Git LFS)')

# ================================================================ 4. FALAISES NORD CENTRE (pack 10 x jour/nuit)
CC = W / 'stage/cliffcentre/MOD_CLIFF_NORD_CENTRE_PMDO'
copy_content_dir(CC)
for p in sorted((CC / 'Data/Ground').glob('*.rsground')):
    sc = CC / 'Data/Script/ground' / p.stem / 'init.lua'
    if not sc.exists():
        sc = None
    text = None
    if sc:
        text = sc.read_text(encoding='utf-8')
        if "require" not in text:
            text = "require 'origin.common'\n" + text
    add_ground(p, 'falaises_nord_centre', source_note='projet-creation-pmdo livrables_cliff_nord_centre_pmdo/PACK_CLIFF_NORD_CENTRE_PMDO_0812.zip', script=text)

# ================================================================ 5. ATELIERS : 13 zips renders (gtp) + tour céleste
G13 = W / 'stage/gen13'
for pack in sorted(G13.iterdir()):
    if not pack.is_dir():
        continue
    copy_content_dir(pack)
    for p in sorted((pack / 'Data/Ground').glob('*.rsground')):
        sc = None
        for cand in pack.glob(f'Data/Script/*/ground/{p.stem}/init.lua'):
            sc = cand
        for cand in pack.glob(f'Data/Script/ground/{p.stem}/init.lua'):
            sc = cand
        # les scripts des paquets sont des coquilles vides (« base d'édition, aucun warp ») :
        # on applique le squelette Destiny (fondu d'entrée), comme pour les autres cartes de l'atelier.
        add_ground(p, 'ateliers_donjons', source_note=f'guilde-treehouse-pmd renders/*/{pack.name} ({p.name})')
TC = W / 'stage/extra/tour_celeste'
copy_content_dir(TC)
for name, note in [('stc1_tour_celeste', 'projet-creation-pmdo commit 106b6e49 renders/tour_celeste_sommet_v1/package (sha = inventaire 262)'),
                   ('rtc1_tour_celeste', 'projet-creation-pmdo commit a35f9a3d renders/tour_celeste_relais_v1/package')]:
    sc = TC / 'Data/Script'
    text = None
    for cand in sc.rglob(f'{name}/init.lua'):
        text = cand.read_text(encoding='utf-8').replace("require 'common'", "require 'origin.common'")
    add_ground(TC / f'Data/Ground/{name}.rsground', 'ateliers_donjons', source_note=note, script=text)

# ================================================================ 6. ARCHIVES (anciennes versions / cartes hors socle)
A = W / 'stage/archives'
copy_content_dir(A)
for p in sorted((A / 'Data/Ground').glob('*.rsground')):
    add_ground(p, 'archives', source_note='projet-pmdo main cotes_v2_0812_pmdo.zip / cote_metano_v2_pmdo.zip (sha = inventaire 262)')
# café Spinda (branche 64113588 / racine projet)
cand = W / 'stage/candidates'
for f, note in [('caféspindaaccueil__490832c3', 'projet-creation-pmdo racine caféspindaaccueil.rsground'),
                ('spindacaféétage1__0052a0ae', 'projet-creation-pmdo racine spindacaféétage1.rsground'),
                ('spindacaféétage1salle2__20b4fe53', 'projet-creation-pmdo racine spindacaféétage1salle2.rsground'),
                ('spindacafetest__c8bdbff0', 'projet-creation-pmdo racine spindacafetest.rsground')]:
    add_ground(cand / f'{f}.rsground', 'archives', new_name=f.split('__')[0], source_note=note)
# reverie town v1 (gtp exports), forêt v1, beach cave v2, etc1
copy_content_dir(W / 'stage/extra/rvt')
for f, note in [('rvt_ne_jour__4999bf9d', 'guilde-treehouse-pmd exports reverie_town_v1'), ('rvt_ne_nuit__6696d80e', 'guilde-treehouse-pmd exports reverie_town_v1'),
                ('rvt_no_jour__f322fec2', 'guilde-treehouse-pmd exports reverie_town_v1'), ('rvt_no_nuit__b55c1037', 'guilde-treehouse-pmd exports reverie_town_v1'),
                ('v50812_beach_cave_entrance_v2__e4df4aa7', 'guilde-treehouse-pmd renders beach_cave_entrance_v2'),
                ('forest_render_v1__5dba77d7', 'guilde-treehouse-pmd exports/forest_cave_render_v1_pmdo (version antérieure, commit 3d24de1d)')]:
    add_ground(cand / f'{f}.rsground', 'archives', new_name=f.split('__')[0], source_note=note)
copy_content_dir(W / 'stage/extra/forest')
copy_content_dir(W / 'stage/extra/forest_v1')
add_ground(W / 'stage/extra/forest/Data/Ground/forest_magenta_v1.rsground', 'archives', source_note='guilde-treehouse-pmd exports/forest_cave_magenta_v1_pmdo')
add_ground(TC / 'Data/Ground/etc1_tour_celeste.rsground', 'archives', source_note='projet-creation-pmdo commit a35f9a3d renders/tour_celeste_entree_v1/package — version antérieure de tour_celeste_entree')
# anciennes versions nocturnes des falaises
copy_content_dir(W / 'stage/cliffnuit/MOD_CLIFF_NORD_NUIT_PMDO')
copy_content_dir(W / 'stage/extra/nuit_animee')
copy_content_dir(W / 'stage/extra/nuit_compat')
copy_content_dir(W / 'stage/extra/town02')
add_ground(W / 'stage/cliffnuit/MOD_CLIFF_NORD_NUIT_PMDO/Data/Ground/cliffdaytest_nuit.rsground', 'archives', new_name='cliffdaytest_nuit_v1_nord_nuit', source_note='projet-creation-pmdo commit c96645d4 PACK_CLIFF_NORD_NUIT (conversion nuit v1)')
add_ground(W / 'stage/extra/nuit_animee/Data/Ground/cliffdaytest_nuit.rsground', 'archives', new_name='cliffdaytest_nuit_v2_animee', source_note='projet-creation-pmdo commit 9d95a275 (nuages animés + mer 8 phases)')
add_ground(W / 'stage/extra/nuit_compat/Data/Ground/cliffdaytest_nuit.rsground', 'archives', new_name='cliffdaytest_nuit_v3_compat_town02', source_note='projet-creation-pmdo commit e6c22020 (compat town02)')
add_ground(W / 'stage/cliffnuit/MOD_CLIFF_NORD_NUIT_PMDO/Data/Ground/cliffnordouesttest1_nuit.rsground', 'archives', new_name='cliffnordouesttest1_nuit_v1_nord_nuit', source_note='projet-creation-pmdo commit c96645d4 (conversion nuit v1)')
add_ground(W / 'stage/extra/nuit_animee/Data/Ground/cliffnordouesttest1_nuit.rsground', 'archives', new_name='cliffnordouesttest1_nuit_v2_animee', source_note='projet-creation-pmdo commit 9d95a275 (nuages animés)')
add_ground(W / 'stage/extra/jour_compat/Data/Ground/cliffnordouesttest1.rsground', 'archives', new_name='cliffnordouesttest1_compat_town02', source_note='projet-creation-pmdo commit e6c22020 (compat town02, blob b40eaa93)')

# musiques référencées par les cartes, récupérées dans meromoonmeri/town02 (Content/Music, Git LFS)
(GAME / 'Content/Music').mkdir(parents=True, exist_ok=True)
for p in sorted((W / 'stage/extra/music').glob('*.ogg')):
    d = GAME / 'Content/Music' / p.name
    if not d.exists():
        shutil.copy2(p, d)
        report['notes'].append(f'musique ajoutée depuis town02 : {p.name}')

# ================================================================ 7. ZONES JSON + index
def zone_doc(zid, name_en, name_fr, comment, grounds):
    base = json.loads(json.dumps(zone_meta['destiny_hub']))
    o = base['Object']
    o['Name'] = {'DefaultText': name_en, 'LocalTexts': {'fr': name_fr}}
    o['Comment'] = comment
    o['GroundMaps'] = grounds
    return base

for zid, doc in [
    ('personality_test', json.loads((S / 'Data/Zone/personality_test.json').read_text(encoding='utf-8-sig'))),
    ('destiny_cliff_tests', json.loads((S / 'Data/Zone/destiny_cliff_tests.json').read_text(encoding='utf-8-sig'))),
    ('lost_wood', json.loads((S / 'Data/Zone/lost_wood.json').read_text(encoding='utf-8-sig'))),
    ('town02_waterfallvillage', json.loads((S / 'Data/Zone/town02_waterfallvillage.json').read_text(encoding='utf-8-sig'))),
]:
    doc['Object']['GroundMaps'] = zones.get(zid, [])
    zone_meta[zid] = doc
zone_meta['falaises_nord_centre'] = zone_doc('falaises_nord_centre', 'Northern Central Cliffs', 'Falaises nord centrées',
    "Pack « 10 Falaises Nord Centrées Nues » (textures canoniques Métano, jour/nuit) — projet-creation-pmdo livrables_cliff_nord_centre_pmdo.", zones['falaises_nord_centre'])
zone_meta['archives'] = zone_doc('archives', 'Archives', 'Archives',
    "Anciennes versions et variantes conservées telles quelles (comparaison avant remplacement). Voir docs/UNIFICATION_DESTINY.md.", zones['archives'])
for zid, doc in zone_meta.items():
    doc['Object']['GroundMaps'] = zones.get(zid, doc['Object']['GroundMaps'])
    (ZONE / f'{zid}.json').write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding='utf-8')

def counted_floors(doc):
    n = 0
    for seg in doc['Object'].get('Segments', []):
        n += len(seg.get('Floors', []))
    return n

old_index = json.loads((ZONE / 'index.idx').read_text(encoding='utf-8-sig'))
order = ['destiny_hub', 'personality_test', 'destiny_cliff_tests', 'lost_wood', 'town02_waterfallvillage', 'cotes_metano', 'falaises_nord_centre', 'reverie', 'ateliers_donjons', 'chapitres_destiny', 'archives']
idx_obj = {'$type': old_index['Object']['$type']}
for i, zid in enumerate(order):
    doc = zone_meta[zid]['Object']
    prev = old_index['Object'].get(zid, {})
    idx_obj[zid] = {
        '$type': 'RogueEssence.Data.ZoneEntrySummary, RogueEssence',
        'ExpPercent': doc['ExpPercent'], 'Level': doc['Level'], 'LevelCap': doc['LevelCap'], 'KeepSkills': doc['KeepSkills'],
        'TeamRestrict': doc['TeamRestrict'], 'TeamSize': doc['TeamSize'], 'MoneyRestrict': doc['MoneyRestrict'], 'BagRestrict': doc['BagRestrict'],
        'KeepTreasure': doc['KeepTreasure'], 'BagSize': doc['BagSize'], 'Rescues': doc['Rescues'], 'CountedFloors': counted_floors(zone_meta[zid]),
        'Rogue': doc['Rogue'], 'Grounds': list(doc['GroundMaps']), 'Maps': prev.get('Maps', []), 'Name': doc['Name'], 'Released': doc['Released'],
        'Comment': doc['Comment'], 'SortOrder': prev.get('SortOrder', i * 10),
    }
(ZONE / 'index.idx').write_text(json.dumps({'Version': old_index['Version'], 'Object': idx_obj}, ensure_ascii=False, indent=2), encoding='utf-8')
assert set(zone_meta) == set(order), set(zone_meta) ^ set(order)

# AutoTile index (3 entrées lost_wood)
at_entries = {'$type': 'System.Collections.Generic.Dictionary`2[[System.String, System.Private.CoreLib],[RogueEssence.Data.EntrySummary, RogueEssence]], System.Private.CoreLib'}
for p in sorted((GAME / 'Data/AutoTile').glob('*.json')):
    d = json.loads(p.read_text(encoding='utf-8-sig'))
    nm = d['Object'].get('Name', {'DefaultText': p.stem, 'LocalTexts': {}})
    at_entries[p.stem] = {'Name': nm, 'Released': True, 'Comment': d['Object'].get('Comment', ''), 'SortOrder': 0}
(GAME / 'Data/AutoTile/index.idx').write_text(json.dumps({'Version': '0.8.12.0', 'Object': at_entries}, ensure_ascii=False, indent=2), encoding='utf-8')

# ================================================================ 8. index des tuiles
def write_7bit(n):
    out = bytearray()
    while True:
        b = n & 0x7F; n >>= 7
        if n: out.append(b | 0x80)
        else:
            out.append(b); break
    return bytes(out)
tiles = sorted(TILE.glob('*.tile'), key=lambda p: p.stem)
buf = io.BytesIO()
buf.write(struct.pack('<i', len(tiles)))
for p in tiles:
    with open(p, 'rb') as f:
        raw = f.read(8)
        _, n = struct.unpack('<ii', raw)
        raw += f.read(n * 16)
    nm = p.stem.encode('utf-8')
    buf.write(write_7bit(len(nm))); buf.write(nm); buf.write(raw)
(TILE / 'index.idx').write_bytes(buf.getvalue())

# ================================================================ 9. StartParams (départ scénario) + scriptvars
sp = (GAME / 'Data/StartParams.xml').read_text(encoding='utf-8')
sp = sp.replace('<DefaultZone>destiny_hub</DefaultZone>', '<DefaultZone>personality_test</DefaultZone>')
sp = sp.replace('<Zone>destiny_hub</Zone>\n    <Segment>-1</Segment>\n    <ID>0</ID>', '<Zone>personality_test</Zone>\n    <Segment>-1</Segment>\n    <ID>1</ID>')
assert '<Zone>personality_test</Zone>' in sp
(GAME / 'Data/StartParams.xml').write_text(sp, encoding='utf-8')
sv = (SCRIPT / 'scriptvars.lua').read_text(encoding='utf-8')
if 'SV.Destiny' not in sv:
    sv += """
-- Drapeaux du scénario (arena/64113588) : les scripts testent toujours `SV.Destiny ~= nil`,
-- la table est simplement pré-créée ici.
SV.Destiny = SV.Destiny or {
  PartenaireParti = false, RetourAccompli = false, LostWoodTrip = nil,
  LostWoodTutorialDone = false, HeroAssemblyIndex = nil, FinaleDestiny = false,
}
"""
    (SCRIPT / 'scriptvars.lua').write_text(sv, encoding='utf-8')

json.dump(report, open(W / 'audit/assemble_report.json', 'w'), ensure_ascii=False, indent=1)
print('grounds added', len(report['grounds']), 'tiles added', len(report['tiles_added']), 'bg added', len(report['bg_added']), 'conflicts', len(report['conflicts']))
for c in report['conflicts']:
    print('CONFLICT', c)
