from PIL import Image,ImageDraw,ImageFont
import numpy as np,cv2
im=np.asarray(Image.open('reverie-055-phase0.png').convert('RGB'));met=np.asarray(Image.open('reference-Metano_Town_Trimmed.png').convert('RGBA'));target=im[2212:2216,1048:1104,:];out=[]
for name,a in [('Reverie',im),('Metano',met[:,:,:3])]:
 h,w=a.shape[:2];res=cv2.matchTemplate(a,target,cv2.TM_SQDIFF_NORMED)
 for y in range(12,h-4,8):
  for x in range(0,w-56,8):
   score=float(res[y,x]);
   if score>0.04:continue
   # Above 12 rows of target patch: enough grass and sand, a nonflat edge.
   p=a[y-12:y+4,x:x+56];R,G,B=[p[:,:,i].astype(int) for i in range(3)]
   grass=(G>R)&(G>170)&(B<130)&(R>140);sand=(R>230)&(G>165)&(G<225)&(B>90)&(B<165)
   if grass[:5].mean()<.30 or sand[-3:,12:44].mean()<.5 or sand[:5,10:46].mean()>.38:continue
   # Local top 16 rows have both colours and not many dark/foreign pixels.
   if (grass|sand).mean()<.70:continue
   if name=='Metano' and np.count_nonzero(met[y-12:y+4,x:x+56,3])<56*16*.98:continue
   out.append((score,name,x,y-12))
out=sorted(out)[:160];print('hits',len(out));
# Spatially suppress neighbours to show variety.
sel=[]
for hit in out:
 score,name,x,y=hit
 if any(n==name and abs(x-sx)<64 and abs(y-sy)<40 for _,n,sx,sy in sel):continue
 sel.append(hit)
 if len(sel)>=32:break
print(sel)
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',14);board=Image.new('RGB',(4*260,((len(sel)+3)//4)*180),'#202020');d=ImageDraw.Draw(board)
for i,(sc,name,x,y) in enumerate(sel):
 a=im if name=='Reverie' else met[:,:,:3];crop=Image.fromarray(a[max(0,y-12):y+36,x:x+56]).resize((224,192),Image.Resampling.NEAREST);bx=i%4*260;by=i//4*180;crop=crop.crop((0,0,224,152));board.paste(crop,(bx,by+25));d.text((bx,by+3),f'{name} {x},{y} {sc:.4f}',fill='white',font=font)
board.save('candidats-cap-haut.png')
