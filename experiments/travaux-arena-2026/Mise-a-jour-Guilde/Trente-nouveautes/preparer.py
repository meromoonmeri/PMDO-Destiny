from PIL import Image,ImageDraw
import numpy as np,json
from pathlib import Path
p=Path(__file__).resolve().parent
specs=[('banc-feuillage','Banc aux feuilles',56,38,False),('fauteuil-lierre','Fauteuil au lierre',32,42,False),('table-racines','Table aux racines',42,38,False),('pupitre-lecture','Pupitre de lecture',25,34,False),('bibliotheque','Bibliothèque de la Guilde',54,42,False),('etagere-graines','Étagère murale à graines',36,28,True),('coffre-feuille','Coffre aux feuilles',32,27,False),('armoire-nature','Armoire de la Guilde',36,46,False),('portemanteau-branche','Portemanteau branche',28,44,False),('panier-baies','Panier de baies',28,22,False),('jardiniere-bourgeons','Jardinière aux bourgeons',42,26,False),('fougere-en-pot','Fougère en pot',28,36,False),('pot-suspendu','Pot mural de lierre',27,36,True)]
out=[]
for i,(slug,label,w,h,wall) in enumerate(specs,1):
 im=Image.open(p/'source'/f'{i:02}.png').convert('RGBA');a=np.array(im); rgb=a[:,:,:3].astype(np.int16); bg=np.median(np.array([rgb[2,2],rgb[-3,2],rgb[2,-3],rgb[-3,-3]]),axis=0)
 dist=np.max(np.abs(rgb-bg),axis=2); mask=dist<45
 # Discard flat keyed backdrop including internal holes; maintain dark outlines.
 a[mask,3]=0; r,g,b=rgb.transpose(2,0,1); fringe=(r>100)&(b>85)&(r-g>60)&(b-g>45);a[fringe,3]=0;a[a[:,:,3]==0,:3]=0;im=Image.fromarray(a);box=im.getbbox();assert box; im=im.crop(box);im.thumbnail((w,h),Image.Resampling.NEAREST)
 canvas=Image.new('RGBA',(w,h));canvas.alpha_composite(im,((w-im.width)//2,h-im.height));canvas.save(p/f'{slug}.png')
 out.append({'id':'nouveau-guilde-'+slug,'label':label,'w':w,'h':h,'wall':wall,'file':slug+'.png'})
(p/'index.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
check=Image.new('RGB',(800,510),'#25243c');d=ImageDraw.Draw(check)
for j,item in enumerate(out):
 im=Image.open(p/item['file']);im.thumbnail((128,125),Image.Resampling.NEAREST);im=im.resize((im.width*2,im.height*2),Image.Resampling.NEAREST); x=(j%5)*160+80-im.width//2;y=(j//5)*170+12;check.paste(im,(x,y),im);d.text(((j%5)*160+5,y+125),f"{j+1}. {item['label']}",fill='white')
check.save(p/'catalogue-13.png')
