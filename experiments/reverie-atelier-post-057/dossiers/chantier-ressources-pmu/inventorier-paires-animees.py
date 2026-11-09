from pathlib import Path
import sys,collections,sqlite3,zlib,struct,json
R=Path('/home/user/PMU-Destiny-module');sys.path.insert(0,str(R));import pmu_core as c
pairs=collections.Counter();layers=collections.Counter();bad=collections.Counter();mapset=set();tot=0
with c.connect() as con:
 for id,blob in con.execute('select id,data from cartes'):
  for row in struct.iter_unpack('<HH20h',zlib.decompress(blob)):
   v=row[2:]
   for i in range(5):
    n,an=v[2*i:2*i+2];s,as_=v[10+2*i:12+2*i]
    if not an:continue
    tot+=1;mapset.add(id);p=(s,n,as_,an);pairs[p]+=1;layers[c.LAYERS[i]]+=1
    if (n and c.locate(s,n) is None) or c.locate(as_,an) is None:bad[p]+=1
out={'source_client':'c25c01f9879369647cd5a19731b2e4e5acd33e67','source_serveur':'8fb424a520e559e94cff4973def8172cf29d90a2','cadence_client':'MapViewer.OnTick : inversion globale quand e.Tick > lastAnimTick + 250 ms','cartes':len(mapset),'occurrences':tot,'paires_uniques':len(pairs),'occurrences_paires_avec_reference_invalide':sum(bad.values()),'paires_avec_reference_invalide':len(bad),'par_couche':dict(layers),'paires':[{'base_set':k[0],'base_tile':k[1],'anime_set':k[2],'anime_tile':k[3],'occurrences':v,'references_valides':k not in bad} for k,v in pairs.most_common()]}
p=Path('/home/user/chantier-ressources-pmu/inventaire-paires-animees.json');p.write_text(json.dumps(out,ensure_ascii=False,indent=2));print({k:v for k,v in out.items() if k!='paires'})
