#!/usr/bin/env python3
from pathlib import Path
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from urllib.parse import urlsplit
import mimetypes

O=Path(__file__).resolve().parent.parent;G=O.parent;P=G/'Guilde-Destiny-Nuit-Vivante.html'
FILES={'/':P,'/Guilde-Destiny-Nuit-Vivante.html':P,'/reference-sans-lianes':G/'Guilde-Destiny-Toutes-les-Salles.html','/Extrait-Nuit-Vivante.mp4':O/'Extrait-Nuit-Vivante.mp4','/Kit-Nuit-Vivante-Destiny.zip':O/'Kit-Nuit-Vivante-Destiny.zip'}
class Preview(BaseHTTPRequestHandler):
 def do_GET(self):self.reply(False)
 def do_HEAD(self):self.reply(True)
 def reply(self,head):
  route=urlsplit(self.path).path
  if route=='/favicon.ico':self.send_response(204);self.end_headers();return
  f=FILES.get(route)
  if f is None or not f.is_file():self.send_error(404);return
  self.send_response(200);self.send_header('Content-Type',mimetypes.guess_type(f.name)[0] or 'application/octet-stream');self.send_header('Content-Length',str(f.stat().st_size));self.send_header('Cache-Control','no-store');self.end_headers()
  if not head:
   try:self.wfile.write(f.read_bytes())
   except (BrokenPipeError,ConnectionResetError):pass
if __name__=='__main__':
 print('Guilde Destiny · Nuit vivante : http://0.0.0.0:4177',flush=True)
 ThreadingHTTPServer(('0.0.0.0',4177),Preview).serve_forever()
