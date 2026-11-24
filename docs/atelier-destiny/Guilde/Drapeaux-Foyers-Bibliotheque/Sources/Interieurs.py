#!/usr/bin/env python3
"""Masonry fixed to the dining room and a transparent inset library layer."""
from Commun import *
from PIL import ImageDraw
from scipy.ndimage import binary_fill_holes, gaussian_filter
import random

FD=ROOT/'Cheminées'; RD=ROOT/'Rayonnages'; WS=ROOT/'Calques'
# x, y at left edge, projected width, column rise/slope. No slots over windows or pillars.
RACKS=[('ouest','Travée ouest',71,77,43,-25,'herbiers'),('centre','Niche centrale',205,29,70,0,'archives'),('est','Travée est',366,49,43,25,'atlas')]
PITS=[('ouest','Grès miel',76,116,59,-36,(1.04,1.01,.94)),('est','Pierre fumée',441,80,59,36,(.91,.96,1.06))]
BOOKS=[('archives','Archives miel'),('herbiers','Herbiers mousse'),('atlas','Atlas bleu')]


def darkoutline(im):
    # remove colour in the transparent pixels, retaining hard pixel contours.
    a=np.array(im);a[a[...,3]==0]=0;return Image.fromarray(a)


def fill_rack(v):
    im=pixel_photo('Rayon',(76,81),48)
    if v=='archives':return im
    # Retain the moulded AI frame and counted shelves; redraw holdings / stacks within each recess.
    d=ImageDraw.Draw(im);r=random.Random(813 if v=='herbiers' else 1031)
    palettes={
     'herbiers':[('#325043','#658258','#9bb172'),('#55623b','#829956','#dbbd72'),('#624232','#9e6740','#d3ac65'),('#415760','#64818c','#afbea3'),('#805a32','#bd904b','#e5c88c')],
     'atlas':[('#294450','#496978','#a8b6b9'),('#344552','#577181','#bbc5b7'),('#594033','#875a44','#d7b075'),('#5e3b3f','#a4605a','#c99967'),('#494d38','#767d53','#ccb686')]
    }
    rows=[(31,18),(44,35),(57,48),(71,61)]; pal=palettes[v]
    for j,(shelf,top) in enumerate(rows):
        left,right=(14,62) if j==0 else (11,65)
        d.rectangle((left,top,right,shelf),fill='#3e2c23' if j%2 else '#3a281f')
        x=left+1
        stack=(j in [0,2]) if v=='herbiers' else j in [1,2,3]
        while x<=right-2:
            c=pal[(r.randrange(len(pal))+j)%len(pal)]
            if stack and ((x-left)%13>=8 or x>=right-14):
                width=min(r.randrange(8,13),right-x+1)
                if width>=7:
                    for i in range(r.randint(2,3)):
                        y=shelf-1-3*i; ci=pal[(j+i+1)%len(pal)];off=i%2
                        d.rectangle((x+off,y-2,x+width-1,y),fill=ci[0]);d.line((x+off,y-2,x+width-2,y-2),fill=ci[1]);d.line((x+off+1,y-1,x+width-3,y-1),fill='#bda77b');d.point((x+width-2,y),fill=ci[2])
                    x+=width+1;stack=False;continue
            wide=min(r.choice([2,3,4,4,5,6 if v=='atlas' else 3]),right-x+1);h=r.randint(6,10 if j else 12);y0=max(top,shelf-h)
            d.rectangle((x,y0,x+wide-1,shelf-1),fill=c[1]);d.line((x,y0,x,shelf-1),fill=c[0]);d.line((x+1,y0+2,x+wide-1,y0+2),fill=c[2]);
            if h>=8:d.point((x+wide-1,shelf-3),fill=c[2])
            x+=wide+1
    return darkoutline(im)


