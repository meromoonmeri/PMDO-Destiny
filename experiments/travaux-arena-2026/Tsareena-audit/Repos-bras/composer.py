from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,hashlib
p=Path(__file__).parent;r=p.parent
configs=[('droite',r/'revision-corpulence/repos-trois-quart-01.png',[(350,525),(650,525),(700,625),(718,675),(710,736),(280,736),(280,680),(320,600)]),('gauche',r/'Huit-directions/avant-gauche.png',[(310,520),(615,520),(650,575),(680,660),(680,735),(245,735),(230,675),(255,625)])]
for name,src,poly in configs:
 a=Image.open(src).convert('RGB'); b=Image.open(p/f'repos-02-{name}-brut.png').convert('RGB');assert a.size==b.size
 m=Image.new('L',a.size,0);ImageDraw.Draw(m).polygon(poly,fill=255)
 out=Image.composite(b,a,m)
 aa=np.asarray(a);bb=np.asarray(b); rr,gg,bl=[bb[:,:,i].astype(int) for i in range(3)];Y,X=np.indices((a.height,a.width)); ar=aa[:,:,0].astype(int);ag=aa[:,:,1].astype(int);ab=aa[:,:,2].astype(int)
 bright=(Y>=640)&(Y<=810)&(ar>175)&(ag>175)&(ab>175)&(np.max(aa,axis=2).astype(int)-np.min(aa,axis=2).astype(int)<45)
 pink=(rr>95)&(rr>gg*1.35)&(rr>bl*1.15)
 outarray=np.array(out);outarray[bright&~pink]=aa[bright&~pink];out=Image.fromarray(outarray)
 out.save(p/f'repos-02-{name}-masque.png');m.save(p/f'masque-{name}.png')
 x=np.asarray(a);y=np.asarray(out);mask=np.asarray(m)>0;assert np.array_equal(x[~mask],y[~mask]);print(name,'pixels modifiés hors masque',np.any(x[~mask]!=y[~mask],axis=-1).sum())
