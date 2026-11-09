from pathlib import Path
import requests,json,hashlib,concurrent.futures,zipfile
R=Path(__file__).resolve().parent;T=json.loads(Path('/home/user/halcyon-reference-tree.json').read_text())['tree'];names={'Data/Ground/metano_town.rsground'}|{'Content/Tile/'+n+'.tile' for n in ['Metano_Town_Base','Metano_Town_Cliffs','Metano_Town_Trimmed','Metano_Town_River','Metano_Town_River_Animation_1','Metano_Town_River_Animation_2','Metano_Town_River_Animation_3','Metano_Town_River_Animation_4','Metano_Town_River_Sparkles','Metano_Town_Objects','Metano_Town_Animated','Metano_Town_Animated_Over','Metano_Town_Animated_Under','Metano_Town_Animation_Tileset']};sel=[x for x in T if x['path'] in names];assert len(sel)==len(names)
def get(x):
 p=x['path'];out=R/'reference-metano'/p
 if out.exists() and out.stat().st_size==x['size']:b=out.read_bytes()
 else:
  r=requests.get('https://raw.githubusercontent.com/Palikadude/Halcyon/1522c7a8b7a34d70078e11ed605b21d563b0dc51/'+p,timeout=180);r.raise_for_status();b=r.content
 assert len(b)==x['size'] and hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==x['sha'],p
 out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(b);print('Référence vérifiée',p,len(b),flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:list(ex.map(get,sel))
with zipfile.ZipFile(R/'reference-metano-interne.zip','w',zipfile.ZIP_DEFLATED) as z:
 for x in sel:z.write(R/'reference-metano'/x['path'],x['path'])
with zipfile.ZipFile(R/'reference-metano-interne.zip') as z:assert z.testzip() is None
print('références sauvegardées',len(sel),flush=True)
