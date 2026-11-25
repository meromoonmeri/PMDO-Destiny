#!/usr/bin/env python3
"""Build atlases and browser catalog, then validate every export before packaging."""
from pathlib import Path
from zipfile import ZipFile, ZIP_STORED, ZIP_DEFLATED
from collections import Counter
from hashlib import sha256
import csv
import json
import shutil
import numpy as np
from PIL import Image
from Produire import ROOT,W,DIRS, js,decode,trim,png,digest

S=Path(__file__).resolve().parent
K=W/'Kit'
INDEX='Index-PMU-8.json'
ZIP=ROOT/'Kit-Destiny-PMU-8-orientations.zip'


def stage():
    D=json.loads((K/INDEX).read_text());assert D['nombre']==360 and D['nombre_de_png']==2880
    atlas=K/'Atlas-4x2';atlas.mkdir(exist_ok=True)
    reader=[]
    for r in D['objets']:
        vv=r['vues'];mx=max(0,*[a['pivot'][0] for a in vv])+2;my=max(0,*[a['pivot'][1] for a in vv])+2
        w=max(a['taille'][0]-a['pivot'][0] for a in vv)+mx+2;h=max(a['taille'][1]-a['pivot'][1] for a in vv)+my+2
        a=Image.new('RGBA',(4*w,2*h));compact=[]
        for i,q in enumerate(vv):
            x=w*(i%4)+mx-q['pivot'][0];y=h*(i//4)+my-q['pivot'][1];p=Image.open(K/q['fichier']).convert('RGBA')
            assert x>=w*(i%4)+2 and y>=h*(i//4)+2 and x+p.width<=w*(i%4+1)-2 and y+p.height<=h*(i//4+1)-2
            a.paste(p,(x,y));q['rectangle_atlas']=[x,y,p.width,p.height]
            compact.append([q['fichier'],p.width,p.height,*q['pivot']])
        ap=atlas/(r['repere']+'-8.png');b=png(np.asarray(a));ap.write_bytes(b)
        ff=ap.relative_to(K).as_posix();r['atlas']={'fichier':ff,'taille':list(a.size),'grille':[4,2],'cellule':[w,h],'pivot_case':[mx,my],'sha256':digest(b)}
        reader.append({'id':r['id'],'code':r['repere'],'nom':r['nom'],'prov':'new' if r['nouvelle_generation'] else 'ai' if r['ia_existante'] else 'pmu','methode':r['reconstruction']['methode'],'collection':r['collection'],'famille':r['famille'],'frame':[w,h,mx,my],'vues':compact,'atlas':ff})
    js(K/INDEX,D)
    with (K/'Index-PMU-8.csv').open('w',encoding='utf-8-sig',newline='') as f:
        cw=csv.writer(f,delimiter=';');cw.writerow(['Code','Objet','Famille','Catégorie','Orientation','PNG','Largeur','Hauteur','Pivot X','Pivot Y','Atlas PNG','Atlas X','Atlas Y','Pivot case X','Pivot case Y'])
        for r in D['objets']:
            for v in r['vues']:
                a=r['atlas'];cw.writerow([r['repere'],r['nom'],r['famille'],r['collection'],v['direction'],v['fichier'],*v['taille'],*v['pivot'],a['fichier'],*v['rectangle_atlas'][:2],*a['pivot_case']])
    content=(S/'Catalogue.html').read_text().replace('/* STYLES_AUTONOMES */',(S/'Catalogue.css').read_text()).replace('/* LOGIQUE_AUTONOME */',(S/'Catalogue.js').read_text())
    (K/'Catalogue.html').write_text(content.replace('DONNEES_COMPACTES',json.dumps({'projection':D['projection'],'objets':reader},ensure_ascii=False,separators=(',',':')).replace('</','<\\/')))
    for p in ('Lisez-moi.md','Inventaire-sources-PMU.csv'):shutil.copyfile(ROOT/p,K/p)
    return D


def verify(D):
    inv=json.loads((ROOT/'Inventaire-sources-PMU.json').read_text());original={r['id']:r for r in inv['objets']}
    seen=set();refs=set();dupes=[];numbers=Counter();offset=[]
    for r in D['objets']:
        assert r['id'] not in seen;seen.add(r['id']);files=r['vues']
        assert [v['direction'] for v in files]==list(DIRS)
        assert len(set(q['fichier'] for q in files))==8;assert not refs&{q['fichier'] for q in files};refs.update(q['fichier'] for q in files)
        if r['id'] in original:
            a,rx,ry=trim(decode(original[r['id']]),0);b=np.asarray(Image.open(K/files[0]['fichier']).convert('RGBA'));assert np.array_equal(a,b),r['id']
            assert [rx,ry,a.shape[1],a.shape[0]]==r['source']['coupe_down']
        else:assert r['nouvelle_generation']
        a=r['atlas'];ap=K/a['fichier'];assert digest(ap.read_bytes())==a['sha256']
        am=np.asarray(Image.open(ap).convert('RGBA'));mask=np.zeros(am.shape[:2],bool)
        cw,ch=a['cellule'];mx,my=a['pivot_case'];hashes=[]
        for i,v in enumerate(files):
            p=K/v['fichier'];b=p.read_bytes();assert digest(b)==v['sha256'];hashes.append(v['sha256'])
            im=Image.open(p);assert list(im.size)==v['taille'] and im.mode=='RGBA';im=np.asarray(im);assert np.any(im[:,:,3]>0)
            assert not np.any(im[im[:,:,3]==0,:3]);x,y,w,h=v['rectangle_atlas'];px,py=v['pivot']
            assert np.array_equal(am[y:y+h,x:x+w],im) and not mask[y:y+h,x:x+w].any()
            assert [x+px,y+py]==[cw*(i%4)+mx,ch*(i//4)+my];mask[y:y+h,x:x+w]=True
            if not 0<=px<w or not 0<=py<h:offset.append((r['repere'],v['direction']))
        assert not am[~mask,3].any()
        if len(set(hashes))<8:dupes.append({'code':r['repere'],'vues_distinctes':len(set(hashes))})
        numbers['Créations inédites' if r['nouvelle_generation'] else 'Créations existantes' if r['ia_existante'] else 'PMU 0.7.7']+=1
    assert original.keys()<=seen and numbers=={'PMU 0.7.7':346,'Créations existantes':10,'Créations inédites':4};assert len(refs)==2880
    assert set(p.relative_to(K).as_posix() for p in (K/'PNG').glob('*/*.png'))==refs
    assert len(list((K/'Atlas-4x2').glob('*.png')))==360
    with (K/'Index-PMU-8.csv').open('r',encoding='utf-8-sig') as f:assert sum(1 for r in csv.reader(f,delimiter=';'))==2881
    report={'statut':'PASS','sources_par_provenance':dict(numbers),'vues_png':len(refs),'atlases_png':len(seen),'ordre_direction_verifie':list(DIRS),'sources_down_verifiees_pixel_par_pixel':len(original),'sha256_png_et_rectangles_atlas_verifies':len(refs),'gabarits':D['methodes'],'symetries_exactes':dupes,'pivots_en_dehors_du_png_detoure':len(offset),'note':'Les contrôles de pixels et d’emprise ne garantissent pas que les dos reconstitués soient les dos des objets originaux.'}
    js(K/'Verification-graphique.json',report);print(f"PASS · {len(refs)} PNG, 360 atlas, 356 Down conformes et 2 880 pivots d’atlas.",flush=True)
    return report


def archive():
    order=['Catalogue.html','Lisez-moi.md','Index-PMU-8.csv','Index-PMU-8.json','Inventaire-sources-PMU.csv','Verification-graphique.json']
    order+=[p.relative_to(K).as_posix() for p in sorted((K/'Atlas-4x2').glob('*.png'))]+[p.relative_to(K).as_posix() for p in sorted((K/'PNG').glob('*/*.png'))]
    assert len(order)==3246
    with ZipFile(ZIP,'w',allowZip64=False) as z:
        for x in order:z.write(K/x,x,compress_type=ZIP_STORED if x.endswith('.png') else ZIP_DEFLATED,compresslevel=8)
    with ZipFile(ZIP) as z:assert z.testzip() is None and len(set(z.namelist()))==3246
    for n in ('Verification-graphique.json','Index-PMU-8.csv'):shutil.copyfile(K/n,ROOT/n)
    # The full JSON is in the ZIP; the small CSV remains easy to preview directly.
    print(f'{ZIP.name}: {ZIP.stat().st_size:,} octets · {len(order)} fichiers',flush=True)

if __name__=='__main__':
    D=stage();verify(D);archive()
