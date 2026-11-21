#!/usr/bin/env python3
"""Contrôle binaire et mise en scène : géométrie, alpha, sons et événements natifs."""
import argparse, hashlib, io, json, re, struct
from pathlib import Path
from PIL import Image, ImageChops


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def lire_atlas(path,r):
    b=path.read_bytes();n=struct.unpack_from('<q',b)[0];assert len(b)==n+24
    w,h,rotation,f=struct.unpack_from('<iiii',b,n+8)
    assert (w,h,rotation,f)==(r['width'],r['height'],0,r['frames'])
    assert hashlib.sha256(b).hexdigest()==r['sha256']
    im=Image.open(io.BytesIO(b[8:8+n])).convert('RGBA');cx=im.width//w
    assert im.width%w==im.height%h==0 and (im.height//h)*cx==f
    return [im.crop((i%cx*w,i//cx*h,(i%cx+1)*w,(i//cx+1)*h)) for i in range(f)]


def same(a,b):
    return a.tobytes()==b.tobytes() # compare aussi les RGB hors alpha


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for x in ('base','lot','pmdo'):p.add_argument('--'+x,type=Path,required=True)
    args=p.parse_args();q=args.lot;s=args.base;j=args.pmdo
    source=q/'tools/cinematiques_kingambit'; reg=read(source/'Banques.json');p=read(source/'Plans.json')
    assert len(reg)==len(set(x['sha256'] for x in reg))==54
    assert len(p)==len(set(z['signe'] for z in p.values()))==len(set(z['noir'] for z in p.values()))==18
    sons={x.stem for x in (j/'Content/Sound/Battle').glob('*.ogg')}
    assert {'EVT_Chest_Click','_UNK_DUN_Clank','EVT_EP_Pitfall_Reveal','EVT_EP_Pitfall_Fall','EVT_EP_Pitfall_Land'}<=sons
    assert max(len(z['noir']) for z in p.values())<150
    if q.resolve()!=s.resolve():
        assert not any((q/'game/Data'/x).exists() for x in ('Ground','Map','Zone'))
    planslua=(q/'game/Data/Script/destiny/dojo_kingambit_plans.lua').read_text()
    for i,(k,z) in enumerate(p.items()):
        assert set(z['sons'])<=sons,(k,z['sons'])
        assert z['noir'] in planslua and z['replique'] in planslua and z['chef'] in planslua
        assert sorted(z['ordre'])==[1,2,3]
        m=read(s/'game/Data/Map'/f'dojo_kingambit_dedales_{k}.rsmap')['Object']
        ev=m['MapEffect']['OnMapStarts']
        assert m['Element']==k and m['Music']=='Marowak Dojo.ogg'
        assert [x['Key']['str'][0] for x in ev]==[-15,-11,-9,-5]
        assert [x['Value'].get('Script') for x in ev][1:3]==['DestinyDojoTroupeMasquer','DestinyDojoTroupeJouer']
        assert 'BeginBattleEvent' in ev[-1]['Value']['$type'] and 'map_clear_check' in str(ev[-1])
        rs=reg[i*3:(i+1)*3]
        assert rs[0]['path']==f'Kingambit_Signaux_{k}.dir'
        gfx=q/'game/Content';fs=lire_atlas(gfx/'BG'/rs[0]['path'],rs[0]);assert len(fs)==16
        assert all(a.getbbox() for a in fs[:-1]) and not fs[-1].getbbox()
        assert all(max(r,g,b)<=a for a0 in fs[::3] for r,g,b,a in a0.getdata()),k
        for r,calque in zip(rs[1:],('Sol','Rebord')):
            assert r['path']==f'Kingambit_Mecanisme_{k}_{calque}.dir';fs=lire_atlas(gfx/'Particle'/r['path'],r)
            assert len(fs)==24 and len({a.tobytes() for a in fs[:20]})>=8
            original=Image.open(s/'art/dojo_dedales_trappes'/f'{k}_{calque.lower()}.png').convert('RGBA')
            assert not ImageChops.difference(original,fs[-1]).convert('RGB').getbbox() or same(original,fs[-1])
            assert original.getchannel('A').tobytes()==fs[-1].getchannel('A').tobytes()
    print('PASS 54 DirSheets natives et 59 fichiers de jeu, 18 finales et formes existantes, 18 motifs uniques, sons PMDO, silhouette des trappes intacte.')


if __name__=='__main__': main()
