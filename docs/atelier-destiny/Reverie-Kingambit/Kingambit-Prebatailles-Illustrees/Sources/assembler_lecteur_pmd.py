#!/usr/bin/env python3
"""Assemble la galerie locale et l'alternative d'essai, sans modifier Destiny."""
from __future__ import annotations
import argparse
from base64 import b64encode
from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256
import io
import json
from pathlib import Path
import shutil
import subprocess as sp
from zipfile import ZipFile, ZIP_DEFLATED, ZIP_STORED
from PIL import Image

HERE=Path(__file__).resolve().parent
FINAL=HERE.parent


def as_uri(b,mime):return 'data:'+mime+';base64,'+b64encode(b).decode('ascii')
def jsonread(p):return json.loads(p.read_text(encoding='utf-8'))


def media_for_viewer(clips,item):
    # Revenir aux vrais pixels 320x240 (fenêtre capturée à 2x) accélère le chargement
    # du lecteur hors ligne. Le ZIP, lui, conserve les captures à 640x480.
    web=clips/'Web';web.mkdir(exist_ok=True)
    source=clips/item['video'];out=web/item['video']
    sp.run(['ffmpeg','-nostdin','-hide_banner','-loglevel','error','-y','-threads','2','-i',str(source),
            '-vf','scale=320:240:flags=neighbor','-c:v','libx264','-threads','2','-preset','fast','-crf','23',
            '-maxrate','640k','-bufsize','950k','-pix_fmt','yuv420p','-c:a','aac','-b:a','88k',
            '-movflags','+faststart',str(out)],check=True)
    jpg=io.BytesIO()
    Image.open(clips/item['poster']).resize((320,240),Image.Resampling.NEAREST).save(jpg,format='JPEG',quality=84,optimize=True)
    return as_uri(out.read_bytes(),'video/mp4'),as_uri(jpg.getvalue(),'image/jpeg')


def build(galerie,banques,capture):
    rs=jsonread(galerie/'Capsules.json')
    assert [x['numero'] for x in rs]==list(range(19))
    assert len({x['image_source'] for x in rs[1:]})==12 and sum(x['adaptation'] for x in rs[1:])==6
    template=(HERE/'modele-lecteur-pmd.html').read_text(encoding='utf-8')
    po=[]
    with ThreadPoolExecutor(max_workers=3) as pool:
        rendered=list(pool.map(lambda r:media_for_viewer(galerie/'Clips',r),rs))
    for r,(movie,jpg) in zip(rs,rendered):
        item={x:r[x] for x in ('id','numero','type','boss','titre','note','couleur','duration','t_balayage','t_blanc','t_reprise')}
        for x in ('image_source','adaptation'):
            if x in r:item[x]=r[x]
        item['img']=jpg
        item['clip']=movie
        po.append(item)
    html=FINAL/'Voir-les-18-wooshes-PMD.html'
    payload=json.dumps(po,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')
    assert template.count('__CAPSULES__')==1
    html.write_text(template.replace('__CAPSULES__',payload),encoding='utf-8')

    qa=subprocess_check()
    checks=''.join(f"{x['type']} · blanc réel : {x['nb_images_blanches']} images à 30 i/s ; cue native r={x['correlation_woosh_natif']:.3f} ; "+
                   ('combat natif atteint\n' if x['passage_combat'] else 'référence arrêtée sur le blanc\n') for x in rs)
    pack={}
    for x in rs:
        pack['Apercus/'+x['video']]=(galerie/'Clips'/x['video']).read_bytes()
        if x['numero']==0:continue
        asset=(banques/'Content/BG'/x['texture']).read_bytes()
        assert sha256(asset).hexdigest()==x['sha256']
        pack['Variante-PMD/game/Content/BG/'+x['texture']]=asset
    pack['Variante-PMD/game/Data/Script/destiny/dojo_kingambit_prebatailles.lua']=(HERE/'dojo_kingambit_prebatailles.lua').read_bytes()
    pack['Lisez-moi.md']=(FINAL/'Lisez-moi.md').read_bytes()
    pack['Provenance-des-textures.json']=(banques/'Index-Illustrations.json').read_bytes()
    pack['Contrôles/Verification-image-son.txt']=checks.encode()
    pack['Contrôles/Mesures-et-index.json']=(galerie/'Capsules.json').read_bytes()
    pack['Contrôles/Journal-PMDO.txt']=(capture/'Journal-PMDO.txt').read_bytes()
    pack['Contrôles/Tests-Lua.txt']=qa
    pack['Contrôles/test_wooshes_pmd.lua']=(HERE/'test_wooshes_pmd.lua').read_bytes()
    pack['SHA256SUMS.txt']=''.join(f'{sha256(b).hexdigest()}  {k}\n' for k,b in sorted(pack.items())).encode()
    archive=FINAL/'Wooshes-PMD-par-type.zip'
    tmp=archive.with_suffix('.tmp')
    with ZipFile(tmp,'w') as z:
        for name,b in sorted(pack.items()):z.writestr(name,b,compress_type=ZIP_STORED if name.endswith('.mp4') else ZIP_DEFLATED)
    with ZipFile(tmp) as z:
        assert not z.testzip()
        assert set(z.namelist())==set(pack)
        for name,b in pack.items():assert sha256(z.read(name)).hexdigest()==sha256(b).hexdigest(),name
    tmp.replace(archive)
    shutil.copyfile(galerie/'Clips'/rs[0]['video'],FINAL/'Reference-PMDO.mp4')
    print(f'{len(rs)} clips vérifiés, galerie {html.stat().st_size:,} octets, archive {archive.stat().st_size:,} octets.')


def subprocess_check():
    return sp.check_output(['lua',str(HERE/'test_wooshes_pmd.lua'),str(HERE/'dojo_kingambit_prebatailles.lua')])


if __name__=='__main__':
    a=argparse.ArgumentParser(description=__doc__)
    for x in ('galerie','banques','capture'):a.add_argument('--'+x,required=True,type=Path)
    u=a.parse_args();build(u.galerie,u.banques,u.capture)
