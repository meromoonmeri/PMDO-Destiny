#!/usr/bin/env python3
"""Model the distinct PMU objects using measured screen-space tops, relief envelopes, and props.
The source never implies known unseen faces: the other seven views are graphic reconstructions.
"""
from collections import Counter
from pathlib import Path
import math
import numpy as np
from scipy import ndimage as ndi
from Volumes import K, Model

# Tilt/height values are native measured projected dimensions, not scales for individual views.
IA={1:('Cheminée à portrait, bois grenat','foyer'),2:('Grande bibliothèque à corniche','biblio'),3:('Lit à baldaquin vert et or','lit'),4:('Trône royal bleu','siege'),5:('Orgue de guilde','buffet'),6:('Grande armoire à panneau doré','armoire'),7:('Comptoir de la Réserve','kiosque'),8:('Comptoir de l’Oracle','kiosque'),9:('Comptoir des Techniques','kiosque'),10:('Comptoir de la Banque','kiosque')}
NEW={
 'Pupitre-aux-cartes':('Pupitre aux cartes','pupitre',(68,49)),
 'Chariot-a-the':('Chariot à thé','chariot',(62,54)),
 'Grainotheque':('Grainothèque','grainotheque',(63,57)),
 'Horloge-lunaire':('Horloge lunaire','horloge',(35,78)),
}
CLASS={}
for row in Path(__file__).with_name('Modeles.txt').read_text().splitlines():
    if row and not row.startswith('#'):
        n,label,mode,*extras=row.split('|');depth=int(extras[0]) if extras and extras[0] else None;top=int(extras[1]) if len(extras)>1 and extras[1] else None
        CLASS[int(n)]=(label.strip(),mode,depth,top)
assert set(CLASS)==set(range(1,312))
WALL={'toile','miroir','paroi','arche','echelle'}
REGION={
 'Sol & tapis':{'sol','coussin'},'Séjours & chambres':{'siege','lit','lit-long','table','table-nappe','banc','gueridon','banquet','pupitre'},
 'Rangements & service':{'buffet','commode','armoire','biblio','bahut','caisse','pile','coffre','coffre-ouvert','chariot','grainotheque','etagere','sac','rouleaux'},
 'Végétaux & bassins':{'plante','palmier','pot','rocher','souche','orbe'},
 'Panneaux & tentures':{'panneau','drapeau','toile','miroir','echelle','paroi','arche'},
 'Ensembles':{'ensemble'},
 'Autres objets':{'bloc','foyer','kiosque','moulin','statue','mannequin','luminaire','horloge','relief'},
}
CATEGORY={t:g for g,count in REGION.items() for t in count}

def caption(row):
    name=row['id'];preferred=row.get('nom_atelier')
    if row['famille']=='IA':
        label,mode=IA[int(name.split('_')[3])];return label,mode,None,None
    if row['famille'] in {'Mob','Cpt','DecA','DecB'}:
        label,mode,d,top=CLASS[int(name.rsplit('_',1)[1])];return preferred or label,mode,d,top
    n=name.removeprefix('Guilde_Imm_pmu_')
    if n.startswith(('tapis_','paillasson_')):mode='sol'
    elif n.startswith(('panneau_','tableau_')):mode='panneau'
    elif n.startswith('banniere_'):mode='drapeau'
    elif n.startswith('caisse_'):mode='caisse'
    elif n.startswith('coffre_'):mode='coffre'
    elif n.startswith('table_rondin_'):mode='souche'
    else:mode={'buches_bois':'pile','fourneau_cuisine':'foyer','lit_fourrure':'coussin','table_banquet_seule':'banquet','PMU_Lampe_sur_pied_01':'luminaire','PMU_Table_bois_01':'table'}[n]
    return preferred or {'luminaire':'Lampe haute','table':'Table de paille'}.get(mode,n),mode,None,None

MATERIAL={'drapeau':'tissu','toile':'tissu','sol':'tissu','siege':'tissu','lit':'tissu','lit-long':'tissu','coussin':'tissu','mannequin':'tissu','sac':'tissu','rouleaux':'tissu',
          'plante':'feuille','palmier':'feuille','pot':'feuille','statue':'metal','bloc':'pierre','foyer':'pierre','arche':'pierre','paroi':'pierre','rocher':'pierre','orbe':'eau','luminaire':'cuivre'}
