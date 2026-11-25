from pathlib import Path
from PIL import Image
import numpy as np,json
from scipy import ndimage
from collections import Counter
R=Path('/home/user/chantier-cliff-ciel-guilde');B=Path('/home/user/chantier-cliff-raccord-metano');W,H=480,520
terrain=Image.open(B/'cliff-corrige-transparent.png').convert('RGBA');td=np.array(terrain);vis=td[:,:,3]>0;td[:,:,:3][vis]=(td[:,:,:3][vis].astype(float)*[.70,.57,.68]).astype('uint8');terr_dusk=Image.fromarray(td)
# Ciel T00P04A : reconstruire les régions cachées par la guilde à partir
# des couleurs réellement présentes dans chaque rangée et de leur alternance.
ref=np.array(Image.open('/home/user/chantier-cap-escalier-nuages/T00P04A-source.gif').convert('RGBA'));sky=np.zeros((H,W,4),np.uint8);match=total=0
for y in range(152):
 sy=min(135,max(0,y-16));row=ref[sy,:,:3];valid=(row[:,0]<151)&(row[:,1]>=175)&(row[:,2]>=248)
 assert valid.any()
 for parity in (0,1):
  xs=np.arange(480);which=valid & ((xs%2)==parity);vals=row[which];col=Counter(map(tuple,vals)).most_common(1)[0][0];sky[y,parity::2,:3]=col;sky[y,parity::2,3]=255
  match+=sum(np.all(vals==np.array(col),axis=1));total+=len(vals)
day_sky=Image.fromarray(sky)
# Nuage entier de la référence : composant isolé, marge transparente.
r,g,b=[ref[:,:,i].astype(int) for i in range(3)];mask=(r>=160)&(g>=210)&(b>=230);mask[:72]=False;mask[102:]=False;mask[:,:20]=False;mask[:,61:]=False
lab,_=ndimage.label(mask,np.ones((3,3)));count=np.bincount(lab.ravel());count[0]=0;i=count.argmax();yy,xx=np.where(lab==i);assert (xx.min(),yy.min(),xx.max()+1,yy.max()+1)==(26,82,55,101)
def component(src,labels,index,xx,yy,file):
 x0,x1=int(xx.min()),int(xx.max()+1);y0,y1=int(yy.min()),int(yy.max()+1);a=src[y0:y1,x0:x1].copy();a[:,:,3]=((labels[y0:y1,x0:x1]==index)*255).astype('uint8');out=Image.new('RGBA',(x1-x0+16,y1-y0+16));out.paste(Image.fromarray(a),(8,8));out.save(R/file);alpha=np.array(out.getchannel('A'));assert not(alpha[0].any() or alpha[-1].any() or alpha[:,0].any() or alpha[:,-1].any());return out
day_cloud=component(ref,lab,i,xx,yy,'nuage-guilde-jour-entier.png')
# V02P01A canonique : couleur de ciel dominante par ligne, deux nuages entiers.
dusk=np.array(Image.open(R/'V02P01A.png').convert('RGBA'));back=np.array([Counter(map(tuple,row[:,:3])).most_common(1)[0][0] for row in dusk]);back[45]=dusk[45,160,:3];back[46]=dusk[46,160,:3];diff=np.any(dusk[:,:,:3]!=back[:,None,:],axis=2);dl,_=ndimage.label(diff,np.ones((3,3)));comps=[]
for j in range(1,dl.max()+1):
 y,x=np.where(dl==j)
 if len(x)>1000 and x.min()>0 and x.max()<dusk.shape[1]-1 and y.min()>75:comps.append((j,x,y))
comps.sort(key=lambda q:q[2].min());assert len(comps)>=2
c_dusk=[]
for k,(j,x,y) in enumerate(comps[:2],1):c_dusk.append(component(dusk,dl,j,x,y,f'nuage-eos-crepuscule-{k}.png'))
dsky=np.zeros((H,W,4),np.uint8)
for y in range(152):dsky[y,:,0:3]=back[y];dsky[y,:,3]=255
# Deux lignes de transition sont tramées dans l'original, non une bande unie.
for y in (45,46):
 for parity in (0,1):dsky[y,parity::2,:3]=dusk[y,160+parity,:3]
