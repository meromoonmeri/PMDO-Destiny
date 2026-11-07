#!/usr/bin/env python3
"""Tests statiques des cartes et simulation Lua ; pas une partie en jeu."""
from pathlib import Path
import json,sys,os
from executer_lua import run
ROOT=Path(__file__).resolve().parents[2]
D=ROOT/'game/Data/Ground'
markers={'reverie_post_office':'entrance_south','reverie_inn':'Main_Entrance_Marker','reverie_water_home':'Main_Entrance_Marker','dojo_kingambit':'MarowakDojoExitMarker','reverie_hutte_aquatique':'Main_Entrance_Marker','reverie_rock_home':'Main_Entrance_Marker','reverie_grass_home':'Main_Entrance_Marker','reverie_fire_home':'Main_Entrance_Marker','maison_equipe_falaise':'entree','reverie_normal_home':'Main_Entrance_Marker','reverie_electric_home':'Main_Entrance_Marker','ledian_dojo':'Main_Entrance_Marker','caféspindaaccueil':'NewObject_17','spindacaféétage1':'NewObject_3','spindacaféétage1salle2':'NewObject_11'}
offsets=[(24,0),(-24,0),(0,-24),(0,24),(32,0),(-32,0),(0,-32),(0,32),(24,-24),(-24,-24),(24,24),(-24,24)]
for name, marker in markers.items():
    s=(ROOT/'game/Data/Script/destiny/ground'/name/'init.lua').read_text(encoding='utf8')
    assert "require 'destiny.suivi_interieurs'" in s,name
    if name=='caféspindaaccueil':
        assert s.count('pcall(suivi_interieurs.Activer, map)') == 2,name
        for func in ('Enter', 'GameLoad'):
            part=s.split('function cafespindaaccueil.'+func+'(map)',1)[1].split('\nend',1)[0]
            assert part.index('GAME:FadeIn(30)') < part.index('pcall(suivi_interieurs.Activer, map)'),func
    else:
        assert s.count('suivi_interieurs.Activer(map)') == 2,name
    d=json.loads((D/(name+'.rsground')).read_text(encoding='utf-8-sig'))['Object']
    entities=d['Entities'];mk=next(x for e in entities for x in e.get('Markers',[]) if x['EntName']==marker)['Collider'];x,y=mk['X'],mk['Y'];obs=d['obstacles'];p=None
    for dx,dy in offsets:
        a,b=x+dx,y+dy
        if a<0 or b<0 or a+16>len(obs)*8 or b+16>len(obs[0])*8:continue
        if any(obs[cx][cy]['Tags'] != 0 for cx in range(a//8,(a+15)//8+1) for cy in range(b//8,(b+15)//8+1)):continue
        p=(a,b);break
    assert p is not None,name
    a,b=p
    for e in entities:
        for o in e.get('GroundObjects',[])+e.get('MapChars',[]):
            c=o.get('Collider')
            if c and not o.get('Passable',False):
                assert not(a<c['X']+c['Width'] and a+16>c['X'] and b<c['Y']+c['Height'] and b+16>c['Y']), (name,p,o['EntName'])
    print('PASS placement statique',name,marker,p)
r=(ROOT/'game/Data/Script/destiny/ground/reveil_nuit/init.lua').read_text(encoding='utf8')
n=(ROOT/'game/Data/Script/destiny/ground/cliffdaytest_nuit/init.lua').read_text(encoding='utf8')
c=(ROOT/'game/Data/Script/destiny/ground/cliffdaytest/init.lua').read_text(encoding='utf8')
for s in (r,n):assert "UI:ResetSpeaker() -- question système, pas une réplique\n  UI:ChoiceMenuYesNo('Souhaitez-vous retourner dans les Bois Perdus ?'" in s
assert 'UI:ResetSpeaker() -- choix du joueur, sans portrait' in r
assert 'C’est la même falaise que cette nuit' not in c
print('PASS choix système, retour à la falaise')
os.chdir(ROOT);run(ROOT/'tools/tests/test_suivi_interieurs.lua',ROOT);run(ROOT/'tools/tests/test_sorties_suivi.lua',ROOT)
