#!/usr/bin/env python3
from pathlib import Path
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from urllib.parse import urlsplit
P=Path(__file__).resolve().parents[2]/'Guilde-Destiny-Bourgeons-PMD.html'
class App(BaseHTTPRequestHandler):
 def do_GET(self):self.send(False)
 def do_HEAD(self):self.send(True)
 def send(self,head):
  path=urlsplit(self.path).path
  if path=='/favicon.ico':self.send_response(204);self.end_headers();return
  if path not in ('/','/'+P.name):self.send_error(404);return
  if not P.is_file():self.send_error(503);return
  body=P.read_bytes();self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(body)));self.end_headers()
  if not head:
   try:self.wfile.write(body)
   except (BrokenPipeError,ConnectionResetError):pass
if __name__=='__main__':
 print('Guilde Destiny · Bourgeons et lumière PMD · 4179',flush=True)
 ThreadingHTTPServer(('0.0.0.0',4179),App).serve_forever()
