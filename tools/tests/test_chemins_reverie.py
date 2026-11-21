#!/usr/bin/env python3
"""Recadrage, accès préservés, routes marchables et arène de Liane."""
from collections import deque
import gzip
import json
from pathlib import Path
import sys
from xml.etree import ElementTree

import ijson
from lupa import LuaRuntime

from executer_lua import run

R = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(R/'tools'))
from lib_tiles import read_tilesheet
from build_duel_reverie import MAP, BANK, ZONE
from rogner_sud_reverie import RANGS


def obj(p): return json.loads(p.read_text(encoding='utf-8-sig'))['Object']


def s(name): return R/'game/Data/Script/destiny'/name


def obstacles(n):
    with gzip.open(R/'payload'/f'{n}.rsground.gz') as f:
        if f.read(3) != b'\xef\xbb\xbf': f.seek(0)
        g = [bytes(e['Tags'] for e in c) for c in ijson.items(f,'Object.obstacles.item')]
    assert len(g) == 200 and all(len(c) == RANGS and c[-1] == 1 for c in g),n
    return g


def libre(g,x,y):
    return (0 <= x <= 1584 and 0 <= y <= len(g[0])*8-16
            and all(g[i][j] == 0 for i in range(x//8,(x+15)//8+1) for j in range(y//8,(y+15)//8+1)))


def atteignables(g, depart):
    assert libre(g,*depart),depart
    q = deque([depart]); vus = {depart}
    while q:
        x,y = q.popleft()
        for p in ((x-4,y),(x+4,y),(x,y-4),(x,y+4)):
            if p not in vus and libre(g,*p):
                vus.add(p);q.append(p)
    return vus


def verifier_sud():
    for n in ('reverie_residentiel','WaterfallVillageCapital','reverie_residentiel_Dev'):
        g = obstacles(n)
        a = atteignables(g, (700,1976))
        cibles = {
            'Pierre': (456,2360), 'Plante': (584,2568), 'Citrouille': (776,2552),
            'Escalier P': (1120,2432), 'Pont ouest (rive sud)': (88,2880),
            'Pont central (rive sud)': (688,2880), 'Maison ronde': (888,2944),
            'Reprise ancienne sauvegarde': (688,2896), 'Partenaire de reprise': (688,2920),
        }
        assert all(p in a for p in cibles.values()), (n,{k:p for k,p in cibles.items() if p not in a})
        assert max(y for _,y in a) == (RANGS-1)*8-16
    print('PASS bord à 2 976 px, limite solide, trois seuils, deux ponts, maison ronde et point de reprise joignables.')


def verifier_routes():
    defs = LuaRuntime().execute(s('reverie_itinerants_recits.lua').read_text(encoding='utf-8'))
    origine = R/'game/Data'
    terrain = {n:obstacles(n) for n in ('reverie_centre','reverie_residentiel','reverie_etang','WaterfallVillageCapital')}
    for p in defs.values():
        x = [int(k) for k in p['x'].values()]; y = p['y']; n = p['carte']; ident=p['id']
        assert len(x) == 3 and x == sorted(set(x)) and x[-1]-x[0] >= 160
        for g in (terrain[n],terrain['WaterfallVillageCapital']):
            assert all(libre(g,i,y) for i in range(x[0],x[-1]+1)),ident
            assert any(all(libre(g,i,y+dy) for i in range(x[0],x[-1]+1)) for dy in (16,-16)),ident
        mon = origine/'Monster'/f'{p["espece"]}.json'
        assert mon.is_file() or (R/'base/Data/Monster'/mon.name).is_file(),mon
        if p['objet']:
            item = origine/'Item'/f'{p["objet"]}.json'
            assert item.is_file() or (R/'base/Data/Item'/item.name).is_file(),item
        print('PASS itinéraire praticable et latéral libre :',ident,n,x,y)


def verifier_arene():
    d = R/'game/Data'; z = obj(d/'Zone'/f'{ZONE}.json'); idx = obj(d/'Zone/index.idx')[ZONE]
    mp = obj(d/'Map'/f'{MAP}.rsmap'); ts, bank = read_tilesheet(R/'game/Content/Tile'/f'{BANK}.tile')
    assert z['NoEXP'] and not z['Released'] and z['Rescues'] == 0 and idx['Maps'] == [[0]] and idx['Grounds'] == []
    assert len(z['Segments']) == len(z['Segments'][0]['Floors']) == 1
    assert z['Segments'][0]['Floors'][0]['GenSteps'][0]['Value']['MapID'] == MAP == mp['AssetName']
    assert len(mp['MapTeams']) == len(mp['MapTeams'][0]['Players']) == 1 and mp['NoRescue'] and not mp['Items']
    p = mp['MapTeams'][0]['Players'][0]
    assert p['Nickname'] == 'Liane' and p['BaseForm']['Species'] == 'mienfoo' and p['Unrecruitable']
    # Formule native de MonsterFormData : aucun PV initial au-dessus du maximum.
    mon = next(f for f in (d/'Monster/mienfoo.json',R/'base/Data/Monster/mienfoo.json') if f.is_file())
    form = obj(mon)['Forms'][p['BaseForm']['Form']]
    max_level = int(ElementTree.parse(d/'StartParams.xml').findtext('MaxLevel'))
    base_hp = form['BaseHP']; somme = sum(form['Base'+k] for k in ('HP','Atk','Def','MAtk','MDef','Speed'))
    bonus_hp = p['MaxHPBonus'] * (1536 * base_hp // somme - base_hp) // 256
    assert p['HP'] == (base_hp + 130) * p['Level'] // max_level + 10 + bonus_hp == 52
    assert len(p['BaseSkills']) == len(p['Skills']) == 4 and [v['BackRef'] for v in p['Skills']] == list(range(4))
    assert any(e['Value'].get('CheckClearStatus') == 'map_clear_check' for e in mp['MapEffect']['OnMapStarts'])
    assert ts == 24 and len(mp['Tiles']) == 32 and all(len(c)==24 for c in mp['Tiles'])
    de = mp['EntryPoints'][0]['Loc']; en = p['serializationLoc']
    assert all(mp['Tiles'][de['X']][y]['Data']['ID']=='floor' for y in range(en['Y'],de['Y']+1))
    nb = 0
    for layer in mp['Layers']:
        for col in layer['Tiles']:
            for c in col:
                for piste in c['Layers']:
                    fr = piste['Frames']; nb += len(fr)>1
                    assert len(fr)==1 or len(fr)==12 and piste['FrameLength']==6
                    for f in fr:
                        ref = f['TexLoc']
                        assert f['Sheet']=='' or (f['Sheet']==BANK and (ref['X'],ref['Y']) in bank)
    assert nb > 20
    print('PASS duel : zone fixe, adversaire réel, déclenchement victoire, ressources valides et animations.')


if __name__ == '__main__':
    verifier_sud();verifier_routes();verifier_arene()
    run(R/'tools/tests/test_chemins_reverie.lua', R)
