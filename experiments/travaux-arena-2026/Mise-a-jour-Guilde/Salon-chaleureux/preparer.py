from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json
p=Path(__file__).resolve().parent
specs=[('01-table','table-repas','Table de repas en bois',88,48,'meubles',False),('02-banc','banc-repas','Banc de réfectoire',60,22,'meubles',False),('03-chaise','tabouret-repas','Tabouret vert',22,20,'meubles',False),('04-buffet','buffet-vaisselle','Buffet et vaisselle',54,40,'meubles',False),('05-vaisselle','etagere-vaisselle','Étagère murale de vaisselle',38,25,'panneaux',True),('06-bois','panier-buches','Panier à bûches',24,22,'meubles',False),('07-tapis','tapis-chaleureux','Tapis du réfectoire · Emblème',90,48,'tapis',False),('08-the','plateau-the','Plateau de thé',24,17,'meubles',False)]
manifest=[]
for file,slug,label,w,h,category,wall in specs:
 im=Image.open(p/'source'/f'{file}.png').convert('RGBA');a=np.array(im);rgb=a[:,:,:3].astype('int16');r,g,b=rgb.transpose(2,0,1);bg=np.median([rgb[2,2],rgb[2,-3],rgb[-3,2],rgb[-3,-3]],axis=0);distance=np.max(np.abs(rgb-bg),axis=2);mask=(distance<45)|((r>100)&(b>85)&(r-g>60)&(b-g>45));a[mask]=[0,0,0,0];im=Image.fromarray(a);im=im.crop(im.getbbox());im.thumbnail((w,h),Image.Resampling.NEAREST);can=Image.new('RGBA',(w,h));can.alpha_composite(im,((w-im.width)//2,h-im.height));can.save(p/f'{slug}.png');manifest.append({'id':'refectoire-chaleureux-'+slug,'label':label,'w':w,'h':h,'category':category,'wall':wall,'file':slug+'.png'})
(p/'index.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2));check=Image.new('RGB',(800,340),'#25243c');d=ImageDraw.Draw(check)
for j,item in enumerate(manifest):
 im=Image.open(p/item['file']);im.thumbnail((140,110),Image.Resampling.NEAREST); im=im.resize((im.width*2,im.height*2),Image.Resampling.NEAREST); x=(j%4)*200+100-im.width//2;y=(j//4)*170+3;check.paste(im,(x,y),im);d.text(((j%4)*200+4,y+130),item['label'],fill='white')
check.save(p/'catalogue.png')
