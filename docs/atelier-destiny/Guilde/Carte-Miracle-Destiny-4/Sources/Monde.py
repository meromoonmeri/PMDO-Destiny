#!/usr/bin/env python3
"""Integrate indexed coastlines and generated ink, then make the Destiny 4 explorer assets."""
from pathlib import Path
from hashlib import sha256
import json, shutil
import numpy as np
from PIL import Image
from scipy import ndimage as nd
from scipy.optimize import linear_sum_assignment
from Grille import navigation
D=Path(__file__).resolve().parents[1];S=D/'Sources'; G=D/'Generations'; C=D/'Calques'; B=D.parent/'Carte-Miracle-Destiny'; E=D.parent/'Fond-Nu-EoS';C.mkdir(exist_ok=True)
W,H=2224,1112; BASE=(32,200); HER=(1148,168); HER_SHAPE=(1040,778)
N=Image.Resampling.NEAREST; ST=np.ones((3,3),np.uint8)

def jj(f):return json.loads(f.read_text())
def savej(f,o):f.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n')
def digest(f):return sha256(f.read_bytes()).hexdigest()
def save(im,f):im.save(f,optimize=True)
def px(a):return Image.fromarray(a)
def bbox(m):
 y,x=np.where(m);return int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)
def pil_rgba(a,m):
 z=np.dstack((a,m.astype('uint8')*255));z[~m]=0;return px(z)
def nearest_pixel(mask,x,y):
 y0,x0=np.nonzero(mask);i=np.argmin((x0-x)**2+(y0-y)**2);return int(x0[i]),int(y0[i])
def read(p):return Image.open(p).convert('RGBA')
def split(m):
 l,u=nd.label(m,structure=ST);objs=nd.find_objects(l);ct=np.bincount(l.ravel());ct[0]=0;return l,[(i+1,ob,int(ct[i+1])) for i,ob in enumerate(objs)]
def box_ob(ob):y,x=ob;return x.start,y.start,x.stop,y.stop

def trim(p,extra=False):
 a=np.asarray(Image.open(p).convert('RGB'));r,g,b=np.moveaxis(a.astype('int16'),-1,0)
 key=((r>142)&(b>139)&(g<(.60 if not extra else .70)*np.minimum(r,b))&(np.abs(r-b)<113)) | ((r>75)&(b>66)&(g<.49*np.minimum(r,b))&(np.abs(r-b)<96))
 l,n=nd.label(~key,structure=ST);ct=np.bincount(l.ravel());ct[0]=0
 m=np.isin(l,np.flatnonzero(ct>=(max(80,ct.max()*.0017) if extra else max(60,ct.max()*.00025))))
 m|=(nd.binary_fill_holes(m,structure=ST)&(g>=65));
 # No outside matte, no pure pink fringe. Recover edge pigments from nearby generated pixels.
 lx,ly,rx,ry=bbox(m);a=a[ly:ry,lx:rx].copy();m=m[ly:ry,lx:rx]
 r,g,b=np.moveaxis(a.astype('int16'),-1,0);edge=m&(nd.distance_transform_edt(m)<7.0)&(r-g>30)&(b-g>26)&(r>126)&(b>121)
 if edge.any():
  z=nd.distance_transform_edt(~(m&~edge),return_distances=False,return_indices=True);a[edge]=a[z[0][edge],z[1][edge]]
 return a,m

def stretched(a,m,w,h):
 b=np.array(px(a).resize((w,h),N));k=np.array(px(m.astype('uint8')*255).resize((w,h),N))>0
 if not k.any():return np.full((h,w,3),np.median(a[m],axis=0),dtype=np.uint8),k
 near=nd.distance_transform_edt(~k,return_distances=False,return_indices=True);fill=~k;b[fill]=b[near[0][fill],near[1][fill]]
 return b,k

