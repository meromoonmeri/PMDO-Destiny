#!/usr/bin/env python3
"""Day/intermediate lighting for the native atlas, with the approved night untouched.

Reads the Grodoudou reference atlas and the current Destiny HTML; no downloads.
Day: amber samples from paired interior art. Dusk: G01P01A→B facade transfer.
Dawn has no source map; it is a pale transition built from the same endpoint colours.
Only RGB curves and the already registered window panes are edited.
"""
from collections import Counter
from pathlib import Path
from io import BytesIO
import base64, copy, hashlib, json, re
import numpy as np
from PIL import Image

S=Path(__file__).resolve().parent;G=S.parent.parent;H=Path.home();W=H/'.cache/grodoudou-ambiances';W.mkdir(parents=True,exist_ok=True)
F=G/'Guilde-Destiny-Toutes-les-Salles.html'; REF=G.parent/'Reference-Guildhouse/Project-Pokemon/Guilde-de-Grodoudou.html'
BRUN=np.array([104,72,47]); VALEURS=np.arange(256); LUMA=np.array([.2126,.7152,.0722])

def catalogue_reference():
 out={}
 for f in re.findall(r'<figure\b[^>]*>.*?</figure>',REF.read_text(encoding='utf-8'),re.S):
  n=re.search(r'<figcaption><b>(G01P[0-9]+[ABC])\.png</b>',f);img=re.search(r'<img src="data:image/[^;]+;base64,([^"]+)',f)
  if n and img and 'APNG' not in f:
   pixels=np.array(Image.open(BytesIO(base64.b64decode(img[1]))).convert('RGB'),dtype=np.int16)
   # The index includes small detail crops as well as the full maps.
   if n[1] not in out or pixels.size>out[n[1]].size:out[n[1]]=pixels
 return out

def decode(s):return np.array(Image.open(BytesIO(base64.b64decode(s.split(',',1)[1]))).convert('RGBA'))
def encode(a):
 b=BytesIO();Image.fromarray(a).save(b,'WEBP',lossless=True,method=6,exact=True)
 encoded='data:image/webp;base64,'+base64.b64encode(b.getvalue()).decode('ascii');assert np.array_equal(decode(encoded),a)
 return encoded

def colour(layer,lut):
 out=layer.copy()
 for c in range(3):out[:,:,c]=lut[c,layer[:,:,c]]
 return out

def rounded(x):return np.rint(np.clip(x,0,255)).astype(np.uint8)
def contrast(x):return np.array(x,dtype=float)@LUMA

def decor_jour(a,wall,vitres):
 rr,gg,bb=a.transpose(2,0,1); yy,xx=np.indices(rr.shape); w=np.asarray(wall);depth=np.interp(xx,w[:,0],w[:,1]); f=(xx>w[0,0]+5)&(xx<w[-1,0]-5)&(yy<depth)&(yy>depth-62)
 f&=(rr>=205)&(gg>=95)&(bb>=32)&(rr-gg>=28)&(rr-gg<90)&(gg-bb>=29)&(gg-bb<100)
 assert f.sum()>100
 amber=rounded(np.median(a[f],axis=0)); lit=[]
 for x0,y0,x1,y1 in vitres:
  p=a[y0:y1,x0:x1];k=(p[...,0]>=235)&(p[...,1]>=210)&(p[...,2]>=145);lit.extend(map(tuple,p[k]))
 return amber,(np.array(Counter(lit).most_common(1)[0][0]) if lit else None)

def learn_facade(j,c):
 yy,xx=np.indices(j.shape[:2]);r,g,b=j.transpose(2,0,1)
 terrain=(yy>181)&(xx>103)&(xx<376)&(r>=130)&(r-g>=12)&(g-b>=18)&(r-g<110)&(g>=65)
 x,y=j[terrain],c[terrain]; coeff=[]
 for i in range(3):
  ma=np.stack([x[:,i],np.ones(len(x))],1);keep=np.ones(len(x),bool)
  for _ in range(4):
   s,t=np.linalg.lstsq(ma[keep],y[keep,i],rcond=None)[0];keep=np.abs((ma@[s,t])-y[:,i])<10
  coeff.append((float(s),float(t)))
 nuage=(yy<172)&(r>232)&(g>233)&(b>235)&(c[...,1]>130)&(c[...,2]>75)
 cloud=np.array(Counter(map(tuple,c[nuage])).most_common(1)[0][0]);sky=c[0,0].copy()
 assert sky.tolist()==[215,119,71] and cloud.tolist()==[215,151,87]
 return coeff,sky,cloud

def native_floor(d):
 spots=[]
 for r in d['rooms']:
  a=decode(r['base']);ys,xs=np.where(np.asarray([list(x) for x in r['floor']])=='1');u=a[ys*8+4,xs*8+4,:3].astype(int)
  r,g,b=u.T;m=(r>198)&(g>105)&(g<215)&(b>10)&(b<100)&(g-b>52)&(r-g>28);spots.extend(u[m])
 assert len(spots)>1000
 return rounded(np.median(spots,axis=0))

