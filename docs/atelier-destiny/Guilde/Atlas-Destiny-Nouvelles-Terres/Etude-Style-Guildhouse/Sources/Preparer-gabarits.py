#!/usr/bin/env python3
"""Geographical references only: align gifts from the image generator without importing foreign contours."""
from pathlib import Path
from PIL import Image
from scipy import ndimage as nd
import json,numpy as np
D=Path(__file__).resolve().parents[1];S=D/'Sources'; M=D.parent/'Terres-EoS-Magenta/Sources'
index=np.asarray(Image.open(M/'Index-terres-validees.png'));wet=np.asarray(Image.open(M/'Eaux-de-reference.png').convert('RGBA'));N=Image.Resampling.NEAREST
# Brush intent keyed to approved global anchors. No texture, landmarks or outside coast in these images.
catalog={
 'Seracine':(2,(688,344),2,(185,156,116),[(662,94,165,48,(216,229,233)),(596,138,113,46,(179,199,205)),(552,189,66,50,(116,145,112)),(794,186,88,29,(151,158,104)),(930,148,112,54,(207,164,105)),(883,242,72,48,(140,161,104)),(1042,197,45,49,(198,170,109))]),
 'Estrel':(3,(478,478),2,(201,174,107),[(746,415,83,71,(135,153,89)),(790,511,112,81,(118,152,93)),(758,568,72,72,(93,136,100)),(914,371,101,54,(222,201,140)),(1016,449,57,39,(201,175,109)),(963,565,75,74,(221,203,151)),(1020,594,39,38,(156,168,103)),(841,627,90,39,(180,151,98))]),
 'Torselune':(4,(468,312),2,(197,142,85),[(350,524,90,40,(174,109,63)),(417,477,45,24,(192,130,70)),(398,592,91,27,(152,156,91)),(541,557,83,31,(162,117,95)),(563,505,68,35,(183,106,75)),(457,644,73,41,(192,132,72)),(603,637,69,39,(226,198,135))]),
 'Reverie':(5,(216,216),4,(184,158,100),[(134,513,50,52,(119,157,91)),(150,487,55,26,(132,151,92)),(204,502,33,31,(195,182,120)),(105,563,36,40,(105,145,94)),(151,548,25,26,(150,164,91)),(194,588,57,41,(195,171,104)),(130,611,32,27,(191,173,116))]),
 'Les-Haltes':(6,(256,256),3,(198,167,101),[(497,260,38,26,(230,205,136)),(530,345,29,26,(202,155,88)),(602,410,43,39,(126,156,93)),(618,402,28,25,(176,173,111))]),
}
def bounds(m):
 y,x=np.where(m);return [int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)]
manifest={}
for name,(i,(W,H),zoom,base,fields) in catalog.items():
 m=index==i;x,y,u,v=bounds(m);w,h=u-x,v-y;Y,X=np.mgrid[y:v,x:u];mask=m[y:v,x:u];a=np.zeros((h,w,3),np.float32)+base
 for cx,cy,rx,ry,co in fields:
  f=np.clip(1.35-((X-cx)/rx)**2-((Y-cy)/ry)**2,0,.93)[...,None];a=a*(1-f)+f*co
 if name=='Reverie':
  # Soft warm clearing above the tree's foot at validated atlas point (150,551). No preview glyph.
  f=(np.clip(1-((X-146)/13)**2-((Y-542)/11)**2,0,1)*.38)[...,None];a=a*(1-f)+f*np.array([208,186,99])
 a=np.rint(a).astype('uint8');a[~mask]=(255,0,255);t=wet[y:v,x:u];a[(t[...,3]>0)&mask]=t[(t[...,3]>0)&mask,:3];dd=nd.distance_transform_edt(mask);a[(dd<=1.0)&mask&(t[...,3]==0)]=[108,78,47]
 ox=(W-w)//2;oy=(H-h)//2;im=Image.new('RGB',(W,H),(255,0,255));im.paste(Image.fromarray(a),(ox,oy));im.resize((W*zoom,H*zoom),N).save(S/f'{name}-Gabarit-geographique.png',optimize=True)
 manifest[name]={'index':i,'box':[x,y,u,v],'template_units':[W,H],'template_zoom':zoom,'template_land':[ox,oy,ox+w,oy+h]}
(D/'Sources'/'Gabarits.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
# Crop style cues from Gen 1 and the old repository. Deliberately do not use older coastlines as guides.
raw=Image.open(S/'Orival-genere.png').convert('RGB')
raw.crop((206,190,487,448)).save(S/'Orival-Detail-palette.png',optimize=True)
old=Image.open(Path.home()/'.cache/guildhouse-atlas-style/Neuf-continents-magenta-brut.png').convert('RGB');old.crop((193,656,357,711)).save(S/'Guildhouse-Detail-Neige.png',optimize=True);old.crop((576,114,732,232)).save(S/'Guildhouse-Detail-Dunes.png',optimize=True)
print(json.dumps(manifest,indent=1))
