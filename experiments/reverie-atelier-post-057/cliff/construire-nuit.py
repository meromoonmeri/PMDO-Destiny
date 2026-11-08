from pathlib import Path
from PIL import Image
import numpy as np
from scipy import ndimage
import json,hashlib
R=Path('/home/user/chantier-cliff-bordures'); B=Path('/home/user/chantier-cliff-bordures');W,H=480,520
sources={'jour':Path('/home/user/apercu-cliff-guilde-ambiances/assets/V24P02A-day-apng.png'),'nuit':Path('/home/user/chantier-grand-cap-nuit/V24P01A-original-anime.png')}
def phases(path):
 im=Image.open(path);res=[]
 for i in range(12):im.seek(i);res.append(im.convert('RGBA').copy())
 assert len(res)==12 and im.size==(312,240)
 return res
ph={k:phases(p) for k,p in sources.items()}
# Nuages de jour intégraux, dans le ciel EoS V24P08A : aucune coupe sur un bord.
a=np.asarray(Image.open(R/'v24p08a.png').convert('RGBA'));rgb=a[:,:,:3].astype(int);sel=(rgb[:,:,0]>95)&(rgb[:,:,1]>140);lab,n=ndimage.label(sel,np.ones((3,3)))
def extract_cloud(label,out):
 ys,xs=np.where(lab==label);box=(int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1));x0,y0,x1,y1=box
 # Sur le masque, chaque composant est entouré d'au moins un pixel de ciel.
 assert x0>0 and y0>0 and x1<a.shape[1] and y1<a.shape[0]
 clip=a[y0:y1,x0:x1].copy();clip[:,:,3]=((lab[y0:y1,x0:x1]==label)*255).astype('uint8');outim=Image.new('RGBA',(x1-x0+16,y1-y0+16));outim.paste(Image.fromarray(clip),(8,8));outim.save(R/out)
 return outim,box
c1,b1=extract_cloud(1,'nuage-jour-01.png');c2,b2=extract_cloud(3,'nuage-jour-02.png')
cn=Image.open(B/'nuage-PMD-entier-transparent.png').convert('RGBA');cn.save(R/'nuage-nuit.png')
for c in [c1,c2,cn]:
 a1=np.array(c.getchannel('A'));assert not (a1[0].any() or a1[-1].any() or a1[:,0].any() or a1[:,-1].any())
terrain=Image.open(B/'cliff-bordures-transparent.png').convert('RGBA');terrain.save(R/'falaise-jour-transparent.png')
a=np.array(terrain);visible=a[:,:,3]>0;a[:,:,:3][visible]=(a[:,:,:3][visible].astype(float)*[.38,.46,.62]).astype('uint8');terrain_nuit=Image.fromarray(a);terrain_nuit.save(R/'falaise-nuit-apercu-transparent.png')
# Sélectionner dix étoiles présentes dans le ciel original, sans répéter la bande.
n=np.array(ph['nuit'][0]);rgb=n[:,:,:3].astype(int);sm=(rgb[:,:,0]>=47)&(abs(rgb[:,:,0]-rgb[:,:,1])<10);sm[128:,:]=False;sl,_=ndimage.label(sm,np.ones((3,3)));groups=[]
for i,slc in enumerate(ndimage.find_objects(sl),1):
 if not slc:continue
 ys,xs=np.where(sl==i)
 if len(xs)>0 and len(xs)<20:groups.append((int(xs.min()),int(ys.min()),i,len(xs)))
chosen=[]
for x,y,i,size in groups:
 if y>115:continue
 if all(abs(x-x0)>20 or abs(y-y0)>17 for x0,y0,_,_ in chosen):chosen.append((x,y,i,size))
 if len(chosen)==10:break
assert len(chosen)==10
# Ecume : extraire une vague complète (composant connexe) dans chacune des
# 12 phases ; on ne répète pas la bande de 24 px tout le long de la mer.
def wave(ref):
 a=np.array(ref.convert('RGBA'));bg=a[212,0,:3];z=a[224:236,:,:3];mask=np.any(z!=bg,axis=2);lab,num=ndimage.label(mask,np.ones((3,3)));ids=np.unique(lab[:,33:80]);cand=[]
 for k in ids:
  if k==0:continue
  yy,xx=np.where(lab==k)
  if len(xx)>40 and xx.min()>0 and xx.max()<311:cand.append((abs(xx.mean()-57),k,xx,yy))
 if not cand:return Image.new('RGBA',(1,1))
 _,k,xx,yy=min(cand,key=lambda v:v[0]);x0,x1=int(xx.min()),int(xx.max()+1);y0,y1=int(yy.min()),int(yy.max()+1);crop=a[224+y0:224+y1,x0:x1].copy();crop[:,:,3]=((lab[y0:y1,x0:x1]==k)*255).astype('uint8');return Image.fromarray(crop)
