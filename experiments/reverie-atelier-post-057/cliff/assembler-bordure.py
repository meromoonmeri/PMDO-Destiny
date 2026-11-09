from pathlib import Path
from PIL import Image
import numpy as np,json
from scipy.ndimage import binary_erosion
R=Path('/home/user/chantier-cliff-bordures');S=R/'sauvegarde';W,H=480,416
hist=Image.open('/home/user/apercu-cliff-guilde-ambiances/assets/grand-cap-historique-jour.png').convert('RGBA');srcalpha=np.array(Image.open('/home/user/chantier-grand-cap-nuit/L01_herbe_native.png').convert('RGBA').getchannel('A'))>0;arim=np.array(Image.open('/home/user/chantier-grand-cap-nuit/L03_bordure_nord_native.png').convert('RGBA').getchannel('A')); assert hist.size==(1200,880)
h=np.array(hist);h[:,:,3]=arim;source=Image.fromarray(h);source.save(R/'source-bord-metano-jour-transparent.png')
plateau=Image.open(S/'02-plateau.png').convert('RGBA');wall=Image.open(S/'01-parois.png').convert('RGBA');stairs=Image.open(S/'04-escalier.png').convert('RGBA')
# Arrondir les angles de la courbe avant de quelques pixels seulement ;
# le tracé général, l'emprise et l'escalier sont conservés.
from scipy.ndimage import gaussian_filter1d
original=np.array(plateau.getchannel('A'))>0;before=original.copy()
bottom=np.array([np.where(original[:,x])[0].max() if original[:,x].any() else 0 for x in range(W)])
rounded=np.rint(gaussian_filter1d(bottom.astype(float),4)).astype(int)
for x in range(80,400):
 by=int(bottom[x]);newy=int(rounded[x]);
 if newy>by:original[by+1:newy+1,x]=True
 elif newy<by:original[newy+1:by+1,x]=False
changed=int(np.count_nonzero(original!=before));target=original
plateau.putalpha(Image.fromarray((target*255).astype('uint8')))
# Raccorder le devant avec la lisière native de la falaise de Réverie,
# suivant le nouveau bord arrondi, par modules 8×11 px à l'échelle 1×.
city=Image.open('/home/user/chantier-grand-cap-nuit/apercu/nord-reverie.png').convert('RGBA');front=Image.new('RGBA',(W,H))
new_bottom=np.array([np.where(target[:,x])[0].max() if target[:,x].any() else 0 for x in range(W)])
for x in range(64,416,8):
 sy=int(round(np.median(new_bottom[x:x+8])));sx=(x-64)%128
 front.paste(city.crop((sx,19,sx+8,30)),(x,sy-3))
fa=np.minimum(np.array(front.getchannel('A')),np.array(wall.getchannel('A')));front.putalpha(Image.fromarray(fa))
# Candidats de 8×8 extraits de blocs réels de la bordure Métano historique.
# Comparaison sur un voisinage 24×24, sans miroir, rotation, recoloration
# ni redimensionnement. La segmentation est au pixel, pas une carte PMDO.
sp=np.pad(srcalpha,((8,8),(8,8)));tp=np.pad(target,((8,8),(8,8)));candidates=[];vectors=[]
for y in range(8,864,8):
 for x in range(8,1184,8):
  tile=arim[y:y+8,x:x+8]
  if not np.any(tile):continue
  v=sp[y:y+24,x:x+24]
  # éliminer les morceaux intégralement intérieurs ou extérieurs
  if np.all(v[8:16,8:16]) or not np.any(v[8:16,8:16]):continue
  candidates.append((x,y));vectors.append(v.ravel())
