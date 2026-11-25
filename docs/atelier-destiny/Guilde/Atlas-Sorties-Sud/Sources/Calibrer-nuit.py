#!/usr/bin/env python3
"""Only colour the 15 native rooms. Calibrate against paired Grodoudou renders.

The setup uses the same extracted references and 0.7.7 archives as the atlas
builder. The resulting LUTs/patches are embedded, so Assembler.py and the
HTML preview themselves do not require those archives or any network access.
"""
from pathlib import Path
from io import BytesIO
import base64
from collections import Counter
import hashlib
import json
import sys

import numpy as np
from PIL import Image
from scipy.ndimage import binary_dilation

H=Path.home();S=Path(__file__).resolve().parent;G=S.parent.parent
REF=H/'.cache/layouts-grodoudou-bois-destiny/refs'
A=H/'.cache/atelier-guilde'; WORK=H/'.cache/nuit-grodoudou'; WORK.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(A)); import preparer as source
from corriger import panes
from compacter import webp

PAIRS={
 'commune':('G01P04A','G01P04C'), 'maitre':('G01P05A','G01P05C'),
 'refectoire':('G01P06A','G01P06B'), 'equipe':('G01P07A','G01P07C'),
 'nord':('G01P09A','G01P09C'), 'sud':('G01P10A','G01P10C'),
}
MAP={
 'accueil':'commune','missions':'commune','grand_salon':'commune','bureau_maitre':'maitre',
 'carrefour':'commune','refectoire':'refectoire','cuisine':'refectoire','reserve':'refectoire',
 'couloir_ouest':'commune','couloir_est':'commune','dortoir_nord_1':'nord','dortoir_nord_2':'nord',
 'dortoir_sud_1':'sud','dortoir_sud_2':'sud','chambre_heros':'equipe',
}
BRUN=[104,72,47]

def read_json(p): return json.loads(p.read_bytes())
def pixels(f): return np.array(Image.open(f).convert('RGB'),dtype=np.int16)
def image(uri): return np.array(Image.open(BytesIO(base64.b64decode(uri.split(',',1)[1]))).convert('RGBA'))
def sample(u,xy):
 x,y,w,h=xy; return u[y:y+h,x:x+w]

def calibre(j,n,windows):
 """Robust per-channel affine match. Exclude glass and trim animated-light outliers."""
 day,night=pixels(REF/(j+'.png')),pixels(REF/(n+'.png'))
 keep=(day!=day[0,0]).any(2)&(night!=night[0,0]).any(2); glasses=[]
 for x0,y0,x1,y1 in windows:
  a=day[y0:y1,x0:x1,:]; b=night[y0:y1,x0:x1,:]; m=(a[...,0]>=235)&(a[...,1]>=210)&(a[...,2]>=145)
  glasses.extend(map(tuple,b[m]));keep[y0:y1,x0:x1]=False
 if glasses:
  glass=list(map(int,Counter(glasses).most_common(1)[0][0]));assert glass[2]>glass[1]>glass[0]
 else:glass=None
 x=day[keep].astype(float);y=night[keep].astype(float);rates=[];lut=[];error=[]
 for c in range(3):
  m=np.stack((x[:,c],np.ones(len(x))),axis=1);inliers=np.ones(len(x),bool)
  for _ in range(4):
   a,b=np.linalg.lstsq(m[inliers],y[inliers,c],rcond=None)[0]
   err=np.abs(y[:,c]-np.clip(m@[a,b],0,255));inliers=err<9
  assert 0.6<a<1.06 and -28<b<0 and np.percentile(err,90)<9.5,(j,c,a,b)
  curve=np.clip(np.rint(a*np.arange(256)+b),0,255).astype(np.uint8)
  error.append(round(float(np.median(np.abs(y[:,c]-curve[x[:,c].astype(np.int16)]))),2))
  rates.append([round(float(a),5),round(float(b),5)]);lut.append(curve.tolist())
 twilight=[lut[i][g] for i,g in enumerate(BRUN)];assert twilight[0]>twilight[1]>twilight[2]
 return dict(source=[j,n],lut=lut,verre=glass,fond=twilight),dict(source=[j,n],courbes=rates,erreur_mediane_RVB=error,verre_RGB=glass,fond_Nuit_RGB=twilight)

def recolor(layer,lut):
 y=layer.copy()
 for c in range(3):y[:,:,c]=lut[c][y[:,:,c]]
 return y

