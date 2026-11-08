from pathlib import Path
from PIL import Image, ImageDraw
import numpy as np,json
R=Path('/home/user/chantier-cliff-raccord-metano');S=R/'sauvegarde';P=Path('/home/user/chantier-cap-escalier-nuages');W,H=480,416
old=[Image.open(S/f'{n}.png').convert('RGBA') for n in ('01-parois','02-plateau','03-bord','04-escalier')]
ref=Image.open(P/'escalier-reverie-source.png').convert('RGBA');oldwall=old[0]; face=np.array(oldwall.getchannel('A'));face[320:H,64:416]=255
left=ref.crop((16,0,80,128));right=ref.crop((136,0,200,128));tex=Image.new('RGBA',(W,H))
for y in range(128,H,128):
 for x in range(0,W,64):tex.paste(left if (x//64)%2==0 else right,(x,y))
# Au-dessus de y=320, conserver à l'octet près le calque antérieur ; prolonger seulement vers le bas.
wall=oldwall.copy();addition=tex.copy();m=np.zeros((H,W),dtype='uint8');m[320:H,64:416]=255;addition.putalpha(Image.fromarray(m));wall.alpha_composite(addition)
# Supprimer deux lignes d'herbe accidentelles qui venaient du bord du
# cadrage source : remplacer uniquement ces pixels par le pixel roche
# immédiatement voisin, sans recoloration (retouche locale explicitée).
w=np.array(wall)
retouches=0
for x in (128,384):
 for y in range(264,H):
  r,g,b,a=map(int,w[y,x])
  if a and g>r*.90 and r>160 and g>170 and b<130:
   w[y,x]=w[y,x+1];retouches+=1
wall=Image.fromarray(w)
# Réemploi de bandes adjacentes de 8 pixels de la lisière horizontale de la
# carte rendue de Réverie, en taille d'origine, déplacées suivant la courbe.
# Elles ne sont ni étirées, ni retournées, ni recolorées.
city=Image.open('/home/user/chantier-grand-cap-nuit/apercu/nord-reverie.png').convert('RGBA')
knots=[(0,195),(64,195),(78,198),(96,207),(112,228),(145,231),(158,257),(179,260),(208,260),(272,260),(301,260),(322,257),(335,231),(368,228),(384,207),(402,198),(416,195),(479,195)]
curve=np.interp(np.arange(W),*[np.array([p[i] for p in knots]) for i in (0,1)])
rim=Image.new('RGBA',(W,H))
for x in range(64,416,8):
 # Décalage de chaque module pour épouser la pente sans modifier ses pixels.
 y=int(round(curve[min(x+4,479)]));sx=(x-64)%128
 module=city.crop((sx,19,sx+8,30));rim.paste(module,(x,y-3))
# Pas de bordures en dehors de la face.
a=np.minimum(np.asarray(rim.getchannel('A')),np.asarray(wall.getchannel('A')));rim.putalpha(Image.fromarray(a))
stairs=old[3];grass=old[1];images=[wall,grass,rim,stairs]
for n,img in zip(('01-parois','02-plateau','03-raccord-metano','04-escalier'),images):img.save(R/f'{n}.png')
out=Image.new('RGBA',(W,H));
for im in images:out.alpha_composite(im)
out.save(R/'cliff-corrige-transparent.png');mag=Image.new('RGBA',(W,H),(255,0,255,255));mag.alpha_composite(out);mag.convert('RGB').save(R/'cliff-corrige-magenta.png')
# Tests : géométrie du plateau/escalier inchangée et face présente en bas.
assert grass.tobytes()==old[1].tobytes() and stairs.tobytes()==old[3].tobytes()
assert np.all(np.array(wall.getchannel('A'))[415,64:416]==255)
assert not np.any(np.array(wall.getchannel('A'))[415,:64]) and not np.any(np.array(wall.getchannel('A'))[415,416:])
diff=np.any(np.array(wall)[:320]!=np.array(oldwall)[:320],axis=2)
assert all(x in (128,384) for x in np.where(diff)[1])
info={'dimensions':[W,H],'grille_px':8,'sortie_escalier':[212,268],'pixels_paroi_au_bas':'x64–415 inclus','plateau_et_escalier_inchanges':True,'paroi_au_dessus_de_y320':'inchangée hors retouche des deux coutures x128 et x384', 'pixels_herbe_sur_paroi_corriges':retouches,'source_paroi_et_escalier':'escalier-reverie-source.png (rendu Réverie)','source_bord':'nord-reverie.png bande source y19–29, modules contigus 8×11 déplacés le long du tracé','limites':'adaptation par modules, jonctions à contrôler ; non intégré ni validé moteur'}
(R/'verifications.json').write_text(json.dumps(info,indent=2,ensure_ascii=False));print(json.dumps(info,ensure_ascii=False,indent=2))
