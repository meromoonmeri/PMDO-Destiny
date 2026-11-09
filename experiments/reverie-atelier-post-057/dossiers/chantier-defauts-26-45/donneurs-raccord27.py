from PIL import Image,ImageDraw,ImageFont
import cv2,numpy as np,json
P='audit-pixel-integral/';im=np.array(Image.open(P+'rendu-apres-trous.png').convert('RGB'));orig=np.array(Image.open('reference-Metano_Town_Trimmed.png').convert('RGB'));x,y,w,h=664,1776,24,40;target=im[y:y+h,x:x+w];mask=np.zeros((h,w,3),dtype=np.uint8);mask[:5,:,:]=255;mask[-5:,:,:]=255;mask[:,:4,:]=255;mask[:,-4:,:]=255;hits=[]
for name,a in [('Reverie',im),('Metano',orig)]:
 score=cv2.matchTemplate(a,target,cv2.TM_SQDIFF_NORMED,mask=mask);score=np.nan_to_num(score,nan=1,posinf=1,neginf=1)
 # Eliminer le candidat cible et éléments étrangers : dominance des couleurs d'herbe et de sable.
 for n in range(50):
  val,_,loc,_=cv2.minMaxLoc(score);dx,dy=loc
  if val>0.015:break
  crop=a[dy:dy+h,dx:dx+w];r,g,b=[crop[:,:,i].astype('int16') for i in range(3)];grass=(g>=r)&(g>170)&(b<130)&(r>140);sand=(r>220)&(g>135)&(g<225)&(b>70)&(b<165)
  if (grass|sand).mean()>.95 and not (name=='Reverie' and abs(dx-x)<40 and abs(dy-y)<60):hits.append((float(val),name,dx,dy))
  cv2.rectangle(score,(max(0,dx-32),max(0,dy-48)),(min(score.shape[1]-1,dx+32),min(score.shape[0]-1,dy+48)),1,-1)
hits=sorted(hits)[:30];print(hits)
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',13);board=Image.new('RGB',(5*160,((len(hits)+4)//5)*225),'#202020');d=ImageDraw.Draw(board)
for i,(v,name,x,y) in enumerate(hits):
 a=im if name=='Reverie' else orig;p=Image.fromarray(a[y-4:y+h+4,x-4:x+w+4]).resize((128,192),Image.Resampling.NEAREST);X=i%5*160;Y=i//5*225;board.paste(p,(X,Y+28));d.text((X,Y),f'{name} {x},{y}',font=font,fill='white');d.text((X,Y+13),f'{v:.5f}',font=font,fill='white')
board.save(P+'donneurs-raccord27.png');open(P+'donneurs-raccord27.json','w').write(json.dumps(hits))