waves={k:[wave(p) for p in seq] for k,seq in ph.items()}
# L'horizon et la mer haute utilisent le véritable fond EoS à 1×. Pour
# alléger, un seul des deux rangs d'écume d'origine reste dans la partie haute.
def mksea(ref, waveim):
 out=Image.new('RGBA',(W,H));base=tuple(np.array(ref)[212,0]);out.paste(base,(0,264,W,H))
 water=ref.crop((0,128,312,240)); flat=ref.crop((0,212,312,213))
 # Masquer la vague inférieure dans le rectangle d'origine avec sa couleur
 # d'eau native ; les miroitements de l'horizon sont conservés.
 for sy in range(224,236):water.paste(flat,(0,sy-128))
 for x in range(0,W,312):out.paste(water,(x,152))
 for x,y in [(10,355),(425,435)]:out.alpha_composite(waveim,(x,y))
 return out
# Ciel Réveil à l'échelle 1× : recadrage central 480×120 puis extension
# de la rangée supérieure, sans redimensionnement des pixels source.
def adapted(mode):
 src=Image.open(R/f'reveil-{mode}-ciel-source.png').convert('RGBA').crop((144,0,624,120))
 # Les quatre dernières lignes de la couche source sont transparentes (la mer
 # de Réveil les couvre en jeu). Prolonger la dernière ligne opaque au lieu
 # de laisser un trou noir ; la bande supérieure utilise une couleur source.
 from collections import Counter
 top=Counter(src.crop((0,0,W,1)).getdata()).most_common(1)[0][0]
 out=Image.new('RGBA',(W,H),top);out.alpha_composite(src,(0,32))
 bottom=src.crop((0,115,W,116))
 for yy in range(148,152):out.paste(bottom,(0,yy))
 if mode=='nuit':
  astre=Image.open(R/'reveil-nuit-03.png').convert('RGBA').crop((144,0,624,120));out.alpha_composite(astre,(0,32))
 return out
backgrounds={'jour':adapted('jour'),'nuit':adapted('nuit')}
# 24 phases de scintillement de la carte Réveil (5 ticks/phase).
import sys
sys.path.insert(0,'/home/user/destiny-reference/tools');from preview_maps import SheetReader
placements=json.loads((R/'sources/etoiles-reveil-placements.json').read_text())
reader=SheetReader(R/'sources/ZRV2N_02_ETOILES.tile');star_frames=[]
for phase in range(24):
 img=Image.new('RGBA',(W,H))
 for entry in placements:
  x,y=entry['x'],entry['y']
  if not 18<=x<78 or y>=15:continue
  ff=entry['frames'];pos=ff[phase%len(ff)]['TexLoc'];tile=reader.get_tile(pos['X'],pos['Y'])
  if tile is not None:img.alpha_composite(tile,((x-18)*8,y*8+32))
 star_frames.append(img)
reader.close()
clouds={'jour':[(c1,25,18),(c2,265,76)],'nuit':[(cn,24,22),(cn,264,70)]}
verification={}
for mode in ['nuit']:
 seq=[]
 for i in range(121):
  out=backgrounds[mode].copy()
  if mode=='nuit':out.alpha_composite(star_frames[(i*8//5)%24])
  out.alpha_composite(mksea(ph[mode][i%12],waves[mode][i%12]))
  for c,x0,y in clouds[mode]:
   x=(x0-4*i)%W
   for k in (-1,0,1):out.alpha_composite(c,(x+k*W,y))
  out.alpha_composite(terrain if mode=='jour' else terrain_nuit,(0,104));seq.append(out.convert('RGB'))
 assert seq[0].tobytes()==seq[120].tobytes();verification[mode]=True
 seq[0].save(R/f'cliff-{mode}-phase00.png')
 seq[0].save(R/f'cliff-{mode}-anime.png',format='PNG',save_all=True,append_images=seq[1:120],duration=[1000*8/60]*120,loop=0,disposal=0,blend=0,optimize=True)
print('cloud boxes',b1,b2,'native star groups',len(chosen),'loops',verification)
info={'source_ciels':'PMDO-Destiny ee39156a24f350b67e81740478be8505f4ff1a05 zrv2_zone_reveil_jour et nuit, calques 01 ciel, 02 etoiles et 03 astre', 'source_mer_jour':'https://projectpokemon.org/home/gallery/image/77604-v24p02apng/','source_mer_et_nuages_nuit':'https://projectpokemon.org/home/gallery/image/77603-v24p01apng/','source_nuages_jour':'https://projectpokemon.org/home/gallery/image/77526-v24p08apng/','nuages_jour_boxes':[b1,b2],'etoiles_nocturnes':'calque original Réveil 24 phases sur recadrage central, 5 ticks/phase','mer':'mer haute native 12 phases, deuxième ligne de vagues masquée, fond bas prolongé de couleur native et deux vagues isolées extraites des phases correspondantes','période_secondes':16,'égalité_phase_0_120_avant_encodage':verification,'rendu':'simulation hors moteur','mer_sharpedo':'identification exacte non établie'}
(R/'verifications-nuit.json').write_text(json.dumps(info,indent=2,ensure_ascii=False))
