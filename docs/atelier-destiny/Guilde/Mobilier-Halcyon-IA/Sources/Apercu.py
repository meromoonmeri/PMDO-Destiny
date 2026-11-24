#!/usr/bin/env python3
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit
import argparse

O = Path(__file__).resolve().parents[1]
PAGE = O.parent/'Guilde-Destiny-Mobilier-Halcyon-IA.html'
ZIP = O/'Kit-Halcyon-Creations-IA.zip'
PLANCHE = O/'Planche-Creations-IA.png'
ROUTES = {
    '/': (PAGE, 'text/html; charset=utf-8'),
    '/'+PAGE.name: (PAGE, 'text/html; charset=utf-8'),
    '/'+ZIP.name: (ZIP, 'application/zip'),
    '/'+PLANCHE.name: (PLANCHE, 'image/png'),
}

class App(BaseHTTPRequestHandler):
    def do_GET(self): self.send(False)
    def do_HEAD(self): self.send(True)
    def send(self, head):
        path = urlsplit(self.path).path
        if path == '/favicon.ico':
            self.send_response(204); self.end_headers(); return
        if path not in ROUTES or not ROUTES[path][0].is_file():
            self.send_error(404); return
        source, mimetype = ROUTES[path]
        content = source.read_bytes()
        self.send_response(200)
        self.send_header('Content-Type', mimetype)
        self.send_header('Cache-Control','no-store')
        self.send_header('Content-Length', str(len(content)))
        if source==ZIP: self.send_header('Content-Disposition', f'attachment; filename="{ZIP.name}"')
        self.end_headers()
        if not head:
            try: self.wfile.write(content)
            except (BrokenPipeError,ConnectionResetError): pass

if __name__ == '__main__':
    p=argparse.ArgumentParser();p.add_argument('--port',type=int,default=4185);args=p.parse_args()
    print(f'Créations IA de Halcyon · :{args.port}',flush=True)
    ThreadingHTTPServer(('0.0.0.0',args.port),App).serve_forever()
