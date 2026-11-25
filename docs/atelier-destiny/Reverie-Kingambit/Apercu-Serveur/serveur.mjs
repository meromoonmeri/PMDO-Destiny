import { createServer } from 'node:http';
import { createReadStream } from 'node:fs';
import { readdir, stat } from 'node:fs/promises';
import { dirname, extname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const publicDir = join(here, 'public');
const types = new Map(Object.entries({
  '.html':'text/html; charset=utf-8', '.css':'text/css; charset=utf-8',
  '.js':'text/javascript; charset=utf-8', '.json':'application/json; charset=utf-8',
  '.woff2':'font/woff2', '.webp':'image/webp', '.svg':'image/svg+xml',
  '.png':'image/png', '.mp4':'video/mp4', '.txt':'text/plain; charset=utf-8',
}));
const routes = new Map();
async function expose(directory, prefix) {
  for (const file of await readdir(directory, { withFileTypes: true })) {
    const path = join(directory, file.name);
    const route = `${prefix}/${file.name}`;
    if (file.isDirectory()) await expose(path, route);
    else if (file.isFile() && types.has(extname(path))) routes.set(route, path);
  }
}
await expose(publicDir, '');
routes.set('/', join(publicDir, 'index.html'));
const movie = join(here, '..', 'Kingambit-Mise-a-jour', 'Apercu-18-wooshes-PMD.mp4');
await stat(movie);
routes.set('/media/dojo-v077.mp4', movie);

const csp = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; media-src 'self'; object-src 'none'; base-uri 'none'; form-action 'none'";
const server = createServer(async (request, response) => {
  const headers = { 'Content-Security-Policy': csp, 'X-Content-Type-Options': 'nosniff', 'Referrer-Policy': 'no-referrer' };
  function small(code, msg, extra = {}) {
    response.writeHead(code, { ...headers, 'Content-Type': 'text/plain; charset=utf-8', ...extra });
    response.end(request.method === 'HEAD' ? undefined : msg);
  }
  if (!['GET', 'HEAD'].includes(request.method)) return small(405, 'Lecture seule.', { Allow: 'GET, HEAD' });
  let route;
  try { route = decodeURIComponent(new URL(request.url, 'http://apercu.local').pathname); }
  catch { return small(400, 'Requête invalide.'); }
  if (route === '/healthz') return small(200, 'Réverie v0.7.7 — en ligne.');
  const path = routes.get(route);
  if (!path) return small(404, 'Page introuvable.');
  try {
    const file = await stat(path);
    if (!file.isFile()) return small(404, 'Fichier introuvable.');
    const size = file.size;
    const ext = extname(path);
    Object.assign(headers, {
      'Content-Type': types.get(ext), 'Accept-Ranges': 'bytes',
      'Cache-Control': ['.html', '.css', '.js', '.json'].includes(ext) ? 'no-cache' : 'public, max-age=3600',
      'Last-Modified': file.mtime.toUTCString(),
    });
    let start = 0, end = size - 1, status = 200;
    if (request.headers.range) {
      const m = /^bytes=(\d*)-(\d*)$/.exec(request.headers.range);
      if (!m || !`${m[1]}${m[2]}` || size === 0) return small(416, 'Plage hors fichier.', { 'Content-Range': `bytes */${size}` });
      if (!m[1]) start = Math.max(0, size - Number(m[2]));
      else {
        start = Number(m[1]);
        if (m[2]) end = Math.min(end, Number(m[2]));
      }
      if (start >= size || start > end) return small(416, 'Plage hors fichier.', { 'Content-Range': `bytes */${size}` });
      headers['Content-Range'] = `bytes ${start}-${end}/${size}`;
      status = 206;
    }
    headers['Content-Length'] = end - start + 1;
    response.writeHead(status, headers);
    if (request.method === 'HEAD' || size === 0) return response.end();
    const fileStream = createReadStream(path, { start, end });
    fileStream.on('error', () => response.destroy());
    response.once('close', () => fileStream.destroy());
    fileStream.pipe(response);
  } catch {
    if (!response.headersSent) small(404, 'Fichier indisponible.');
    else response.destroy();
  }
});

const port = Number(process.env.PORT || 4173);
server.listen(port, '0.0.0.0', () => console.log(`Réverie · aperçu v0.7.7 disponible sur le port ${port}`));
