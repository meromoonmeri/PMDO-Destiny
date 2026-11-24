#!/usr/bin/env python3
"""Live viewer for the self-contained atlas with its comparison video."""
from pathlib import Path
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from urllib.parse import urlsplit

G=Path(__file__).resolve().parents[2];PAGE=G/'Guilde-Destiny-Lumiere-Ancree.html'
class App(BaseHTTPRequestHandler):
 def do_GET(self):self.serve(False)
 def do_HEAD(self):self.serve(True)
 def serve(self,head):
  path=urlsplit(self.path).path
  if path=='/favicon.ico':self.send_response(204);self.end_headers();return
  if path not in ('/','/'+PAGE.name):self.send_error(404);return
  data=PAGE.read_bytes();self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.send_header('Content-Length',str(len(data)));self.send_header('Cache-Control','no-store');self.end_headers()
  if not head:
   try:self.wfile.write(data)
   except (BrokenPipeError, ConnectionResetError):pass
if __name__=='__main__':
 print('Guilde Destiny · Vidéo intégrée · 4178',flush=True)
 ThreadingHTTPServer(('0.0.0.0',4178),App).serve_forever()