def main():
 file=G/'Guilde-Destiny-Toutes-les-Salles.html';s=file.read_text(encoding='utf-8')
 base=json.loads(s.split('<script id="donnees" type="application/json">',1)[1].split('</script>',1)[0]); data=json.loads(json.dumps(base))
 geom={r['id']:r for r in read_json(G/'Plans-Grodoudou-Bois-Destiny/Geometrie.json')}
 specs={};notes={}
 for key,(j,n) in PAIRS.items():
  specs[key],notes[key]=calibre(j,n,geom[j[:-1]]['vitres'])
  print(j,n,'· verre',specs[key]['verre'],'· fond brun',specs[key]['fond'],flush=True)
 data['nuits']=specs
 rd=source.loader();rd.ROOT=source.C;win=rd.fenetres();total=0;rooms=[]
 for r,a in zip(data['rooms'],base['rooms'],strict=True):
  name=r['id'];style=MAP[name.removeprefix('guilde_destiny_')];spec=specs[style]
  layer=image(r['base']);front=image(r['front']);lut=np.asarray(spec['lut'],dtype=np.uint8)
  shaded=recolor(layer,lut);new=shaded.copy();shape=shaded.shape[:2];mask=np.zeros(shape,bool)
  patches=[];proof_slots=[]
  for tag,x,y,w,h,names in win.get(name,[]):
   d,n=(np.asarray(source.image(rd.obj(names[p]),'jour')) for p in ('jour','nuit'))
   assert d.shape==n.shape==(h,w,4)
   m=panes(d,n);r0,g0,b0,alpha=d.astype(int).transpose(2,0,1);rr,gg,bb,aa=n.astype(int).transpose(2,0,1)
   # Include the darker one-pixel edge of some existing panes, not the wooden mullions.
   fringe=(r0>=165)&(g0>=135)&(b0>=78)&(r0-g0<=60)&(bb>=rr+13)&(bb>=gg+8)&(alpha==255)&(aa==255)
   q=(y,x); m=m|(binary_dilation(m)&fringe)
   roi=sample(layer,(x,y,w,h));m&=(np.abs(roi.astype(int)-d.astype(int)).max(2)<=1)
   assert m.sum()>500 and not sample(mask,(x,y,w,h))[m].any() and spec['verre'],(name,tag,m.sum())
   target=sample(new,(x,y,w,h));target[m,:3]=spec['verre'];sample(mask,(x,y,w,h))[m]=True
   yy,xx=np.where(m);y0,y1=yy.min()+y,yy.max()+y+1;x0,x1=xx.min()+x,xx.max()+x+1
   patch=new[y0:y1,x0:x1].copy();patches.append([int(x0),int(y0),webp(patch)])
   visible=int((m&(sample(front,(x,y,w,h))[...,3]==0)).sum());assert visible>300
   proof_slots.append(dict(nom=tag,pixels_verre=int(m.sum()),visibles=visible,zone=[int(x0),int(y0),int(x1-x0),int(y1-y0)]));total+=1
  assert len(patches)==r['fenetres'];assert np.array_equal(shaded[~mask],new[~mask]);assert np.array_equal(new[:,:,3],layer[:,:,3])
  assert np.array_equal(recolor(front,lut)[:,:,3],front[:,:,3]);assert new[0,0,:3].tolist()==spec['fond'],name
  r['nuit']=style;r['patches'][3]=patches
  assert {k:v for k,v in r.items() if k not in ('patches','nuit')}=={k:v for k,v in a.items() if k not in ('patches','nuit')}
  assert r['patches'][:3]==a['patches'][:3]
  rooms.append(dict(salle=name,palette=style,vitres=proof_slots,dimensions=[r['w'],r['h']],sud=r['south']))
 assert total==14 and len(rooms)==15;assert base['catalog']==data['catalog']
 m=json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')
 (WORK/'Donnees.json').write_text(m,encoding='utf-8')
 h=hashlib.sha256(s.encode('utf-8')).hexdigest(); (WORK/('Atlas-avant-'+h[:8]+'.html')).write_text(s,encoding='utf-8')
 rapport=dict(statut='PASS',palettes=notes,salles=rooms,total_fenetres=total,jour_aube_crepuscule='identiques',plan_et_cadrage_sud='identiques',fond='brun conservé, assombri par la courbe de la salle',jeu_modifie=False)
 (G/'Atlas-Sorties-Sud/Palette-nuit.json').write_text(json.dumps(rapport,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print('PASS · 15 salles et 14 fenêtres ; les autres ambiances, les seuils et les plans ne changent pas.')

if __name__=='__main__':main()
