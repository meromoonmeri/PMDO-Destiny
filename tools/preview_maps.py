#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Aperçus statiques des cartes au sol de Destiny (game/Data/Ground/*.rsground).

Rendu hors-moteur, fidèle aux formats PMDO 0.8.12 (vérifiés dans engine/) :
- Fonds : MapBG / LayeredBG -> Content/BG/*.dir (DirSheet), pose 0, a MapLoc (pixels carte).
- Tuiles : pour chaque GroundLayer visible (ordre du fichier), chaque cellule empile
  ses sous-calques (Layers[].Frames[0]) résolus via TileGuide : (Sheet, TexLoc) ->
  position dans Content/Tile/<Sheet>.tile -> blob TileSheet [int64 len][PNG][tileW][tileH],
  première pose de la bande. Taille de cellule = TexSize * 8 px (GroundMap.TileSize).
- Décorations : pose 0 à leur Loc, insérées à leur rang de calque (best effort).
Les entités (PNJ/objets), l'animation (phases d'eau, parallaxe) et la musique ne sont
pas rendues : c'est un aperçu statique, pas une capture du moteur.

Sorties (dossier --out, par défaut import_work/apercus_site, hors Git) :
- full/<carte>.png   rendu pleine résolution
- thumbs/<carte>.jpg vignette (<= 560 px)
- manifest.json      métadonnées pour la galerie (index.html généré à côté)

Usage : python tools/preview_maps.py [--only substr] [--out DIR] [--no-html]
Nécessite Pillow. Sert ensuite par ex. : python -m http.server --directory <out>
"""
from __future__ import annotations

import argparse
import io
import json
import struct
import sys
import time
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
GAME_TILE = ROOT / "game/Content/Tile"
GAME_BG = ROOT / "game/Content/BG"
GAME_OBJ = ROOT / "game/Content/Object"
BASE_TILE = ROOT / "base/Content/Tile"
BASE_BG = ROOT / "base/Content/BG"
BASE_OBJ = ROOT / "base/Content/Object"
GROUND_DIR = ROOT / "game/Data/Ground"
ZONE_DIR = ROOT / "game/Data/Zone"

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def find_file(basename_dirs, name):
    for d in basename_dirs:
        p = d / name
        if p.is_file():
            return p
    return None


class SheetReader:
    """Lit un .tile PMDO : en-tête TileIndexNode + blobs TileSheet adressés par position."""

    def __init__(self, path: Path):
        self.path = path
        self._f = open(path, "rb")
        head = self._f.read(8)
        self.tile_size, count = struct.unpack("<ii", head)
        raw = self._f.read(count * 16)
        self.positions = {}
        for i in range(count):
            x, y, pos = struct.unpack_from("<iiq", raw, i * 16)
            self.positions[(x, y)] = pos
        self.header_size = 8 + count * 16
        self._cache = {}
        self._rel = None  # True si les positions sont relatives après l'en-tête

    def close(self):
        try:
            self._f.close()
        except Exception:
            pass

    def _read_blob(self, offset):
        """Blob BaseSheet (GraphicsManager.GetTile -> BaseSheet.Load) : [int64 len][PNG], rien d'autre."""
        self._f.seek(offset)
        head = self._f.read(8)
        if len(head) < 8:
            raise ValueError("blob tronqué")
        (plen,) = struct.unpack("<q", head)
        png = self._f.read(plen)
        if not png.startswith(PNG_MAGIC):
            raise ValueError("pas de PNG à cette position")
        return png

    def get_tile(self, x, y):
        key = (x, y)
        if key in self._cache:
            return self._cache[key]
        img = None
        pos = self.positions.get(key, 0)
        if pos:  # positions absolues depuis le début du fichier (SeekOrigin.Begin)
            try:
                png = self._read_blob(pos)
                full = Image.open(io.BytesIO(png)).convert("RGBA")
                ts = self.tile_size or full.height
                img = full.crop((0, 0, min(ts, full.width), min(ts, full.height)))
            except Exception:
                img = None
        self._cache[key] = img
        return img


class DirReader:
    """Lit un .dir (DirSheet) : [int64 len][PNG atlas][tileW][tileH][rotate][frames]. Frame 0 = coin haut-gauche."""

    cache = {}

    @classmethod
    def frame0(cls, path: Path):
        key = str(path)
        if key in cls.cache:
            return cls.cache[key]
        img = None
        try:
            raw = path.read_bytes()
            (plen,) = struct.unpack_from("<q", raw, 0)
            png = raw[8:8 + plen]
            tw, th, _rot, _frames = struct.unpack_from("<iiii", raw, 8 + plen)
            atlas = Image.open(io.BytesIO(png)).convert("RGBA")
            img = atlas.crop((0, 0, min(tw, atlas.width), min(th, atlas.height)))
        except Exception:
            img = None
        cls.cache[key] = img
        return img

    @classmethod
    def prune(cls, keep=24):
        if len(cls.cache) > keep:
            cls.cache = dict(list(cls.cache.items())[-keep:])


def localized_name(name_obj, fallback):
    if isinstance(name_obj, str):
        return name_obj or fallback
    if isinstance(name_obj, dict):
        lt = name_obj.get("LocalTexts") or {}
        return lt.get("fr") or name_obj.get("DefaultText") or fallback
    return fallback


def paste_over(canvas: Image.Image, img: Image.Image, x: int, y: int):
    """SrcOver exact (crop+alpha_composite), avec clipping aux bords du canevas."""
    if img is None:
        return
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(canvas.width, x + img.width), min(canvas.height, y + img.height)
    if x1 <= x0 or y1 <= y0:
        return
    piece = img.crop((x0 - x, y0 - y, x1 - x, y1 - y)) if (x0, y0, x1 - x0, y1 - y0) != (x, y, img.width, img.height) else img
    region = canvas.crop((x0, y0, x1, y1))
    canvas.paste(Image.alpha_composite(region, piece), (x0, y0))


class GroundRenderer:
    def __init__(self):
        self.sheets = {}   # name -> SheetReader (borné)
        self.missing_sheets = set()
        self.missing_tiles = 0

    def sheet(self, name):
        if name in self.sheets:
            return self.sheets[name]
        reader = None
        path = find_file([GAME_TILE, BASE_TILE], f"{name}.tile")
        if path is not None:
            try:
                reader = SheetReader(path)
            except Exception:
                reader = None
        if reader is None:
            self.missing_sheets.add(name)
        if len(self.sheets) > 40:  # borne mémoire : fermer les plus anciens
            for k in list(self.sheets)[:20]:
                old = self.sheets.pop(k)
                if old:
                    old.close()
        self.sheets[name] = reader
        return reader

    def bg_image(self, anim_index, alpha=255):
        if not anim_index:
            return None
        path = find_file([GAME_BG, BASE_BG, GAME_OBJ, BASE_OBJ], f"{anim_index}.dir")
        if path is None:
            self.missing_sheets.add(anim_index)
            return None
        img = DirReader.frame0(path)
        if img is not None and alpha is not None and 0 <= alpha < 255:
            img = img.copy()
            img.putalpha(img.getchannel("A").point(lambda a: a * alpha // 255))
        return img

    def render(self, ground_path: Path):
        doc = json.loads(ground_path.read_text(encoding="utf-8-sig"))
        o = doc["Object"]
        tex = int(o.get("TexSize") or 1)
        cell = tex * 8
        layers = [l for l in (o.get("Layers") or []) if l.get("Visible", True)]
        ref_tiles = next((l.get("Tiles") for l in layers if l.get("Tiles")), None) or (o.get("Layers") or [{}])[0].get("Tiles") or []
        tiles_x = len(ref_tiles)
        tiles_y = len(ref_tiles[0]) if tiles_x else 0
        map_w, map_h = tiles_x * cell, tiles_y * cell

        # --- Fonds (MapBG simple ou LayeredBG) ---
        bgs = []
        bg_obj = o.get("Background") or {}
        sub = bg_obj.get("Layers")
        entries = [c.get("BG") for c in sub if isinstance(c, dict)] if isinstance(sub, list) else [bg_obj]
        for b in entries:
            if not isinstance(b, dict):
                continue
            anim = b.get("BGAnim") or {}
            idx = anim.get("AnimIndex") or ""
            img = self.bg_image(idx, anim.get("Alpha", 255))
            loc = b.get("MapLoc") or {}
            if img is not None:
                bgs.append((img, int(loc.get("X", 0)), int(loc.get("Y", 0))))

        # --- Canevas = zone de tuiles exacte (les débordements de fonds servent à la
        #     parallaxe en jeu ; dans un aperçu de carte on les rogne au bord de la map) ---
        ox = oy = 0
        canvas = Image.new("RGBA", (map_w, map_h), (0, 0, 0, 0))
        for img, x, y in bgs:
            paste_over(canvas, img, x - ox, y - oy)

        # --- Décorations groupées par rang de calque (insérées après le calque de même rang) ---
        decors_by_rank = {}
        for dlay in (o.get("Decorations") or []):
            if not isinstance(dlay, dict) or not dlay.get("Visible", True):
                continue
            for anim in (dlay.get("Anims") or []):
                try:
                    loc = anim.get("Loc") or {}
                    a = anim.get("Anim") or anim.get("BGAnim") or {}
                    img = self.bg_image(a.get("AnimIndex") or "", a.get("Alpha", 255))
                    if img is not None:
                        decors_by_rank.setdefault(int(dlay.get("Layer", 0)), []).append(
                            (img, int(loc.get("X", 0)), int(loc.get("Y", 0))))
                except Exception:
                    continue

        # --- Calques de tuiles ---
        used_sheets = set()
        for li, layer in enumerate(layers):
            tiles = layer.get("Tiles") or []
            for tx, col in enumerate(tiles):
                if not isinstance(col, list):
                    continue
                for ty, tile in enumerate(col):
                    if not isinstance(tile, dict):
                        continue
                    subs = tile.get("Layers") or []
                    if not subs:
                        continue
                    cell_img = None
                    for sub_layer in subs:
                        frames = (sub_layer or {}).get("Frames") or []
                        if not frames:
                            continue
                        f0 = frames[0] or {}
                        sheet_name = f0.get("Sheet") or ""
                        if not sheet_name:
                            continue
                        used_sheets.add(sheet_name)
                        reader = self.sheet(sheet_name)
                        if reader is None:
                            self.missing_tiles += 1
                            continue
                        tloc = f0.get("TexLoc") or {}
                        tim = reader.get_tile(int(tloc.get("X", 0)), int(tloc.get("Y", 0)))
                        if tim is None:
                            self.missing_tiles += 1
                            continue
                        if tim.size != (cell, cell):
                            tim = tim.resize((cell, cell), Image.NEAREST)
                        cell_img = tim if cell_img is None else Image.alpha_composite(cell_img, tim)
                    if cell_img is not None:
                        paste_over(canvas, cell_img, tx * cell - ox, ty * cell - oy)
            for img, x, y in decors_by_rank.get(int(layer.get("Layer", li)), []):
                paste_over(canvas, img, x - ox, y - oy)
        # décorations de rang supérieur à tous les calques
        max_rank = max([int(l.get("Layer", i)) for i, l in enumerate(layers)] + [-1])
        for rank, items in sorted(decors_by_rank.items()):
            if rank > max_rank:
                for img, x, y in items:
                    paste_over(canvas, img, x - ox, y - oy)

        meta = {
            "asset": o.get("AssetName") or ground_path.stem,
            "title": localized_name(o.get("Name"), ground_path.stem),
            "version": doc.get("Version"),
            "tex_size": tex,
            "cell_px": cell,
            "tiles_x": tiles_x,
            "tiles_y": tiles_y,
            "px_w": canvas.width,
            "px_h": canvas.height,
            "map_px_w": map_w,
            "map_px_h": map_h,
            "layers": len(o.get("Layers") or []),
            "sheets_used": len(used_sheets),
            "file": f"full/{ground_path.stem}.png",
            "thumb": f"thumbs/{ground_path.stem}.jpg",
        }
        return canvas, meta


def zone_map():
    mapping = {}
    zones = {}
    for zp in sorted(ZONE_DIR.glob("*.json")):
        try:
            zo = json.loads(zp.read_text(encoding="utf-8-sig"))["Object"]
        except Exception:
            continue
        zones[zp.stem] = localized_name(zo.get("Name"), zp.stem)
        for g in zo.get("GroundMaps") or []:
            mapping[g] = zp.stem
    return mapping, zones


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Aperçu des maps — PMD Destiny</title>
<style>
  :root{--bg:#0d1420;--panel:#16202f;--panel2:#1c2a3d;--txt:#e8eef6;--dim:#9fb4c8;--acc:#ffd45e}
  *{box-sizing:border-box} body{margin:0;background:var(--bg);color:var(--txt);font-family:system-ui,'Segoe UI',sans-serif}
  header{position:sticky;top:0;z-index:5;background:rgba(13,20,32,.94);backdrop-filter:blur(6px);padding:14px 20px;border-bottom:1px solid #26374d}
  h1{margin:0 0 4px;font-size:20px} .sub{color:var(--dim);font-size:13px}
  .row{display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin-top:10px}
  input[type=search]{background:var(--panel);border:1px solid #2c435f;color:var(--txt);border-radius:8px;padding:7px 10px;min-width:240px}
  .chip{background:var(--panel);border:1px solid #2c435f;color:var(--txt);border-radius:999px;padding:6px 12px;cursor:pointer;font-size:13px}
  .chip.on{background:var(--acc);color:#221a02;border-color:var(--acc);font-weight:600}
  main{padding:18px 20px 60px} h2{margin:26px 0 6px;font-size:17px} .zcount{color:var(--dim);font-size:13px;font-weight:400}
  .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:14px}
  .card{background:var(--panel);border:1px solid #26374d;border-radius:10px;overflow:hidden;cursor:pointer}
  .card:hover{border-color:var(--acc)}
  .card img{width:100%;aspect-ratio:4/3;object-fit:contain;background:#0a0f18;display:block;image-rendering:auto}
  .card .m{padding:8px 10px} .card .t{font-weight:600;font-size:14px} .card .a{color:var(--dim);font-size:12px;word-break:break-all}
  .err{padding:18px;color:#f2b8b5;font-size:13px}
  #ov{position:fixed;inset:0;background:rgba(4,8,14,.92);display:none;z-index:20;overflow:auto}
  #ov .bar{position:sticky;top:0;background:rgba(13,20,32,.95);padding:10px 16px;display:flex;gap:10px;align-items:center;border-bottom:1px solid #26374d}
  #ov button{background:var(--panel2);color:var(--txt);border:1px solid #2c435f;border-radius:8px;padding:7px 12px;cursor:pointer}
  #ov img{display:block;margin:18px auto;image-rendering:pixelated;background:#0a0f18;max-width:none}
  #ov .cap{color:var(--dim);font-size:13px}
</style></head><body>
<header>
  <h1>🗺️ Aperçu des maps — Pokémon Mystery Dungeon: Destiny</h1>
  <div class="sub" id="subtitle"></div>
  <div class="row" id="chips"></div>
  <div class="row"><input type="search" id="q" placeholder="Rechercher une map (titre, nom de fichier)…"></div>
</header>
<main id="main"></main>
<div id="ov"><div class="bar">
  <button onclick="closeOv()">✕ Fermer</button>
  <button onclick="navOv(-1)">◀ Préc.</button><button onclick="navOv(1)">Suiv. ▶</button>
  <span id="ovtitle" style="font-weight:600"></span><span class="cap" id="ovcap"></span>
  <span class="cap">Astuce : molette = défilement ; Échap ferme.</span>
</div><img id="ovimg" alt=""></div>
<script>
let DATA=null, flat=[], idx=0;
const ZONE_ORDER = ["destiny_hub","chapitres_destiny","menu_titre","cotes_metano","reverie","ateliers_donjons","autres"];
fetch('manifest.json').then(r=>r.json()).then(d=>{DATA=d;render();});
function allMaps(){return DATA.maps;}
function render(){
  document.getElementById('subtitle').textContent =
    DATA.maps.length + " rendus statiques générés par tools/preview_maps.py — " + DATA.generated +
    " · fonds + calques de tuiles (pose 0) ; animations, PNJ et parallaxe non rendus.";
  const zones=[...new Set(allMaps().map(m=>m.zone||'autres'))].sort((a,b)=>ZONE_ORDER.indexOf(a)-ZONE_ORDER.indexOf(b));
  const chips=document.getElementById('chips'); chips.innerHTML='';
  const mk=(id,label)=>{const b=document.createElement('button');b.className='chip'+(id==='__all'?' on':'');b.textContent=label;b.onclick=()=>{document.querySelectorAll('.chip').forEach(c=>c.classList.remove('on'));b.classList.add('on');draw(id);};chips.appendChild(b);};
  mk('__all','Toutes ('+DATA.maps.length+')');
  zones.forEach(z=>mk(z,(DATA.zone_titles[z]||z)+' ('+allMaps().filter(m=>(m.zone||'autres')===z).length+')'));
  draw('__all');
}
function draw(zone){
  const q=(document.getElementById('q').value||'').toLowerCase();
  const byZone={};
  allMaps().filter(m=>(zone==='__all'||(m.zone||'autres')===zone) && (!q || (m.title+' '+m.asset).toLowerCase().includes(q)))
    .forEach(m=>{(byZone[m.zone||'autres']=byZone[m.zone||'autres']||[]).push(m);});
  flat=[]; const main=document.getElementById('main'); main.innerHTML='';
  Object.keys(byZone).sort((a,b)=>ZONE_ORDER.indexOf(a)-ZONE_ORDER.indexOf(b)).forEach(z=>{
    const h=document.createElement('h2'); h.innerHTML=(DATA.zone_titles[z]||z)+' <span class="zcount">— '+byZone[z].length+' maps</span>'; main.appendChild(h);
    const g=document.createElement('div'); g.className='grid'; main.appendChild(g);
    byZone[z].forEach(m=>{
      const i=flat.push(m)-1;
      const c=document.createElement('div'); c.className='card';
      c.innerHTML = m.error ? '<div class="err">Échec du rendu : '+m.error+'</div>'
        : '<img loading="lazy" src="'+m.thumb+'" alt="'+m.title+'">';
      c.innerHTML += '<div class="m"><div class="t">'+m.title+'</div><div class="a">'+m.asset+
        (m.tiles_x? ' · '+m.tiles_x+'×'+m.tiles_y+' cases ('+m.cell_px+'px) · '+m.px_w+'×'+m.px_h+'px':'')+'</div></div>';
      if(!m.error) c.onclick=()=>openOv(i);
      g.appendChild(c);
    });
  });
}
function openOv(i){ idx=i; const m=flat[i];
  document.getElementById('ovimg').src=m.file;
  document.getElementById('ovtitle').textContent=m.title;
  document.getElementById('ovcap').textContent=m.asset+' · '+(m.tiles_x||'')+'×'+(m.tiles_y||'')+' cases · '+m.px_w+'×'+m.px_h+' px · '+(m.layers||'')+' calques · '+(m.version||'');
  document.getElementById('ov').style.display='block';
}
function navOv(d){ if(flat.length) openOv((idx+d+flat.length)%flat.length); }
function closeOv(){ document.getElementById('ov').style.display='none'; }
document.getElementById('q').addEventListener('input',()=>{const on=document.querySelector('.chip.on'); if(on) on.click();});
document.addEventListener('keydown',e=>{if(e.key==='Escape')closeOv(); if(e.key==='ArrowRight')navOv(1); if(e.key==='ArrowLeft')navOv(-1);});
</script></body></html>
"""


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--only", default="", help="ne rendre que les maps contenant cette chaîne")
    ap.add_argument("--out", default=str(ROOT / "import_work/apercus_site"))
    ap.add_argument("--no-html", action="store_true")
    args = ap.parse_args()

    out = Path(args.out)
    (out / "full").mkdir(parents=True, exist_ok=True)
    (out / "thumbs").mkdir(parents=True, exist_ok=True)

    g2z, zone_titles = zone_map()
    renderer = GroundRenderer()
    results = []
    paths = sorted(GROUND_DIR.glob("*.rsground"))
    if args.only:
        paths = [p for p in paths if args.only.lower() in p.stem.lower()]
    print(f"{len(paths)} maps à rendre -> {out}")
    t0 = time.time()
    for i, p in enumerate(paths, 1):
        entry = {"asset": p.stem, "title": p.stem, "zone": g2z.get(p.stem, "autres")}
        try:
            img, meta = renderer.render(p)
            entry.update(meta)
            entry["zone"] = g2z.get(p.stem, "autres")
            img.save(out / meta["file"], format="PNG", optimize=False)
            thumb = img.copy()
            thumb.thumbnail((560, 560), Image.NEAREST)
            flat = Image.new("RGB", thumb.size, (10, 15, 24))
            flat.paste(thumb, (0, 0), thumb)
            flat.save(out / meta["thumb"], format="JPEG", quality=84)
            print(f"[{i}/{len(paths)}] {p.stem}: {meta['tiles_x']}x{meta['tiles_y']} cases, {img.size[0]}x{img.size[1]}px")
        except Exception as exc:
            entry["error"] = f"{type(exc).__name__}: {exc}"
            print(f"[{i}/{len(paths)}] {p.stem}: ECHEC {entry['error']}")
        results.append(entry)
        DirReader.prune()

    # Menu-titre : réutiliser les aperçus reconstruits si présents
    menu_src = ROOT / "import_work/menu_out"
    for tag, label in (("jour", "Écran-titre — JOUR (menu animé, fond + blason)"),
                       ("nuit", "Écran-titre — NUIT (menu animé, fond + blason)")):
        src = menu_src / f"preview_ecran_titre_{tag}.png"
        if src.is_file():
            (out / f"menu_{tag}.png").write_bytes(src.read_bytes())
            results.insert(0 if tag == "jour" else 1, {
                "asset": f"menu_titre_{tag}", "title": label, "zone": "menu_titre",
                "file": f"menu_{tag}.png", "thumb": f"menu_{tag}.png",
                "px_w": 320, "px_h": 240,
            })
    zone_titles["menu_titre"] = "Menu-titre (animé, voir docs/MENU_TITRE.md)"
    zone_titles["autres"] = "Hors zone"

    manifest = {
        "generated": time.strftime("%d/%m/%Y %H:%M"),
        "zone_titles": zone_titles,
        "maps": results,
        "renderer_notes": "Apercus statiques (pose 0) ; animations/PNJ/parallaxe non rendus.",
    }
    (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
    if not args.no_html:
        (out / "index.html").write_text(HTML_TEMPLATE, encoding="utf-8")
    print(f"Terminé en {time.time()-t0:.0f} s. Fichiers manquants vus : {sorted(renderer.missing_sheets)[:20]}"
          f" ; tuiles irrésolues : {renderer.missing_tiles}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
