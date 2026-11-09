#!/usr/bin/env python3
"""Raccords locaux C05/C06 sur les payloads officiels. Ne modifie jamais la base."""
from pathlib import Path
from PIL import Image,ImageChops,ImageDraw,ImageFont
import numpy as np,io,struct,gzip,json,hashlib,zipfile,sys,collections
import ijson
R=Path('/home/user/chantier-chemins-reverie'); B=R/'base'; O=R/'correctif-falaises-eau-0.5.0'; (O/'payload').mkdir(parents=True,exist_ok=True);(O/'game/Content/Tile').mkdir(parents=True,exist_ok=True);(O/'art/reverie/tilesheets').mkdir(parents=True,exist_ok=True)
img=Image.open(R/'reverie-0.5.0-rendu-phase0.png').convert('RGBA'); after=img.copy()
# Bordure issue d'un chemin Réverie existant, coin inférieur gauche puis miroir.
left=img.crop((26,1191,46,1207));right=left.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
for x in (80,680):after.paste(left,(x,2936));after.paste(right,(x+20,2936))
a=np.array(img);b=np.array(after);change=np.any(a!=b,axis=2); ys,xs=np.where(change); assert len(xs)>0 and xs.min()>=80 and xs.max()<720 and ys.min()>=2936 and ys.max()<2952
# Raccord inférieur C01 : adoucir l'arrêt rectiligne au moyen de sable de Réverie.
# Les teintes proviennent du même bord que le premier correctif ; aucun pixel d'objet.
a0=np.array(img); b0=np.array(after)
b0[1584:1592,208:216]=a0[1584:1592,200:208]
src=a0[1193:1201,46:86];target=b0[1584:1592,176:216]
m=(src[:,:,0]>220)&(src[:,:,0]>src[:,:,1]+6)&(src[:,:,2]>90);target[m]=src[m]
# C03 : fragment de sable et deux pixels d'herbe recadrés au milieu du chemin.
b0[2584:2596,1064:1072]=a0[2584:2596,1056:1064]
# Carreau d'herbe isolé au milieu du sable ; source sable mitoyen.
b0[1576:1584,992:1000]=a0[1576:1584,984:992]
# Reconstituer la moitié gauche de la touffe rognée à l’aide d’une touffe Réverie identique et complète.
b0[568:576,72:80]=a0[2240:2248,336:344]
# Coutures de teinte sous forme d'une ligne verticale isolée en pleine route.
b0[2216:2248,544:552]=a0[2216:2248,536:544]
# HERBE : les pixels propres sont reconstruits depuis la tuile Réverie placée en dessous.
sheet=Image.open(B/'art/reverie/tilesheets/Reverie_Geo_01_Sol_herbe.png').convert('RGBA')
def clean_tile(tx,ty):return np.array(sheet.crop((tx*8,ty*8,tx*8+8,ty*8+8)))
# G01 : restes d'un composant objet près d'une fleur ; utiliser le calque Base intact.
base=np.array(Image.open(R/'calques-publies-png/01_Base.png').convert('RGBA'))
b0[496:512,160:168]=base[496:512,160:168]
# G02 : deux tuiles d'herbe sous une bordure rose coupée en plein pré.
t=clean_tile(31,205)
b0[2552:2560,400:408]=t;b0[2552:2560,408:416]=t
# G03 : trait vertical, sans toucher aux cellules de fleur animée à y >= 352.
t=clean_tile(477,189)
for yy in range(301,352):b0[yy,371]=t[yy%8,371%8]
# G04 : ligne verte horizontale isolée sous l'arbre, pas d'objet à ces pixels.
t=clean_tile(19,84)
for xx in range(1189,1207):b0[2256,xx]=t[2256%8,xx%8]
# G05 : ligne foncée et résidus pastel, cases d'herbe seules sans animation.
t=clean_tile(19,84)
for xx in range(1008,1024):b0[2303,xx]=t[2303%8,xx%8]
b0[2304:2312,1008:1016]=clean_tile(39,218)
# Falaises : ne remplir que les pixels alpha zéro relevés, par un pixel voisin
# opaque de la même image Réverie, sans lissage, interpolation ou nouvelle couleur.
from scipy.ndimage import distance_transform_edt
holes=json.loads((R/'trous-alpha-candidats.json').read_text());ignored={(1118,1702),(1048,1720),(1591,807)};holes_filled=0
for x,y,w,h,n,rock in holes:
 if (x,y) in ignored:continue
 x1=max(0,x-5);y1=max(0,y-5);x2=min(1600,x+w+5);y2=min(4000,y+h+5);crop=a0[y1:y2,x1:x2];transparent=crop[:,:,3]==0
 iy,ix=distance_transform_edt(transparent,return_distances=False,return_indices=True)
 for yy in range(y,y+h):
  for xx in range(x,x+w):
   if a0[yy,xx,3]!=0:continue
   sy=y1+int(iy[yy-y1,xx-x1]);sx=x1+int(ix[yy-y1,xx-x1]);assert a0[sy,sx,3]==255
   b0[yy,xx]=a0[sy,sx];holes_filled+=1
