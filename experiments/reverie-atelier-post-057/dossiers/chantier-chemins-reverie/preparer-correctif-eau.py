from pathlib import Path
s=Path('harmoniser-herbe.py').read_text().replace('correctif-herbe-et-chemins-0.5.0','correctif-falaises-eau-0.5.0').replace('Reverie_Herbe_Chemins_050','Reverie_Raccords_Eau_050').replace('correctif-herbe-et-chemins-Reverie-0.5.0-ESSAI.zip','correctif-falaises-et-cascades-Reverie-0.5.0-ESSAI.zip')
marker='after=Image.fromarray(b0);a=np.array(img);b=np.array(after);change='
inject='''# Falaises : ne remplir que les pixels alpha zéro relevés, par un pixel voisin
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
after=Image.fromarray(b0);a=np.array(img);b=np.array(after);change='''
assert marker in s;s=s.replace(marker,inject)
s=s.replace("'tuiles':len(atlas),'cartes':{}", "'tuiles':len(atlas),'pixels_transparents_falaises':holes_filled,'cadences':{'cascade_kecleon':'10 -> 6','ecumes':'60 -> 20'},'cartes':{}")
start=s.index(' # Reconstruction qui copie octet pour octet chaque segment non modifié.');end=s.index(" manifest['cartes'][path.name]",start)
replacement=''' # Reconstruction par colonnes ciblées, les autres octets restent identiques.
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
'''
s=s[:start]+replacement+s[end:]
s=s.replace("'colonnes_recrites':len(splices)","'colonnes_recrites':len(splices),'ecumes_accelerees':speed['ecume'],'tuiles_cascade_kecleon_accelerees':speed['cascade_kecleon']")
start=s.index('# Comparaison des retouches');end=s.index('with zipfile.ZipFile(',start)
s=s[:start]+'''# Planche des trous de falaises : le rose révèle les pixels auparavant transparents.
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
'''+s[end:]
Path('corriger-falaises-cascades.py').write_text(s)