def build_library():
    result={'salle':BIB,'nom':'Bibliothèque','layer':'Rayonnages encastrés','canvas':[480,360],'slots':[],'modeles':[{'id':v,'nom':n} for v,n in BOOKS]}
    r=room(BIB);f0=dec(r['base']);f0.alpha_composite(dec(r['front']));default=Image.new('RGBA',(r['w'],r['h'])); variants={v:fill_rack(v) for v,n in BOOKS}
    for slot,nom,x,y,w,dz,opt in RACKS:
        y+=min(dz,0);alt={};
        for uid,_ in BOOKS:
            sz=(76,63 if slot=='centre' else 47);frame=variants[uid].resize(sz,Image.Resampling.NEAREST)
            # Light is stronger on the left-facing inner moulding; side wood darkens by depth.
            t=np.array(frame);z=(np.linspace(.90,1.025,sz[0]) if slot=='ouest' else np.linspace(1.03,.895,sz[0]) if slot=='est' else np.ones(sz[0]));t[...,:3]=np.rint(t[...,:3]*z[None,:,None]).clip(0,255).astype('uint8');frame=Image.fromarray(t)
            frame=tangente(frame,w,dz);path=str(png(frame,RD/f'{slot}-{uid}.png').relative_to(ROOT));alt[uid]={'png':path,'w':frame.width,'h':frame.height}
            # Every visible pixel is on a real plank/wall pixel, not a foreground void.
            test=np.asarray(f0.crop((x,y,x+w,y+frame.height)))[...,3];a=np.asarray(frame)[...,3];assert not ((a>0)&(test<200)).any(),(slot,uid, np.count_nonzero((a>0)&(test<200)))
            if uid==opt:default.alpha_composite(frame,(x,y))
        result['slots'].append({'id':slot,'nom':nom,'xy':[x,y],'defaut':opt,'choix':alt})
    path=png(default,WS/'Bibliotheque-Rayonnages-480x360.png');result['calque_defaut']=str(path.relative_to(ROOT));write_json(RD/'Index-Rayonnages.json',result)
    basep=preview(BIB,0);a=preview(BIB,0,walls=default);png(a,W/'Essai-Bibliotheque.png')
    return result


def orange_fire():
    apng=Image.open(REF/'G01P05C-Interieur-Nuit.png');assert apng.n_frames==4
    out=[]
    for k in range(4):
        apng.seek(k);a=np.array(apng.convert('RGB').crop((124,153,166,193))).astype('uint8');r,g,b=a.astype(int).transpose(2,0,1)
        mask=(r==231)&(((g>=47)&(g<=199)&(b<=32))|((g>=199)&(b<=47))|((g==231)&(b==183)))
        # Crop around the brazier itself, discarding luminous grains on the floor.
        mask[:,0:3]=False;mask[:,39:]=False;mask[-2:]=False
        a=np.dstack([a,mask.astype('uint8')*255]);a[~mask]=0;im=Image.fromarray(a);out.append(im)
        assert mask.sum()>440,mask.sum()
    # Every phase uses the same projected window so the blaze does not jump as it loops.
    box=tuple(fn(i.getbbox()[j] for i in out) for j,fn in enumerate([min,min,max,max]));return [im.crop(box).resize((31,30),Image.Resampling.NEAREST) for im in out]


def pit_shell(palette):
    im=pixel_photo('Foyer',(64,53),40);a=np.array(im);a[...,:3]=np.rint(a[...,:3]*np.array(palette)).clip(0,255).astype('uint8');im=Image.fromarray(a)
    return im


def cavity(im):
    a=np.array(im);y,x=np.indices(a.shape[:2]);v=(a[...,0]<67)&(a[...,1]<53)&(a[...,2]<55)&(y>=14)&(y<=46)&(x>=14)&(x<=49)&(a[...,3]>0)
    ids,n=label(v);k=ids[38,32];assert k and (ids==k).sum()>500;return ids==k


