import cv2,numpy as np,json
from pathlib import Path
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parent
base=cv2.imread(str(R/'reverie-057-phase0.png'));small=cv2.resize(base,None,fx=.5,fy=.5,interpolation=cv2.INTER_AREA);rows=[]
for k in range(46,53):
 im=cv2.imread('/home/user/uploads/image-%d.png'%k);h,w=im.shape[:2]
 # Encre des annotations : couleurs saturées verte, cyan, magenta ou rouge.
 B,G,C=cv2.split(im); ink=((G>110)&(G>1.6*C)&(G>1.4*B))|((B>85)&(G>75)&(B>1.6*C)&(G>1.5*C))|((C>110)&(C>1.5*G)&(C>1.3*B))|((C>110)&(B>80)&(C>1.5*G)&(B>1.4*G))
 ink=cv2.dilate(ink.astype('uint8'),np.ones((7,7),np.uint8));mask=(1-ink)*255
 # Retirer bords et bandes d'interface, mais garder le décor non annoté.
 mask[:5,:]=0;mask[-15:,:]=0;mask[:,:4]=0;mask[:,-4:]=0
 vals=[]
 for scale in [1.8,2,2.2,2.5,3]:
  tw,th=round(w/scale*.5),round(h/scale*.5)
  if min(tw,th)<10:continue
  t=cv2.resize(im,(tw,th),interpolation=cv2.INTER_AREA);m=cv2.resize(mask,(tw,th),interpolation=cv2.INTER_NEAREST)
  res=cv2.matchTemplate(small,t,cv2.TM_CCORR_NORMED,mask=m);res=np.nan_to_num(res,nan=-1,posinf=-1)
  for _ in range(3):
   _,v,_,(x,y)=cv2.minMaxLoc(res);vals.append((float(v),scale,x*2,y*2,tw*2,th*2));cv2.rectangle(res,(max(0,x-80),max(0,y-80)),(x+80,y+80),-1,-1)
 vals.sort(reverse=True);rows.append({'image':k,'candidates':vals[:5]});print(k,vals[:2],flush=True)
(R/'localisation-46-52.json').write_text(json.dumps(rows,indent=2))
# Montage de diagnostic seulement, destiné à vérifier la localisation, pas une retouche.
out=Image.new('RGB',(900,7*220),'white');d=ImageDraw.Draw(out);big=Image.open(R/'reverie-057-phase0.png').convert('RGB')
for i,row in enumerate(rows):
 v,s,x,y,w,h=row['candidates'][0];a=Image.open('/home/user/uploads/image-%d.png'%row['image']).convert('RGB');a.thumbnail((435,185));b=big.crop((x,y,x+w,y+h));b=b.resize((b.width*2,b.height*2),Image.Resampling.NEAREST);b.thumbnail((435,185));y0=i*220;d.text((0,y0),f"image-{row['image']}  {v:.4f} echelle {s}, origine {x},{y}",fill='black');out.paste(a,(0,y0+22));out.paste(b,(460,y0+22))
out.save(R/'reperage-46-52.png')
