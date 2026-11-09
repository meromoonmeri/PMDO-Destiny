#!/usr/bin/env python3
"""Aperçu non destructif : éclairages discrets et grille levante existante."""
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
p=Path(__file__).resolve().parent
src=Image.open(p/'grille-levante-essai.png'); w,h=src.size
Y,X=np.mgrid[0:h,0:w]
# Éclairage fixe au sol, cantonné aux seuils ; ne touche ni au fond magenta
# ni à la grille. Dégradé arrondi et quantifié pour rester discret en pixel-art.
maskn=Image.new('L',(w,h));ImageDraw.Draw(maskn).polygon([(250,216),(340,216),(365,252),(224,252)],fill=255)
masks=Image.new('L',(w,h));ImageDraw.Draw(masks).polygon([(254,399),(337,399),(337,455),(254,455)],fill=255)
north=np.exp(-((X-295)/42)**2-((Y-230)/23)**2)*np.asarray(maskn)/255
south=np.exp(-((X-295)/43)**2-((Y-424)/25)**2)*np.asarray(masks)/255
# Quantification des intensités pour éviter un halo photoréaliste lissé.
strength=np.round(np.clip(north*.095+south*.13,0,.15)*64)/64
frames=[];dur=[]
for i in range(src.n_frames):
 src.seek(i);a=np.asarray(src.convert('RGBA')).copy();rgb=a[:,:,:3].astype(np.float32);rgb += (np.array([255,225,143])-rgb)*strength[:,:,None];a[:,:,:3]=np.clip(np.round(rgb),0,255).astype('uint8');frames.append(Image.fromarray(a));dur.append(int(src.info.get('duration',100)))
out=p/'accueil-grille-animee-halos.png';frames[0].save(out,save_all=True,append_images=frames[1:],duration=dur,loop=0,disposal=0,blend=0,optimize=True)
frames[0].save(p/'accueil-halos-grille-fermee.png');frames[12].save(p/'accueil-halos-grille-ouverte.png')
with Image.open(out) as im:
 assert im.size==(590,456) and im.n_frames>=24
 print('Aperçu',im.size,'phases',im.n_frames,'durée',sum(dur),'ms ; halos fixes, salle inchangée.')