def inner_pit(im,sp,k):
    a=np.array(im);cav=cavity(im);y,x=np.indices(a.shape[:2]);blaze=bool(sp);coeff=([1,.9,.85,.94][k] if blaze else 0)
    r2=((x-32)/29)**2+((y-42)/34)**2
    glow=clip(1-r2)**1.6*(.76*cav+.24*(a[...,3]>0))*coeff*(1-ss(5,18,49-y)*.27)
    a[...,:3]=np.rint(a[...,:3]+glow[...,None]*(np.array([113,49,12]) if blaze else 0)).clip(0,255).astype('uint8');im=Image.fromarray(a)
    overlay=Image.new('RGBA',im.size);d=ImageDraw.Draw(overlay)
    d.ellipse((17,39,48,49),fill='#281d19');
    # Draw soot-black logs on the same brick ledge, with a hot ember edge only when lit.
    d.polygon([(18,43),(43,39),(47,42),(24,47),(19,47)],fill='#513629',outline='#261b17');d.line([(20,44),(42,41)],fill='#a05e36' if blaze else '#674534');d.polygon([(22,39),(47,43),(47,47),(22,44)],fill='#4b3025',outline='#261a18');d.line([(24,41),(44,44)],fill='#9d5e3d' if blaze else '#755139');
    if blaze:
        i=overlay.copy();i.alpha_composite(sp,(16,13));overlay=i;d=ImageDraw.Draw(overlay);d.line((22,44,43,44),fill=[(215,98,32),(231,120,46),(205,75,24),(226,105,31)][k]);
        for j in [(23,45),(28,44),(36,45),(41,44)]:d.point(j,fill='#f9c16b')
    ar=np.array(overlay);ar[~cav]=0;im.alpha_composite(Image.fromarray(ar));return darkoutline(im)


def shadows_surface(r,lights):
    y,x=np.indices((r['h'],r['w'])).astype(float);a=np.asarray(dec(r['base']))[...,3]/255
    floor=np.array([list(f) for f in r['floor']])=='1';floor=np.repeat(np.repeat(floor,8,axis=0),8,axis=1)
    floor=gaussian_filter(floor.astype(float),.9)
    # Warm fan shapes on floor and a smaller spill on each nearby upright wall.
    shadow=np.zeros_like(x);banks=[]
    for pos in lights:
        px,py,direction=pos
        # A few pixels of projected contact shadow under the base in the direction of the floor.
        du=x-px;side=y-py-du*direction*.45
        shadow+=.35*clip(1-(du/31)**2-((side-2)/7)**2)**1.65 *a
        r2=((x-(px+direction*15))/85)**2+((y-(py+28))/78)**2
        floorheat=clip(1-r2)**2.2*ss(-12,10,side)*floor
        wallheat=clip(1-(du/56)**2-((side+22)/48)**2)**2.3*(1-ss(-10,11,side))
        banks.append((.88*floorheat+.30*wallheat)*a)
    shade=Image.new('RGBA',(r['w'],r['h']),(28,20,16,0));shade.putalpha(Image.fromarray(np.rint(255*clip(shadow)).astype('uint8')));return shade,banks


def save_partial(im,path):
    b=im.getbbox();p=png(im.crop(b),path);return [b[0],b[1],str(p.relative_to(ROOT))]


