from pathlib import Path
import gzip,ijson,json,hashlib,collections
R=Path(__file__).resolve().parent;A=R/'base/payload';B=R/'correction-locale/payload';K=R/'reprise-raccord-51';K.mkdir(exist_ok=True);maps={};h=lambda b:hashlib.sha256(b).hexdigest()
for p in sorted(A.glob('*.gz')):
 print('Vérification',p.name,flush=True);a=p.read_bytes();b=(B/p.name).read_bytes();changes=[]
 with gzip.open(p,'rb') as f,gzip.open(B/p.name,'rb') as g:
  assert f.read(3)==g.read(3)==b'\xef\xbb\xbf'
  for old,new in zip(ijson.items(f,'Object.Layers.item'),ijson.items(g,'Object.Layers.item'),strict=True):
   assert {k:v for k,v in old.items() if k!='Tiles'}=={k:v for k,v in new.items() if k!='Tiles'}
   for x,(ac,bc) in enumerate(zip(old['Tiles'],new['Tiles'],strict=True)):
    for y,(v,w) in enumerate(zip(ac,bc,strict=True)):
     if v!=w:
      assert old['Name']=='Base' and 179<=x<=185 and 73<=y<=74,(p.name,old['Name'],x,y)
      assert w['Layers'][:-1]==v.get('Layers',[])
      assert w['Layers'][-1]['Frames'][0]['Sheet']=='Reverie_Raccord_Escalier_058'
      if v:assert {k:v2 for k,v2 in v.items() if k!='Layers'}=={k:v2 for k,v2 in w.items() if k!='Layers'}
      changes.append([old['Name'],x,y,v,w])
 assert len(changes)==14,(p.name,len(changes))
 # Le correcteur ne touche qu'aux colonnes du tableau Base ; comparer
 # le préfixe et le suffixe bruts de tout l'objet pour couvrir les autres données.
 ra=gzip.decompress(a);rb=gzip.decompress(b)
 marker=b'"Name":"Base"';end=b'"Name":"Cliffs"'
 sa=ra.index(marker);sb=rb.index(marker);ea=ra.index(end,sa);eb=rb.index(end,sb)
 assert ra[:sa]==rb[:sb] and ra[ea:]==rb[eb:],p.name
 maps[p.name]={'source_gzip_sha256':h(a),'source_raw_sha256':h(ra),'result_raw_sha256':h(rb),'cells':changes}
 print('PASS 14 cases, toutes les autres identiques et sections hors couche intactes',flush=True)
assert len(maps)==10
(K/'delta-cellules.json.gz').write_bytes(gzip.compress(json.dumps({'base_commit':'ee39156a24f350b67e81740478be8505f4ff1a05','maps':maps},ensure_ascii=False,separators=(',',':')).encode(),9,mtime=0))
print('PASS 10 cartes ; delta reproductible produit',flush=True)