def patch(name,mask,heritage=False):
 # Only the registered generated art may populate these coastlines. No relief is synthesized.
 a,m=trim(G/(name+'.png')); la,ta,ra,ba=bbox(mask);t=mask[ta:ba,la:ra]; hh,ww=t.shape
 out,fitted=stretched(a,m,ww,hh)
 matches=0
 if heritage:
  root,cs=split(t);sr,gs=split(m)
  lt=[(i,ob,n) for i,ob,n in cs if n>=20];lg=[(i,ob,n) for i,ob,n in gs if n>=120]
  if lt and lg:
   def metrics(it,w,h,ss):
    _,ob,n=it;x,y,x2,y2=box_ob(ob);return [(x+x2)/(2*w),(y+y2)/(2*h),np.log(max(1e-6,n/ss))]
   aa=np.array([metrics(q,ww,hh,t.sum()) for q in lt]);bb=np.array([metrics(q,m.shape[1],m.shape[0],m.sum()) for q in lg]);d=((aa[:,None]-bb[None,:])**2*[1.,1.,.043]).sum(axis=2)
   ii,jj0=linear_sum_assignment(d)
   for i,j in zip(ii,jj0):
    if d[i,j]>.33:continue
    k,ob,n=lt[i];g,box,p=lg[j];x,y,x2,y2=box_ob(ob)
    c,_=stretched(a[box],sr[box]==g,x2-x,y2-y);co=root[ob]==k;out[ob][co]=c[co];matches+=1
  # Remap extreme wine/pink ink from one generated source to the natural umber shade family.
  # The underlying pixel marks and contours are unchanged.
  if name=='Terres-du-Centre':
   rr,gg,bb=np.moveaxis(out.astype('float32'),-1,0);garnet=t&(bb>gg*1.28)&(rr>gg*1.48)&(bb>39)
   rr[garnet]=(.73*rr+41)[garnet];gg[garnet]=(.79*gg+.15*rr+31)[garnet];bb[garnet]=(.56*bb+.085*rr+9)[garnet]
   out=np.uint8(np.clip(np.dstack((rr,gg,bb)),0,255))
  if name=='Terres-du-Levant':
   # The generated Levant was grass-heavy. Shift green pigments toward the neighbouring amber/olive atlas palette.
   rr,gg,bb=np.moveaxis(out.astype('float32'),-1,0);sel=(gg>rr*1.02)&(gg>bb+13)&t
   rr[sel]=(.78*rr+.22*gg+9)[sel];gg[sel]=(gg*.925+3)[sel];bb[sel]=(bb*.88+6)[sel]
   out=np.uint8(np.clip(np.dstack((rr,gg,bb)),0,255))
 ans=np.zeros((*mask.shape,4),np.uint8);ans[ta:ba,la:ra]=np.asarray(pil_rgba(out,t))
 assert np.array_equal(ans[...,3]>0,mask)
 return ans,{'brut':name+'.png','sha256':digest(G/(name+'.png')),'silhouette_px':int(mask.sum()),'appariements_du_brut':matches,'couverture_avant_recalage':round(float((t&fitted).sum()/t.sum()),4)}

base=jj(B/'Atlas.json');region=dict(base['regions']);realm={k:'Destiny' for k in region};atlas_sites=base['sites'];used_refs=[]
labels_all=np.zeros((H,W),np.int32);owners=np.zeros_like(labels_all,np.int16);L=0; area_id={k:i for i,k in enumerate(region,1)}; placements={};hints={}
def add_area(k,nom,origine):
 assert k not in area_id;region[k]=nom;realm[k]=origine;area_id[k]=len(area_id)+1

def land_component(mask,area):
 global L
 assert mask.any() and not np.any(mask&(labels_all>0));L+=1;labels_all[mask]=L;owners[mask]=area_id[area];return L

def place_mask(mask,offset):
 ox,oy=offset;h,w=mask.shape;a=np.zeros((H,W),bool);a[oy:oy+h,ox:ox+w]=mask;return a

def paste_layer(layer,off=BASE):
 terr.alpha_composite(layer,off)

terrain_base=np.array(read(B/'Calques/01-Terres.png'));orig_mask=terrain_base[...,3]>0;bl,blists=split(orig_mask);assert len(blists)==26
for nid,name in [(1,'Seracine'),(19,'Torselune')]:
 mask=bl==nid;piece,rec=patch(name,mask);terrain_base[mask]=piece[mask];used_refs.append(rec);save(px(piece).crop(bbox(mask)),C/(name+'-Detoure.png'))
assert np.array_equal(orig_mask,terrain_base[...,3]>0)
tex=Image.new('RGBA',(1112,732));tex.alpha_composite(px(terrain_base));tex.alpha_composite(read(B/'Calques/06-Archipels.png'))
for q in base['glyphs'].values():tex.alpha_composite(read(B/'Calques'/q['file']),(q['x'],q['y']))
base_img=np.asarray(tex); base_land=base_img[...,3]>0
for key,q in base['glyphs'].items():
 if key!='fosse': base_land=base_land.copy();base_land[q['y']:q['y']+q['h'],q['x']:q['x']+q['w']]=False