def build_pits():
    parts=[];r=room(REFEC);flames=orange_fire();lights=[]
    for slot,nom,x,yl,w,dz,palette in PITS:
        y=yl+min(0,dz);shell=pit_shell(palette);m=cavity(shell);off=inner_pit(shell,None,0)
        frame=tangente(off,w,dz);parts0={'id':slot,'nom':nom,'xy':[x,y],'size':list(frame.size),'arret':[],'anime':[],'grille':4}
        lights.append([x+w/2,yl+dz/2+frame.height-abs(dz)-7,-1 if dz<0 else 1]);sample=np.asarray(dec(r['base']).crop((x,y,x+w,y+frame.height)))[...,3];assert not ((np.asarray(frame)[...,3]>0)&(sample<200)).any(),slot
        for j,p in enumerate(P):
            dst=FD/p;s0=roomtone(off,REFEC,j);f0=tangente(s0,w,dz);pieces=[]
            parts0['arret'].append(str(png(f0,dst/f'{slot}-eteinte.png').relative_to(ROOT)))
            for k,f in enumerate(flames):
                # The fireplace follows the room palette; flames persist as emissive pixels.

                lit=inner_pit(shell,f,k)
                # Profile from the lit shape mixes environment-coloured stone (not flame) with heat.
                lit_tone=roomtone(lit,REFEC,j);a=np.array(lit_tone);env=np.array(s0);src=np.array(lit);raw=np.array(off)
                cap=(m&((src[...,0]>165)&(src[...,1]>22)))
                a[~cap,:3]=np.clip(env[~cap,:3].astype(float)+np.maximum(0.,src[~cap,:3].astype(float)-raw[~cap,:3])*(.83 if j==3 else .64),0,255).astype('uint8')
                a[cap]=src[cap];pieces.append(tangente(Image.fromarray(a),w,dz))
            n=Image.new('RGBA',(w*4,frame.height));
            for k,im in enumerate(pieces):n.alpha_composite(im,(k*w,0))
            parts0['anime'].append(str(png(n,dst/f'{slot}-4poses.png').relative_to(ROOT)))
        parts.append(parts0)
    sh,heat=shadows_surface(r,lights);ambient=[]
    for k in range(4):
        glow=Image.new('RGBA',(r['w'],r['h']),(230,126,42,0));a=clip((heat[0]*[1,.93,.84,.95][k]+heat[1]*[.83,.94,1,.91][k])*.68)
        glow.putalpha(Image.fromarray(np.rint(255*a).astype('uint8')));ambient.append(save_partial(glow,FD/'Reflets'/f'parquet-{k+1}.png'))
    counts={p0['id']:sum(1 for g in r['gates'] if overlaps([*p0['xy'],*p0['size']],g['rect'])) for p0 in parts};assert not any(counts.values())
    result={'salle':REFEC,'layer':'Cheminées et reflets','fps':10,'modules':parts,'reflets':ambient,'ombre':save_partial(sh,FD/'Reflets'/'contacts.png'),'source':{'fichier':str((REF/'G01P05C-Interieur-Nuit.png').relative_to(ROOT)),'url':'https://projectpokemon.org/home/gallery/image/77578-g01p05cpng/','sha256':filehash(REF/'G01P05C-Interieur-Nuit.png')},'zones_passages_intactes':True}
    write_json(FD/'Index-Cheminees.json',result)
    for j in (0,3):
        fo=Image.new('RGBA',(r['w'],r['h']));a=preview(REFEC,j);bb=ambient[0];re=Image.open(ROOT/bb[2]);
        for x,y,p in [result['ombre']]:fo.alpha_composite(Image.open(ROOT/p),(x,y))
        a.alpha_composite(fo);a=screen(a,re,bb[:2],.64 if j==0 else 1.)
        for i,mo in enumerate(parts):
            w,h=mo['size'];fp=Image.open(ROOT/mo['anime'][j]);a.alpha_composite(fp.crop((w*i,0,w*(i+1),h)),tuple(mo['xy']))
        pn=W/('Essai-Cheminees-' + P[j]+'.png');png(a,pn)
    return result


def overlaps(a,b):return a[0]<b[0]+b[2] and b[0]<a[0]+a[2] and a[1]<b[1]+b[3] and b[1]<a[1]+a[3]


def screen(im,overlay,coords,level):
    z=np.array(im);g=np.asarray(overlay);x,y=coords;region=z[y:y+overlay.height,x:x+overlay.width,:3].astype(float);ar=g[...,3:4]/255.;region+=(255-region)*(g[...,:3]/255.)*ar*level
    z[y:y+overlay.height,x:x+overlay.width,:3]=np.rint(region).clip(0,255).astype('uint8');return Image.fromarray(z)


def preview(rid,p,walls=None):
    d=atelier();r=room(rid);v=d['balade_nuit'];rgb=v['fonds'][rid]['rgb'][p];page=Image.new('RGBA',(r['w'],r['h']),tuple(rgb)+(255,))
    page.alpha_composite(roomtone(dec(r['base']),rid,p));
    for x,y,b in r['patches'][p]:page.alpha_composite(dec(b),(x,y))
    l=v['ronces'].get(rid,d['lianes'][rid]);page.alpha_composite(roomtone(dec(l['s']),rid,p));page.alpha_composite(roomtone(dec(r['front']),rid,p))
    if walls:page.alpha_composite(roomtone(walls,rid,p))
    page.alpha_composite(roomtone(dec(l['t']),rid,p));return page

if __name__=='__main__':
    W.mkdir(parents=True,exist_ok=True);a=build_library();b=build_pits();print('Bibliothèque : 3 variantes dans 3 niches. Réfectoire : 2 cheminées indépendantes / 4 phases.')
