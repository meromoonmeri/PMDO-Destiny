#!/usr/bin/env python3
"""Keep the new generation's pixels and constrain the alpha to the approved coast."""
from pathlib import Path
from PIL import Image
from scipy import ndimage as nd
from hashlib import sha256
import numpy as np,json

root=Path(__file__).resolve().parents[1]; src=root/'Sources'; N=Image.Resampling.NEAREST
raw=Image.open(src/'Orival-genere.png').convert('RGB'); a=np.array(raw).astype(np.int16)
r,g,b=np.moveaxis(a,-1,0);key=(r>140)&(b>135)&(g<.63*np.minimum(r,b))&(np.abs(r-b)<109)
l,n=nd.label(~key); counts=np.bincount(l.ravel());counts[0]=0;main=l==counts.argmax()
y,x=np.where(main);bbox=(int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1));raw=raw.crop(bbox);m=main[bbox[1]:bbox[3],bbox[0]:bbox[2]]
img=Image.open(root.parent/'Terres-EoS-Magenta/Sources/Index-terres-validees.png'); ref=np.asarray(img)==1
y,x=np.where(ref); t=(int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)); c=ref[t[1]:t[3],t[0]:t[2]]
k=2;sz=(k*c.shape[1],k*c.shape[0]);mr=Image.fromarray(m.astype('uint8')*255)
a0=np.asarray(mr.resize((c.shape[1],c.shape[0]),N))>0;iou=float(np.count_nonzero(a0&c)/np.count_nonzero(a0|c));assert iou>.985
coast=np.repeat(np.repeat(c,k,axis=0),k,axis=1);a=np.array(raw.resize(sz,N));sample=np.asarray(mr.resize(sz,N))>0
r,g,b=np.moveaxis(a.astype(np.int16),-1,0);spill=(r>140)&(b>135)&(g<.63*np.minimum(r,b))&(abs(r-b)<109)
valid=sample&~spill;n2=nd.distance_transform_edt(~valid,return_indices=True,return_distances=False);fix=coast&~valid;a[fix]=a[n2[0][fix],n2[1][fix]]
z=np.zeros((*coast.shape,4),np.uint8);z[coast,:3]=a[coast];z[coast,3]=255
alpha=Image.fromarray(z);alpha.save(root/'Orival-Guildhouse-Transparent-2x.png',optimize=True)
tint=np.full(coast.shape+(3,),[255,0,255],np.uint8);tint[coast]=a[coast];assert np.array_equal(np.all(tint==[255,0,255],axis=-1),~coast)
out=Image.new('RGB',(sz[0]+68,sz[1]+68),(255,0,255));out.paste(Image.fromarray(tint),(34,34));out.save(root/'Orival-Guildhouse-Magenta.png',optimize=True)
assert np.array_equal(np.asarray(alpha.getchannel('A'))>0,coast)
assert np.array_equal(a[coast&valid],np.asarray(raw.resize(sz,N))[coast&valid])
rep={'statut':'PASS','place_sur_plan_atlas':[t[0],t[1]],'taille_plan_atlas':list(img.size),'region_boite_native':t,'alpha_2x':list(sz),'marge_apercu_px':34,'magenta':[255,0,255],
     'iou_silhouette_brute_une_fois_cadree':round(iou,6),'silhouette_livree_egale_au_masque_valide':True,'pixels_interieurs_remplis_au_raccord':int(fix.sum()),
     'rendus_interieurs':'pixels du générateur conservés par voisin le plus proche, sans filtre de grain ni recoloration','generation_sha256':sha256((src/'Orival-genere.png').read_bytes()).hexdigest()}
(root/'Verification-Orival.json').write_text(json.dumps(rep,ensure_ascii=False,indent=2)+'\n');print(rep)
