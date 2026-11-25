from pathlib import Path
import gzip,json,hashlib,shutil,copy
R=Path(__file__).resolve().parent;S=R/'corrections-global-eaux-en-cours';O=R/'corrections-pont-en-cours'
for sub in ['payload','game/Content/Tile','art/reverie/tilesheets']:
 (O/sub).mkdir(parents=True,exist_ok=True)
 if sub!='payload':
  for p in (S/sub).iterdir():shutil.copy2(p,O/sub/p.name)
# Même direction et même cote : séquences de berge natives de l'étang.
# Le pont et les fleurs restent dans leurs couches supérieures inchangées.
pairs={1056:1032,1064:1040,1072:1048,1080:1056,1136:1064,1144:1072,1152:1080,1160:1088};target_y=1104//8;source_y=2192//8
results=[]
for path in sorted((S/'payload').glob('*.gz')):
 print('Rive de pont',path.name,flush=True);raw=gzip.decompress(path.read_bytes()).decode('utf8');start=raw.index('"Name":"River"');pos=raw.index('"Tiles":[',start)+len('"Tiles":[');dec=json.JSONDecoder();splices=[];donors={};targets={};cols={}
 for cx in range(200):
  col,end=dec.raw_decode(raw,pos)
  if cx*8 in set(pairs)|set(pairs.values()):cols[cx*8]=(pos,end,col)
  pos=end
  if cx<199:assert raw[pos]==',';pos+=1
 for target,source in pairs.items():
  src=cols[source][2][source_y]['Layers'];assert len(src)==1 and len(src[0]['Frames'])==4 and src[0]['FrameLength']==10,(source,src)
  donor=copy.deepcopy(src[0]);pos,end,col=cols[target];cell=col[target_y]
  if not cell:cell.update({'AutoTileset':'','Associates':[],'Layers':[],'NeighborCode':-1})
  cell.setdefault('Layers',[]).append(donor)
  splices.append((pos,end,json.dumps(col,ensure_ascii=False,separators=(',',':'))))
 # Les plages sont toutes des colonnes distinctes, le reste du JSON est recopié.
 splices.sort();parts=[];pos=0
 for lo,hi,v in splices:parts.extend([raw[pos:lo],v]);pos=hi
 parts.append(raw[pos:]);modified=''.join(parts).encode();dest=O/'payload'/path.name;dest.write_bytes(gzip.compress(modified,compresslevel=6,mtime=0));assert gzip.decompress(dest.read_bytes())==modified
 # Contrôle que l'ajout seul modifie les colonnes, aucune animation supprimée.
 for lo,hi,v in splices:
  old=json.loads(raw[lo:hi]);new=json.loads(v)
  for y,(a,b) in enumerate(zip(old,new)):
   if y!=target_y:assert a==b
   else:assert a.get('Layers',[])==b['Layers'][:-1] and (a=={} or {k:v for k,v in a.items() if k!='Layers'}=={k:v for k,v in b.items() if k!='Layers'})
 results.append({'carte':path.name,'cases':len(pairs),'sha256':hashlib.sha256(modified).hexdigest()})
assert len(results)==10
(O/'manifest-pont.json').write_text(json.dumps({'base':'97847f618dd16d99f9475e75b74242c247146631','donneurs':pairs,'source_y':2192,'cible_y':1104,'phases':4,'duree':10,'cartes':results},ensure_ascii=False,indent=2))
print('PASS : huit segments de berge animés, 10 variantes, animations déjà présentes intactes',flush=True)
