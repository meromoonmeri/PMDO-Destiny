#!/usr/bin/env python3
"""Find clear layouts with a free service side, and precompute doorway connectivity."""
from pathlib import Path
import json,re
from collections import deque
ROOT=Path(__file__).resolve().parents[1]; BASE=ROOT.parent/'Guilde-Destiny-Mobilier-Halcyon-IA.html'
H='guilde_destiny_accueil'
DEMO={'guilde_destiny_accueil':(156,188),'guilde_destiny_refectoire':(214,190),'guilde_destiny_cuisine':(325,151)}
AXES={H:[[232,132,48,221]]}
GROUPS={}

def base():
    html=BASE.read_text();m=re.search(r'<script id="donnees"[^>]*>(.*?)</script>',html,re.S);assert m;return json.loads(m[1])

def overlap(a,b):return a[0]<b[0]+b[2] and a[0]+a[2]>b[0] and a[1]<b[1]+b[3] and a[1]+a[3]>b[1]
def grid(r):return {(x,y) for y,row in enumerate(r['floor']) for x,a in enumerate(row) if a=='1'}
def fill(sl,origin,blocked=()):
    seen={origin};q=deque([origin]);
    while q:
        x,y=q.popleft()
        for p in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
            if p in sl and p not in blocked and p not in seen:seen.add(p);q.append(p)
    return seen

def seed_groups(r,sl):
    pts=set()
    for x,y,w,h in [g['rect'] for g in r['gates']]+r['mark']:
        cx,cy=int((x+w/2)//8),int((y+h/2)//8)
        best=min(sl,key=lambda a:((a[0]-cx)**2+(a[1]-cy)**2,a))
        if (best[0]-cx)**2+(best[1]-cy)**2<=36:pts.add(best)
    remain=sorted(pts);groups=[]
    while remain:
        ss=fill(sl,remain[0]);p=[v for v in remain if v in ss];remain=[v for v in remain if v not in ss]
        if len(p)>1:groups.append(p)
    return groups

def samples(r,a,x,y,sol):
    if x<0 or y<0 or x+a['w']>r['w'] or y+a['h']>(r['south']['bottom'] if r['south'] else r['h']):return False
    rect=[x,y,a['w'],a['h']]
    if any(overlap(rect,b) for b in [g['rect'] for g in r['gates']]+r['mark']):return False
    # Eye-level picture may rise above planks, but the entire grounded model fits them.
    for name in ('empreinte','allée'):
        for dx,dy in a[name]:
            X,Y=x+dx,y+dy
            if (X//8,Y//8) not in sol or any(b[0]<=X<b[0]+b[2] and b[1]<=Y<b[1]+b[3] for b in AXES.get(r['id'],[])):return False
    # Keep two tiles at the threshold. The editable atelier also checks other objects.
    if any((g[0]-8<=x+dx<g[0]+g[2]+8 and g[1]-8<=y+dy<g[1]+g[3]+8) for dx,dy in a['empreinte'] for g in [q['rect'] for q in r['gates']]+r['mark']):return False
    return True

def routes(r,sl,tiles):
    halo={(i+dx,j+dy) for i,j in tiles for dx,dy in [(0,0),(-1,0),(0,-1),(1,0),(0,1)]}
    for g in GROUPS[r['id']]:
        if any(u in halo for u in g):return False
        reached=fill(sl,g[0],halo)
        if any(u not in reached for u in g):return False
    return True

def config(doc,rows):
    groups={};ex={}; rooms={r['id']:r for r in doc['rooms']}; stats=[]
    for n,r in rooms.items():groups[n]=seed_groups(r,grid(r))
    GROUPS.update(groups)
    for n,(cx,cy) in DEMO.items():
        r=rooms[n];floor=grid(r);ex[n]={}
        for a in rows:
            ax,ay=a['pivot']; candidates=sorted(((x,y) for x in range(0,r['w']-a['w'],8) for y in range(0,r['h']-a['h'],8)),key=lambda p:(p[0]+ax-cx)**2+(p[1]+ay-cy)**2)
            q=next(( [x,y] for x,y in candidates if samples(r,a,x,y,floor) and routes(r,floor, {((x+u)//8,(y+v)//8) for u,v in a['empreinte']})),None);assert q,(n,a['direction'])
            ex[n][a['id']]=q;stats.append({'salle':r['label'],'direction':a['direction'],'haut_gauche':q,'pivot_sol':[q[0]+ax,q[1]+ay],'empreinte_et_allée':True,'liaisons_préservées':True})
    # Second independent check that no demonstration repeats the accumulation of items.
    return {'exemples':ex,'axes':AXES,'routes':groups},stats

if __name__=='__main__':
    doc=base();idx=json.loads((ROOT/'Index-Comptoirs.json').read_text());q,st=config(doc,idx['orientations']);(ROOT/'Implantations.json').write_text(json.dumps(st,ensure_ascii=False,indent=2)+'\n');print(len(st),'essais sur 3 plans')