basel,bodies=split(base_land)
asites=[s for s in atlas_sites if s['island']];converts={}
def shift(p,off):return [int(p[0]+off[0]),int(p[1]+off[1])]

def closest_site(ob,mask,qs):
 xx,yy=np.where(mask);coords=np.array([yy+ob[1].start,xx+ob[0].start]).T
 q=np.array([s['point'] for s in qs]);j=int(np.argmin(((q[:,None,:]-coords[None,:,:])**2).sum(axis=2).min(axis=1)));return qs[j]
for isl,ob,c in bodies:
 act=basel==isl
 direct=[s for s in asites if act[s['point'][1],s['point'][0]]]
 # Preserve the area assignment of the earlier hand-tested locations and attached specks.
 if direct:key=direct[0]['area'];assert len({s['area'] for s in direct})==1
 else:
  key=None
  for r in base['archipels']:
   x,y,x2,y2=box_ob(ob)
   if r['x']<=x and r['y']<=y and x2<=r['x']+r['w'] and y2<=r['y']+r['h']:key=r['id'];break
  if not key:key=closest_site(ob,act[ob],asites)['area']
 lid=land_component(place_mask(act,BASE),key)
 for s in direct:converts[s['island']]=lid
for q in base['glyphs'].values():
 if q is base['glyphs']['fosse']:continue
 x,y=shift([q['x'],q['y']],BASE);a=np.asarray(read(B/'Calques'/q['file']))[...,3]>0;owners[y:y+q['h'],x:x+q['w']][a]=area_id['mer']
for s in atlas_sites:
 s['island']=converts[s['island']] if s['island'] else 0;s['loc']=shift(s['loc'],BASE);s['point']=shift(s['point'],BASE)
 s.pop('node',None);s.pop('arrival_hint',None)
terr=Image.new('RGBA',(W,H));paste_layer(tex)
save(tex,C/'01-Noyau-Destiny.png')

legacy=jj(S/'Heritage.json');index=np.array(Image.open(S/'Index-Heritage.png'));orig_groups=index.copy()
# The large and small land groups from Image 4 are kept in the same north-up arrangement.
rawindex=np.array(px(index).resize(HER_SHAPE,N));world_H=Image.new('RGBA',HER_SHAPE)
new_areas={
 'caps-ouest':('Îles Blanches','Les crêtes pâles et les îlots à l’extrême nord-ouest des anciens mondes.'),
 'falaises-ouest':('Falaises Occidentales','Un relief très découpé, entre forêts, vallons et caps rocheux.'),
 'escales-givre':('Escales du Givre','Deux groupes de terres froides de part et d’autre du continent central.'),
 'terres-centre':('Terres du Centre','Un réseau de vallons cultivés, de collines ocre et de petits lacs.'),
 'croissant-vents':('Croissant des Vents','Des terres effilées ouvertes sur le passage du nord-est.'),
 'cap-aurores':('Cap des Aurores','Le promontoire séparé à l’ouest des grandes Terres Boréales.'),
 'boreales':('Terres Boréales','Les massifs du nord-est, avec des pins serrés et leurs caps de neige.'),
 'austral':('Grande Île Australe','La grande terre méridionale et ses petites îles de sable et de roche.'),
 'anneaux-austraux':('Anneaux Austraux','Les atolls et terres en chapelet à l’est de l’île australe.'),
 'pointe-levant':('Pointe du Levant','L’île rocheuse détachée qui garde les abords du Levant.'),
 'levant':('Terres du Levant','Les forêts et longues péninsules du sud-est des anciens mondes.')}
for a,(nom,_) in new_areas.items():add_area(a,nom,'Anciens mondes')

def subarea(k,x,y):
 if k==1:return 'caps-ouest' if y<59 else 'falaises-ouest'
 if k==2:
  if y<89 or (y>=244 and 258<x<342):return 'escales-givre'
  return 'croissant-vents' if x>=350 else 'terres-centre'
 if k==3:return 'cap-aurores' if x<=416 else 'boreales'
 if k==4:return 'austral' if x<129 else 'anneaux-austraux'
 if k==5:return 'pointe-levant' if x<432 else 'levant'
 raise ValueError(k)

