import pathlib,json,collections,hashlib,requests,struct,concurrent.futures
R=pathlib.Path(__file__).parent;T={x['path']:x for x in json.loads((R.parent/'chantier-defauts-46-52/arbre-057.json').read_text())['tree'] if x['type']=='blob'};refs=collections.defaultdict(list)
for name in ['caféspindaaccueil','spindacaféétage1','spindacaféétage1salle2']:
 o=json.load(open(R/'original/game/Data/Ground'/f'{name}.rsground',encoding='utf-8-sig'))['Object']; print('CARTE',name,'identifiant',o['AssetName'],'calques',len(o['Layers']),'points entrée',[(m['EntName'],m['Collider']) for e in o['Entities'] for m in e['Markers']]);
 for l in o['Layers']:
  for col in l['Tiles']:
   for cell in col:
    for a in cell.get('Layers',[]):
     for f in a.get('Frames',[]):
      if f.get('Sheet'):refs[f['Sheet']].append((name,f['TexLoc']['X'],f['TexLoc']['Y']))
for n in refs:
 p='game/Content/Tile/'+n+'.tile';q='base/Content/Tile/'+n+'.tile'
 if p not in T:p=q
 assert p in T,(n,'banque introuvable')
 e=T[p];r=requests.get('https://raw.githubusercontent.com/meromoonmeri/PMDO-Destiny/ee39156a24f350b67e81740478be8505f4ff1a05/'+requests.utils.quote(p,safe='/'),timeout=60);r.raise_for_status();b=r.content;assert len(b)==e['size'] and hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==e['sha'];s,c=struct.unpack_from('<ii',b);locs={struct.unpack_from('<iiq',b,8+16*i)[:2] for i in range(c)}
 bad=[x for x in refs[n] if (x[1],x[2]) not in locs];print('BANQUE',n,'références',len(refs[n]),'tuiles absentes',len(bad),'exemples',bad[:3]);
print('Audio',"game/Content/Music/Spinda's Cafe.ogg" in T)
