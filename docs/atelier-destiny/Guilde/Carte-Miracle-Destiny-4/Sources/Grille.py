"""Bake reversible travel legs. Check new routes against the actual composed geographical alpha."""
import numpy as np
from scipy import ndimage as nd
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import dijkstra, connected_components
from math import hypot, sqrt


def navigation(lands, wet, sites, coast_hints, spiral):
 h,w=lands.shape; step=4; xs,ys=np.arange(2,w,step),np.arange(2,h,step);gh,gw=len(ys),len(xs)
 idx=np.arange(gw*gh).reshape((gh,gw));g=lands[np.ix_(ys,xs)];wetg=wet[np.ix_(ys,xs)]
 X,Y=np.meshgrid(xs,ys); moves=[(1,0,1),(-1,0,1),(0,1,1),(0,-1,1),(1,1,sqrt(2)),(-1,1,sqrt(2)),(1,-1,sqrt(2)),(-1,-1,sqrt(2))]
 fine=lands==0;ym,xm=np.ogrid[:h,:w];fine&=(xm-spiral[0])**2+(ym-spiral[1])**2>=18**2
 fine[:13]=False;fine[-13:]=False;fine[:,:15]=False;fine[:,-15:]=False
 def graph(mask,fine_allowed,pen):
  a=[];b=[];v=[]
  for dx,dy,d in moves:
   x1,x2=max(0,-dx),min(gw,gw-dx);y1,y2=max(0,-dy),min(gh,gh-dy)
   skip=np.s_[y1:y2,x1:x2];dest=np.s_[y1+dy:y2+dy,x1+dx:x2+dx]
   ok=mask[skip]&mask[dest]
   if dx and dy:ok&=mask[np.s_[y1:y2,x1+dx:x2+dx]]&mask[np.s_[y1+dy:y2+dy,x1:x2]]
   for t in (1,2,3):ok&=fine_allowed[np.ix_(ys[y1:y2]+dy*t,xs[x1:x2]+dx*t)]
   if not ok.any():continue
   a.append(idx[skip][ok]);b.append(idx[dest][ok]);v.append(step*d*(1+.5*(pen[skip][ok]+pen[dest][ok])))
  if not a: raise ValueError('No traversable cells in this land mass')
  return coo_matrix((np.concatenate(v),(np.concatenate(a),np.concatenate(b))),shape=(gh*gw,gh*gw)).tocsr()
 def core(comp,allowed):
  _,cats=connected_components(comp,directed=False)
  allowed=allowed.ravel();best=np.bincount(cats[allowed]).argmax();return (allowed&(cats==best)).reshape((gh,gw))
 def point(n):y,x=divmod(int(n),gw);return [int(xs[x]),int(ys[y])]
 def nearest(m,p,pen=None):
  q=(X-p[0])**2+(Y-p[1])**2
  if pen is not None:q=q+pen
  if not m.any():raise ValueError('No node for '+str(p))
  return int(np.argmin(np.where(m,q,np.inf)))
 def compress(nodes):
  if len(nodes)<3:return [point(n) for n in nodes]
  return [point(nodes[0])]+[point(nodes[i]) for i in range(1,len(nodes)-1) if nodes[i]-nodes[i-1]!=nodes[i+1]-nodes[i]]+[point(nodes[-1])]
 tr=[]
 def paths(grid,stops,m):
  stops=list(stops.items()); added=0
  for i,(key,n) in enumerate(stops[:-1]):
   ds,before=dijkstra(grid,directed=False,indices=n,return_predecessors=True)
   for k,e in stops[i+1:]:
    assert np.isfinite(ds[e]),(key,k,'accès impossible')
    q=[e];u=e
    for _ in range(gw*gh):
     if u==n:break
     u=int(before[u]);assert u>=0;q.append(u)
    p=compress(q[::-1]);tr.append({'a':key,'b':k,'mode':m,'p':p,'distance':round(sum(hypot(u[0]-v[0],u[1]-v[1]) for u,v in zip(p,p[1:])),4)});added+=1
  return added
 sea=fine[np.ix_(ys,xs)];pen=.67*np.clip(1-nd.distance_transform_edt(sea)/8,0,1);ocean=graph(sea,fine,pen);sea=core(ocean,sea)
 seab={}; ports={}; count=0
 for s in sites:
  if not s['island']:
   n=nearest(sea,s['point']);seab[s['id']]=n;s['point']=point(n)
 for lab in sorted({s['island'] for s in sites}- {0}):
  a=[s for s in sites if s['island']==lab];mat=lands==lab;allowed=g==lab
  gd=graph(allowed,mat,2.8*wetg+.43*np.clip(1-nd.distance_transform_edt(allowed)/5,0,1));allowed=core(gd,allowed)
  here={};used=set()
  for s in a:
   px,py=s['loc'];safe=allowed&~wetg
   # Avoid parking Pikachu on the marker. Narrow islands may still have a marker at the foot.
   clearance=~((X-22<=px+6)&(X+23>=px-6)&(Y-37<=py+6)&(Y+8>=py-6))
   reduced=safe&clearance&((X-px)**2+(Y-py)**2<=58**2)
   if not reduced.any():reduced=safe if safe.any() else allowed
   for n0 in used:reduced=reduced.copy();reduced.ravel()[n0]=False
   n=nearest(reduced if reduced.any() else allowed,s['point'],125.*wetg);here[s['id']]=n;s['point']=point(n);used.add(n)
  hint=coast_hints.get(lab,a[0]['point']);opts=[]
  for yy,xx in zip(*np.nonzero(allowed)):
   for dx,dy,_ in moves[:4]:
    bx,by=xx+dx,yy+dy
    if not (0<=bx<gw and 0<=by<gh and sea[by,bx]):continue
    xp,yp=xs[xx],ys[yy];opts.append(((xp-hint[0])**2+(yp-hint[1])**2+215*wetg[yy,xx],int(idx[yy,xx]),int(idx[by,bx])))
  assert opts,(lab,[s['id'] for s in a]);_,dn,sn=min(opts)
  k,j='port-'+str(lab),'mer-'+str(lab);here[k]=dn;seab[j]=sn;ports[lab]={'terre':point(dn),'mer':point(sn)}
  tr.append({'a':k,'b':j,'mode':'port','p':[point(dn),point(sn)],'distance':4.})
  count+=paths(gd,here,'terre')
 count+=paths(ocean,seab,'mer');assert len(tr)==count+len(ports)
 # Check the interpolated legs at true pixel resolution, excluding the deliberate shore changes.
 for e in tr:
  if e['mode']=='port':continue
  v=e['p'];lab=lands[v[0][1],v[0][0]]
  for (x,y),(xx,yy) in zip(v,v[1:]):
   num=max(abs(x-xx),abs(y-yy))+1;u=np.linspace(x,xx,num).round().astype(int);k=np.linspace(y,yy,num).round().astype(int)
   assert ((lands[k,u]==lab).all() if e['mode']=='terre' else fine[k,u].all()),e
 return tr,ports
