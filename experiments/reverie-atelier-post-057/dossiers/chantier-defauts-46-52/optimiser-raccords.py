from PIL import Image,ImageDraw
import numpy as np
im=np.array(Image.open('reverie-057-phase0.png').convert('RGBA'));cl=np.array(Image.open('calques/02_Cliffs.png').convert('RGBA'))[:,:,3];idx=np.arange(80);s=im[1074:1118,764:844][:,np.where(idx<40,idx+8,idx-8)];base=im.copy();mask=cl[586:630,1412:1492]==0;base[586:630,1412:1492][mask]=s[mask];met=np.array(Image.open('/home/user/chantier-chemins-reverie/metano-reference-sol-falaises.png').convert('RGBA'))
boxes=[(1380,604,1440,648),(1466,604,1544,648)];results=[]
for (x0,y0,x1,y1),dxs,dys in [(boxes[0],range(166,190),range(6,25)),(boxes[1],range(180,204),range(16,40))]:
 target=base[y0:y1,x0:x1].astype(np.int16);h,w=target.shape[:2];mask=np.zeros((h,w),bool);mask[0,:]=True;mask[-1,:]=True;mask[:,0]=True;mask[:,-1]=True
 vals=[]
 for dx in dxs:
  for dy in dys:
   src=met[y0-dy:y1-dy,x0-dx:x1-dx].astype(np.int16)
   if src.shape!=target.shape:continue
   delta=np.abs(src[:,:,:3]-target[:,:,:3]).mean(2); score=delta[mask].mean();vals.append((score,dx,dy))
 vals.sort();results.append(vals);print('best',vals[:15])
for j in range(8):
 out=base.copy();chosen=[]
 for box,vals in zip(boxes,results):
  score,dx,dy=vals[j];chosen.append((round(score,2),dx,dy));x0,y0,x1,y1=box;out[y0:y1,x0:x1]=met[y0-dy:y1-dy,x0-dx:x1-dx]
 a=Image.fromarray(out).crop((1368,580,1560,665)).resize((960,425),Image.Resampling.NEAREST);d=ImageDraw.Draw(a);d.text((2,2),str(chosen),fill='black');a.save('optimisation-arrondi51-'+str(j)+'.png')
