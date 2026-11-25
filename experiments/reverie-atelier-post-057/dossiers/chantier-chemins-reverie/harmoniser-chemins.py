#!/usr/bin/env python3
"""Raccords locaux C05/C06 sur les payloads officiels. Ne modifie jamais la base."""
from pathlib import Path
from PIL import Image,ImageChops,ImageDraw,ImageFont
import numpy as np,io,struct,gzip,json,hashlib,zipfile,sys,collections
import ijson
R=Path('/home/user/chantier-chemins-reverie'); B=R/'base'; O=R/'correctif-chemins-et-sable-0.5.0'; (O/'payload').mkdir(parents=True,exist_ok=True);(O/'game/Content/Tile').mkdir(parents=True,exist_ok=True);(O/'art/reverie/tilesheets').mkdir(parents=True,exist_ok=True)
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
after=Image.fromarray(b0);a=np.array(img);b=np.array(after);change=np.any(a!=b,axis=2);ys,xs=np.where(change)
# Les nouvelles tuiles ne comprennent que les pixels changés, avec transparence ailleurs.
patches={}; atlas=[];lookup={}
for cy,cx in sorted(set(zip((ys//8).tolist(),(xs//8).tolist()))):
 old=a[cy*8:cy*8+8,cx*8:cx*8+8];new=b[cy*8:cy*8+8,cx*8:cx*8+8];m=np.any(old!=new,axis=2)
 if not m.any():continue
 p=np.zeros((8,8,4),dtype=np.uint8);p[m]=new[m];key=p.tobytes()
 if key not in lookup:lookup[key]=len(atlas);atlas.append(Image.fromarray(p))
 patches[(cx,cy)]=lookup[key]
N='Reverie_Chemins_Sable_050'; header=8+16*len(atlas);body=bytearray();rec=[];sheet=Image.new('RGBA',(256,8*((len(atlas)+31)//32)))
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
manifest={'commit_base':'a2db214dc89e675347f670f26594df92158fc9d9','zones':['C01','C03','C05','C06','herbe-isolee','ligne-sable-544','touffe-rognée'],'donneur_reverie':[26,1191,46,1207],'cases_modifiees':len(patches),'pixels_modifies_phase0':int(change.sum()),'tuiles':len(atlas),'cartes':{}}
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
 # Reconstruction qui copie octet pour octet chaque segment non modifié.
 original=gzip.decompress(path.read_bytes());s=original.decode('utf-8'); start=s.index('"Name":"Objects Over"'); i=s.index('"Tiles":[',start)+len('"Tiles":[');decoder=json.JSONDecoder();splices=[]
 for cx in range(200):
  assert s[i]=='[',(path.name,cx,s[i:i+10]); col,end=decoder.raw_decode(s,i)
  relevant=[(cy,p) for (x,cy),p in patches.items() if x==cx]
  if relevant:
   for cy,p in relevant:
    cell=col[cy]
    if not cell:cell.update({'AutoTileset':'','Associates':[],'Layers':[],'NeighborCode':-1})
    cell.setdefault('Layers',[]).append({'Frames':[{'Sheet':N,'TexLoc':{'X':p%32,'Y':p//32}}],'FrameLength':60})
   replacement=json.dumps(col,ensure_ascii=False,separators=(',',':'));splices.append((i,end,replacement))
  i=end
  if cx<199:assert s[i]==',';i+=1
 out=[];pos=0
 for lo,hi,replacement in splices:out.extend([s[pos:lo],replacement]);pos=hi
 out.append(s[pos:]);modified=''.join(out).encode('utf-8');dest=O/'payload'/path.name;dest.write_bytes(gzip.compress(modified,compresslevel=9,mtime=0));assert gzip.decompress(dest.read_bytes())==modified
 # Contrôle sémantique de chaque colonne réécrite : uniquement les cellules visées.
 for lo,hi,replacement in splices:
  oldcol=json.loads(s[lo:hi]);newcol=json.loads(replacement)
  for cy,(old,new) in enumerate(zip(oldcol,newcol)):
   if old!=new:
    assert new.get('Layers',[])[:-1]==old.get('Layers',[]) and new['Layers'][-1]['Frames'][0]['Sheet']==N
    assert {k:v for k,v in old.items() if k!='Layers'}=={k:v for k,v in new.items() if k!='Layers'} or old=={}
 manifest['cartes'][path.name]={'sha256_avant':hashlib.sha256(original).hexdigest(),'sha256_apres':hashlib.sha256(modified).hexdigest(),'colonnes_recrites':len(splices)}
assert len(manifest['cartes'])==10
(O/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
# Comparaison 6 défauts, coordonnées d'origine, agrandissement sans interpolation.
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',18);small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',14)
can=Image.new('RGB',(1050,7*285+70),'#1b2222');d=ImageDraw.Draw(can);d.text((24,14),'Réverie Town — bordures et nuances de sable',font=font,fill='white');d.text((24,40),'Rendu phase 0 sans personnages · avant et après · pixels natifs agrandis',font=small,fill='#c8d5cb')
views=[('C01 · raccord en angle',190,1585),('C03 · nuance rognée',1068,2588),('Carré d’herbe isolé',996,1580),('Ligne de sable rognée',548,2233),('Touffe rognée',80,571),('C05 · extrémité sud',100,2940),('C06 · extrémité sud',700,2940)]
for row,(name,x,y) in enumerate(views):
 for col,(label,im) in enumerate([('AVANT',img),('APRÈS',after)]):
  x0=20+col*520;y0=70+row*285;d.text((x0,y0),name+' — '+label,font=font,fill='#f4ca78');crop=im.crop((x-52,y-30,x+52,y+32)).convert('RGB').resize((416,248),Image.Resampling.NEAREST);can.paste(crop,(x0,y0+29))
can.save(R/'avant-apres-chemins-et-sable.png')
(O/'LISEZ-MOI.txt').write_text("""Correctif sources Réverie 0.5.0 — expérimental, non publié

Base indispensable : commit a2db214dc89e675347f670f26594df92158fc9d9. Après sauvegarde de votre checkout et de vos parties, copier payload/, game/Content/Tile/ et art/reverie/tilesheets/ à la racine du projet Destiny. Exécuter python tools/build_tile_index.py dans le checkout COMPLET pour reconstruire l'index avec toutes les banques présentes. Ne pas construire l'index depuis l'échantillon limité de la sauvegarde. Redémarrer et recharger la carte.

Corrige C05/C06, C01/C03, un carré d'herbe isolé, une ligne de sable rognée et une touffe coupée restaurée. Les teintes et pixels proviennent de Réverie ; aucun élément graphique Metano. Collisions, scripts, objets et durées d'animation inchangés. Dix payloads sont modifiés car ils partagent ces coordonnées graphiques. La banque ajoute uniquement des pixels sur les cases explicitement corrigées, dans Objects Over. Autres données inchangées.

Des zones détectées n'ont pas été corrigées quand elles pouvaient être des ombres ou décorations ; l'inspection statique ne peut pas garantir l'absence de tous les défauts. Ni éditeur, ni jeu, ni sauvegarde réelle, ni CI testés. Pour annuler : restaurer les dix payloads du ZIP de sauvegarde, supprimer la banque et le PNG ajoutés et régénérer l'index complet.
""")
with zipfile.ZipFile(R/'correctif-chemins-et-sable-Reverie-0.5.0-ESSAI.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in sorted(O.rglob('*')):
  if p.is_file():z.write(p,p.relative_to(O))
with zipfile.ZipFile(R/'correctif-chemins-et-sable-Reverie-0.5.0-ESSAI.zip') as z:assert z.testzip() is None
print('Terminé',len(patches),'cases',len(atlas),'tuiles',int(change.sum()),'pixels',flush=True)