def phase_specs(nuit,amber,clear,native,facade,sky,cloud):
 night=np.asarray(nuit['lut'],dtype=float);target=rounded(native.astype(float)+.72*(amber.astype(float)-native))
 day=np.array([np.interp(VALEURS,[0,native[c],255],[0,target[c],255]) for c in range(3)])
 # Warm, slightly pastel early light. Less direct light than daytime; no historic Aube map.
 dawn=.73*day+.27*night+np.array([4,0,10])[:,None]*(VALEURS[None,:]/255.)**.55*(1-day/255.)
 # Transfer the orange exterior light, gently moderated for the wood inside.
 sun=np.array([np.minimum(day[c],a*day[c]+b*np.minimum(1,day[c]/96)) for c,(a,b) in enumerate(facade)])
 dusk=.82*(.50*day+.50*sun)+.18*night
 glass=[clear, (.62*clear+.38*cloud) if clear is not None else None, (.70*sky+.30*cloud) if clear is not None else None]
 phases=[];levels=[]
 for lut,glazing in zip([day,dawn,dusk],glass,strict=True):
  qt=rounded(lut);assert (np.diff(qt.astype(np.int16),axis=1)>=0).all()
  brown=qt[np.arange(3),BRUN].tolist();assert brown[0]>brown[1]>brown[2]
  levels.append(round(float(contrast(qt[np.arange(3),native])),1));phases.append(dict(lut=qt.tolist(),verre=rounded(glazing).tolist() if glazing is not None else None,fond=brown))
 levels.append(round(float(contrast(night[np.arange(3),native])),1));assert all(a>b for a,b in zip(levels,levels[1:])),levels
 return phases,levels,target.tolist()

def main():
 s=F.read_text(encoding='utf-8');d=json.loads(s.split('<script id="donnees" type="application/json">',1)[1].split('</script>',1)[0]);data=copy.deepcopy(d)
 refs=catalogue_reference(); geom={e['id']:e for e in json.loads((G/'Plans-Grodoudou-Bois-Destiny/Geometrie.json').read_bytes())};
 facade,sky,cloud=learn_facade(refs['G01P01A'],refs['G01P01B']);floor=native_floor(d)
 report_night=json.loads((G/'Atlas-Sorties-Sud/Palette-nuit.json').read_bytes());authority={r['salle']:r for r in report_night['salles']}
 data['lumieres']={};proof={};cases=[]
 for k,night in d['nuits'].items():
  origin=night['source'][0];g=geom[origin[:-1]];amber,clear=decor_jour(refs[origin],g['ligne_paroi'],g['vitres']);phases,levels,target=phase_specs(night,amber,clear,floor,facade,sky,cloud)
  data['lumieres'][k]=phases;proof[k]={'jour_source':origin,'ambre_source_RVB':amber.tolist(),'ambre_destiny_corrige_RVB':target,'luminosites_Jour_Aube_Crepuscule_Nuit':levels,'vitres':[p['verre'] for p in phases]+[night['verre']],'fonds_bruns':[p['fond'] for p in phases]+[night['fond']]}
  print(k,'· ambre',target,'· vitres',proof[k]['vitres'],'· lumière',levels,flush=True)
 count=0
 for r,a in zip(data['rooms'],d['rooms'],strict=True):
  style=r['nuit'];night=d['nuits'][style];base=decode(r['base']);notes=authority[r['id']]['vitres'];assert len(notes)==r['fenetres']==len(r['patches'][3]);slots=[]
  for (x,y,bit),note in zip(a['patches'][3],notes,strict=True):
   old=decode(bit);h,w=old.shape[:2];area=base[y:y+h,x:x+w].copy();same=(old[:,:,:3]==night['verre']).all(2)&(old[:,:,3]==255)
   shade=colour(area,np.asarray(night['lut'],dtype=np.uint8));assert (shade[~same]==old[~same]).all() and same.sum()==note['pixels_verre']
   slots.append((x,y,area,same,note));count+=1
  for i,p in enumerate(data['lumieres'][style]):
   deltas=[];lut=np.asarray(p['lut'],dtype=np.uint8)
   for x,y,area,m,note in slots:
    q=colour(area,lut);q[m,:3]=p['verre'];assert np.array_equal(q[:,:,3],area[:,:,3]);deltas.append([x,y,encode(q)])
   r['patches'][i]=deltas
  cases.append(dict(salle=r['id'],palette=style,vitres=[n for *_,n in slots],south=r['south']))
  assert r['patches'][3]==a['patches'][3] and {k:v for k,v in r.items() if k!='patches'}=={k:v for k,v in a.items() if k!='patches'}
 assert count==14 and len(cases)==15 and data['nuits']==d['nuits'] and data['catalog']==d['catalog']
 data['habillage']='Bois natif sans verdure · 4 lumières de Grodoudou · sorties sud corrigées sans rallonge'
 (W/'Donnees.json').write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('</','<\\/'),encoding='utf-8')
 h=hashlib.sha256(s.encode('utf-8')).hexdigest();(W/('Atlas-avant-'+h[:8]+'.html')).write_text(s,encoding='utf-8')
 report=dict(statut='PASS',jour='couleurs relevées sur les cartes claires de Grodoudou',aube='interprétée : transition pâle et pêche, sans carte originale',crepuscule='transfert de la façade G01P01A → G01P01B',nuit='identique à la version précédente',ambiances=proof,salles=cases,fenetres=count,facade_ciel_RVB=sky.tolist(),facade_nuage_RVB=cloud.tolist(),jeu_modifie=False)
 (G/'Atlas-Sorties-Sud/Palettes-ambiances.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print('PASS · 45 vues recolorées, 15 vues de nuit conservées ; aucune modification des chemins, du mobilier ou des seuils.')

if __name__=='__main__':main()
