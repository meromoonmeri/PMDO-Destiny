#!/usr/bin/env python3
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit
import argparse, mimetypes

O=Path(__file__).resolve().parent.parent;G=O.parent;PAGE=G/'Guilde-Destiny-Lianes-et-PMU-100.html'; ORIGINAL=G/'Guilde-Destiny-Toutes-les-Salles.html'
FILES={'/':PAGE,'/Guilde-Destiny-Lianes-et-PMU-100.html':PAGE,'/reference-sans-verdure':ORIGINAL,'/Tilesheet-PMU-Halcyon-100.png':O/'Tilesheet-PMU-Halcyon-100.png','/Kit-PMU-Halcyon-et-Lianes-Reverie.zip':O/'Kit-PMU-Halcyon-et-Lianes-Reverie.zip'}
class Handler(BaseHTTPRequestHandler):
 def do_GET(self):self.serve(False)
 def do_HEAD(self):self.serve(True)
 def serve(self,head):
  path=urlsplit(self.path).path
  if path=='/favicon.ico':self.send_response(204);self.end_headers();return
  f=FILES.get(path)
  if f is None or not f.is_file():self.send_error(404);return
  data=f.read_bytes();self.send_response(200);self.send_header('Content-Type',mimetypes.guess_type(f.name)[0] or 'application/octet-stream');self.send_header('Content-Length',str(len(data)));self.send_header('Cache-Control','no-store');self.end_headers()
  if not head:self.wfile.write(data)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--port',default=4176,type=int);x=p.parse_args();print('Guilde Destiny · lianes et mobilier — aperçu sur le port',x.port,flush=True);ThreadingHTTPServer(('0.0.0.0',x.port),Handler).serve_forever()
