from pathlib import Path
import gzip,json,copy,gc,collections
R=Path('/home/user/chantier-deplacement-arbres-bassin');F=Path('/home/user/chantier-corrections-bassin-55');journal=json.loads((R/'journal-deplacement.json').read_text())
def read(p):return json.loads(gzip.decompress(p.read_bytes()).decode('utf-8-sig'))
def reachable(o,start):
 obs=o['obstacles'];w=len(obs);h=len(obs[0]);
 def free(x,y):return 0<=x<w-1 and 0<=y<h-1 and all(obs[x+i][y+j]['Tags']==0 for i in (0,1) for j in (0,1))
 assert free(*start),start
 q=collections.deque([start]);seen={start}
 while q:
  x,y=q.popleft()
  for t in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
   if t not in seen and free(*t):seen.add(t);q.append(t)
 return seen
for entry in journal['cartes']:
 name=entry['carte'];before=read(F/'candidat/payload'/name);after=read(R/'candidat/payload'/name);bo=before['Object'];ao=after['Object'];bl={x['Name']:x['Tiles'] for x in bo['Layers']};al={x['Name']:x['Tiles'] for x in ao['Layers']};
 for c in entry['calques']:
  x,y,n=c['x'],c['y'],c['layer'];assert bl[n][x][y]==c['avant'] and al[n][x][y]==c['apres'];al[n][x][y]=copy.deepcopy(c['avant'])
 for c in entry['collisions']:
  x,y=c['x'],c['y'];assert bo['obstacles'][x][y]==c['avant'] and ao['obstacles'][x][y]==c['apres'];ao['obstacles'][x][y]=copy.deepcopy(c['avant'])
 assert before==after, 'modifications non journalisées';del before,after,bo,ao,bl,al;gc.collect()
 b=read(F/'candidat/payload'/name)['Object'];a=read(R/'candidat/payload'/name)['Object']; rb=reachable(b,(155,257));ra=reachable(a,(155,257));targets=[(155,257),(170,257),(153,263),(171,263),(157,272),(170,272)]
 print(name,'intégrité PASS ; changements',len(entry['calques']),'cellules,',len(entry['collisions']),'collisions ; BFS approximatif 16×16',len(rb),'->',len(ra),'cibles',[(p,p in rb,p in ra) for p in targets]);
 assert all((t in rb)==(t in ra) for t in targets)
 del b,a;gc.collect()
exec(open(R/'analyser-placement.py').read().split('for label,x0,y0 in trees:')[0])
for label,x0,y0,dx,dy in [('haut',97,253,-2,-1),('milieu',97,262,-2,-1),('bas',98,272,-3,-1),('est',158,263,0,-3)]:
 n=0
 for sx in range(124,134):
  for sy in range(19,24):
   t=r.get_tile(sx,sy)
   if t is None:continue
   cl=imcell('Cliffs',x0+sx-124+dx,y0+sy-15+dy)
   n+=sum(a in colors and b[3]==255 for a,b in zip(t.get_flattened_data(),cl.get_flattened_data()))
 assert n==0,(label,n)
 print(label,'ombre basse / falaise:',n,'pixel')
# Check each animation cell has migrated with the identical 3 frames and timing.
for variant in ['reverie_etang.rsground.gz','reverie_etang_Dev.rsground.gz']:
 b=read(F/'candidat/payload'/variant)['Object'];a=read(R/'candidat/payload'/variant)['Object'];bl=next(l['Tiles'] for l in b['Layers'] if l['Name']=='Objects Anim');al=next(l['Tiles'] for l in a['Layers'] if l['Name']=='Objects Anim')
 for x in range(95,98):
  for y in range(260,263):assert bl[x][y]==al[x-1][y]
 print(variant, 'touffe : 9 cellules animées, images et cadence identiques après translation')
 del a,b,bl,al;gc.collect()
