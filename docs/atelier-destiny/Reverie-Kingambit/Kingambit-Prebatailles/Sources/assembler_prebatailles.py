#!/usr/bin/env python3
"""Vérifier puis archiver le delta. Aucun fichier du jeu n'est édité ici."""
from __future__ import annotations
from hashlib import sha256
import io
import json
import lzma
import os
from pathlib import Path
import struct
import subprocess as sp
import tempfile
from zipfile import ZipFile, ZIP_DEFLATED

import numpy as np
from PIL import Image

D=Path.home()/'.cache/spawns-kingambit'
S=D/'source'; U=D/'prebatailles'; B=U/'natif'
V=Path(__file__).resolve().parents[1]
BASE='79ddccca57331787d145eda262773fb50fd944e0'
COMMIT='7fcd0610402958c2d2262c2d1093e459097d13af'
VIDEO=V/'Les-18-prebatailles-dans-PMDO.mp4'
ZIP=V/'Kingambit-Prebatailles.zip'
FILE_PATCH=U/'Integration/Prebatailles-depuis-Cyclones-Meteo.patch.xz'
FILE_BUNDLE=U/'Integration/Prebatailles.bundle'


def cmd(args,**kw):return sp.check_output(list(map(str,args)),**kw)

def git(*args,env=None,input=None):
    e={**os.environ,'GIT_NO_LAZY_FETCH':'1'} if env is None else env
    return cmd(('git','-C',S,*args),env=e,input=input).decode().strip()

def data(path):return json.loads(path.read_text(encoding='utf-8'))

def hash_(b):return sha256(b).hexdigest()