anc_lists={k:[] for k in new_areas}
for name,item in legacy.items():
 k=item['id'];bits=rawindex==k; art,rec=patch(name,bits,True);used_refs.append(rec);world_H.alpha_composite(px(art))
 parts,obs=split(index==k);pl=np.array(px(parts.astype('int32')).resize(HER_SHAPE,N))
 assert len(obs)==item['silhouettes']
 for i,ob,n in obs:
  y,x=np.nonzero(parts[ob]==i);cx=x.mean()+ob[1].start;cy=y.mean()+ob[0].start;area=subarea(k,cx,cy)
  mask=place_mask(pl==i,HER);z=land_component(mask,area);anc_lists[area].append((z,n,(cx,cy)))
assert np.array_equal(np.asarray(world_H)[...,3]>0,rawindex>0)
placements['heritage']={'origine':list(HER),'dimensions':list(HER_SHAPE),'source':'image-14.png','silhouettes':sum(x['silhouettes'] for x in legacy.values())}
paste_layer(world_H,HER);save(world_H,C/'02-Anciens-Mondes.png')

extras=[('alizes','Archipel des Alizés','Archipel-des-Alizes',160,(1138,443),'Phare des Alizés'),('emeraude','Récifs d’Émeraude','Recifs-d-Emeraude',174,(1110,969),'Lagon d’Émeraude')]
extra_lists={}
for k,n,f,w,at,marker in extras:
 add_area(k,n,'Destiny 4');a,m=trim(G/(f+'.png'),True);im=pil_rgba(a,m);h=round(w*im.height/im.width);im=im.resize((w,h),N);alpha=np.asarray(im)[...,3]>0
 dis=nd.distance_transform_edt(np.asarray(terr)[...,3]==0);cx,cy=at
 free=sorted((dx*dx+dy*dy,cx-w//2+dx,cy-h//2+dy) for dx in range(-164,165,4) for dy in range(-320,285,4))
 for _,x,y in free:
  if 35<=x<=W-w-35 and 32<=y<=H-h-32 and float(dis[y:y+h,x:x+w][alpha].min())>=14:break
 else:raise ValueError(k+' / no free berth')
 p,obs=split(alpha);aa=[]
 for i,ob,c in obs:aa.append((land_component(place_mask(p==i,(x,y)),k),c))
 extra_lists[k]=sorted(aa,key=lambda z:-z[1]);paste_layer(im,(x,y));save(im,C/(f+'-Detoure.png'))
 placements[k]={'origine':[x,y],'dimensions':[w,h],'silhouettes':len(obs)};used_refs.append({'brut':f+'.png','sha256':digest(G/(f+'.png'))})

A=np.asarray(terr);r,g,b=np.moveaxis(A[...,:3].astype('int16'),-1,0);wet=(g-r>17)&(b-r>28)&(b>=g-15)&(r<150)&(labels_all>0)

# Site coordinates of this adaptation. Heritage names identify map zones, not assertions about game canon.
specs={
 'caps-ouest':[('col-iles-blanches','Col des Îles Blanches','Glace',(.53,.56))],
 'falaises-ouest':[('refuge-falaises','Refuge des Falaises','Falaises',(.29,.53)),('sources-sepia','Sources Sépia','Source',(.64,.44))],
 'escales-givre':[('escale-givre','Escale du Givre','Glace',(.52,.57))],
 'terres-centre':[('hautes-rives','Sentier des Hautes-Rives','Vallée',(.38,.53)),('bassin-anciens','Bassin des Anciens','Lac',(.65,.66))],
 'croissant-vents':[('croissant','Croissant des Vents','Cap',(.55,.56))],
 'cap-aurores':[('vigie-aurores','Vigie des Aurores','Vigie',(.49,.41))],
 'boreales':[('bastion-boreal','Bastion boréal','Crêtes',(.33,.39)),('vallee-sapins','Vallée des Sapins','Forêt',(.65,.57))],
 'austral':[('port-austral','Port Austral','Rivage',(.52,.29)),('bosquet-safran','Bosquet Safran','Bosquet',(.38,.64))],
 'anneaux-austraux':[('passe-australe','Passe Australe','Atoll',(.46,.61))],
 'pointe-levant':[('pointe','Pointe du Levant','Falaises',(.53,.54))],
 'levant':[('rivage-ivoire','Rivage d’Ivoire','Littoral',(.43,.60)),('foret-levant','Forêt du Levant','Forêt',(.69,.34))],
 'alizes':[('phare-alizes','Phare des Alizés','Vigie',(.59,.47)),('anse-rose','Anse Rose','Grès',(.34,.75))],
 'emeraude':[('lagon-emeraude','Lagon d’Émeraude','Mangrove',(.42,.39)),('arche-emeraude','Arche d’Émeraude','Récif',(.73,.65))]}
for area,sl in specs.items():
 comp=max(anc_lists[area],key=lambda z:z[1])[0] if area in anc_lists else extra_lists[area][0][0]
 z=labels_all==comp; lo,t,hi,m=bbox(z); local=z&~wet
 for j,(id,name,typ,anchor) in enumerate(sl):
  choose_comp=comp
  if j and area in extra_lists and len(extra_lists[area])>1 and extra_lists[area][1][1]>=120:
   choose_comp=extra_lists[area][1][0];z=labels_all==choose_comp;lo,t,hi,m=bbox(z);local=z&~wet
  cx,cy=nearest_pixel(local if local.any() else z,lo+anchor[0]*(hi-lo),t+anchor[1]*(m-t));region_info=new_areas.get(area,('', 'Un archipel de Destiny 4. Les traversées relient ses rives à Réverie et aux Anciens Mondes.'))
  atlas_sites.append({'id':id,'name':name,'area':area,'island':choose_comp,'category':typ,'region':region[area],'text':region_info[1], 'loc':[cx,cy],'point':[cx,cy],'new':True,'realm':realm[area]})

# Move the two landmark symbols to the new painted motifs, keep the rest of the old positions.
for s in atlas_sites:
 area=s['area'];s['realm']=realm[area];z=labels_all==s['island']
 target={'grotte-ocre':shift((518,576),BASE),'grotte-givre':shift((774,224),BASE)}.get(s['id'])
 if target:
  px0=list(nearest_pixel(z&~wet,*target));s['loc']=px0;s['point']=px0

# Ensure all named marker and arrival locations are in their own allocated cloud territory.
for s in atlas_sites:
 if s['island']:
  x,y=s['loc'];assert owners[y,x]==area_id[s['area']],(s['id'],x,y)

# Native Wonder Map cloud art; opaque veil is composed from its original solid hatch and cloud sprites.
cloud0=read(E/'Calques/Sprites-mobiles/Pose-00.png');cloud1=read(E/'Calques/Sprites-mobiles/Pose-01.png');bank=read(E/'Calques/Sprites-mobiles/Pose-11.png')
save(cloud0,C/'Nuage-00.png');save(cloud1,C/'Nuage-01.png')
fogimg=Image.new('RGBA',(W,H),(235,197,134,255));patch0=bank.crop((24,23,104,71)).resize((160,96),N)
for y in range(0,H,96):
 for x in range(0,W,160):fogimg.alpha_composite(patch0,(x,y))
for row,y in enumerate(range(-20,H,82)):
 for col,x in enumerate(range(-28,W,144)):
  art=cloud0 if (row+col)%4!=0 else cloud1;n=[138,170,110,152][(row*3+col)%4];v=art.resize((n,round(art.height*n/art.width)),N)
  v.putalpha(v.getchannel('A').point(lambda p:p*.53));fogimg.alpha_composite(v,(x+(row%2)*53+((col*17+row*11)%25),y+(col*13)%22))
veil= fogimg.convert('RGB');save(veil,C/'Voile.png')

# Use the same validated parchment with a continuous enlarged frame (not two pasted sheet seams).
parchment=read(B/'Calques/00-Parchemin.png').resize((W,H),N);full=parchment.copy();full.alpha_composite(terr);save(full.convert('RGB'),C/'00-Monde.png')
mag=Image.new('RGBA',(W,H),'#ff00ff');mag.alpha_composite(terr);save(mag.convert('RGB'),D/'Brut-Destiny-4-Magenta.png')

def cloud_mask(area):
 n=area_id[area];mat=owners==n;assert mat.any(),area
 x,y,x2,y2=bbox(mat); w,h=x2-x,y2-y; margin=min(66,max(27,round(.22*min(w,h)+26)))
 r=margin+14;u,v=max(0,x-r),max(0,y-r);U,V=min(W,x2+r),min(H,y2+r)
 spec=np.s_[v:V,u:U]; m=mat[spec]; own=owners[spec];dist=nd.distance_transform_edt(~m)
 # Scallop the cloud shore at chart scale. Protected pixels in another area are never included.
 yy,xx=np.ogrid[v:V,u:U]; p=margin+5*np.cos(xx/12.8+yy/16.7)+3*np.sin((xx-yy)/8.1)
 alpha=(np.clip((p+3-dist)/5,0.,1.)*255).astype(np.uint8)
 other=(own>0)&(own!=n);zone_edges=nd.distance_transform_edt(~other)<=8 if other.any() else other
 alpha[zone_edges]=0;alpha[m]=255;assert not alpha[other].any()
 file=f'Entrees-{area}.png';im=Image.new('RGBA',(alpha.shape[1],alpha.shape[0]),(255,255,255,0));im.putalpha(px(alpha));save(im,C/file)
 return {'asset':'zone_'+area,'file':file,'x':u,'y':v,'w':U-u,'h':V-v,'c':[(x+x2)//2,(y+y2)//2], 'largeur_terres':w,'hauteur_terres':h,'region':region[area],'realm':realm[area],'pixels_territoire':int(mat.sum())}

zones={k:cloud_mask(k) for k in area_id};assert len(zones)==24,(len(zones),region.keys())
spiral=shift([base['glyphs']['spirale']['cx'],base['glyphs']['spirale']['cy']],BASE)
oldports={18:(223,529),4:(399,348),1:(749,221),13:(684,539),19:(332,503),9:(472,271),14:(505,348),16:(568,421)}
for old,crd in oldports.items():
 if old in converts:hints[converts[old]]=shift(crd,BASE)
for q in base['archipels']:
 lab=converts.get(q['main']);
 if lab:hints[lab]=shift(q['port']['terre'],BASE)
travel,ports=navigation(labels_all,wet,atlas_sites,hints,spiral)

art={'fond':'00-Monde.png','voile':'Voile.png','cloud0':'Nuage-00.png','cloud1':'Nuage-01.png'}
for k,f in base['art'].items():
 if k=='barque' or k in ('red','yellow','dim','arrowA') or (k.startswith('p') and k[1:].isdigit()):
  shutil.copyfile(B/'Calques'/f,C/f);art[k]=f
for z in zones.values():art[z['asset']]=z['file']
shutil.copyfile(B/'Calques'/base['audio'],C/base['audio'])
order=['grotte-ocre','houle','grotte-amethystes','signal-voiles','grotte-ramures','volcan-geant','grotte-givre','bois-petales','bourg-ecume','atoll-coraux','lagon-emeraude','phare-alizes','refuge-falaises','col-iles-blanches','bassin-anciens','escale-givre','croissant','vigie-aurores','bastion-boreal','foret-levant','pointe','passe-australe','port-austral']
assert {s['area'] for s in atlas_sites if s['id'] in order}==set(zones)-{'reve'} and len(order)==len(zones)-1
out={'version':4,'width':W,'height':H,'regions':region,'realms':realm,'zones':zones,'sites':atlas_sites,'edges':travel,'art':art,'audio':base['audio'],'poses':base['poses'],'walk':base['walk'],'circuits':{**base['circuits'],'nuages':order},'placements':placements,'nuages':{'duree':1.38,'depart':'reve'}}
savej(D/'Atlas.json',out)
# Verify that every played region is accessible across the two formerly separate groups of maps.
reach={'reverie'}
for _ in range(len(travel)):
 size=len(reach)
 for e in travel:
  if e['a'] in reach or e['b'] in reach:reach|={e['a'],e['b']}
 if len(reach)==size:break
assert set(s['id'] for s in atlas_sites)<=reach
savej(D/'Verification-geographie.json',{'statut':'PASS','dimensions':[W,H],'silhouettes_image_4':placements['heritage']['silhouettes'],'silhouettes_ajouts_en_mer':sum(placements[q]['silhouettes'] for q in ('alizes','emeraude')),'silhouettes_Destiny_inchangees':26,'zones':len(zones),'sites':len(atlas_sites),'troncons':len(travel),'ports':len(ports),'zones_inexplorees_entierement_masquees':True,'art_brut_genere':used_refs,'placements':placements})
save(pil_rgba(terrain_base[...,:3],orig_mask),C/'Terres-Destiny-Alpha.png')
# Two replacement continents alone, on the requested separate key colour for studio use.
sr,ds=read(C/'Seracine-Detoure.png'),read(C/'Torselune-Detoure.png');sheet=Image.new('RGBA',(790,580),'#ff00ff');sheet.alpha_composite(sr,((790-sr.width)//2,34));sheet.alpha_composite(ds,((790-ds.width)//2,279));save(sheet.convert('RGB'),D/'Desert-et-Glace-Magenta.png')
print('PASS',len(zones),'zones',len(atlas_sites),'repères',len(ports),'embarcadères',len(travel),'trajets,',placements['heritage']['silhouettes'],'silhouettes image 4')
