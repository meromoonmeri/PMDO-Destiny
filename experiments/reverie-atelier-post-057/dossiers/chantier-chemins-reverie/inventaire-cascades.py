import gzip,ijson,collections,json
p='base/payload/reverie_centre.rsground.gz'; cnt=collections.Counter(); positions=collections.defaultdict(list)
with gzip.open(p,'rb') as f:
 if f.read(3)!=b'\xef\xbb\xbf':f.seek(0)
 for l in ijson.items(f,'Object.Layers.item'):
  for x,col in enumerate(l['Tiles']):
   for y,c in enumerate(col):
    for a in c.get('Layers',[]):
     fr=a.get('Frames',[])
     if len(fr)>1:
      key=(l['Name'],tuple(sorted(set(v.get('Sheet','') for v in fr))),len(fr),a.get('FrameLength'))
      cnt[key]+=1;positions[str(key)].append([x*8,y*8])
for k,v in cnt.most_common():
 pos=positions[str(k)];print(k,v,'bbox',min(p[0] for p in pos),min(p[1] for p in pos),max(p[0] for p in pos),max(p[1] for p in pos),flush=True)
json.dump(positions,open('positions-animations-centre.json','w'))
