#!/usr/bin/env python3
"""Galerie de banc : seuls les fichiers explicitement listés sont servis."""
import json, os, re, mimetypes, zipfile, threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs, quote
from pathlib import Path

ROOT=Path(__file__).resolve().parent
def catalogue():
 return json.loads((ROOT/'catalogue.json').read_text(encoding='utf-8'))
PROJECTS={'/projets/guilde':Path.home()/'Mise-a-jour-Guilde/Apercu-actuel/index.html','/projets/mega-tsareena':Path.home()/'Tsareena-audit/Apercu-actuel/index.html'}
DOCS={'capacites.csv':ROOT/'capacites-public.csv','statut.csv':ROOT.parent/'Inventaire/239-capacites-statut-z.csv','inventaire.md':ROOT/'inventaire-public.md'}
ZIP=Path.home()/'.cache/destiny-test/galerie-tous-les-tests.zip'; LOCK=threading.Lock()

def archive():
 with LOCK:
  if ZIP.exists() and ZIP.stat().st_mtime >= (ROOT/'catalogue.json').stat().st_mtime: return ZIP
  data=catalogue()
  ZIP.parent.mkdir(parents=True,exist_ok=True);tmp=ZIP.with_suffix('.tmp')
  with zipfile.ZipFile(tmp,'w',compression=zipfile.ZIP_STORED,allowZip64=True) as z:
   z.writestr('LISEZ-MOI.txt', 'Tests PMDO en copie isolée. Les capacités ne sont pas intégrées au menu ni aux règles Z complètes. Placement et lancement scriptés. Les vidéos génériques utilisent Dracaufeu, Ectoplasma, Absol, Mackogneur ou Carchacrok ; Pikachute utilise Pikachu et Supernova utilise Mew. La vidéo Pyro est une compilation Pyro + Tourbillon. La vidéo Méga est un banc séparé.\n')
   for v in data['videos']:
    z.write(v['path'],f"videos/{v['id']}.mp4")
   for name,path in DOCS.items():z.write(path,'inventaires/'+name)
  os.replace(tmp,ZIP)
 return ZIP

class Handler(BaseHTTPRequestHandler):
 def do_HEAD(self): self.serve(False)
 def do_GET(self): self.serve(True)
 def serve(self,body):
  url=urlparse(self.path);path=url.path;download='download' in parse_qs(url.query,keep_blank_values=True);target=None;filename=None
  data=catalogue();videos={x['id']:x for x in data['videos']}
  if path=='/':target=ROOT/'index.html'
  elif path in PROJECTS:target=PROJECTS[path]
  elif path=='/api/catalogue':
   safe={'videos':[{k:v for k,v in x.items() if k!='path'} for x in data['videos']],'pending':data['pending']}
   b=json.dumps(safe,ensure_ascii=False).encode();self.send_response(200);self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Content-Length',str(len(b)));self.send_header('Access-Control-Allow-Origin','*');self.send_header('Cache-Control','no-store');self.end_headers()
   if body:self.wfile.write(b)
   return
  elif path.startswith('/media/'):
   key=path.removeprefix('/media/');item=videos.get(key)
   if item:target=Path(item['path']);filename=target.name
  elif path.startswith('/telecharger/') and path.endswith('.mp4'):
   key=path.removeprefix('/telecharger/')[:-4];item=videos.get(key)
   if item:
    target=Path(item['path']);filename=target.name;download=True
  elif path.startswith('/vignettes/'):
   name=path.removeprefix('/vignettes/')
   if re.fullmatch(r'[a-z0-9_]+\.jpg',name) and name[:-4] in videos:target=ROOT/'vignettes'/name
  elif path.startswith('/docs/'):
   name=path.removeprefix('/docs/');target=DOCS.get(name);filename=name
  elif path=='/tout-telecharger.zip':target=archive();filename='destiny-videos-et-inventaires.zip';download=True
  if not target or not target.is_file():self.send_error(404);return
  size=target.stat().st_size;start=0;end=size-1;part=False
  if self.headers.get('Range'):
   m=re.fullmatch(r'bytes=(\d*)-(\d*)',self.headers['Range'].strip())
   if not m or (not m[1] and not m[2]): self.send_error(416);return
   if m[1]:start=int(m[1]);end=min(int(m[2]),end) if m[2] else end
   else:start=max(0,size-int(m[2]))
   if start>end or start>=size:self.send_error(416);return
   part=True
  self.send_response(206 if part else 200)
  ctype=mimetypes.guess_type(str(target))[0] or 'application/octet-stream'
  if target.suffix in ('.html','.csv','.md'):ctype+='; charset=utf-8'
  self.send_header('Content-Type',ctype);self.send_header('Content-Length',str(end-start+1));self.send_header('Accept-Ranges','bytes');self.send_header('X-Content-Type-Options','nosniff')
  if part:self.send_header('Content-Range',f'bytes {start}-{end}/{size}')
  if download and filename:
   fallback=re.sub(r'[^A-Za-z0-9._-]+','-',filename).strip('-.') or f'download{target.suffix}'
   self.send_header('Content-Disposition',f"attachment; filename=\"{fallback}\"; filename*=UTF-8''{quote(filename, safe='')}")
  if target.suffix in ('.html','.json'):self.send_header('Cache-Control','no-store')
  self.end_headers()
  if body:
   try:
    with target.open('rb') as f:
     f.seek(start);remaining=end-start+1
     while remaining:
      data=f.read(min(1024*256,remaining))
      if not data:break
      self.wfile.write(data);remaining-=len(data)
   except (BrokenPipeError,ConnectionResetError):pass

if __name__=='__main__':
 port=int(os.environ.get('PORT','8768'))
 print(f'Galerie Destiny sur le port {port}',flush=True)
 ThreadingHTTPServer(('0.0.0.0',port),Handler).serve_forever()