print('Pixels de falaise transparents réparés',holes_filled,flush=True)
after=Image.fromarray(b0);a=np.array(img);b=np.array(after);change=np.any(a!=b,axis=2);ys,xs=np.where(change)
# Les nouvelles tuiles ne comprennent que les pixels changés, avec transparence ailleurs.
patches={}; atlas=[];lookup={}
for cy,cx in sorted(set(zip((ys//8).tolist(),(xs//8).tolist()))):
 old=a[cy*8:cy*8+8,cx*8:cx*8+8];new=b[cy*8:cy*8+8,cx*8:cx*8+8];m=np.any(old!=new,axis=2)
 if not m.any():continue
 p=np.zeros((8,8,4),dtype=np.uint8);p[m]=new[m];key=p.tobytes()
 if key not in lookup:lookup[key]=len(atlas);atlas.append(Image.fromarray(p))
 patches[(cx,cy)]=lookup[key]
N='Reverie_Raccords_Eau_050'; header=8+16*len(atlas);body=bytearray();rec=[];sheet=Image.new('RGBA',(256,8*((len(atlas)+31)//32)))
for i,im in enumerate(atlas):
 x=i%32;y=i//32;out=io.BytesIO();im.save(out,format='PNG');data=out.getvalue();rec.append((x,y,header+len(body)));body+=struct.pack('<q',len(data))+data;sheet.paste(im,(x*8,y*8))
raw=struct.pack('<ii',8,len(atlas))+b''.join(struct.pack('<iiq',*v) for v in rec)+body
(O/'game/Content/Tile'/f'{N}.tile').write_bytes(raw);sheet.save(O/'art/reverie/tilesheets'/f'{N}.png')
for i,(_,_,off) in enumerate(rec):
 n=struct.unpack_from('<q',raw,off)[0];assert Image.open(io.BytesIO(raw[off+8:off+8+n])).convert('RGBA').tobytes()==atlas[i].tobytes()
# Réaliser la composition native des seules cases modifiées pour chaque carte et
# s'assurer que toutes phases et tous calques affectés sont statiques et identiques.
cache={};banks={}
def tile(fr):
 name=fr.get('Sheet',''); x=fr['TexLoc']['X'];y=fr['TexLoc']['Y'];key=(name,x,y)
 if not name:return None
 if key in cache:return cache[key]
 if name not in banks:
  data=(B/'game/Content/Tile'/f'{name}.tile').read_bytes();size,n=struct.unpack_from('<ii',data);assert size==8
  banks[name]=(data,{struct.unpack_from('<iiq',data,8+16*i)[:2]:struct.unpack_from('<iiq',data,8+16*i)[2] for i in range(n)})
 data,index=banks[name];off=index[(x,y)];n=struct.unpack_from('<q',data,off)[0];cache[key]=Image.open(io.BytesIO(data[off+8:off+8+n])).convert('RGBA');return cache[key]
manifest={'commit_base':'a2db214dc89e675347f670f26594df92158fc9d9','zones':['C01','C03','C05','C06','herbe-isolee','ligne-sable-544','touffe-rognée','herbe-fragment-160','herbe-fragment-400','herbe-trait-371','herbe-trait-1189','herbe-trait-1008'],'donneur_reverie':[26,1191,46,1207],'cases_modifiees':len(patches),'pixels_modifies_phase0':int(change.sum()),'tuiles':len(atlas),'pixels_transparents_falaises':holes_filled,'cadences':{'cascade_kecleon':'10 -> 6','ecumes':'60 -> 20'},'cartes':{}}
for path in sorted((B/'payload').glob('*.gz')):
 print('Vérification',path.name,flush=True); comps={cell:Image.new('RGBA',(8,8)) for cell in patches};upper=[];layernames=[]
 with gzip.open(path,'rb') as f:
  if f.read(3)!=b'\xef\xbb\xbf':f.seek(0)
  for li,layer in enumerate(ijson.items(f,'Object.Layers.item')):
   layernames.append(layer['Name'])
   for (cx,cy),pi in patches.items():
    for anim in layer['Tiles'][cx][cy].get('Layers',[]):
     frames=anim.get('Frames',[])
     if not frames:continue
     assert len(frames)==1,(path,li,cx,cy,'animation présente')
     im=tile(frames[0]);
     if im:
      comps[(cx,cy)].alpha_composite(im)
      if li>8:
       changed_alpha=np.array(atlas[pi])[:,:,3]>0;above_alpha=np.array(im)[:,:,3]>0
       assert not np.any(changed_alpha & above_alpha),(path,li,cx,cy,'surimpression')
 assert len(layernames)==11 and layernames[8]=='Objects Over',layernames
 for (cx,cy),im in comps.items():
  expected=img.crop((cx*8,cy*8,cx*8+8,cy*8+8));assert im.tobytes()==expected.tobytes(),(path.name,cx,cy,'rendu différent de la référence')
  im.alpha_composite(atlas[patches[(cx,cy)]]);assert im.tobytes()==after.crop((cx*8,cy*8,cx*8+8,cy*8+8)).tobytes()
 # Reconstruction par colonnes ciblées, les autres octets restent identiques.
 original=gzip.decompress(path.read_bytes());s=original.decode('utf-8');decoder=json.JSONDecoder();splices=[];speed=collections.Counter()
 def foam(anim):
  fr=anim.get('Frames',[]);v=[f for f in fr if f.get('Sheet')]
  return len(fr)==6 and bool(v) and all(f['Sheet']=='Reverie_Geo_13_Objets_frames' and 0<=f['TexLoc']['X']<56 and 40<=f['TexLoc']['Y']<56 for f in v)
 def waterfall(anim,cx,cy,li):
  fr=anim.get('Frames',[])
  return li==2 and 584<=8*cx<=640 and 816<=8*cy<=840 and len(fr)==4 and all(f.get('Sheet')=='Reverie_Geo_11_Cascades_frames' for f in fr)
 def transform(col,cx,li):
  altered=False
  for cy,cell in enumerate(col):
   seq=cell.get('Layers',[])
   for anim in seq:
    if foam(anim):
     assert anim['FrameLength']==60,(path,li,cx,cy,anim['FrameLength']);anim['FrameLength']=20;speed['ecume']+=1;altered=True
    elif waterfall(anim,cx,cy,li):
     assert anim['FrameLength']==10,(path,li,cx,cy,anim['FrameLength']);anim['FrameLength']=6;speed['cascade_kecleon']+=1;altered=True
   p=patches.get((cx,cy)) if li==8 else None
   if p is not None:
    if not cell:cell.update({'AutoTileset':'','Associates':[],'Layers':[],'NeighborCode':-1})
    cell.setdefault('Layers',[]).append({'Frames':[{'Sheet':N,'TexLoc':{'X':p%32,'Y':p//32}}],'FrameLength':60});altered=True
  return altered
 target_layers=[1,2,6,7,8];cursor=s.index('"Layers":[{"Name":"Base"')
 for li in target_layers:
  name=layernames[li];start=s.index('"Name":'+json.dumps(name,ensure_ascii=False),cursor);i=s.index('"Tiles":[',start)+len('"Tiles":[');cursor=i
  for cx in range(200):
   assert s[i]=='[',(path.name,li,cx,s[i:i+10]);col,end=decoder.raw_decode(s,i)
   if transform(col,cx,li):splices.append((i,end,json.dumps(col,ensure_ascii=False,separators=(',',':')),li,cx))
   i=end
   if cx<199:assert s[i]==',';i+=1
 assert speed['ecume']>250 and speed['cascade_kecleon']==32,(path.name,speed)
 out=[];pos=0
 for lo,hi,replacement,li,cx in splices:out.extend([s[pos:lo],replacement]);pos=hi
 out.append(s[pos:]);modified=''.join(out).encode('utf-8');dest=O/'payload'/path.name;dest.write_bytes(gzip.compress(modified,compresslevel=9,mtime=0));assert gzip.decompress(dest.read_bytes())==modified
 # Test indépendant : toute différence de cellule doit être soit un ajout de
 # tuile transparente autorisé, soit un changement de durée ciblé, rien d'autre.
 for lo,hi,replacement,li,cx in splices:
  oldcol=json.loads(s[lo:hi]);newcol=json.loads(replacement)
  for cy,(old,new) in enumerate(zip(oldcol,newcol)):
   if old==new:continue
   oldseq=old.get('Layers',[]);newseq=new.get('Layers',[]);expected_extra=int(li==8 and (cx,cy) in patches)
   assert len(newseq)==len(oldseq)+expected_extra,(path.name,li,cx,cy)
   if expected_extra:assert newseq[-1]['Frames'][0]['Sheet']==N
   for aa,bb in zip(oldseq,newseq):
    if aa==bb:continue
    assert aa.get('Frames')==bb.get('Frames') and {k:v for k,v in aa.items() if k!='FrameLength'}=={k:v for k,v in bb.items() if k!='FrameLength'}
    assert (foam(aa) and aa['FrameLength']==60 and bb['FrameLength']==20) or (waterfall(aa,cx,cy,li) and aa['FrameLength']==10 and bb['FrameLength']==6),(li,cx,cy)
   assert {k:v for k,v in old.items() if k!='Layers'}=={k:v for k,v in new.items() if k!='Layers'} or old=={}
 manifest['cartes'][path.name]={'sha256_avant':hashlib.sha256(original).hexdigest(),'sha256_apres':hashlib.sha256(modified).hexdigest(),'colonnes_recrites':len(splices),'ecumes_accelerees':speed['ecume'],'tuiles_cascade_kecleon_accelerees':speed['cascade_kecleon']}
assert len(manifest['cartes'])==10
(O/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
# Planche des trous de falaises : le rose révèle les pixels auparavant transparents.
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',18);small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',14)
views=[('Falaise ouest',33,872),('Falaise sud',396,2015),('Raccord résidentiel',840,2355),('Raccord est',1359,1920)]
can=Image.new('RGB',(1040,len(views)*280+70),'#1b2222');d=ImageDraw.Draw(can);d.text((20,12),'Réverie — trous transparents dans les falaises',font=font,fill='white');d.text((20,40),'Avant : rose = transparence ; après : pixels Réverie voisins. Aucun décor déplacé.',font=small,fill='#c8d5cb')
for row,(name,x,y) in enumerate(views):
 for col,(label,im) in enumerate([('AVANT',img),('APRÈS',after)]):
  x0=20+col*510;y0=70+row*280;d.text((x0,y0),name+' — '+label,font=font,fill='#f4ca78');crop=im.crop((x-48,y-30,x+48,y+30));bg=Image.new('RGBA',crop.size,(255,0,255,255));bg.alpha_composite(crop);can.paste(bg.convert('RGB').resize((384,240),Image.Resampling.NEAREST),(x0,y0+28))
can.save(R/'avant-apres-falaises.png')
(O/'LISEZ-MOI.txt').write_text("""Correctif expérimental Réverie 0.5.0 — non publié

Base indispensable : commit a2db214dc89e675347f670f26594df92158fc9d9. Sauvegarder le checkout et les parties. Copier payload/, game/Content/Tile/ et art/reverie/tilesheets/ à la racine du projet Destiny, puis exécuter python tools/build_tile_index.py dans le checkout COMPLET. Redémarrer et recharger la carte.

Inclut les correctifs antérieurs des chemins, herbes et touffe ; il remplace les archives précédentes, ne pas les empiler. Répare les trous transparents statiques de falaises avec pixels voisins issus de Réverie. Cascade derrière Kecleon FrameLength 10→6, écumes détectées 60→20 ; frames et ordre inchangés, pas d'autres cadences modifiées. Dimensions, scripts, objets, obstacles et autres séquences inchangés. Pas de graphisme Metano.

Le bassin sud est un aperçu autonome et n'est PAS dans ce patch, en attente de validation et de vérification des collisions. Des imperfections peuvent subsister. Tests structure et rendu statique seulement ; ni jeu, ni sauvegarde réelle, ni CI. Pour annuler : restaurer les dix payloads de la sauvegarde, supprimer la banque et le PNG ajoutés, régénérer l'index complet.
""")
with zipfile.ZipFile(R/'correctif-falaises-et-cascades-Reverie-0.5.0-ESSAI.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in sorted(O.rglob('*')):
  if p.is_file():z.write(p,p.relative_to(O))
with zipfile.ZipFile(R/'correctif-falaises-et-cascades-Reverie-0.5.0-ESSAI.zip') as z:assert z.testzip() is None
print('Terminé',len(patches),'cases',len(atlas),'tuiles',int(change.sum()),'pixels',flush=True)
