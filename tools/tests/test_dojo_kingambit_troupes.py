#!/usr/bin/env python3
"""Reconstruction exacte des particules ; contrat des whooshes natifs et scènes."""
from pathlib import Path
import io
import json
import shutil
import struct
import subprocess
import sys
from PIL import Image
from executer_lua import run

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from dessiner_entrees_kingambit import W,H,frames,depart,motifs,TROUPES,POSES
from synthetiser_whooshes_kingambit import DUREES


def lire_dir(path):
    r=path.read_bytes();length=struct.unpack_from('<q',r)[0]
    w,h,orient,n=struct.unpack_from('<iiii',r,length+8)
    assert (w,h,orient)==(W,H,0) and len(r)==length+24
    c=4 if n>=8 else 3
    with Image.open(io.BytesIO(r[8:length+8])) as a:
        assert a.mode=='RGBA' and a.size==(w*c,h*((n+c-1)//c))
        return [a.crop((i%c*w,i//c*h,(i%c+1)*w,(i//c+1)*h)) for i in range(n)]


def assets():
    d=ROOT/'game/Content';p=d/'Particle';son=d/'Sound/Battle'
    im=motifs(ROOT/'art/dojo_kingambit_troupes'); expected=set()
    assert im['petale-cerisier'].getbbox() and im['prisme'].getbbox() and im['ombre'].getbbox()
    dep=p/'Kingambit_Entree_psychic_Depart.dir';expected.add(dep)
    assert [a.tobytes() for a in lire_dir(dep)]==[depart(i,im['prisme']).tobytes() for i in range(6)]
    for typ in TROUPES:
        for nom,ref in zip(('Sol','Air'),frames(typ,im)):
            bank=p/f'Kingambit_Entree_{typ}_{nom}.dir';expected.add(bank)
            xs=lire_dir(bank);assert len(xs)==POSES
            assert xs[-1].getbbox() is None and len({x.tobytes() for x in xs})>=8
            for x,y in zip(xs,ref):
                assert x.tobytes()==y.tobytes()
                assert set(x.getchannel('A').tobytes())<={0,255}
                assert not any(a and r>138 and b>138 and r-g>74 and b-g>74 for r,g,b,a in struct.iter_unpack('4B',x.tobytes()))
    assert set(p.glob('Kingambit_Entree_*.dir'))==expected
    print('PASS 37 particules / 582 poses à la grille native, alpha net sans pixels magenta.')
    assert {x.name for x in son.glob('Kingambit_Whoosh_*.ogg')}=={f'Kingambit_Whoosh_{t}.ogg' for t in TROUPES}
    distincts=set()
    ffprobe=shutil.which('ffprobe')
    for typ,dur in DUREES.items():
        path=son/f'Kingambit_Whoosh_{typ}.ogg'; data=path.read_bytes();distincts.add(data)
        assert data.startswith(b'OggS') and b'vorbis' in data[:256]
        if ffprobe:
            o=json.loads(subprocess.check_output([ffprobe,'-v','error','-show_entries','stream=codec_name,channels,sample_rate,duration',
                                                '-of','json',str(path)]))['streams']
            assert len(o)==1 and (o[0]['codec_name'],o[0]['channels'],o[0]['sample_rate'])==('vorbis',2,'44100')
            assert abs(float(o[0]['duration'])-dur)<.005, o
    assert len(distincts)==18
    print('PASS 18 whooshes de synthèse indépendants.' + (' Ogg Vorbis stéréo 44,1 kHz décodables.' if ffprobe else ''))


if __name__=='__main__':
    assets()
    run(Path(__file__).with_suffix('.lua'),ROOT)
