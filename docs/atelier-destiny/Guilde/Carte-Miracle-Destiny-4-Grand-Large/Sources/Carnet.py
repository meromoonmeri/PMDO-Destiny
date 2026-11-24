"""Offline design catalogue. Small terrain crops, never the entire map."""
from pathlib import Path
from PIL import Image
from io import BytesIO
from base64 import b64encode
from html import escape as h
import json
D=Path(__file__).resolve().parents[1];a=json.loads((D/'Atlas.json').read_text());C=D/'Calques/Extension-EoS';R=a['placements'];ds=Image.open(D/'Extension-EoS-Grand-Large.png').convert('RGB');sections=[]
for k in a['nuages']['zones_grand_large']:
 p=R[k];count=0;cards=[]
 for s in a['sites']:
  if s['area']!=k:continue
  x,y=s['motif_ds'];im=ds.crop((x-21,y-17,x+22,y+18));f=BytesIO();im.save(f,format='PNG',optimize=True);u=b64encode(f.getvalue()).decode();count+=1
  cards.append(f'<article><img src="data:image/png;base64,{u}" alt="Motif sur le terrain : {h(s["name"])}" width="43" height="35" loading="lazy"><div><span>{h(s["category"])}</span><h3>{h(s["name"])}</h3><p>{h(s["text"])}</p></div></article>')
 sections.append(f'<section id="{k}"><div class="heading"><h2>{h(a["regions"][k])}</h2><small>{count} lieux</small></div><div class="detail">'+''.join(cards)+'</div></section>')
style='''*{box-sizing:border-box}html{background:#17241e;color:#f3e4bf;scroll-behavior:smooth}body{margin:0;font:14px/1.5 system-ui,sans-serif}main{max-width:1120px;margin:auto;padding:clamp(17px,5vw,52px)}header{border-bottom:1px solid #ae8e5b77;padding:12px 0 26px}.kicker{color:#d9ba7c;letter-spacing:.16em;font-size:11px;font-weight:750}h1,h2,h3{font-family:Georgia,serif}h1{font-size:clamp(37px,7vw,68px);line-height:1;margin:10px 0}header p{color:#cdcbb5;max-width:53ch}.nav{display:flex;flex-wrap:wrap;gap:8px;padding:21px 0 12px}.nav a{color:#ead2a1;background:#2a3b30;border:1px solid #a889555e;text-decoration:none;padding:4px 9px;border-radius:5px;font-size:12px}.nav a:hover{background:#40503b}section{scroll-margin-top:12px;margin-top:29px}.heading{display:flex;gap:14px;align-items:center;justify-content:space-between;margin-bottom:9px;border-bottom:1px solid #a889555e}.heading h2{font-size:24px;font-weight:500;margin:0 0 5px}.heading small{color:#dac08f;white-space:nowrap}.detail{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,285px),1fr));gap:8px}article{background:#24372b;border:1px solid #88744767;border-radius:8px;padding:8px;display:flex;align-items:center;gap:11px;min-width:0}article img{display:block;width:86px;height:70px;image-rendering:pixelated;border-radius:4px;border:1px solid #ad865c;flex:0 0 auto}article span{font-size:10px;text-transform:uppercase;letter-spacing:.06em;color:#dfbe7b}article h3{font-size:17px;line-height:1.15;margin:1px 0 3px;font-weight:600}article p{font-size:11px;line-height:1.35;margin:0;color:#cfceb9}footer{color:#c3b18a;border-top:1px solid #ae8e5b77;margin-top:30px;padding-top:15px;font-size:11px}@media(max-width:350px){article img{width:64px;height:52px}}'''
links=''.join(f'<a href="#{k}">{h(a["regions"][k])}</a>' for k in a['nuages']['zones_grand_large'])
out='<!doctype html><html lang="fr"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Les 50 lieux du Grand Large</title><style>'+style+'</style><main><header><div class="kicker">DESTINY IV · CARNET DE DESSIN</div><h1>Les 50 lieux du Grand Large</h1><p>Quatre grandes îles et quatre archipels. Chaque vignette est un détail du motif dessiné sur la carte jouable, agrandi sans lisser le pixel DS.</p></header><nav class="nav" aria-label="Huit régions">'+links+'</nav>'+''.join(sections)+'<footer>Les noms et la géographie ajoutés sont des créations pour Destiny. Les pigments et certains motifs de terrain proviennent de la référence DS fournie.</footer></main></html>'
(D/'Carnet-des-50-lieux.html').write_text(out);assert out.count('<article>')==50