MAT={k:i for i,k in enumerate(('bois','pierre','tissu','metal','feuille','peau','cuivre','osier','eau'),start=1)}
THICKNESS={
 'panneau':(.16,3,19),'drapeau':(.26,8,18),'miroir':(.072,3,9),'toile':(.048,3,7),'echelle':(.16,4,10),'paroi':(.15,5,22),'arche':(.23,10,31),
 'biblio':(.42,13,31),'armoire':(.45,12,34),'buffet':(.44,13,28),'etagere':(.38,11,26),'bahut':(.42,13,33),'commode':(.43,10,30),
 'caisse':(.73,9,47),'coffre':(.62,8,38),'coffre-ouvert':(.79,11,49),'pile':(.56,7,50),'bloc':(.60,8,58),'foyer':(.44,14,40),
 'table-nappe':(.74,16,99),'banc':(.32,10,36),'table':(.71,13,134),'banquet':(.27,14,51),'gueridon':(.89,13,64),'pupitre':(.54,18,52),
 'siege':(.64,13,47),'lit':(.58,14,59),'lit-long':(.58,16,115),'sac':(.63,8,33),'rouleaux':(.59,9,31),'coussin':(.96,7,105),
 'plante':(.90,7,64),'palmier':(1.,16,42),'pot':(.84,10,56),'statue':(.64,7,53),'mannequin':(.55,8,33),'orbe':(.9,8,55),'souche':(.86,10,63),
 'rocher':(.72,12,85),'kiosque':(.74,14,93),'moulin':(.71,11,47),'luminaire':(.91,8,28),'relief':(.48,4,38),
 'chariot':(.65,16,57),'grainotheque':(.48,16,34),'horloge':(.38,10,21),
}
ROUND={'plante','palmier','pot','coussin','mannequin','statue','rouleaux','sac','souche','rocher','orbe','luminaire','moulin','kiosque','pile','relief'}

