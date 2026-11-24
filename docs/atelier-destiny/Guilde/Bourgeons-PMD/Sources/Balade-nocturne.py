#!/usr/bin/env python3
"""Original Grodoudou backdrops, Carrefour brambles, and plant-driven light."""
import hashlib,re
from io import BytesIO
from base64 import b64decode
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage as nd
from scipy.interpolate import PchipInterpolator
import importlib.util

S=Path(__file__).resolve().parent; PROJECT=S.parents[1]

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod

R=load('rive_sources',S/'Recaler-rives.py'); L,V,T,F=R.L,R.V,R.T,R.F
A=load('texture_de_lueur',PROJECT/'Lumiere-Ancree/Sources/Lueur.py')
REF=PROJECT.parent/'Reference-Guildhouse/Project-Pokemon/Guilde-de-Grodoudou.html'
ID=lambda key:'guilde_destiny_'+key
HALL=ID('accueil');CROSS=ID('carrefour')
REFLECT_MAX=53
BUD_MAX=147
GROUPS={
 'commune':('G01P04A','G01P04C'), 'maitre':('G01P05A','G01P05C'),
 'refectoire':('G01P06A','G01P06B'), 'equipe':('G01P07A','G01P07C'),
 'nord':('G01P09A','G01P09C'), 'sud':('G01P10A','G01P10C'),
}
ARCADE_RESERVE=(224,64,64,80)
THRESHOLD_RESERVE=(224,313,64,39)


def swatches(path=REF):
    """Read corner plateaus from the largest embedded original per map ID."""
    codes={k for group in GROUPS.values() for k in group}|{'G01P02A','G01P03A','G01P08A'}
    found={}
    for fig in re.findall(r'<figure\b[^>]*>.*?</figure>',path.read_text(encoding='utf8'),re.S):
        title=re.search(r'<figcaption><b>(G01P\d{2}[A-C])\.png</b>',fig)
        src=re.search(r'<img src="data:image/[^;]+;base64,([^"]+)',fig)
        if not title or not src or title[1] not in codes or 'APNG' in fig:continue
        raw=b64decode(src[1]);im=Image.open(BytesIO(raw)).convert('RGBA');w,h=im.size
        if title[1] not in found or w*h>found[title[1]][0]:
            a=np.asarray(im);rgb=a[0,0];top=int(np.all(a==rgb,axis=2).sum())
            found[title[1]]=(w*h,dict(dimensions=[w,h],rgb=rgb[:3].tolist(),pixels_de_cette_teinte=top,
                                       sha256=hashlib.sha256(raw).hexdigest(),coins_uniformes=all(np.all(p==rgb) for p in [a[:8,:8],a[-8:,:8],a[:8,-8:],a[-8:,-8:]])))
    assert found.keys()==codes
    data={k:v[1] for k,v in sorted(found.items())}
    for k,v in data.items():
        assert v['coins_uniformes'] and v['pixels_de_cette_teinte']>50000,(k,v)
    assert data['G01P02A']['rgb']==[31,31,63]
    assert data['G01P04A']['rgb']==[23,23,63] and data['G01P04C']['rgb']==[15,15,47]
    assert data['G01P09C']['rgb']==[7,7,31]
    return data


