from pathlib import Path
from PIL import Image
import numpy as np, json
from scipy import ndimage
R=Path('/home/user/chantier-cliff-raccord-metano');src=Image.open('/home/user/chantier-grand-cap-nuit/V24P01A-original-anime.png');assert src.n_frames==12 and src.size==(312,240)
src.seek(0);original=np.array(src.convert('RGBA'));rgb=original[:,:,:3].astype(int);mask=(rgb[:,:,1]>rgb[:,:,0]+5)&(rgb[:,:,2]>rgb[:,:,1]+25);mask[:20]=False;mask[75:]=False;labels,_=ndimage.label(mask,structure=np.ones((3,3)));sizes=np.bincount(labels.ravel());sizes[0]=0;idx=sizes.argmax();region=(labels==idx);ys,xs=np.where(region);box=(xs.min(),ys.min(),xs.max()+1,ys.max()+1);assert box==(145,24,265,70),box
cloud=np.zeros((62,136,4),dtype=np.uint8);crop=original[24:70,145:265].copy();crop[:,:,3]=(region[24:70,145:265]*255).astype('uint8');cloud[8:54,8:128]=crop;Image.fromarray(cloud).save(R/'nuage-PMD-entier-transparent.png')
# Valider le contour transparent autour du nuage entier : aucun pixel au bord.
assert not cloud[0,:,3].any() and not cloud[-1,:,3].any() and not cloud[:,0,3].any() and not cloud[:,-1,3].any()
# Sélection volontaire de 10 étoiles seulement, sans répétition artificielle du ciel.
stars=[(41,21),(117,43),(179,13),(253,35),(336,18),(409,42),(19,87),(210,78),(378,93),(460,72)]
terrain=Image.open(R/'cliff-corrige-transparent.png').convert('RGBA');a=np.array(terrain);visible=a[:,:,3]>0;a[:,:,:3][visible]=(a[:,:,:3][visible].astype(float)*[.38,.46,.62]).astype('uint8');night=Image.fromarray(a);night.save(R/'cliff-nu-nuit-transparent.png')
W,H=480,520;cloudim=Image.fromarray(cloud);frames=[]
# Mettre les phases en mémoire : seek(0) après la dernière image APNG
# peut altérer certains décodeurs Pillow sur les images indexées.
phases=[]
source_frais=Image.open('/home/user/chantier-grand-cap-nuit/V24P01A-original-anime.png')
for j in range(12):
 source_frais.seek(j);phases.append(source_frais.convert('RGBA').copy())
for i in range(121):
 ref=phases[i%12];out=Image.new('RGBA',(W,H),(0,0,79,255))
 for j,(x,y) in enumerate(stars):out.putpixel((x,y),(135,135,167,255) if j%3 else (183,175,199,255))
 # Horizon et eau source PMD sans changement de palette. Une bande native
 # basse est répétée verticalement pour couvrir la hauteur sous l'horizon.
 ocean=ref.crop((0,128,312,240))
 for x in range(0,W,312):out.paste(ocean,(x,152))
 band=ref.crop((0,216,312,240))
 for y in range(264,H,24):
  for x in range(0,W,312):out.paste(band,(x,y))
 # L'objet entier est translaté à travers la bordure et réapparaît :
 # copie(s) décalée(s) pour dessiner l'entrée et la sortie sans saut.
 for x0,y in [(24,24),(264,70)]:
  x=(x0-4*i)%W
  for k in (-1,0,1):out.alpha_composite(cloudim,(x+k*W,y))
 out.alpha_composite(night,(0,104));frames.append(out.convert('RGB'))
assert frames[0].tobytes()==frames[-1].tobytes(),'La boucle ne revient pas exactement à son origine'
frames[0].save(R/'cliff-mer-nuit-phase00.png')
# Fichier APNG d'aperçu : 120 phases, cadence 8 ticks; aucun pixel du dernier
# état théorique n'est stocké en doublon, la 121e phase prouve le bouclage.
frames[0].save(R/'cliff-nuit-boucle-apercu.png',format='PNG',save_all=True,append_images=frames[1:120],duration=[1000*8/60]*120,loop=0,disposal=0,blend=0,optimize=True)
# GIF navigateur indicatif ; quantification et timing GIF peuvent différer.
frames[0].save(R/'cliff-nuit-boucle-apercu.gif',save_all=True,append_images=frames[1:120],duration=130,loop=0,optimize=True,disposal=2)
info={'mer':'V24P01A APNG 312×240 ; 12 phases originelles ; crop x0–311 y128–239, couleurs conservées ; bandes basses répétées','attribution_sharpedo':'non prouvée indépendamment ; fond PMD précédemment demandé','nuage_source_box':[145,24,265,70],'nuage_complet_marge_px':8,'etoiles':len(stars),'boucle_phases':120,'periode_secondes':16,'nuage_vitesse_px_phase':4,'egalite_premiere_phase_phase120':frames[0].tobytes()==frames[120].tobytes(),'nature':'simulation hors moteur; terrain nocturne recoloré pour l’aperçu','echelle':1}
(R/'verification-boucle.json').write_text(json.dumps(info,ensure_ascii=False,indent=2));print(json.dumps(info,indent=2,ensure_ascii=False))