def build(src,mode,depth=None,top=None,*,strict=False):
    h,w=src.shape[:2];mask=src[:,:,3]>127
    assert mask.any(),(src.shape,mode)
    f,mi,ma=THICKNESS[mode]
    d=int(np.clip(w*f,mi,ma)) if depth is None else depth
    if top and mode not in ('biblio',):d=max(5,int(round(top/K))) if depth is None else depth
    if top and mode=='biblio' and depth is None:d=max(8,min(35,int(round(top/K))))
    if mode=='lit-long':d=max(20,int((h-min(19,max(12,h*.27)))/K))
    # Lamps / plants have wider crowns than their bases. The ground pivot is at the trunk, not the tip of a leaf.
    fBase=.5 if mode not in ROUND else (.34 if mode in ('plante','palmier','mannequin','luminaire','statue') else .44)
    d=min(max(3,d),max(3,int((h-max(2,h*.22))/K)))
    if mode in {'sol'}:raise AssertionError('Planar sprite passed to the volume renderer.')
    if mode in {'table','banc','gueridon'} and top is None and depth is None:
        # Infer the front apron line after the widest part. Insets / feet don't stretch the table top.
        fill=mask.sum(axis=1);good=np.where(fill>max(2,w*.71))[0]
        if len(good)>2:
            y0=min(h-max(4,h//6),max(4,int(good[-1])-max(2,round(h*.095))))
            if mode=='gueridon':y0=max(3,min(y0,round(w*.62)))
            d=max(5,min(ma,round(y0/K)))
    py=float(h-K*d*fBase);H=float(h-K*d*(.5+fBase))
    zsz=h+6
    zz=(np.arange(zsz)+.5)[:,None,None];vv=(np.arange(d)+.5-d/2)[None,:,None];xx=(np.arange(w)+.5)[None,None,:]
    pp=np.floor(py+K*vv-zz).astype('intp');ppk=np.clip(pp,0,h-1)
    M=np.pad(mask,((0,0),(0,0)))  # Source edge, not the cast shadow.
    grid=np.zeros((zsz,d,w),np.uint8)
    refOK=(pp>=0)&(pp<h)&M[ppk,np.arange(w)[None,None,:]]
    mat=MATERIAL.get(mode,'bois')
    def fill(b,material=mat):np.copyto(grid,MAT[material],where=np.broadcast_to(b,grid.shape))
    def rb(x0,x1,v0,v1,z0,z1,material=mat,clip=False):
        b=(xx>=x0)&(xx<x1)&(vv>=v0)&(vv<v1)&(zz>=z0)&(zz<z1)
        fill(b&refOK if clip else b,material)
    def el(x0,rx,v0,rv,z0,z1,material=mat,clip=False):
        b=(((xx-x0)/max(1,rx))**2+((vv-v0)/max(1,rv))**2<=1)&(zz>=z0)&(zz<z1)
        fill(b&refOK if clip else b,material)
    def yzu(u0,rx,v0,ry,z0,rz,material=mat,clip=False):
        b=((xx-u0)/max(1,rx))**2+((vv-v0)/max(1,ry))**2+((zz-z0)/max(1,rz))**2<=1
        fill(b&refOK if clip else b,material)
    def silhouette(limit=H,rnd=False,sub=.90,withrelief=False,material=mat):
        if rnd:
            # A different ellipse for each contour level (rather than cardboard or a circular cylinder).
            lo=np.argmax(M,axis=1);ri=w-np.argmax(M[:,::-1],axis=1);valid=M.any(1)
            lo[~valid]=0;ri[~valid]=w
            mid=ndi.gaussian_filter1d((lo+ri).astype(float)/2,1.45);rad=ndi.gaussian_filter1d((ri-lo).astype(float)/2,1.4)
            offset=(xx-mid[ppk])/np.maximum(1.6,rad[ppk]);th=np.sqrt(np.maximum(.12,1.-(sub*offset)**2))
            narrow=np.clip((rad[ppk]*2/max(1,w))**.68,.24,1.) if mode in {'plante','statue','mannequin','luminaire','souche','moulin','orbe'} else 1.
            vOK=np.abs(vv)<=np.maximum(1.15,(d*.5)*th*narrow)
        else:
            # Side and back have real thickness. Chamfer very outer corners only.
            bev=(np.abs(vv)>d/2-1.15)&((xx<1)|(xx>w-1));vOK=~bev
        if withrelief:
            # A shallow free-standing relief keeps single-pixel cut-outs on wrought work and poles.
            vOK=vOK&(np.abs(vv)<max(1.15,d*.4))
        fill(refOK&vOK&(zz<max(1.5,limit)),material)
    def table(deck,solidLegs=True,elliptic=False,lower=False,bodyW=None,matTop='bois'):
        L,R=(0.,float(w)) if bodyW is None else bodyW
        W=R-L
        b=min(d/2-1.,max(1.,d*.45)); lf=min(8,max(2,round(W*.052)));lift=max(0,deck-min(8,max(3,round(h*.105))))
        if elliptic:el((L+R)/2,W/2,0,d/2,lift,deck,matTop)
        else:rb(L,R,-d/2,d/2,lift,deck,matTop)
        if solidLegs:
            legXs=(L+max(1,W*.062),R-max(1,W*.062)-lf)
            if elliptic:
                for a in (.14,2.24,4.34):
                    xp=L+W/2+math.cos(a)*W*.31;yp=math.sin(a)*d*.31
                    rb(xp-lf*.62,xp+lf*.62,yp-lf*.52,yp+lf*.52,0,lift+.9,'cuivre')
                return
            for x in legXs:
                for v in (-b,b-lf):
                    rb(x,x+lf,v,v+lf,0,lift+.8,'bois')
                    if mode=='banc' and lift>8:rb(max(0,x-.8),min(w,x+lf+.8),v-.65,v+lf+.65,0,min(5,lift*.3),'pierre')
            if W>40:
                zzr=max(3,int(lift*.42));thk=1+int(lift>17)
                if lift>6 and mode in {'table','banc','pupitre'}:
                    for v in (-b,b-lf):rb(legXs[0],legXs[1]+lf,v,v+lf*.65,zzr,zzr+thk,'bois')
            if lower:rb(L+2,R-2,-b,b,max(4,lift*.23),max(6,lift*.23+3),'bois')
    if mode in {'table','banc','gueridon','banquet','pupitre'}:
        dh=max(5,H);elipse=mode=='gueridon'
        if mode=='banquet':
            # The trenchers and platters sit slightly above the plank, not on its fascia.
            hh=min(5,max(3,h*.09));table(dh-hh,True,False)
            for u in np.linspace(w*.06,w*.94,7):
                for v in (-d*.33,d*.33):el(u,max(3,w*.041),v,max(2,d*.101),dh-hh,dh-hh+2.35,'cuivre',True)
        elif mode=='gueridon':
            table(dh-1,True,True)
            if w<55 and np.sum((src[:,:,0]>173)&(src[:,:,1]>173)&(src[:,:,2]>125)&(np.indices((h,w))[0]<h*.4))>12:
                for u,v in [(w*.37,-d*.18),(w*.65,d*.16)]:el(u,3.4,v,3.4,dh-1,dh+2.4,'metal',True)
        elif mode=='pupitre':
            # A real sloping desk; the hinged top rests on front and rear rails.
            thick=max(5,h*.12);zT=dh+(np.clip(-vv/d,-.5,.5)*3.4)
            rb(2,w-2,-d/2+2,d/2-2,max(2,dh-8),dh-4,'bois')
            fill((zz<zT)&(zz>zT-thick)&(abs(vv)<d*.5)&refOK,'bois')
            for u in (3,w-7):
                for v in (-d/2+2,d/2-7):rb(u,u+4,v,v+4,0,dh-thick+1,'bois')
        else:table(dh,True,False)
    elif mode=='chariot':
        # Separate upper tray, wheels, lower tray and handle. The silhouette between floors stays open.
        L=1;R=round(w*.89);hh=max(14,H-5);floor=7
        rb(L,R,-d/2,d/2,hh-4,hh,'bois');rb(L+2,R-2,-d/2+2,d/2-1,floor,floor+3,'bois')
        rb(L+2,R-2,-d/2+2,-d/2+4,floor,hh-2,'bois')
        for u in (L+2,R-6):
            for v in (-d/2+2,d/2-5):rb(u,u+4,v,v+4,3,hh,'bois')
        for u in (L+5,R-4):
            for v in (-d/2+2,d/2-2):
                fill(((xx-u)**2+(zz-4.75)**2<27)&(np.abs(vv-v)<1.65),'bois')
                fill(((xx-u)**2+(zz-4.75)**2<8)&(np.abs(vv-v)<1.95),'cuivre')
        rb(R-1,w-1,-d*.30,-d*.24,hh-2,hh+1,'cuivre');rb(R-1,w-1,d*.18,d*.24,hh-2,hh+1,'cuivre');rb(w-3,w,-d*.30,d*.24,hh-1,hh+1.8,'bois')
        for a in [(.23,-.19,3.,2.9,'metal'),(.39,.12,3.,2.9,'metal'),(.64,-.20,7.,5.,'tissu')]:
            u,v,r,s,mt=a;yzu(w*u,r,d*v,s,hh+1.5,s,mt,False)
        rb(L+5,L+22,-.4*d,.11*d,floor+3,floor+5,'tissu')
    elif mode=='grainotheque':
        dh=max(10,H-6)
        rb(2,w-2,-d/2+1,d/2-1,3,dh-3,'bois');rb(0,w,-d/2,d/2,dh-3,dh,'bois');rb(1,w-1,-d/2+1,d/2-1,3,6,'bois')
        for u in (2,w-6):
            for v in (-d/2+2,d/2-5):rb(u,u+4,v,v+4,0,4,'bois')
        el(w*.78,4.8,-d*.23,4.,dh,dh+8,'feuille');el(w*.64,5.8,d*.12,4.7,dh,dh+3.2,'cuivre')
    elif mode=='biblio':
        L=max(1,round(w*.05));vr=-d/2;vf=d/2
        H=max(4,H);sills=max(4,round(H*.105));cap=max(3,round(H*.067))
        # All six shelves are real planar faces; the contents remain inset from the front uprights.
        rb(L,w-L,vr+1,vr+3,1,H,'bois');rb(0,w,vr,vf,H-cap,H+.3,'bois',True)
        rb(1,w-1,vr,vf,0,sills,'bois',True)
        rb(L,L+3,vr,vf,sills-1,H-cap+.5,'bois',True);rb(w-L-3,w-L,vr,vf,sills-1,H-cap+.5,'bois',True)
        n=4 if H>=42 else 3
        span=(H-cap-sills)/n
        for s in range(n):
            z=sills+s*span;rb(L,w-L,vr+2,vf-.3,z,z+1.65,'bois',True)
            for u in range(L+3,w-L-2,3):
                b1=max(2,span-(1.4+((u//3+s*3)%4)*.70))
                rb(u,min(u+3,w-L),vr+3,vf-1.75-(u//3%2),z+1.5,z+b1,'bois',True)
        # Source frontons taller than the slab are supported by the top of the cabinet.
        fill((zz>=H)&(zz<H+min(8,h*.10))&(vv>-d/2)&(vv<-d/2+min(5,d))&refOK,'bois')
    elif mode=='lit-long':
        # A north-south bed already foreshortened in the original, with a headboard and low mattress.
        dh=max(8,H);vr,vf=-d/2,d/2;L=max(1,w*.06);R=w-L
        rb(L,R,vr+2,vf-1,2,dh*.47,'bois');rb(L,R,vr+2,vf-.75,dh*.46,dh*.74,'tissu')
        rb(L,R,vr,vr+3,2,dh+1.5,'bois',True)
        rb(L,R,vf-2,vf,1,dh*.52,'bois');rb(L+2,R-2,vr+4,vr+max(8,d*.2),dh*.71,dh*.82,'tissu',True)
        for u in (L,R-2.4):
            for v in (vr+1,vf-3.5):rb(u,u+2.4,v,v+2.8,0,max(4,dh*.49),'bois')
    elif mode in {'siege','lit'}:
        dh=max(8,H);cap=dh*(.58 if mode=='lit' else .49)
        uL=max(1.5,w*.053);uR=w-uL;vf=d/2;vr=-d/2
        rb(uL,uR,vr+1,vf-1.,max(1,cap*.27),cap*.66,'bois',True)
        rb(uL,uR,vr+2,vf-1.,cap*.65,cap,'tissu',True)
        for u in (uL,uR-3):
            for v in (vr+2,vf-4):rb(u,u+3,v,v+3,0,cap*.43,'bois')
        if mode=='lit':
            rb(uL,uR,vr,vr+min(7,d*.23),max(1,cap*.42),dh+4,'bois',True)
            rb(uL,uR,vf-3,vf,1,cap*.75,'bois',True)
            # A uniformly thick curtain doesn't become a card at Right.
            if h>w*.9:
                for u in (uL,uR-3):rb(u,u+3,vr+1,vf-1,cap,dh,'tissu',True)
                rb(uL,uR,vr,vf,dh-2.5,dh,'bois',True)
        else:
            rb(uL,uR,vr,vr+max(3,d*.17),cap*.66,dh+3,'bois',True)
            for u0,u1 in [(uL,uL+w*.137),(uR-w*.137,uR)]:
                rb(u0,u1,vr+1,vf-2,cap*.5,cap+dh*.15,'tissu',True)
        # Chamfer source contour on raised ornament / end arm.
    elif mode=='table-nappe':
        if h>=w*.48:
            # Fabric draped over a table or awning rectangular, with thin independent support where present.
            if mask[-max(3,h//7):].mean()<.28:
                table(max(5,H),True,False,False,None,'tissu')
            else:silhouette(H+3,False,material='tissu')
        else:silhouette(H+2,False,material='tissu')
    elif mode=='foyer':
        # The opening's silhouette stays anchored; above the mantle, make the chimney shallower.
        upper=zz>H*.68
        fill(refOK&(zz<=H+min(8,d*.21))&((~upper)|((vv<d*.12)&(vv>-d*.48))),'pierre')
        m=refOK&(zz>=H*.61)&(zz<=H*.72)
        fill(m,'bois')
    elif mode=='drapeau':
        # A folded hanging meets a real crossbar. The folds have millimetres of thickness in profile.
        xp=(xx/w);rp=np.clip(ppk/h,0,1);o=.32*d*np.sin((xp*1.17+.09)*math.tau)+.08*d*np.sin((xp*.9+rp*.7)*math.tau)
        fill(refOK&(np.abs(vv-o)<1.12)&(zz<=H+3.6),'tissu')
        pole=np.where(np.any(mask[-max(3,h//9):],axis=0))[0]
        stem=float(np.median(pole)) if len(pole) else w/2
        fill(refOK&(np.abs(vv)<1.55)&((np.abs(xx-stem)<2.0)|(ppk<h*.22))&(zz<=H+min(4,d*.35)),'bois')
    elif mode=='palmier':
        # The visible branches are reconstructed as radial, drooping leaves around a slender stalk.
        uc=w*.48;P=min(w*.29,h*.145);pot=round(h*.15)+1
        ht=max(14,h-K*d*.37);tm=ht*.63
        for step in range(pot):
            r=P*(.64+.36*step/max(1,pot-1))
            el(uc,r,0.,r*.93,step,step+1,'bois')
        el(uc,P*1.08,0,P,pot,pot+2.1,'cuivre');el(uc,P*.77,0,P*.70,pot+1.75,pot+2.8,'bois')
        for z in range(pot,int(tm)+1):
            u=uc+1.2*math.sin((z-pot)*.124);el(u,1.2,0,1.6,z,z+1,'bois')
        for j in range(9):
            a=j*2.39996+.35;dx,dy=math.cos(a),math.sin(a);ln=.38*w+((j*7)%5-2)
            along=(xx-uc)*dx+vv*dy;cross=(xx-uc)*dy-vv*dx;t=along/ln
            height=tm+(j%3-1)*3+8*np.sin(np.clip(t,0,1)*math.pi*.8)-(2+(j*5)%10)*t*t
            wid=1.1+np.sin(np.clip(t,0,1)*math.pi)**.65*(2.3+(j%3)*.25)
            wis=wid-((np.floor(along*1.2).astype(int)%5)==3)*.65
            fill((t>-.05)&(t<1)&(np.abs(cross)<wis)&(np.abs(zz-height)<1.15),'feuille')
            fill((t>0)&(t<.93)&(np.abs(cross)<.48)&(np.abs(zz-height)<1.3),'feuille')
    elif mode=='kiosque':
        # Separate a low counter/platform from the ornamental upright. A mascot face does not become a lid.
        H=max(9,H);b0=max(4,H*.33);lp=refOK&(zz<=b0+1.4)&(abs(vv)<d*.49)
        rgb=src[mask,:3].astype(int);neutral=(rgb.max(axis=1)-rgb.min(axis=1)<36).mean()>.55
        steel='pierre' if neutral else 'bois'
        fill(lp,steel)
        fade=np.clip((zz-b0)/max(1,H-b0),0,1)
        # Sculpted sides taper as they meet the mask, which sits near the public side of the counter.
        chamber=(vv>=-d*(.43-.23*fade))&(vv<=d*(.44-.08*fade))
        fill(refOK&chamber&(zz>b0)&(zz<=H+d*.22),steel)
        fill(refOK&(zz>=b0-1)&(zz<=b0+2)&(np.abs(vv)<d*.49),'bois' if not neutral else 'pierre')
    elif mode in {'paroi','arche','echelle','miroir','toile','panneau'}:
        # A mounted panel has thin planks and a separate stand. Native holes pass through an arch or ladder.
        short=(mode in ('miroir','toile','drapeau','echelle'))
        silhouette(H+min(3,d*.19),False,withrelief=short)
    elif mode in ROUND or mode=='coffre-ouvert':
        curve=mode not in ('pile','coffre-ouvert')
        silhouette(H+min(14,d*.26),curve,material=mat)
        if mode=='plante':
            fill((grid!=0)&(zz<max(3,min(H*.3,d*.25)))&(pp>h*.71),'bois')
        if mode=='luminaire':
            # The opal glass and brass stem do not become brown in the rear angles.
            fill((grid!=0)&(zz>H*.65)&(pp<h*.30),'tissu')
        if mode=='coffre-ouvert':
            # Projected lid on a hinge at the far edge, in front of a low crenelated base.
            hi=zz>H*.52
            grid[hi & (vv>d*.10) & (grid>0)]=0
            if mask.mean()>.40:
                rb(w*.18,w*.83,-d*.30,d*.30,2,H*.41,'bois',True)
    elif mode=='coffre':
        silhouette(H+2,False)
        # Rounded lid and tiny brass hinges on the back plane; these are reconstructed.
        cap=zz>H*.66
        gate=np.abs(vv)<d/2*(1-.19*np.clip((zz-H*.66)/max(1,H*.34),0,1))
        grid[cap&(~gate)&(grid!=0)]=0
        for x0 in (w*.24,w*.70):rb(x0,x0+max(1,w*.076),-d/2,-d/2+1.1,H*.55,H*.71,'cuivre',True)
    else:
        silhouette(H+(2 if mode in {'buffet','armoire','horloge','bloc','bahut','etagere'} else 0),False)
    if np.count_nonzero(grid)<3:silhouette(max(H+9,3),False)
    m=Model(src,grid,(w/2,py),mode,mat)
    if not strict and m.fit<.56 and mode!='palmier':
        # Unusual franken-sprites (a single native .dir can be a sheet) get an enveloping volume instead of dropping pieces.
        old=grid.copy();grid[:]=0;silhouette(H+max(4,d*.31),mode in ROUND,.68)
        if mode in {'table','banc','gueridon','pupitre','siege','lit'}:
            notlower=zz>H*.30;grid=np.where(notlower&refOK&((old!=0)|(grid!=0)),np.maximum(old,grid),old).astype(np.uint8)
        if np.count_nonzero(grid)>4:
            m1=Model(src,grid,(w/2,py),mode,mat)
            if m1.fit>m.fit:m=m1
    return m


def pieces(src,ident):
    """Group disconnected prop islands; position them from their own feet at the scene pivot."""
    a=src[:,:,3]>127;h,w=a.shape
    if ident.endswith('_006') and h==80 and w==65:
        # The native resource holds a bed, a round stand, a basket and a low porcelain rack.
        regions=[(0,0,32,68,'lit-long'),(32,0,61,21,'gueridon'),(33,21,65,39,'pot'),(32,40,65,80,'etagere')]
        ans=[]
        for x,y,r,b,m in regions:
            a=src[y:b,x:r];Y,X=np.where(a[:,:,3]>127)
            if len(X):ans.append((x+int(X.min()),y+int(Y.min()),a[Y.min():Y.max()+1,X.min():X.max()+1].copy(),m))
        return ans
    smooth=ndi.binary_closing(np.pad(a,2),np.ones((3,3)))[2:-2,2:-2] | a
    L,n=ndi.label(smooth,np.ones((3,3)))
    islands=ndi.find_objects(L); parts=[]
    for k,rect in enumerate(islands,start=1):
        y,x=rect;b=src[rect].copy(); b[L[rect]!=k]=0
        solid=np.sum(b[:,:,3]>127)
        if solid<8:continue
        hh,ww=b.shape[:2]
        if hh<4 or ww<4:continue
        sy,sx=y.start,x.start
        if ('122' in ident and hh>26 and ww>34 and sy<h*.35) or (hh>19 and ww>42 and hh<ww*.50 and solid>ww*hh*.73):typ='sol'
        elif hh>ww*2.3 and hh>32:typ='panneau'
        elif hh<ww*.52 and ww>28:typ='bahut'
        elif hh<ww*.75 and hh>14 and sy>h*.45:typ='caisse'
        elif ident.endswith('_006') and hh>46:typ='lit'
        elif hh>=hw(ww,1.18):typ='statue'
        elif a[rect].mean()>.78 and hh>15 and ww>16:typ='caisse'
        else:typ='relief'
        parts.append((sx,sy,b,typ))
    if len(parts)==1 and parts[0][2].shape[0]*parts[0][2].shape[1]>w*h*.68:return []
    return parts[:24]

def hw(w,f):return w*f