def scenery(r,d,source):
    b=L.decode(r['base']);f=L.decode(r['front']);gid=r['id'];n=r['n']
    assert not ((b[...,3]<255)&(f[...,3]<255)).any()
    merged=np.where(f[...,3:]>0,f[...,:3],b[...,:3]).astype(int)
    distance=abs(merged-T.BRUN).max(2);exact=distance==0
    labels,_=nd.label(exact);edge=np.unique(np.concatenate([labels[0],labels[-1],labels[:,0],labels[:,-1]]))
    border=np.isin(labels,edge[edge>0]);assert border.sum()>55000
    # Key the same visible backdrop on *both* layers: some front tiles have
    # brown padding around the roof and posts. Keep the dark outline. Remove
    # the one-pixel brown fringe, not disconnected flecks in the timber.
    fringe=nd.binary_dilation(border,structure=np.ones((3,3)))&(distance<=3)
    key=border|fringe
    for i,p in enumerate(r['patches']):
        palette=d['nuits'][r['nuit']] if i==3 else d['lumieres'][r['nuit']][i]
        brown=[palette['lut'][c][int(t)] for c,t in enumerate(T.BRUN)]
        for x,y,img in p:
            patch=L.decode(img);h,w=patch.shape[:2];m=key[y:y+h,x:x+w]&(patch[...,3]>0)&(f[y:y+h,x:x+w,3]==0)
            # Some window rectangles include a corner of empty backdrop.
            assert (abs(patch[m,:3].astype(int)-brown)<=5).all(),(gid,x,y,i)
    names=list(GROUPS[r['nuit']]);names[0]={1:'G01P02A',2:'G01P03A',5:'G01P08A',9:'G01P08A',10:'G01P08A'}.get(n,names[0])
    j,nu=(np.array(source[k]['rgb']) for k in names)
    tones=[np.rint(j*(1-z)+nu*z).astype(int).tolist() for z in (0,.19,.58,1)]
    return dict(matte=L.pack(F.rgba(key.astype(np.uint8)*255,(0,0,0))),rgb=tones), key, dict(sources=names,phases=tones,pixels=int(key.sum()),pixels_du_calque_avant=int((key&(f[...,3]>0)).sum()))


def pixels(rects,size):
    return T.mask_rects(size,rects)


def branche_verticale(stock,axis_rows,width,x,y,allowed,flip):
    tex=np.rot90(stock,-1).copy()
    if flip:tex=tex[:,::-1].copy()
    nodes=np.asarray(axis_rows);lo,hi=nodes[[0,-1],1]
    mid=PchipInterpolator(nodes[:,1],nodes[:,0])(np.clip(y,lo,hi));u=np.clip((y-lo)/(hi-lo),0,1)
    spread=width*(.58+.42*u**.65)
    tx=np.rint(((x-mid)/(spread-1)+.5)*(tex.shape[1]-1)).astype(int)
    ty=np.rint(u*(tex.shape[0]-1)).astype(int)
    m=(tx>=0)&(tx<tex.shape[1])&(y>=lo)&(y<=hi)&allowed
    out=np.zeros((*x.shape,4),np.uint8);out[m]=tex[ty[m],tx[m]]
    live=out[...,3]>0;out[live,:3]=np.rint(out[live,:3]*[.91,1.,.86]).astype(np.uint8)
    return out


def ronces(r,d,void=None):
    assert r['id']==CROSS
    _,shed=V.modules();thin=shed[0];stock=V.bramble()
    _,f,x,y,_,_,_,_,allowed,_=F.freeze_support(r,d)
    if void is not None:allowed&=~void
    # Passage drawn at x215–264. Rectangles from the original map remain as they are.
    zones=[[(208,7),(207,17),(207,29),(209,37)],[(272,10),(273,19),(273,27),(270,37)]]
    poles=[[(209,25),(208,37),(208,49),(210,54),(208,64)],[(270,26),(271,39),(271,50),(270,56),(272,65)]]
    items=[];spots=[];info=[]
    for k in (0,1):
        branch_mask=allowed&(y<39)&((x>=204)&(x<=214) if not k else (x>=265)&(x<=275))
        post_mask=allowed&(y>=23)&(y<67)&((x>=200)&(x<=214) if not k else (x>=265)&(x<=279))
        twig=branche_verticale(stock,zones[k],8.4,x,y,branch_mask,k==1)
        # Let the gilded cap rings show through the winding, not a strip of opaque green.
        collars=[(25,29),(44,51)] if not k else [(25,30),(43,50)]
        wrap,ids,_=V.winding(thin,x,y,('Ronce du montant nord',poles[k],14,collars),not k,post_mask)
        weave=np.array(Image.alpha_composite(Image.fromarray(twig),Image.fromarray(wrap)))
        cover=weave[...,3]>0
        assert cover[y<39].sum()>44 and cover.sum()>140
        color=weave.astype(int);looks=[]
        for j in np.unique(ids[cover]):
            if not j:continue
            m=(ids==j)&cover
            cy,cx=np.nonzero(m)
            if len(cx)<2:continue
            z=float(np.hypot((cy.mean()-36)*1.20,cx.mean()-poles[k][0][0]))
            looks.append((z,m))
        if looks:core=min(looks,key=lambda a:a[0])[1]
        else:
            bright=color[...,0]*.38+color[...,1]*.72-.55*(y-36)**2
            near=cover&(y>=30)&(y<=42)&(color[...,0]>=color[...,1])
            q=np.unravel_index(np.argmax(np.where(near,bright,-np.inf)),near.shape);cy,cx=q
            core=cover&((x-cx)**2+(y-cy)**2<3)
        yy,xx=np.where(core);assert 1<len(xx)<35
        px,py=float(xx.mean()),float(yy.mean());assert 23<py<52
        weave[core,:3]=np.rint(weave[core,:3]*.58+np.array([231,201,136])*.42).astype(np.uint8)
        items.append(weave);spots.append((round(px,2),round(py,2),core))
        info.append(dict(montant=['ouest','est'][k],pointe=zones[k],enroulement=poles[k],pixels=int(cover.sum()),bourgeon=[round(px,2),round(py,2)]))
    limit=allowed&(y<66)&((x>=199)&(x<=214)|(x>=265)&(x<=280))
    s,t,_=V.combine(items,limit,f[...,3]>0)
    original=d['lianes'][CROSS];compo=[]
    for k,q in zip(('s','t'),(s,t),strict=True):
        a=L.decode(original[k]);b=np.array(Image.alpha_composite(Image.fromarray(a),Image.fromarray(q)));compo.append(b)
    out=dict(s=L.pack(compo[0]),t=L.pack(compo[1]),v=original['v']+2)
    side=(s[...,3]>0)|(t[...,3]>0)
    assert not side[L.extract_alpha(d,r)|(x>=215)&(x<=264)].any()
    combined=np.array(Image.alpha_composite(Image.fromarray(s),Image.fromarray(t)))
    return out,spots,combined,side,info


