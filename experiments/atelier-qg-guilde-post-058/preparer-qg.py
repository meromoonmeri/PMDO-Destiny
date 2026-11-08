from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np
from scipy.ndimage import binary_propagation
R=Path(__file__).resolve().parent
src=Image.open(R/'qg-sans-drapeaux-ni-torches.png').convert('RGB')
a=np.asarray(src); c=a.astype('int16'); bg=(c[:,:,0]>120)&(c[:,:,2]>105)&(c[:,:,1]<85)&(c[:,:,2]*5>c[:,:,0]*4)&(c[:,:,1]*3<c[:,:,0])
seed=np.zeros(bg.shape,bool);seed[0,:]=bg[0,:];seed[-1,:]=bg[-1,:];seed[:,0]=bg[:,0];seed[:,-1]=bg[:,-1]
# Le magenta est un fond artificiel : retirer aussi les interstices fermés
# (entre les marches et les racines), pas uniquement les régions connectées au bord.
bg=bg
rgba=np.dstack((a,(~bg).astype('uint8')*255)); im=Image.fromarray(rgba).resize((224,224),Image.Resampling.NEAREST)
# Ouverture sous la porte : masque d'arche seulement ; encadrement laissé intact.
mask=Image.new('L',(224,224),0);d=ImageDraw.Draw(mask)
d.polygon([(111,155),(105,156),(100,159),(96,163),(93,168),(93,192),(130,192),(130,168),(128,163),(124,159),(119,156),(113,155)],fill=255)
base=im.copy();base.paste((0,0,0,255),(0,0,224,224),mask)
# Objet indépendant de 48×48 placé à (88,151) ; les deux vantaux se
# compriment latéralement en gardant le trou noir dans le décor.
box=(88,151,136,199);portal=im.crop(box);m=mask.crop(box);original=Image.new('RGBA',(48,48));original.paste(portal,(0,0),m)
# couper au centre de l'arche en deux vantaux ; animation hors moteur.
left=original.crop((0,0,24,48));right=original.crop((24,0,48,48));frames=[]
for width in (24,20,16,12,8,4,0):
 f=Image.new('RGBA',(48,48))
 if width:
  f.alpha_composite(left.resize((width,48),Image.Resampling.NEAREST),(0,0));f.alpha_composite(right.resize((width,48),Image.Resampling.NEAREST),(48-width,0))
 frames.append(f)
base.save(R/'qg-fond-porte-ouverte-transparent.png'); im.save(R/'qg-porte-fermee-transparent.png')
for i,f in enumerate(frames):f.save(R/f'porte-{i:02d}.png')
frames[0].save(R/'porte-ouverture-apng.png',save_all=True,append_images=frames[1:],duration=[140]*6+[700],loop=0,disposal=0,blend=0)
sheet=Image.new('RGBA',(48*len(frames),48))
for i,f in enumerate(frames):sheet.alpha_composite(f,(i*48,0))
sheet.save(R/'porte-ouverture-spritesheet.png')
views=[]
for f in frames+frames[-2:0:-1]:
 v=base.copy();v.alpha_composite(f,(88,151));views.append(v.resize((448,448),Image.Resampling.NEAREST))
views[0].save(R/'qg-porte-demonstration.gif',save_all=True,append_images=views[1:],duration=[160]*6+[800]+[160]*5,loop=0,disposal=2)
print('building',im.size,'door',frames[0].size,'sheet',sheet.size,'offset',box[:2], 'background connected pixels',bg.sum())
