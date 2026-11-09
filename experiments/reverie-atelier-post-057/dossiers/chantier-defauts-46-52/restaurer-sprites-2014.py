from pathlib import Path
import concurrent.futures,hashlib,json,urllib.request,time,zipfile
T=json.loads(Path('/home/user/pmu-PMU-Client-tree.json').read_text()); items=[x for x in T['tree'] if x['path'].startswith('resources/GFX/Sprites/') and x['path'].endswith('.sprite')];assert len(items)==751
base='https://raw.githubusercontent.com/PMUniverse/PMU-Client/'+T['sha']+'/'
def get(x):
 for retry in range(4):
  try:
   with urllib.request.urlopen(base+x['path'],timeout=45) as r:b=r.read()
   assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==x['sha']
   return 'Sprites/'+Path(x['path']).name,b
  except Exception:
   if retry==3:raise
   time.sleep(retry+1)
out=Path('/home/user/chantier-defauts-46-52/pmu_reference/sprites-pmu-2014-original.zip'); out.parent.mkdir(exist_ok=True);tmp=out.with_suffix('.tmp')
with concurrent.futures.ThreadPoolExecutor(max_workers=16) as pool,zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED) as z:
 for i,(name,b) in enumerate(pool.map(get,items),1):
  z.writestr(name,b)
  if i%100==0:print(i,'/ 751',flush=True)
with zipfile.ZipFile(tmp) as z: assert z.testzip() is None and len(z.namelist())==751
tmp.replace(out);print('CRC OK',out,flush=True)
