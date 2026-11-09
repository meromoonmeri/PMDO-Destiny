from PIL import Image,ImageDraw,ImageFont
import numpy as np,cv2,math,json
im=np.array(Image.open('reverie-0.5.0-rendu-phase0.png').convert('RGB'));H,W=im.shape[:2];a=im.astype(np.float32);r,g,b=a[:,:,0],a[:,:,1],a[:,:,2];grass=(g>=r+1)&(g>=160)&(b<=135)&(r>=120);tiles=grass.reshape(H//8,8,W//8,8).mean(axis=(1,3));RGB=a.reshape(H//8,8,W//8,8,3).mean(axis=(1,3));cand=[]
# Carreaux entourés de quatre voisins d'herbe, différence de couleur forte.
for y in range(1,H//8-1):
 for x in range(1,W//8-1):
  if tiles[y,x]<.85 or min(tiles[y-1,x],tiles[y+1,x],tiles[y,x-1],tiles[y,x+1])<.85:continue
  v=RGB[y,x]; ns=RGB[[y-1,y+1,y,y],[x,x,x-1,x+1]];dist=np.linalg.norm(ns-v,axis=1)
  if dist.min()>5 and dist.mean()>9:cand.append((float(dist.min()),8*x,8*y,'tuile',float(dist.mean())))
# Segments rectilignes vert/vert aux limites de colonnes, sur 16 pixels et plus.
def seams(a,green,rotate=False):
 h,w=green.shape;out=[]
 for x in range(8,w-8,8):
  l=a[:,x-2:x,:].mean(axis=1);rr=a[:,x:x+2,:].mean(axis=1);near=(green[:,x-2:x].mean(axis=1)>.8)&(green[:,x:x+2].mean(axis=1)>.8);d=np.linalg.norm(l-rr,axis=1);mask=((d>11)&near).astype('uint8').reshape(1,-1);mask=cv2.morphologyEx(mask,cv2.MORPH_CLOSE,np.ones((1,3),np.uint8)).ravel();delta=np.diff(np.r_[0,mask,0].astype('int16'))
  for y,z in zip(np.where(delta==1)[0],np.where(delta==-1)[0]):
   if z-y>=16:
    score=float(d[y:z].mean())*math.sqrt(z-y)
    out.append((score,int(y+(z-y)//2) if rotate else x, x if rotate else int(y+(z-y)//2), 'horizontale' if rotate else 'verticale',int(z-y)))
 return out
cand+=seams(a,grass);cand+=seams(a.transpose(1,0,2),grass.T,True);cand.sort(reverse=True)
# Éviter des vignettes redondantes.
selected=[]
for p in cand:
 if all((p[1]-q[1])**2+(p[2]-q[2])**2>=50**2 for q in selected):selected.append(p)
print('bruts',len(cand),'groupes',len(selected),flush=True);json.dump([{'score':round(s,1),'x':x,'y':y,'type':t,'mesure':round(d,1)} for s,x,y,t,d in selected],open('audit-herbe-candidats.json','w'),indent=2)
f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',13);base=Image.fromarray(im)
for page in range(math.ceil(len(selected)/40)):
 o=Image.new('RGB',(5*220,8*202),'#202a2a');draw=ImageDraw.Draw(o)
 for i,(score,x,y,t,d) in enumerate(selected[page*40:(page+1)*40]):
  ox=(i%5)*220;oy=(i//5)*202;draw.text((ox,oy),f'{page*40+i+1}: ({x},{y}) {t[0]} {score:.0f}',font=f,fill='white');cro=base.crop((x-40,y-35,x+40,y+35)).resize((208,182),Image.Resampling.NEAREST);o.paste(cro,(ox,oy+18))
 o.save(f'audit-herbe-{page+1:02}.png')
