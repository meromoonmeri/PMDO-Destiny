#!/usr/bin/env python3
"""Dédales : données, feuilles natives, géométrie des entrées et contrat Lua."""
from pathlib import Path
import io
import json
import os
import struct
import sys

from PIL import Image
from executer_lua import run

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'tools'))
from build_dedales_kingambit import ZONE
from dojo_dtef import Dtef, WIDTH, HEIGHT, START, BOSS, plan, verifier, libre
from dessiner_trappe_kingambit import rupture
from dojo_reverie_types import TYPES
from lib_tiles import read_tilesheet

GAME = ROOT/'game'
DATA = GAME/'Data'
ART = GAME/'Content'
SOURCES = ROOT/'art/dojo_dedales_trappes'

def obj(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))['Object']

def gensteps(floor):
    return {p['Value']['$type'].split('`')[0].rsplit('.',1)[-1]: p['Value'] for p in floor['GenSteps']}


def references(layers):
    return ((f['Sheet'], f['TexLoc']['X'], f['TexLoc']['Y']) for l in layers for col in l['Tiles']
            for c in col for a in c['Layers'] for f in a['Frames'] if f['Sheet'])


def dungeon():
    z = obj(DATA/f'Zone/{ZONE}.json')
    entry = obj(DATA/'Zone/index.idx')[ZONE]
    assert len(TYPES) == len(z['Segments']) == len(entry['Maps']) == 18
    assert {t[0] for t in TYPES} == set('normal fire water grass electric ice fighting poison ground flying psychic bug rock ghost dragon dark steel fairy'.split())
    assert z['Released'] and not z['NoEXP'] and z['ExpPercent']==entry['ExpPercent']==175
    assert z['Rescues']==0 and not z['LevelCap'] and z['BagRestrict']==-1 and not z['MoneyRestrict']
    assert entry['CountedFloors']==54 and entry['Maps']==[[0,1,2]]*18
    manifest=json.loads((SOURCES/'biomes.json').read_text(encoding='utf-8'))
    assert len(manifest)==18 and len({plan(t[0]) for t in TYPES})==18
    base=os.getenv('DESTINY_DTEF_DATA')
    dtef=Dtef(base) if base else None
    assert len({t[3] for t in TYPES})==18
    guild = obj(DATA/'Zone/town02_waterfallvillage.json')
    assert guild['GroundMaps'][17]=='dojo_kingambit'
    for i,(typ,label,n,theme,_,glyph,foes,boss) in enumerate(TYPES):
        assert len(glyph)==8 and all(len(l)==8 for l in glyph)
        seg=z['Segments'][i]
        assert len(seg['Floors'])==3
        assert [f['$type'].split('.')[-1].split(',')[0] for f in seg['Floors']]==['GridFloorGen']*2+['LoadGen']
        assert seg['Comment'].startswith(typ+' — ')
        name,pop=seg['ZoneSteps']
        assert n in name['Name']['DefaultText'] and '{0}' in name['Name']['DefaultText']
        for k in range(2):
            st=gensteps(seg['Floors'][k]);tex=st['MapDictTextureStep']
            assert st['FloorStairsStep']['Exits'][0]['Tile']['ID']=='stairs_go_down'
            assert st['MapDataStep']['TimeLimit'] in (650,850)
            assert tex['GroundElement']==typ and tex['TextureMap']=={
                'floor':theme+'_floor','wall':theme+'_wall','unbreakable':theme+'_wall'}
            assert {'DetectIsolatedStairsStep','PlaceRandomMobsStep'} <= st.keys()
            assert not any('Money' in key or 'Item' in key for key in st)
            mobs=[a['Spawn']['Spawn'] for a in pop['Spawns'] if a['Range']=={'Min':k,'Max':k+1}]
            assert len(mobs)==2 and {m['BaseForm']['Species'] for m in mobs}=={foes[k][0],foes[k+1][0]}
            assert all(m['Level']=={'Min':7+2*k,'Max':9+2*k} and m['SpawnFeatures']==[{
                '$type':'PMDC.LevelGen.MobSpawnUnrecruitable, PMDC'}] for m in mobs)
        final=gensteps(seg['Floors'][2])['MappedRoomStep']['MapID']
        assert final==f'{ZONE}_{typ}'
        m=obj(DATA/f'Map/{final}.rsmap')
        assert m['Element']==typ and m['NoRescue'] and not m['Items'] and len(m['MapTeams'])==1
        c=m['MapTeams'][0]['Players'][0]
        assert c['BaseForm']==c['CurrentForm'] and c['BaseForm']['Species']==boss[0]
        assert typ in (c['Element1'],c['Element2']) and c['Unrecruitable'] and c['Level']==12
        assert len(c['Skills'])==len(c['BaseSkills'])==4 and all(n['BackRef']==j for j,n in enumerate(c['Skills']))
        assert tuple(q['SkillNum'] for q in c['BaseSkills'])==(*boss[1:],'','')
        assert any(e['Value'].get('CheckClearStatus')=='map_clear_check' for e in m['MapEffect']['OnMapStarts'])
        g=plan(typ); verifier(g)
        assert manifest[typ]['biome']==theme and manifest[typ]['plan']==list(g)
        assert [l['Name'] for l in m['Layers']]==['Sol DTEF continu','Parois DTEF','Relief secondaire DTEF']
        assert [l['Layer'] for l in m['Layers']]==[-1,0,0] and all(l['Visible'] for l in m['Layers'])
        refs=list(references(m['Layers']))
        assert refs and {s for s,x,y in refs} <= set(manifest[typ]['banques_sha256'])
        assert not any(s.startswith(('Ledian','Ossatueur','Kingambit','Reverie_Duel')) for s,x,y in refs)
        assert m['EntryPoints'][0]['Loc']==dict(zip(('X','Y'),START))
        assert c['serializationLoc']==dict(zip(('X','Y'),BOSS))
        for x in range(WIDTH):
            for y in range(HEIGHT):
                assert [bool(l['Tiles'][x][y]['Layers']) for l in m['Layers']]==[True,g[y][x]=='#',g[y][x]=='~']
        if dtef:
            assert m['Layers']==list(dtef.arene(typ,theme))
            assert dtef.provenance(theme)==manifest[typ]['banques_sha256']
            dtef.apercu(m['Layers'])
        assert len(m['Tiles'])==WIDTH and all(len(col)==HEIGHT for col in m['Tiles'])
        assert all((t['Data']['ID']=='floor')==libre(x,y,typ) and not t['Effect']['ID']
                   for x,col in enumerate(m['Tiles']) for y,t in enumerate(col))
    print('PASS 18 plans DTEF distincts connectés, 36 étages procéduraux et 18 maîtres.' + (' Références et SHA256 natives exacts.' if dtef else ' Contrôle structurel sans le jeu de base.'))


