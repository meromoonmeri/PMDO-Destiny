import gzip,ijson,json
coords=[(176,1584),(184,1584),(192,1584),(200,1584),(208,1584),(176,1592),(184,1592),(192,1592),(200,1592),(208,1592),(152,1280),(160,1280),(152,1288),(160,1288),(152,1296),(160,1296),(992,1576),(1064,2584)]
with gzip.open('base/payload/reverie_centre.rsground.gz','rb') as f:
 if f.read(3)!=b'\xef\xbb\xbf':f.seek(0)
 for layer in ijson.items(f,'Object.Layers.item'):
  print('\n',layer['Name']);
  for x,y in coords:
   v=layer['Tiles'][x//8][y//8]
   if v:print(x,y,json.dumps(v,separators=(',',':')))
