from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,cv2,json
R=Path(__file__).resolve().parent;O=R/'audit-pixel-integral';img=Image.open(O/'rendu-phase0.png').convert('RGBA');a=np.asarray(img);mask=(a[:,:,3]==0).astype('uint8');n,labels,stats,cent=cv2.connectedComponentsWithStats(mask,8)
items=[]
for k in range(1,n):
 x,y,w,h,num=map(int,stats[k]);items.append({'x':x,'y':y,'w':w,'h':h,'pixels':num,'boundary':x==0 or y==0 or x+w==1600 or y+h==4000})
print('Composantes',len(items),'pixels',int(mask.sum()),'limites',sum(z['pixels'] for z in items if z['boundary']),flush=True)
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',13);C=Image.new('RGB',(4*256,((len(items)+3)//4)*180),'#242424');d=ImageDraw.Draw(C)
for i,z in enumerate(items):
 x,y=z['x'],z['y'];box=(x-20,y-18,x+44,y+22);region=img.crop(box);check=Image.new('RGBA',region.size,(255,0,255,255));check.alpha_composite(region);p=check.convert('RGB').resize((256,160),Image.Resampling.NEAREST);bx=i%4*256;by=i//4*180;C.paste(p,(bx,by+20));d.text((bx+1,by+2),f"{x},{y} {z['w']}x{z['h']} ({z['pixels']} px)",font=font,fill='white')
C.save(O/'trous-candidats.png');(O/'trous-candidats.json').write_text(json.dumps(items,ensure_ascii=False,indent=2))
