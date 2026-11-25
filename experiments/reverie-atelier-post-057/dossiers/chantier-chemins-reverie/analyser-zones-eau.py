import gzip,ijson,collections,json
regions={'sud':(256,1870,384,2060),'kecleon':(560,720,680,920),'bassin':(1010,1830,1140,2050)}
with gzip.open('base/payload/reverie_centre.rsground.gz','rb') as f:
 if f.read(3)!=b'\xef\xbb\xbf':f.seek(0)
 for l in ijson.items(f,'Object.Layers.item'):
  for name,(x1,y1,x2,y2) in regions.items():
   stats=collections.Counter();samples={};coords=collections.defaultdict(list)
   for x in range(x1//8,x2//8):
    for y in range(y1//8,y2//8):
     for a in l['Tiles'][x][y].get('Layers',[]):
      fr=a.get('Frames',[])
      if len(fr)>1:
       k=(tuple(sorted({v.get('Sheet','') for v in fr})),len(fr),a.get('FrameLength'));stats[k]+=1;samples[k]=(x*8,y*8,fr);coords[k].append((x*8,y*8))
   if stats:
    print(name,l['Name'])
    for k,n in stats.most_common():
     ps=coords[k];print(' ',k,n,'bbox',(min(x for x,y in ps),min(y for x,y in ps),max(x for x,y in ps),max(y for x,y in ps)),'ex',samples[k])