def smooth(a):
    a=np.clip(a,0,1);return a*a*(3-2*a)


def plein_sol(x,y,floor,wood,sx,sy,hand):
    # Find the local receiver, well below the bud and toward the interior.
    # The collision grid is used to place it, never to silhouette the light.
    z=((x-(sx+hand*8))/1.15)**2+((y-(sy+17))/.88)**2
    valid=floor&wood&(y>=sy-2)
    if not valid.any():valid=floor&wood
    cy,cx=np.unravel_index(np.argmin(np.where(valid,z,np.inf)),z.shape)
    gap=float(np.hypot(cx-sx,cy-sy));return float(cx+hand*7),float(cy+14),gap


def eclairage(r,d,mask,folia,added,matte,paint,response):
    gid=r['id'];n=r['n'];q=d['lianes'][gid]
    b,f,x,y,floor,glass,gates,bottom,allowed,_=F.freeze_support(r,d)
    shape=x.shape;wood=((b[...,:3]!=T.BRUN).any(2)&(b[...,3]>0))|(f[...,3]>0)
    keep=L.extract_alpha(d,r)|~wood|mask
    if gid==HALL:keep|=pixels([ARCADE_RESERVE,THRESHOLD_RESERVE],shape)
    edge_factor=smooth(nd.distance_transform_edt(~keep)/5.5)
    base=night_bitmap(r,d,mask,folia)
    rgb0=np.array(base.convert('RGB'),dtype=float);values=rgb0@L.LUMA
    emissive_gain=.78+.22*smooth((values-13)/119)
    a=q['points'];sources=[]
    for p in a:
        sx,sy=p['x'],p['y'];cx,cy,bit=p['images'][0][1];small=L.decode(bit);h,w=small.shape[:2];core=np.zeros(shape,bool)
        core[cy:cy+h,cx:cx+w]=small[...,3]>0
        assert core.any() and not (core&keep).any(),(gid,sx,sy)
        sources.append((sx,sy,core,p))
    sources.extend((sx,sy,m,None) for sx,sy,m in added)
    foliage=np.array(Image.alpha_composite(Image.fromarray(L.decode(folia['s'])),Image.fromarray(L.decode(folia['t']))))
    lamps=[];ledger=[]
    for sx,sy,core,previous in sources:
        assert foliage[...,3][core].min()>0 and not keep[core].any()
        hand=1 if sx<r['w']/2 else -1; to_floor=previous is not None
        if to_floor:
            fx,fy,gap=plein_sol(x,y,floor,~keep,sx,sy,hand)
            # Distinct wall and wood grain projections; the AI matte softens the
            # footprint off-axis so it is not a flat circle pasted on a canvas.
            w1=T.ellipse(sx+3*hand,sy+7,x,y,28,32)
            near=T.ellipse(sx,sy,x,y,11.5,15.5)
            g=T.ellipse(fx,fy,x,y,40,24)
            generated=matte.project(x,y,fx,fy,74,53,hand,.19)
            assert generated.max()>.75
            reflected=(.67*g+.33*generated)*np.clip(1.12-gap*.0035,.64,1.)
            field=np.maximum(.72*w1+.28*near,.97*reflected)
            ox,oy,bit=previous['images'][0][0];proto=L.decode(bit);h,w=proto.shape[:2]
            old=np.zeros(shape);old[oy:oy+h,ox:ox+w]=proto[...,3]/25.
            field=.91*field+.09*old
        else:
            # Soft side light on the upper passage boards, no broad pool under a gate.
            fx,fy,gap=sx+hand*11,sy+8,0
            generated=matte.project(x,y,fx,fy,43,32,hand,.13)
            field=np.maximum(.88*T.ellipse(sx,sy+2,x,y,13,17),.72*(.65*T.ellipse(fx,fy,x,y,16,14)+.35*generated))
        # Project narrow leaf silhouettes on the wall. The base is never painted;
        # paused playback retains a full, steady reflection at the first phase.
        cast=V.projected_shadow(sx,sy,foliage,x,y,r['w'])
        field=field*(1-.46*np.minimum(1,cast))*emissive_gain*edge_factor
        field[core]=0
        frames=[];seq=[]
        for i,z in enumerate(response[int(hand<0)]):
            phase=.78+.22*z
            amplitude=REFLECT_MAX*(.50+.50*z)*(1. if to_floor else .83)
            alpha=np.rint(np.maximum(0,field*amplitude-1.05)).astype(np.uint8)
            glow=F.rgba(alpha,[0,0,0])
            amber=(.65*np.array([252,214,145])+.35*paint[i,1]).astype(np.uint8)
            ochre=(amber.astype(int)-[8,12,13]).clip(0,255).astype(np.uint8)
            glow[alpha>0,:3]=ochre;glow[alpha>18,:3]=amber
            iris=F.rgba(core.astype(np.uint8)*int(round(BUD_MAX*phase)) if to_floor else core.astype(np.uint8)*int(round(139*phase)),[255,223,154])
            assert not alpha[keep].any() and alpha.max()<=REFLECT_MAX and alpha.max()>=23,(gid,sx,sy)
            frames.append([F.lights_pack(glow),F.lights_pack(iris)]);seq.append(int(alpha.max()))
        assert len({v[0][2] for v in frames})==4
        lamps.append(dict(x=sx,y=sy,images=frames));ledger.append(dict(bourgeon=[sx,sy],reflet=[round(fx,1),round(fy,1)],plafonds_alpha=seq))
    return lamps,ledger,keep


def night_bitmap(r,d,void,folia):
    b,f,lut=T.image_layers(r,d,3)
    # r.base/f contain the unaltered architecture; apply the same matte as the JS.
    tone=d['balade_nuit']['fonds'][r['id']]['rgb'][3];b[void,:3]=tone;b[void,3]=255
    img=Image.fromarray(b)
    for part in (folia['s'],f,folia['t']):
        if isinstance(part,str):
            part=L.decode(part)
            for c in range(3):part[...,c]=lut[c,part[...,c]]
        part[void]=0
        img.alpha_composite(Image.fromarray(part))
    return img


def light_frames(a,points):
    rgb=np.array(a.convert('RGB'),dtype=float);frames=[]
    for i in range(4):
        acc=rgb.copy()
        for s in points:
            for x,y,bit in s['images'][i]:
                q=L.decode(bit);h,w=q.shape[:2];p=acc[y:y+h,x:x+w]
                p+=(255-p)*(q[:,:,:3]/255.)*(q[:,:,3:]/255.)
        frames.append(np.rint(acc).astype(np.uint8))
    return rgb,frames
