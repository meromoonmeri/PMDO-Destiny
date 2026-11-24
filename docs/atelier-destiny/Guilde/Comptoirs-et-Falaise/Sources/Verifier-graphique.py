#!/usr/bin/env python3
"""Verify the pixel exports, original flame frames, and unmodified thresholds."""
from pathlib import Path
import json,hashlib,zlib
import numpy as np
from PIL import Image
from Falaise import O,P,A
from Flammes import BOX,ANCHOR,FIRE,FPS,ref,maskcolors
from Implantation import base,config

def arr(path):return np.array(Image.open(path).convert('RGBA'))

def check():
    lines=json.loads((O/'Index-Comptoirs.json').read_text())['orientations'];cases=json.loads((O/'Cases-Atlas.json').read_text());atlas=Image.open(O/'Atlas-Comptoirs-1x.png').convert('RGBA');seen=set();rect=[]
    assert atlas.size==(384,160)
    for k,v in enumerate(lines):
        n=O/v['png'];a=arr(n);assert (a.shape[1],a.shape[0])==(v['w'],v['h']);assert set(np.unique(a[...,3]))=={0,255}
        assert not np.any(a[a[...,3]==0][:,:3]) and not np.any((a[...,0]>170)&(a[...,1]<60)&(a[...,2]>170))
        h=hashlib.sha256(n.read_bytes()).hexdigest();assert h==v['sha256'];seen.add(h)
        x,y,w,h=cases[k]['rect'];assert cases[k]['direction']==v['direction'];b=np.array(atlas.crop((x,y,x+w,y+h)));assert np.array_equal(a,b)
        rect.append(cases[k]['rect']);assert cases[k]['pivot_dans_sprite']==v['pivot']
    assert len(seen)==8
    doc=base();_,stat=config(doc,lines);assert stat==json.loads((O/'Implantations.json').read_text())
    data=json.loads((O/'Releve-Cliff.json').read_text());assert hashlib.sha256(ref.read_bytes()).hexdigest()==data['source_nuit']['sha256']
    source=Image.open(ref);phases=[]
    for j in range(4):source.seek(j);phases.append(np.array(source.convert('RGB')))
    verified=[]
    for side,entry in enumerate(data['trépieds']):
        q=entry['cote'];loop=Image.open(O/'Braseros'/f'{q}-boucle-nuit.png');assert loop.n_frames==4 and loop.info['loop']==0
        png0=arr(O/'Braseros'/f'{q}-eteint.png');assert not (maskcolors(png0[...,:3],FIRE)&(png0[...,3]>0)).any()
        for k in range(4):
            a=arr(O/'Braseros'/f'{q}-nuit-{k+1}.png');loop.seek(k);assert abs(loop.info['duration']-1000/FPS)<1e-7 and np.array_equal(a,np.array(loop.convert('RGBA')))
            x,y,r,b=BOX[side];expected=phases[k][y:b,x:r];orig=maskcolors(expected,FIRE)&(np.arange(y,b)[:,None]<129)
            copy=np.zeros((b-y,r-x,4),dtype='uint8');ax,ay=map(lambda j:ANCHOR[side][j]-entry['pied_dans_image_nuit'][j],[0,1]);copy[ay:ay+a.shape[0],ax:ax+a.shape[1]]=a
            fire=maskcolors(copy[...,:3],FIRE)&(copy[...,3]>0);assert np.array_equal(orig,fire) and np.array_equal(copy[fire,:3],expected[orig]);verified.append(int(fire.sum()))
    for p in P:
        src=Image.open(O/'Falaise'/f'Cliff-{p}-sans.png').convert('RGBA');assert src.size==(480,520)
        for i,(x,y,file) in enumerate(data['calques'][p]):
            overlay=Image.open(O/'Falaise/Calques'/file).convert('RGBA');res=src.copy();res.alpha_composite(overlay,(x,y)); img=arr(O/'Falaise'/(f'Cliff-nuit-{i+1}.png' if p=='nuit' else f'Cliff-{p}.png'))
            assert np.array_equal(img,np.array(res));mask=(img!=np.array(src)).any(axis=2)
            assert not any((mask[:228].any(),mask[346:].any(),mask[:,218:263].any())) and mask.any()
    prov=json.loads((O/'Provenance-cliff.json').read_text())['fichiers'];assert len(prov)==39
    for q in prov:
        blob=(A/q['fichier']).read_bytes();assert len(blob)==q['octets'] and f'{zlib.crc32(blob):08x}'==q['crc32'] and hashlib.sha256(blob).hexdigest()==q['sha256']
    assert all(all(v==0 for v in tags) for tags in data['sol_aux_pieds_et_axe_central'].values())
    report={'statut':'PASS','png_rgba_1x':len(seen),'atlas_conforme':True,'exemples_validés':len(stat),'pixel_de_flamme_identiques_par_pose':verified,'duree_exacte_par_pose_secondes':'1/6','rendus_cliff':7,'lumieres_locales_sans_affecter_porte_mer_ciel':True,'sol_et_passage_cliff_intacts':True,'ressources_cliff_verifiees':len(prov)}
    (O/'Verification-graphique.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(f'PASS · {len(seen)} images PNG + atlas, {len(stat)} poses, {sum(verified)} pixels de flamme vérifiés et 39 ressources authentifiées.')

if __name__=='__main__':check()
