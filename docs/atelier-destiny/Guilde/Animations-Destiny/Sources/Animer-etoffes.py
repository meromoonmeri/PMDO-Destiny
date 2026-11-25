#!/usr/bin/env python3
"""Animate the existing generated flag art at native pixel scale, without moving its hardware."""
from pathlib import Path
from io import BytesIO
import base64,hashlib,json
import numpy as np
from PIL import Image

S=Path(__file__).resolve().parent;O=S.parent;G=O.parent;W=Path.home()/'.cache/guilde-animee'
A=G/'Drapeaux-Destiny/PNG';OUT=O/'Etoffes-animees';NB=16;COLS=4
PAL=('miel','grenat','sauge','ardoise')
MOD=[(2,'hampe','Drapeau sur hampe',128),(3,'gonfanon','Gonfanon de cérémonie',184),(4,'fanions','Guirlande de fanions',161)]

def px(v):return np.clip(v,0,1)
def ease(v):a=px(v);return a*a*(3-2*a)

def turn(a,kind,t):
 h,w=a.shape[:2];y,x=np.indices((h,w),dtype=float)
 if kind=='hampe':
  amp=ease((x-14)/(w-16))*((y>=5)&(y<=39));amp[0:4]=0
  shiftx=-amp*(.52+.55*np.sin(t-x*.095-.7));shifty=amp*(2.45*np.sin(t-x*.095)+.32*np.sin(2*t+x*.07))
  tone=amp*(.024*np.sin(t-.125*x+1.0)-.012*np.sin(t-.16*x))
  still=(x<=14)|(y<5)|(y>39)
  max_jitter=3
 elif kind=='gonfanon':
  amp=ease((y-13)/43)*((x>=3)&(x<=41)&(y<62));amp[(y>=60)&(abs(x-(w/2))<3.8)]=0
  shiftx=amp*(1.75*np.sin(t-.22*y+.071*x));shifty=amp*.75*np.sin(t-.12*y-.23*x)
  tone=amp*.031*np.sin(t-.10*y+.21*x)
  still=(y<=13)|(y>=62)|((y>=60)&(abs(x-(w/2))<3.8));max_jitter=2
 else:
  top=(a[:,:,3]>0).argmax(0);local=y-top[None,:];above=local<=3
  # Six individual pennants. The cord and brass loops are not animated.
  edges=[11,29,49,69,89,109,129];centers=np.array([18,39,59,79,99,119]);i=np.clip(np.searchsorted(edges,x,side='right')-1,0,5);ph=i*1.19
  amp=ease((local-3)/15)*((x>11)&(x<129));shiftx=amp*1.65*np.sin(t+ph-.073*local);shifty=amp*(.85*np.cos(t+ph)+.025*(x-centers[i]))
  tone=amp*.028*np.sin(t+ph-.137*local);still=above|(x<=11)|(x>=129);max_jitter=2
 shifting=(np.abs(shiftx)>0.499)|(np.abs(shifty)>0.499);assert np.count_nonzero(shifting&~still)>10
 ix=np.rint(x-shiftx).astype(int);iy=np.rint(y-shifty).astype(int);valid=(ix>=0)&(ix<w)&(iy>=0)&(iy<h);out=np.zeros_like(a);out[valid]=a[iy[valid],ix[valid]]
 rgb=out[:,:,:3];rgb[:]=np.clip(np.rint(rgb.astype(float)*(1+tone[:,:,None])),0,255).astype(np.uint8);out[still]=a[still];out[out[:,:,3]==0]=0
 assert np.array_equal(a[still],out[still]);ma=a[:,:,3]>0;mb=out[:,:,3]>0;assert (mb&~ma).sum() < ma.sum()*.15
 shift=np.array([shiftx,shifty]);assert int(np.max(np.abs(np.rint(shift))))<=max_jitter
 return out, int((a!=out).any(2).sum())

def pack(im):
 b=BytesIO();im.save(b,'WEBP',lossless=True,method=6,exact=True);return 'data:image/webp;base64,'+base64.b64encode(b.getvalue()).decode('ascii')

def main():
 (OUT/'Planche-par-variante').mkdir(exist_ok=True,parents=True);(OUT/'Boucles-PNG').mkdir(exist_ok=True);entries=[];meta={}
 for num,key,name,ms in MOD:
  for col in PAL:
   id='destiny_'+key+'_'+col;fit=f'{num:02}-{key}-{col}.png';a=np.array(Image.open(A/fit).convert('RGBA'));h,w=a.shape[:2];rows=NB//COLS;sheet=Image.new('RGBA',(COLS*w,rows*h));frames=[];report=[]
   for i in range(NB):
    phase=2*np.pi*i/NB;q,changed=turn(a,key,phase);report.append(changed);im=Image.fromarray(q);frames.append(im);sheet.paste(im,((i%COLS)*w,(i//COLS)*h))
   assert len({im.tobytes() for im in frames})==NB
   f=OUT/'Planche-par-variante'/fit;sheet.save(f,optimize=True)
   frames[0].save(OUT/'Boucles-PNG'/fit,save_all=True,append_images=frames[1:],duration=ms,loop=0,disposal=0,blend=0,optimize=True)
   # Data URL is self-contained; no network calls or browser image-timing dependencies.
   entries.append(dict(id=id,nom=name,palette=col,carte='Planche-par-variante/'+fit,boucle_PNG='Boucles-PNG/'+fit,ms_par_image=ms,nombre_images=NB,origine_px=[0,0],empreinte=hashlib.sha256(f.read_bytes()).hexdigest(),rectangle_images=[[i%COLS*w,i//COLS*h,w,h] for i in range(NB)],pixels_animes_min=min(report),pixels_animes_max=max(report),support_fixe=True))
   meta[id]=dict(s=pack(sheet),n=NB,c=COLS,dt=ms)
   print(f'{name} · {col} · {NB} images · {ms*NB/1000:.2f}s · max {max(report)} pixels changés',flush=True)
 (OUT/'Index-etoffes.json').write_text(json.dumps(dict(statut='PASS',modeles=3,variantes=12,transparence=True,images=entries),indent=2,ensure_ascii=False)+'\n',encoding='utf-8');(W/'Etoffes.json').write_text(json.dumps(meta,separators=(',',':')),encoding='utf-8')
 print('PASS · trois modèles animés, douze variantes, cordes et supports fixes.',flush=True)
if __name__=='__main__':main()
