#!/usr/bin/env python3
"""Grand costume de Mimiqui : 120 poses et fiche de banc V4."""
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,cv2,struct,io,math,json
H=Path.home();G=H/'.cache/destiny-test/game/PMDO-Destiny';P=H/'Capacites-Z/Prototypes/Patati-Patattrape/Generation-PMDO';V=P/'V4';N=128;T=120
im=Image.open(V/'Sources/grand-deguisement.png').convert('RGB');a=np.asarray(im);r,g,b=[a[:,:,i].astype('int16') for i in range(3)];m=(g>48)&(g>r*1.15)&(g>b*1.15);s=Image.fromarray(np.dstack((a,(~m).astype('uint8')*255)),'RGBA');s=s.crop(s.getbbox()).resize((84,104),Image.Resampling.NEAREST);src=np.asarray(s)
def native(n):
 b=(G/'Content/Particle'/f'{n}.dir').read_bytes();k=struct.unpack_from('<q',b)[0];im=Image.open(io.BytesIO(b[8:8+k])).convert('RGBA');w,h,_,c=struct.unpack_from('<iiii',b,8+k);return [im.crop((i*w,0,(i+1)*w,h)) for i in range(c)]
smoke=native('Smoke_Purple');star=native('Lucky_Chant_Star_Yellow')
def paste(f,im,x,y,alpha=1):
 im=im.copy()
 if alpha<1: im.putalpha(im.getchannel('A').point(lambda q:round(q*max(0,alpha))))
 f.alpha_composite(im,(round(x-im.width/2),round(y-im.height/2)))
frames=[]
for t in range(T):
 f=Image.new('RGBA',(N,N));d=ImageDraw.Draw(f)
 enter=min(1,(t+1)/15); end=min(1,(T-t)/12)
 # Ombre vivante sous le déguisement, lueurs mauves, et absence de cible.
 if t<111:
  d.ellipse((26,79,102,103),fill=(8,3,15,round(245*end)),outline=(100,42,137,round(235*end)),width=2)
  for j in range(5):
   age=(t+j*7)%27;x=37+j*13+4*math.sin(t*.18+j);y=91-age*.55;v=smoke[min(len(smoke)-1,age//3)].resize((15,15),Image.Resampling.NEAREST);paste(f,v,x,y,.42*end)
 # Le costume descend, s'étend, se referme puis gigote comme s'il contenait la cible.
 if t<108:
  amp=1 if 20<=t<91 else .32
  yy,xx=np.indices((104,84),dtype=np.float32)
  lower=np.clip((yy-20)/84,0,1)
  mx=xx+(1.0+4.4*amp*lower)*np.sin(yy*.095+t*.42)+1.5*amp*np.sin(t*.19)
  my=yy+2.2*amp*lower*np.sin(xx*.16+t*.35)
  deformed=Image.fromarray(cv2.remap(src,mx.astype('float32'),my.astype('float32'),cv2.INTER_NEAREST,borderMode=cv2.BORDER_CONSTANT,borderValue=(0,0,0,0)),'RGBA')
  scale=.67+.33*enter; squash=1+(.06*math.sin((t-20)*.55) if 20<=t<91 else 0);w=round(84*scale*squash);h=round(102*scale/squash);deformed=deformed.resize((w,h),Image.Resampling.NEAREST)
  x=64+(3*math.sin(t*.5) if 20<=t<91 else 0);y=57-23*(1-enter)+(2*math.sin(t*.7) if 20<=t<91 else 0);fade=min(1,(108-t)/9)
  paste(f,deformed,x,y,fade)
 # Impacts graphiques synchronisés aux secousses, sans dégâts additionnels.
 if 32<=t<91:
  for j in range(2):
   age=(t-32-j*12)%25
   if age<15:
    v=star[min(len(star)-1,age//2)].resize((13,13),Image.Resampling.NEAREST);paste(f,v,25+j*78,57+math.sin(t*.2+j)*8,min(1,(15-age)/4))
 frames.append(f)
sheet=Image.new('RGBA',(N*8,N*15));bank=Image.new('RGBA',(N*T,N*8))
for i,f in enumerate(frames):
 sheet.alpha_composite(f,((i%8)*N,(i//8)*N))
 for j in range(8):bank.alpha_composite(f,(i*N,j*N))
sheet.save(V/'Patati-V4-grand-costume-120images.png',optimize=True);b=io.BytesIO();bank.save(b,format='PNG',optimize=True);raw=b.getvalue();(V/'PatatiV4_Costume.dir').write_bytes(struct.pack('<q',len(raw))+raw+struct.pack('<iiii',N,N,4,T))
z=json.loads((P/'V3/lets_snuggle_forever-v3-test-only.json').read_text());d=z['Object']['Data'];d['BeforeHits'][0]['Value']['Script']='PatatiV4_Costume';d['OnHits'][-1]['Value']['Script']='PatatiV4_ChanceKO';(V/'lets_snuggle_forever-v4-test-only.json').write_text(json.dumps(z,ensure_ascii=False,indent=2));print('Costume animé de 120 images, banque et fiche V4 préparés.')