v=np.array(vectors,dtype=bool);print('source candidats',len(candidates))
edge=target & ~binary_erosion(target,structure=np.ones((3,3)))
# Front déjà constitué de vrais modules de Réverie. Zone haute/latérale
# autour de la silhouette, s'arrêtant au raccord de la face principale.
knots=[(0,195),(64,195),(78,198),(96,207),(112,228),(145,231),(158,257),(179,260),(208,260),(272,260),(301,260),(322,257),(335,231),(368,228),(384,207),(402,198),(416,195),(479,195)]
curve=np.interp(np.arange(W),*[np.array([p[i] for p in knots]) for i in (0,1)])
curve[64:416]=new_bottom[64:416]
permitted=np.arange(H)[:,None] < curve[None,:]-3; outer=edge & permitted
rim=Image.new('RGBA',(W,H));selected=[]
weights=np.ones((24,24),dtype=np.uint8);weights[8:16,8:16]=4;weights=weights.ravel()
for y in range(0,H,8):
 for x in range(0,W,8):
  if not outer[y:y+8,x:x+8].any():continue
  tv=tp[y:y+24,x:x+24].ravel();scores=np.sum(np.logical_xor(v,tv)*weights,axis=1);idx=int(np.argmin(scores));sx,sy=candidates[idx];tile=source.crop((sx,sy,sx+8,sy+8));rim.paste(tile,(x,y));selected.append({'cible':[x,y],'source':[sx,sy],'score':int(scores[idx])})
# Ne pas mettre de roche en dehors de la surface, ni sur le raccord du devant.
a=np.array(rim);allowed=target & permitted;a[:,:,3]=np.where(allowed,a[:,:,3],0).astype('uint8');rim=Image.fromarray(a)
# Deux retours latéraux complets sont tirés de véritables raccords de la
# carte Réverie. Le masque suit la silhouette préexistante, sans miroir.
cl=Image.open('/home/user/chantier-qualite-reverie/calques/02_Cliffs.png').convert('RGBA')
base=Image.open('/home/user/chantier-qualite-reverie/calques/01_Base.png').convert('RGBA')
def module(box):
 out=base.crop(box);out.alpha_composite(cl.crop(box));return out
leftmod=module((1136,248,1152,264));rightmod=module((1304,760,1320,776));sides=Image.new('RGBA',(W,H))
for y in range(136,196,16):
 sides.paste(leftmod,(62,y));sides.paste(rightmod,(400,y))
sa=np.array(sides);allow=target & permitted;sa[:,:,3]=np.where(allow,sa[:,:,3],0).astype('uint8');sides=Image.fromarray(sa)
# Retirer l'ancien semis de fragments sous ces retours intégraux.
r=np.array(rim);r[136:196,64:80,3]=0;r[136:196,400:416,3]=0;rim=Image.fromarray(r)
# Combiner les quatre calques sans toucher à la géométrie, aux parois ou aux marches.
for name,img in [('01-parois',wall),('02-plateau',plateau),('03-bordure-exterieure-metano',rim),('03b-retours-lateraux-metano',sides),('04-raccord-falaise-avant',front),('05-escalier',stairs)]:img.save(R/f'{name}.png')
out=Image.new('RGBA',(W,H));
for img in [wall,plateau,rim,sides,front,stairs]:out.alpha_composite(img)
out.save(R/'cliff-bordures-transparent.png');bg=Image.new('RGBA',(W,H),(255,0,255,255));bg.alpha_composite(out);bg.convert('RGB').save(R/'cliff-bordures-magenta.png')
# Export d'un contrôle d'occupation de la bordure haute/latérale.
from scipy.ndimage import binary_dilation
coverage=(np.array(rim.getchannel('A'))>0) | (np.array(sides.getchannel('A'))>0);near=binary_dilation(coverage,iterations=2);edge_count=int(outer.sum());covered=int(np.count_nonzero(outer & near));data={'source':'Grand Cap historique jour 9bac5c1, masque L03 et rendu 1×','taille_px':[W,H],'grille_import_px':8,'tuiles_choisies':len(selected),'front':'raccord natif de Réverie réadapté sur une courbe arrondie', 'pixels_masque_plateau_modifies':changed, 'variation_verticale_max_px':4,'limites':'choix par fenêtres de 8×8 guidé par masque, découpes en bord ; jonctions visuellement à vérifier','bord_exterieur_test_proximite_2px':{'pixels_contour':edge_count,'pixels_proches_bordure':covered},'plateau':'ajusté localement sur la courbe avant', 'paroi_et_escalier_inchanges':True,'integration_moteur':False};(R/'placements.json').write_text(json.dumps(selected,ensure_ascii=False,indent=2));(R/'verifications.json').write_text(json.dumps(data,ensure_ascii=False,indent=2));print(json.dumps(data,indent=2,ensure_ascii=False))