def ground():
    expected = {
        'dojo_kingambit': ('Kingambit_Accueil_Natif',768,576,15),
        'dojo_kingambit_arene': ('Kingambit_Arene_Natif',768,576,9),
        'dojo_kingambit_reliques': ('Kingambit_Reliques_Natif',768,576,9),
    }
    originals = os.getenv('DESTINY_DOJO_ORIGINAUX')
    for name,(sheet,w,h,count) in expected.items():
        g=obj(DATA/f'Ground/{name}.rsground'); s,tiles=read_tilesheet(ART/f'Tile/{sheet}.tile'); layers=g['Layers']
        assert s==g['TexSize']*8 and len(layers)==count and len(layers[0]['Tiles'])*s==w and len(layers[0]['Tiles'][0])*s==h
        refs=list(references(layers)); refs1=[(x,y) for b,x,y in refs if b==sheet]
        assert refs1 and set(refs1)==tiles.keys()
        if name.startswith('dojo_kingambit'):
            assert all(len({f['Sheet'] for f in a['Frames']}-{'',sheet})==0 for l in layers for col in l['Tiles']
                       for c in col for a in c['Layers'])
        if originals:
            old=obj(Path(originals)/f'game/Data/Ground/{name}.rsground')
            assert g.keys()==old.keys()
            assert all(g[k]==old[k] for k in g.keys()-{'Layers','Entities'})
            assert [tuple(l[k] for k in ('Name','Layer','Visible')) for l in layers]==[
                tuple(l[k] for k in ('Name','Layer','Visible')) for l in old['Layers']]
            if name=='dojo_kingambit':
                assert g['Entities'][0]['Markers'][:-1]==old['Entities'][0]['Markers']
                g['Entities'][0]['Markers'].pop()
            assert g['Entities']==old['Entities']
    if originals:
        for n in ('ledian_dojo','dojo_ossatueur'):
            p=f'Data/Ground/{n}.rsground'
            assert (GAME/p).read_bytes()==(Path(originals)/'game'/p).read_bytes()
    acc=obj(DATA/'Ground/dojo_kingambit.rsground')
    markers=acc['Entities'][0]['Markers'];assert markers[3]['EntName']=='RetourDedalesMarker'
    p=markers[3]['Collider']; x,y=p['X'],p['Y']
    assert (x,y)==(376,336) and all(not acc['obstacles'][a][b]['Tags'] for a in (47,48) for b in (42,43))
    assert [l['Visible'] for l in acc['Layers'][8:14]] == [True,False,False,True,False,False]
    print('PASS complexe Kingambit : échelles natives, tuiles résolues, 15/9/9 calques, portes et retour.')


def trap():
    art=json.loads((SOURCES/'manifest.json').read_text(encoding='utf-8'))
    assert len(set(o['sha256_brut'] for o in art.values()))==8
    expected=set()
    signatures=set()
    for typ,_,_,theme,*_ in TYPES:
        assert art[typ]['biome']==theme
        base=Image.open(SOURCES/f'{typ}_sol.png');rim=Image.open(SOURCES/f'{typ}_rebord.png')
        signatures.add(base.tobytes()); ref=rupture(base,rim)
        for depth,name in enumerate(('Sol','Rebord')):
            f=ART/f'Particle/Kingambit_Trappe_{typ}_{name}.dir';expected.add(f)
            raw=f.read_bytes();L=struct.unpack_from('<q',raw,0)[0]
            w,h,dirs,n=struct.unpack_from('<iiii',raw,L+8)
            assert (w,h,dirs,n)==(96,80,0,10)
            with Image.open(io.BytesIO(raw[8:L+8])) as im:
                assert im.mode=='RGBA' and im.size==(480,160)
                phases=[im.crop((i%5*w,i//5*h,(i%5+1)*w,(i//5+1)*h)) for i in range(n)]
                assert all(a.tobytes()==b.tobytes() for a,b in zip(phases,ref[depth]))
                for p in phases:
                    assert set(p.getchannel('A').tobytes())<={0,255}
                    assert not any(a and r>138 and b>138 and r-g>74 and b-g>74 for r,g,b,a in struct.iter_unpack('4B',p.tobytes()))
            assert phases[8].tobytes()==phases[9].tobytes()
            assert bool(phases[7].getpixel((48,40))[3])==(name=='Sol')
    assert len(signatures)==18 and set((ART/'Particle').glob('Kingambit_Trappe_*.dir'))==expected
    print('PASS trappes : 18 variantes, 36 DirSheets reconstruites, alpha binaire et 0 frange magenta.')


if __name__=='__main__':
    dungeon();ground();trap()
    run(Path(__file__).with_suffix('.lua'), ROOT)