def banks(rows):
    out=[]
    for r in rows:
        k=r['id']; p=U/'Content/BG'/r['atlas']; q=U/'Content/Sound/Battle'/r['son']; b=p.read_bytes()
        n,=struct.unpack_from('<q',b); assert n==len(b)-24
        assert struct.unpack_from('<4i',b,n+8)==(320,240,0,28)
        art=np.asarray(Image.open(io.BytesIO(b[8:n+8])).convert('RGBA'))
        src=np.asarray(Image.open(U/'Planches'/(k+'.png')).convert('RGBA'))
        assert art.shape==src.shape==(960,2240,4)
        assert np.array_equal(art[...,3],src[...,3])
        assert np.array_equal(art[...,:3],((src[...,:3].astype('uint16')*src[...,3:4]+127)//255).astype('uint8'))
        assert not art[:240,:320].any() and not art[-240:,-320:].any()
        assert len({hash_(art[i//7*240:(i//7+1)*240,i%7*320:(i%7+1)*320].tobytes()) for i in range(28)})>=24
        a=json.loads(cmd(('ffprobe','-v','error','-show_streams','-show_format','-of','json',q)))
        ar=a['streams'][0]; assert ar['codec_name']=='vorbis' and ar['channels']==2 and ar['sample_rate']=='44100'
        assert abs(float(a['format']['duration'])-1.4)<.005
        for f in (p,q):
            assert r['sha256'][f.name]==hash_(f.read_bytes())
            assert f.read_bytes()==(S/'game'/f.relative_to(U)).read_bytes()
        out.append(f"PASS {k:8s} : 320×240 × 28 comparées ; couleurs prémultipliées, alpha 0 aux bornes ; Ogg Vorbis stéréo 44,1 kHz, 1,40 s.")
    return '\n'.join(out)+'\n'


def patch_and_scope(paths):
    assert git('rev-parse','HEAD')==COMMIT and git('rev-parse','HEAD^')==BASE
    allowed=set(paths)
    actual=set(git('diff','--name-only',BASE,COMMIT).splitlines())
    assert actual==allowed and len(actual)==41
    v=git('bundle','verify',FILE_BUNDLE)
    # Isolated index only. A missing historical blob is not needed to re-hash
    # the untouched side of the sparse, promisor working tree.
    with tempfile.TemporaryDirectory(prefix='prebattle-patch-') as tmp:
        env={**os.environ,'GIT_NO_LAZY_FETCH':'1','GIT_INDEX_FILE':str(Path(tmp)/'index')}
        pre=(' -c',)  # apply through -c core.sparseCheckout=false below
        cfg=('-c','core.sparseCheckout=false')
        git(*cfg,'read-tree',BASE,env=env)
        patch=lzma.decompress(FILE_PATCH.read_bytes())
        git(*cfg,'apply','--cached','--binary','--check','-',env=env,input=patch)
        git(*cfg,'apply','--cached','--binary','-',env=env,input=patch)
        a=git(*cfg,'write-tree','--missing-ok',env=env)
        assert a==git('rev-parse',COMMIT+'^{tree}')
        git(*cfg,'apply','--cached','--binary','--reverse','-',env=env,input=patch)
        z=git(*cfg,'write-tree','--missing-ok',env=env)
        assert z==git('rev-parse',BASE+'^{tree}')
    return f'Base {BASE}\nCommit {COMMIT}\nPASS exact : base → {a} → {z}\n41 fichiers du delta ; aucun changement de carte, casting, ancien effet ou Méga.\n{v}\n'


def main():
    rows=data(U/'Index-Prebatailles.json'); assert len(rows)==18 and len({r['id'] for r in rows})==18
    assert len({v for r in rows for v in r['sha256'].values()})==36
    checks=banks(rows)
    paths=[f"game/Content/{folder}/{name}" for r in rows for folder,name in (('BG',r['atlas']),('Sound/Battle',r['son']))]
    paths+=['game/Data/Script/destiny/event.lua','game/Data/Script/destiny/dojo_kingambit_prebatailles.lua',
            'docs/KINGAMBIT_PREBATAILLES.md','tools/dessiner_prebatailles_kingambit.py','tools/tests/test_dojo_kingambit_prebatailles.lua']
    patch=patch_and_scope(paths)
    e={**os.environ,'LUA_PATH':str(S/'game/Data/Script/?.lua')+';;'}
    lua=''.join(cmd(('lua',S/'tools/tests'/f'test_dojo_kingambit_{s}.lua'),env=e).decode() for s in ('troupes','spawns_mega','prebatailles'))
    proof=data(B/'Controle-audiovisuel.json'); assert len(proof)==18 and min(p['correlation_son'] for p in proof)>.35
    j=(B/'Journal-PMDO.txt').read_text();assert j.count(' COMBAT ')==18 and j.count('map_clear_check')==18 and 'ALL DONE 18' in j
    md=json.loads(cmd(('ffprobe','-v','error','-show_format','-show_chapters','-show_streams','-of','json',VIDEO)))
    assert len(md['chapters'])==18 and {s['codec_type'] for s in md['streams']}>={'audio','video'}
    fusion=Path.home()/'Reference-Guildhouse/Mega-sans-colonnes/04-Eclipse-X-Prisme.mp4'
    reference=f'Méga validée : {fusion.name} (aperçu hors moteur ; conservé à part).\nSHA-256 : {hash_(fusion.read_bytes())}\n'
    pack={p:(S/p).read_bytes() for p in paths}
    pack.update({'Preuves/Controle-banques.txt':checks.encode(),'Preuves/Patch-aller-retour.txt':patch.encode(),
                 'Preuves/Tests-Lua.txt':lua.encode(),'Preuves/Reference-Mega-validee.txt':reference.encode(),
                 'Lisez-moi.md':(V/'Lisez-moi.md').read_bytes(),'Index-Prebatailles.json':(U/'Index-Prebatailles.json').read_bytes()})
    for p in (FILE_PATCH,FILE_BUNDLE,U/'Integration/Commit.txt'):pack['Integration/'+p.name]=p.read_bytes()
    for p in (B/'Planche-des-18-dans-PMDO.jpg',B/'Journal-PMDO.txt',B/'Controle-audiovisuel.json',B/'Captures.json'):
        pack['Preuves/'+p.name]=p.read_bytes()
    for p in sorted((V/'Sources').glob('*.py')):pack['Sources/'+p.name]=p.read_bytes()
    pack['MANIFESTE-SHA256.txt']=''.join(f'{hash_(content)}  {name}\n' for name,content in sorted(pack.items())).encode()
    temp=ZIP.with_suffix('.zip.tmp')
    with ZipFile(temp,'w',compression=ZIP_DEFLATED,compresslevel=6) as z:
        for name,content in sorted(pack.items()):z.writestr(name,content)
    with ZipFile(temp) as z:
        assert not z.testzip() and set(z.namelist())==set(pack)
        for name,content in pack.items():assert hash_(z.read(name))==hash_(content),name
    temp.replace(ZIP)
    (V/'SHA256SUMS.txt').write_text(''.join(f'{hash_(p.read_bytes())}  {p.name}\n' for p in (ZIP,VIDEO,V/'Lisez-moi.md')),encoding='utf-8')
    print(f'Pack contrôlé : {len(pack)} fichiers, {ZIP.stat().st_size:,} octets.')
    print(f"Vidéo native : 18 chapitres, {md['format']['duration']} s, {VIDEO.stat().st_size:,} octets.")


if __name__=='__main__':main()
