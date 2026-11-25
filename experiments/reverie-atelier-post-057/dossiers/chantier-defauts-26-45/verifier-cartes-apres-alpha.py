from pathlib import Path
import gzip,ijson,json,collections,hashlib
R=Path(__file__).resolve().parent;BASE=R/'base/payload';FINAL=R/'corrections-alpha-en-cours/payload'
points=[(648,312),(648,416),(664,288),(856,288),(872,328),(880,376),(888,416)]
banks={'Reverie_Ondulations_Rochers_056','Reverie_Raccord_Etang_056','Reverie_Animation_Berge_056','Reverie_Animation_Eaux_056','Reverie_Raccord_Escalier_056','Reverie_Raccord_Chemin30_056','Reverie_Fond_Transparences_056'}
bridge={1056:1032,1064:1040,1072:1048,1080:1056,1136:1064,1144:1072,1152:1080,1160:1088}
def rr(name,x,y):return {'Sheet':name,'TexLoc':{'X':x,'Y':y}}
restore={0:rr('Reverie_Geo_14_Paysages_composites',91,112),1:rr('Reverie_Geo_14_Paysages_composites',91,113),2:rr('Reverie_Geo_12_Eaux_frames',172,157),3:rr('Reverie_Geo_12_Eaux_frames',173,157),4:rr('Reverie_Geo_12_Eaux_frames',200,157)}
def normalize(c,layer,x,y):
 if not c:return c
 q=json.loads(json.dumps(c));L=q.get('Layers',[])
 if layer=='River' and y==1104//8 and x*8 in bridge:
  assert L and len(L[-1]['Frames'])==4 and L[-1]['FrameLength']==10
  L.pop()
 kept=[]
 for a in L:
  fs=a.get('Frames',[])
  if fs and all(fr.get('Sheet') in banks for fr in fs):continue
  for i,fr in enumerate(fs):
   if fr.get('Sheet')=='Reverie_Rochers_Eau_056':
    assert fr['TexLoc']['Y']==0;fs[i]=restore[fr['TexLoc']['X']]
  kept.append(a)
 if 'Layers' in q:q['Layers']=kept
 if not kept and q=={'AutoTileset':'','Associates':[],'Layers':[],'NeighborCode':-1}:return {}
 return q
results=[]
for p in sorted(BASE.glob('*.gz')):
 print('Comparaison intégrale',p.name,flush=True)
 with gzip.open(p,'rb') as f,gzip.open(FINAL/p.name,'rb') as g:
  f.read(3);g.read(3);it=ijson.items(f,'Object.Layers.item');jt=ijson.items(g,'Object.Layers.item');different=collections.Counter();count=0
  for old,new in zip(it,jt,strict=True):
   assert {k:v for k,v in old.items() if k!='Tiles'}=={k:v for k,v in new.items() if k!='Tiles'}
   assert len(old['Tiles'])==len(new['Tiles'])==200;name=old['Name']
   for x,(oc,nc) in enumerate(zip(old['Tiles'],new['Tiles'],strict=True)):
    for y,(a,b) in enumerate(zip(oc,nc,strict=True)):
     if a!=b:
      different[name]+=1
      assert a==normalize(b,name,x,y),(p.name,name,x*8,y*8,a,normalize(b,name,x,y));count+=1
  print('PASS',dict(different),flush=True)
  results.append({'carte':p.name,'cases_differentes':dict(different),'nombre':count,'sha256_final':hashlib.sha256((FINAL/p.name).read_bytes()).hexdigest()})
assert len(results)==10
(R/'audit-pixel-integral/verification-cartes-apres.json').write_text(json.dumps(results,ensure_ascii=False,indent=2));print('PASS : toutes les cellules non modifiées sont identiques ; toutes les cellules modifiées se ramènent aux données de 0.5.5 en retirant les ajouts ciblés.',flush=True)
