#!/usr/bin/env python3
"""Essai de grille levante hors moteur, depuis la proposition générée."""
from pathlib import Path
from PIL import Image
import numpy as np,cv2,json,hashlib
R=Path(__file__).resolve().parent; im=Image.open(R/'accueil-guilde-passage-ouvert.png').convert('RGB');a=np.asarray(im);H,W=a.shape[:2]
# La grille est extraite de la proposition, sa cavité est reconstituée par
# un dégradé sombre : ce ne sont ni des calques natifs ni l'animation Grodoudou.
x0,y0,x1,y1=470,148,713,310;crop=a[y0:y1,x0:x1]
# Barres découpées avec leurs contours foncés ; traverse et pointes isolées.
m=np.zeros((y1-y0,x1-x0),np.uint8)
for left,right in [(483,502),(516,535),(548,566),(581,600),(613,632),(646,665),(678,697)]:
 m[:102,left-x0:right-x0]=255
m[102:132,:]=255
for left,right in [(486,499),(519,532),(551,564),(584,597),(616,629),(649,662),(681,694)]:
 m[132:162,left-x0:right-x0]=255
behind=a.copy()
# Restaurer la cavité sombre derrière la grille : adaptation, pas pixels natifs.
for y in range(y0,y1):
 ratio=(y-y0)/(y1-y0);behind[y,x0:x1]=[int(36-12*ratio),int(18-7*ratio),int(21-11*ratio)]
base=Image.fromarray(behind).convert('RGBA');sprite=np.zeros((y1-y0,x1-x0,4),np.uint8);sprite[:,:,:3]=crop;sprite[:,:,3]=m;gate=Image.fromarray(sprite)
gate.save(R/'grille-detouree-experimentale.png');base.save(R/'fond-grille-reconstitue.png')
frames=[]
for offset in list(range(120,-1,-10))+[0]*8+list(range(10,121,10))+[120]*8:
 screen=base.copy();layer=Image.new('RGBA',(W,H));layer.alpha_composite(gate,(x0,y0+offset))
 # Les barreaux se prolongent jusqu'au linteau pendant la descente ; la partie
 # supérieure était cachée dans le mécanisme quand la grille était relevée.
 for left,right in [(483,502),(516,535),(548,566),(581,600),(613,632),(646,665),(678,697)]:
  bar=gate.crop((left-x0,25,right-x0,85));remain=offset;yy=y0
  while remain>0:
   n=min(remain,bar.height);layer.alpha_composite(bar.crop((0,0,bar.width,n)),(left,yy));yy+=n;remain-=n
 # Occlusion : la grille ne peut pas monter au-dessus de son cadre supérieur.
 layer.paste((0,0,0,0),(0,0,W,y0));screen.alpha_composite(layer)
 frames.append(screen.resize((590,456),Image.Resampling.NEAREST))
frames[0].convert('RGB').save(R/'grille-fermee-essai.png');frames[12].convert('RGB').save(R/'grille-ouverte-essai.png')
frames[0].save(R/'grille-levante-essai.png',save_all=True,append_images=frames[1:],duration=100,loop=0,disposal=0,blend=0,optimize=True)
with Image.open(R/'grille-levante-essai.png') as p:
 print('animation',p.size,p.n_frames,'phases ; captures reconstituées, non-native')
(R/'animation-info.json').write_text(json.dumps({'animation':'grille-levante-essai.png','taille':[590,456],'phases_demandees':len(frames),'pas_vertical_px_original':10,'fond':'cavité reconstituée par dégradé sombre','grille':'détourée de la proposition générée, non native','interaction':False,'moteur':'non intégré'},ensure_ascii=False,indent=2)+'\n')
