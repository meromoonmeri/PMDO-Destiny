#!/usr/bin/env python3
"""Contrôler le patch local puis produire l'archive de révision (pas de push)."""
from io import BytesIO
from pathlib import Path
from PIL import Image
from zipfile import ZipFile, ZIP_DEFLATED
import numpy as np
import hashlib, json, shutil, struct, subprocess as sp, re

O=Path(__file__).resolve().parents[1]
D=Path.home()/'.cache/spawns-kingambit'; S=D/'source'; T=D/'cyclones'; N=T/'natif'; I=T/'Integration'; P=T/'Preuves'
PREV=O.parent/'Kingambit-Spawns-Mega'/'Kingambit-Spawns-et-Mega.zip'
ANCHOR='be14e78c20567c2cff178a6eb03364f5d677578b'

def sha(b):return hashlib.sha256(b).hexdigest()

def git(*x):return sp.check_output(['git','-C',str(S),*x])

def valid():
    info=json.loads((T/'Index-Cyclones-Meteo.json').read_text());head=(I/'Commit.txt').read_text().strip()
    assert set(info)=={'flying','dragon','water','fire'} and git('rev-parse','HEAD').decode().strip()==head
    assert git('rev-parse',head+'^').decode().strip()==ANCHOR
    touched=set(git('diff','--name-only',ANCHOR,head).decode().splitlines())
    allowed={'game/Data/Script/destiny/dojo_kingambit_troupes.lua','tools/tests/test_dojo_kingambit_troupes.lua','tools/tests/test_dojo_kingambit_spawns_mega.lua'}
    report=[]
    for typ,a in info.items():
        assert sha((O/'Sources/dessins-generes'/a['dessin']).read_bytes())==a['dessin_sha256']
        for k,x in a['calques'].items():
            rel=Path(x['dossier'])/x['banque'];r=T/'Content'/rel.with_suffix('.dir');b=r.read_bytes();l,=struct.unpack_from('<q',b)
            allowed.add('game/Content/'+str(rel.with_suffix('.dir')))
            assert sha(b)==x['sha256'] and b==git('show',head+':game/Content/'+str(rel.with_suffix('.dir')))
            w,h=x['cellule_px'];n=x['poses'];nr=x['lignes'];nc=x['colonnes']
            assert n==(26 if k=='Ecran' else 24 if typ in ('dragon','flying') else 16)
            assert len(b)==l+24 and struct.unpack_from('<iiii',b,l+8)==(w,h,0,n)
            straight=np.array(Image.open(T/'Planches'/rel.with_suffix('.png')),dtype='uint16')
            native=np.array(Image.open(BytesIO(b[8:8+l])))
            assert native.shape==(h*nr,w*nc,4) and np.all(native[:,:,3]==straight[:,:,3])
            assert np.all(native[:,:,:3]==(straight[:,:,:3]*straight[:,:,3:4]+127)//255)
            def fr(i):return native[i//nc*h:(i//nc+1)*h,i%nc*w:(i%nc+1)*w,:]
            assert not fr(0).any() and not fr(n-1).any()
            assert len({sha(fr(i).tobytes()) for i in range(n) if fr(i).any()}) >= n-(6 if n==16 else 3)
            if typ in ('water','fire') and k=='Air':assert h==384 and fr(3)[0,:,3].max()>=150
            if k=='Ecran':assert x['dossier']=='BG' and (w,h)==(160,120) and native[:,:,3].max()<248
            report.append(f'PASS {typ}/{k} — {n} poses — {w}×{h} — alpha prémultiplié et début/fin transparents.')
    assert touched<=allowed and len(touched)>=12 and not any('/Data/Map/' in p or '/Data/Item/' in p for p in touched)
    with ZipFile(PREV) as prev:
        for n in prev.namelist():
            prefix='Mega/Addon/'
            if n.startswith(prefix) and not n.endswith('/'):
                p=D/'export/Mega/Addon'/n[len(prefix):];assert p.read_bytes()==prev.read(n),n
    report+=['PASS : aucun changement dans les cartes, les troupes, les objets, les quatorze autres banques ou l’addon Méga livré.']
    caps=json.loads((N/'Captures.json').read_text()); assert len(caps)==4
    for a in caps:
        txt=(N/(a['type']+'.journal.txt')).read_text()
        assert ('KINGAMBIT_QA end '+a['type']+' count=3') in txt and ('MEGA_FORM '+a['species']+' 1') in txt
        assert 3.5<a['mega']-a['action']<5.5
        report.append(f'PASS native 0.8.12 : {a["type"]}, 3 combattants, {a["stone"]}, forme 1 ({a["species"]}).')
        shutil.copy2(N/(a['type']+'.journal.txt'),P/(a['type']+'.journal.txt'))
    for fn,n in (('Apercu-Cyclones-Meteo-et-Mega.mp4',8),('Les-quatre-Mega-Evolutions.mp4',4)):
        doc=json.loads(sp.check_output(['ffprobe','-v','error','-show_chapters','-show_streams','-of','json',str(O/fn)]))
        assert len(doc['chapters'])==n and {'audio','video'}<={s['codec_type'] for s in doc['streams']}
    (P/'Contrôles.txt').write_text('\n'.join(report)+'\n',encoding='utf-8')
    shutil.copy2(N/'planche-native-finale.jpg',P/'Séquences-et-formes-Méga.jpg')
    print('\n'.join(report))

def main():
    valid(); files={}
    def add(p,name):
        assert p.is_file() and name not in files,(p,name)
        files[name]=p
    for k in ('Lisez-moi.md','Credits.md'):add(O/k,k)
    for k in ('Apercu-Cyclones-Meteo-et-Mega.mp4','Les-quatre-Mega-Evolutions.mp4'):add(O/k,'Apercus/'+k)
    add(T/'Index-Cyclones-Meteo.json','Index-Cyclones-Meteo.json')
    for k in ('Cyclones-Meteo.bundle','Cyclones-Meteo-depuis-Spawns-Mega.patch.xz','Commit.txt'):add(I/k,'Integration/'+k)
    for k in ('Content','Planches','Motifs-détourés','Preuves'):
        for p in (T/k).rglob('*'):
            if p.is_file():add(p,p.relative_to(T).as_posix())
    for p in (O/'Sources').rglob('*'):
        if p.is_file() and p.suffix in ('.py','.png'):add(p,p.relative_to(O).as_posix())
    manifest=''.join(f'{sha(p.read_bytes())}  {name}\n' for name,p in sorted(files.items()))
    zpath=O/'Kingambit-Cyclones-Meteo.zip';tmp=zpath.with_suffix('.tmp')
    with ZipFile(tmp,'w',ZIP_DEFLATED,compresslevel=7) as z:
        for name,p in sorted(files.items()):z.write(p,name)
        z.writestr('SHA256SUMS.txt',manifest)
    with ZipFile(tmp) as z:
        assert z.testzip() is None and len(z.namelist())==len(files)+1
        for row in manifest.splitlines():
            h,name=row.split('  ',1);assert sha(z.read(name))==h
    tmp.replace(zpath)
    check=O/'SHA256SUMS.txt';check.write_text(''.join(f'{sha(f.read_bytes())}  {f.name}\n' for f in sorted(O.iterdir()) if f.is_file() and f!=check))
    print('Archive vérifiée :',zpath,len(files)+1,'fichiers',zpath.stat().st_size,'octets')
if __name__=='__main__':main()