# Garder des étoiles originales espacées, sans répétition artificielle.
starmask=(dusk[:24,:,0]>225)&(dusk[:24,:,1]>210)&(dusk[:24,:,2]>210)
for y,x in zip(*np.where(starmask)):dsky[y,x+108]=dusk[y,x]
dusk_sky=Image.fromarray(dsky)
# Mer de jour : les douze phases V24P02A sont conservées, avec une seule
# ligne de vagues hautes et deux vagues isolées ; pas de bandes répétées.
im=Image.open('/home/user/apercu-cliff-guilde-ambiances/assets/V24P02A-day-apng.png');p=[]
for k in range(12):im.seek(k);p.append(im.convert('RGBA').copy())
def wave(ref):
 a=np.array(ref);back=a[212,0,:3];mask=np.any(a[224:236,:,:3]!=back,axis=2);l,_=ndimage.label(mask,np.ones((3,3)));options=[]
 for k in np.unique(l[:,33:80]):
  if k==0:continue
  yy,xx=np.where(l==k)
  if len(xx)>40 and xx.min()>0 and xx.max()<311:options.append((abs(xx.mean()-57),k,xx,yy))
 if not options:return Image.new('RGBA',(1,1))
 _,k,xx,yy=min(options,key=lambda z:z[0]);x0,x1=int(xx.min()),int(xx.max()+1);y0,y1=int(yy.min()),int(yy.max()+1);v=a[224+y0:224+y1,x0:x1].copy();v[:,:,3]=((l[y0:y1,x0:x1]==k)*255).astype('uint8');return Image.fromarray(v)
waves=[wave(q) for q in p]
def sea_day(ref,w):
 out=Image.new('RGBA',(W,H));bg=tuple(np.array(ref)[212,0]);out.paste(bg,(0,264,W,H));water=ref.crop((0,128,312,240));flat=ref.crop((0,212,312,213))
 for sy in range(224,236):water.paste(flat,(0,sy-128))
 for x in range(0,W,312):out.paste(water,(x,152))
 for x,y in [(10,355),(425,435)]:out.alpha_composite(w,(x,y))
 return out
# Coucher de soleil marin V22P01A : image source native, eau étendue au bas
# par la couleur native de son dernier rang. L'eau est fixe dans cette version.
sea_src=Image.open(R/'V22P01A.png').convert('RGBA');assert sea_src.size==(312,240);sea_c=Image.new('RGBA',(W,H));water=sea_src.crop((0,130,312,240));sea_c.paste(tuple(sea_src.getpixel((0,239))),(0,262,W,H));sea_c.paste(water,(84,152))
# Prolonger chaque rang par le pixel d'extrémité natif, sans réintroduire
# les raccords verticaux de la réflexion du soleil au bord des répétitions.
for y in range(110):
 sea_c.paste(water.getpixel((0,y)),(0,152+y,84,153+y))
 sea_c.paste(water.getpixel((311,y)),(396,152+y,480,153+y))
configs={'jour':(day_sky,[(day_cloud,16,84),(day_cloud,112,101),(day_cloud,178,91),(day_cloud,327,103),(day_cloud,419,84)],terrain),'crepuscule':(dusk_sky,[(c_dusk[0],26,57),(c_dusk[1],305,95)],terr_dusk)};tests={}
for mode,(sky,clouds,land) in configs.items():
 seq=[]
 for f in range(121):
  out=sky.copy();out.alpha_composite(sea_day(p[f%12],waves[f%12]) if mode=='jour' else sea_c)
  for cl,x0,y in clouds:
   x=(x0-4*f)%W
   for k in (-1,0,1):out.alpha_composite(cl,(x+k*W,y))
  out.alpha_composite(land,(0,104));seq.append(out.convert('RGB'))
 assert seq[0].tobytes()==seq[120].tobytes();tests[mode]=True
 seq[0].save(R/f'cliff-{mode}-phase00.png');seq[0].save(R/f'cliff-{mode}-anime.png',format='PNG',save_all=True,append_images=seq[1:120],duration=[1000*8/60]*120,loop=0,disposal=0,blend=0,optimize=True)
print('Background agreements:',int(match),'/',total,'loop',tests)
info={'jour_ciel_reference':'https://projectpokemon.org/home/gallery/image/81080-t00p04agif/','jour_sky_reconstruction':'couleurs modales par rangée/parité issue de l’image composée; régions masquées reconstruites','jour_nuage_boite_source':[26,82,55,101],'jour_couleurs_sky_comparaison_parite':{'agree':int(match),'total':int(total)},'crepuscule_ciel_nuages':'https://projectpokemon.org/home/gallery/image/77462-v02p01apng/','crepuscule_mer':'https://projectpokemon.org/home/gallery/image/77513-v22p01apng/','crepuscule_fond_exact_guilde':'non établi, adaptation de deux vrais fonds EoS','nuit':'ciel, lune et étoiles de la zone Réveil Destiny v0.5.7; nuages PMD; génération séparée','images':120,'phase0_egale_phase120_avant_encodage':tests,'period_s':16,'moteur':'non intégré'}
(R/'verifications-jour-crepuscule.json').write_text(json.dumps(info,indent=2,ensure_ascii=False))
