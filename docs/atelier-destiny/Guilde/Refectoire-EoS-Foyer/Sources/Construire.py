#!/usr/bin/env python3
"""A single built-in fireplace on the exact 504×360 EoS plan, with separate planes."""
from collections import Counter
from functools import cache
from hashlib import sha256
from pathlib import Path
from PIL import Image, ImageDraw
from scipy.ndimage import label, binary_fill_holes, binary_dilation, gaussian_filter
import json
import numpy as np

ROOT=Path(__file__).resolve().parents[1];P=ROOT.parent;W=Path.home()/'.cache/foyer-refectoire';W.mkdir(parents=True,exist_ok=True)
BASE=P/'Plans-Grodoudou-Bois-Destiny';RF=ROOT/'Reference';ART=ROOT/'Etude'/'Foyer-dalles-et-chene.png';AP=P/'Drapeaux-Foyers-Bibliotheque/Reference/G01P05C-Interieur-Nuit.png'
C=(504,360);SW,SH=(46,94);x0,y0=(228,83);DUR=100;NECK=7;PAL=['Jour','Nuit'];MATE=[(26,22,38,255),(16,14,31,255)]
WINDOWS=[(179,107,227,153),(275,107,324,153)];TABLE=(173,182,337,232);FONTAINE=(353,133,414,194);EST=(434,118,504,270)
Y,X=np.indices(C[::-1],dtype=float)

def jsonout(path,o):Path(path).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def shot(im,p):p=Path(p);p.parent.mkdir(exist_ok=True,parents=True);im.save(p,optimize=True);return p
def h(p):return sha256(Path(p).read_bytes()).hexdigest()
def col(z):return tuple(bytes.fromhex(z))
def ss(lo,hi,t):r=np.clip((t-lo)/(hi-lo),0,1);return r*r*(3-2*r)
def rgba(a,mask):
    b=a.copy();b[:,:,3]=mask*255;b[~mask]=0;return Image.fromarray(b)
def bboxmask(rect):
    x,y,w,b=rect;return (X>=x)&(X<w)&(Y>=y)&(Y<b)
def maskpoly(pts):
    a=Image.new('1',C);ImageDraw.Draw(a).polygon(pts,fill=1);return np.asarray(a).astype(bool)
def stamp(im,x,y):
    a=Image.new('RGBA',C);a.alpha_composite(im,(x,y));return a

def play(fp):
    r=Image.open(fp);assert r.n_frames==4;frames=[]
    for i in range(4):
        r.seek(i);assert r.info['duration']==100;frames.append(r.convert('RGBA').copy())
    return frames

@cache
def geo():return next(s for s in json.loads((BASE/'Geometrie.json').read_text()) if s['id']=='G01P06')

@cache
def refs():
    data=[play(RF/'G01P06A-Jour.apng'),play(RF/'G01P06B-Nuit.apng')];assert all(i.size==C for s in data for i in s);return data


def luma(a):return a[...,:3]@np.array([.26,.60,.14])
def ramps(t,x,hexes):
    a=np.array([col(q) for q in hexes],float);return np.stack([np.interp(t,x,a[:,j]) for j in range(3)],axis=-1)
def lut(a,fx):
    q=np.asarray(a).copy();m=q[...,3]>0;q[m,:3]=np.clip(np.rint(fx(q[m,:3].astype(float))),0,255).astype(np.uint8);q[~m]=0;return Image.fromarray(q)
def ambience(im,j):return lut(im,lambda a:a*[.62,.61,.71]+[3,2,6]) if j else im.copy()


def banquet(ref):
    a=np.asarray(ref);r,g,b=a[...,:3].astype(int).transpose(2,0,1)
    # Ochres and plates are the native palette; the eight peach colours belong to the ground.
    turf=((g>r-4)&(b<81))|((r>=209)&(b>=60)&(b<=121)&(r-g>=24))
    pit=bboxmask(TABLE)&(~turf)&(((r>=114)&(r>=g+9)&(b<=82))|((r>=175)&(g>=r-18)&(b>=77)))
    lab,n=label(pit,np.ones((3,3)));c=np.bincount(lab.ravel());c[0]=0;m=binary_fill_holes(lab==c.argmax());assert 4350<m.sum()<7300,m.sum()
    p=luma(a);res=a.copy();wood=ramps(p,[91,111,133,155,179,210,238],['473020','674021','83532a','9c682e','b97f39','d09d4b','ebbc6c']);plates=ramps(p,[139,168,196,224,255],['8e7142','ad925d','d4bd86','e7d19e','f8eabf']);known=(r>=175)&(g>=r-18)&(b>=77)
    res[m,:3]=np.rint(np.where(known[...,None],plates,wood)[m]).astype(np.uint8)
    return rgba(res,m),m


def rives(ref):
    a=np.asarray(ref);r,g,b=a[...,:3].astype(int).transpose(2,0,1)
    # Native baskets (kept as a decorative layer) kept inside their exact west arrangement.
    baskets=[(115,152,7,10),(107,161,8.4,10),(128.6,162,8.1,12),(119.4,170.5,8.4,12.6),
             (158.5,170,8.1,12),(150.6,179.5,8.5,12),(129.1,197,9.,12),(120.3,205.4,8.8,12.5)]
    field=np.zeros(C[::-1],bool)
    for x,y,rx,ry in baskets:field|=((X-x)/rx)**2+((Y-y)/ry)**2<=1
    skip=((r>=198)&(r>=g+39)&(g>=102)&(b<100)&(g<b+102))|((g>r+3)&(b<74))
    palette=(r>=109)&(r>=g+4)&(b<94)&(g>=77)
    brightfruit=((r>190)&(g<=110)&(b<130))|((b>=83)&(g>106)&(r<b+38))|((r>=215)&(g>=212)&(b<96))
    # Keep baskets + fruit but leave the rocky/grass backing out of the timber version.
    m=field&((palette&~skip)|brightfruit);m=binary_fill_holes(m)
    ids,n=label(m,np.ones((3,3)));size=np.bincount(ids.ravel());size[0]=0;m=size[ids]>=7
    colors=a.copy();colors[m,:3]=np.clip(np.rint(a[m,:3].astype(float)*[.93,.89,.80]+[0,0,9]),0,255).astype(np.uint8)
    return rgba(colors,m),m


def fontaine(ref,j=0):
    a=np.asarray(ref);r,g,b=a[...,:3].astype(int).transpose(2,0,1)
    rock=maskpoly([(377,141),(380,138),(395,138),(399,142),(401,150),(406,155),(408,161),(413,165),(413,189),(408,193),(398,190),(383,194),(377,191),(369,190),(368,186),(360,183),(358,179),(355,173),(355,166),(361,161),(361,156),(368,152),(373,147)])
    liquid=bboxmask(FONTAINE)&(g>=r+11)&(b>=r+24);m=(rock&(~((g>r+7)&(b<g-19))))|liquid;m=binary_fill_holes(m)
    colors=a.copy();v=luma(a);stone=ramps(v,[75,97,117,138,158,183,220],['564333','694e38','815f42','9b7955','b48f65','cfaa7d','ebc797']);colors[m&~liquid,:3]=np.rint(stone[m&~liquid]).astype(np.uint8)
    if j:
        colors[m&~liquid,:3]=np.rint(colors[m&~liquid,:3].astype(float)*[.73,.74,.79]+[1,2,6]).astype(np.uint8)
        colors[liquid,:3]=np.rint(colors[liquid,:3].astype(float)*[.79,.84,.91]).astype(np.uint8)
    assert m.sum()>1700 and liquid.sum()>450,(int(m.sum()),int(liquid.sum()))
    return rgba(colors,m),m


def key():
    a=np.asarray(Image.open(ART).convert('RGB'));r,g,b=a.astype(float).transpose(2,0,1);bad=(r>95)&(b>98)&(r>1.30*g+26)&(b>1.30*g+20)
    L,n=label(~bad,np.ones((3,3)));ct=np.bincount(L.ravel());ct[0]=0;m=L==ct.argmax();assert ct.max()>50000
    u=Image.fromarray(np.dstack([np.where(m[...,None],a,0),m.astype(np.uint8)*255]));b=u.getbbox()
    u=u.crop(b).resize((SW,SH),Image.Resampling.BOX);s=np.array(u);m=s[...,3]>127;s[~m]=0;s[m,3]=255;u=Image.fromarray(s)
    c=u.convert('RGB').quantize(54,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE).convert('RGB');c.putalpha(u.getchannel('A'))
    q=np.array(c);q[~m]=0
    # Pale limestone courses, with staggered joints. These fit the flat chimney breast from the study.
    Q=np.indices((SH,SW));l=luma(q);p=Q[0]<49;stone=p&m & (l>69)
    warm=ramps(l,[68,109,142,166,188,215],['594832','756348','948061','ac9675','c3ad89','d9c4a2'])
    q[stone,:3]=np.rint(q[stone,:3]*.30+warm[stone]*.70).astype(np.uint8)
    for j,y in enumerate([18,31,44]):
        cols=np.where(m[y]&m[y+1])[0];l0,r0=cols[0]+1,cols[-1]-1
        q[y,l0:r0+1,:3]=np.rint(q[y,l0:r0+1,:3].astype(float)*.60).astype(np.uint8)
        q[y+1,l0:r0+1,:3]=np.clip(q[y+1,l0:r0+1,:3].astype(int)+[22,18,13],0,255).astype(np.uint8)
        px=SW//2+[-4,4,-2][j]
        for z in range(y-9,y):
            if q[z,px,3] and q[z,px+1,3]:
                q[z,px,:3]=np.rint(q[z,px,:3].astype(float)*.71).astype(np.uint8)
                q[z,px+1,:3]=np.clip(q[z,px+1,:3].astype(int)+[13,10,7],0,255).astype(np.uint8)
    return Image.fromarray(q),b


def chamber(s):
    a=np.asarray(s);yy,xx=np.indices((SH,SW));l=luma(a)
    m=(a[...,3]>0)&(yy>=61)&(yy<=88)&(xx>=9)&(xx<SW-8)&(l<64)
    L,n=label(m);mid=L[77,SW//2];assert mid,(a[77,SW//2],a.shape);m=L==mid;y,x=np.where(m);assert 285<m.sum()<850,(m.sum(),np.min(y),np.max(y));return m


def connection(q,j):
    # The cold masonry neck runs up behind the existing crown beam, rather than leaving a bit of post above it.
    cap=Image.new('RGBA',(SW,NECK));u=np.array(q);xlo,xhi=10,37
    d=ImageDraw.Draw(cap);r,g,b=tuple(u[2,23,:3]);d.rectangle((xlo+2,0,xhi-2,NECK-1),fill=(r-28,g-27,b-27));d.line((xlo+2,0,xhi-2,0),fill='#5d4431')
    d.line((xlo+4,2,xhi-5,2),fill=(r-9,g-10,b-14));d.line((xlo+3,3,xlo+3,NECK-1),fill=(r-4,g-3,b-3));d.line((xhi-4,3,xhi-4,NECK-1),fill=(r-47,g-35,b-33))
    return ambience(cap,j)

def flames():
    out=[]
    for im in play(AP):
        a=np.array(im.crop((124,153,166,193)));r,g,b=a[...,:3].astype(int).transpose(2,0,1)
        good=(r==231)&(((g>=47)&(g<=199)&(b<=32))|((g>=199)&(b<=47))|((g==231)&(b==183)))
        good[:,:3]=False;good[:,39:]=False;good[-2:]=False
        out.append(rgba(a,good));assert good.sum()>440
    b=tuple(fn(im.getbbox()[j] for im in out) for j,fn in enumerate((min,min,max,max)))
    return [im.crop(b).resize((23,22),Image.Resampling.NEAREST) for im in out]


def lit_fixtures(q,j,f):
    # q is always the exact same masonry. Timber stays outside the cavity.
    cavity=chamber(q);off=ambience(q,j);a=np.array(off);y,x=np.indices((SH,SW));logs=Image.new('RGBA',q.size);d=ImageDraw.Draw(logs)
    d.polygon([(12,86),(30,81),(34,84),(19,89),(13,88)],fill='#443025' if not j else '#372b26',outline='#1e1915');d.line((14,86,31,83),fill='#7c593e')
    d.polygon([(13,82),(34,86),(35,89),(16,86)],fill='#4d3527' if not j else '#44302a',outline='#251911');d.line((16,83,33,87),fill='#80623d')
    warm=np.clip(1-(((x-22.5)/24)**2+((y-82)/24)**2),0,1)**2
    def on(n):
        st=[1,.90,.84,.95][n];a0=a.copy();hot=warm*st*(.27+.73*cavity)*(a[...,3]>0)
        a0[...,:3]=np.clip(np.rint(a0[...,:3]+hot[...,None]*np.array([99,49,10])*(1 if j else .75)),0,255).astype(np.uint8)
        z=logs.copy();z.alpha_composite(f[n],(11,64));draw=ImageDraw.Draw(z)
        draw.line((15,86,32,85),fill=[(190,77,28),(218,95,27),(170,53,18),(203,82,23)][n]);
        for x1,y1 in [(16,86),(23,85),(28,87),(32,85)]:draw.point((x1,y1),fill='#efb65c')
        oz=np.array(z);oz[~cavity]=0;u=Image.fromarray(a0);u.alpha_composite(Image.fromarray(oz));return u,Image.fromarray(oz)
    z=np.array(logs);z[~cavity]=0;off.alpha_composite(Image.fromarray(z));return off,[on(n) for n in range(4)],cavity


def contact(base,fixture):
    m=np.asarray(base)[...,3]>0;g=geo();floor=maskpoly(g['contour_sol'])&m
    # Annular occlusion where the back of the chimney enters the oak wall; no wash over the windows.
    wall=m&~floor&(Y>=79);glows=[];window=np.any([bboxmask(b) for b in WINDOWS],axis=0);east=bboxmask(EST)
    shadow1=np.clip(1-(((X-251)/28)**2+((Y-173)/11)**2),0,1)**1.3*.40*floor
    shape=np.asarray(stamp(fixture,x0,y0))[...,3]>0
    inset=gaussian_filter(np.roll(np.roll(shape.astype(float),1,1),1,0),1.38)*.48
    S=(shadow1+inset*~shape*wall)*~window*~east
    def tinted(rgb,alpha):
        a=np.zeros((*C[::-1],4),np.uint8);a[...,3]=np.rint(np.clip(alpha,0,1)*255).astype(np.uint8);a[a[...,3]>0,:3]=rgb;return Image.fromarray(a)
    shadow=tinted((49,29,23),S)
    # Parquet receives stronger half-elliptic light across its boards; wall receives a smaller spill.
    rf=((X-251)/73)**2+((Y-184)/44)**2
    hw=((X-251)/51)**2+((Y-158)/41)**2
    spill=(((1-np.clip(rf,0,1))**2.35)*ss(159,174,Y)*floor*.91+((1-np.clip(hw,0,1))**2.2)*wall*.44)*~window*~east
    for p in [1.0,.91,.86,.97]:glows.append(tinted((244,147,57),spill*.78*p))
    return shadow,glows,spill,floor


def screen(room,glow,k):
    a=np.array(room);g=np.asarray(glow).astype(float);p=a[...,:3].astype(float);n=(255-p)*(g[...,:3]/255)*(g[...,3:4]/255)*k
    a[...,:3]=np.rint(p+n).clip(0,255).astype(np.uint8);a[a[...,3]==0]=0;return Image.fromarray(a)


def build():
    g=geo();assert g['dimensions']==list(C) and g['seuils']==[[487,218,504,244]] and g['vitres']==[[180,110,227,149],[276,110,323,149]]
    old=refs();q,keybox=key();fl=flames();L=ROOT/'Calques';PNS=ROOT/'Plans';
    day=Image.open(BASE/'PNG/Jour/G01P06.png').convert('RGBA');night=Image.open(BASE/'PNG/Nuit/G01P06.png').convert('RGBA');assert day.size==night.size==C and np.array_equal(np.asarray(day)[:,:,3],np.asarray(night)[:,:,3]);
    shadow,lights,fall,floor=contact(day,q);shot(q,W/'Foyer-seul.png');shot(shadow,L/'Ombre-de-contact.png')
    refsday=np.array([np.asarray(a) for a in old[0]]);stable=~np.any(refsday!=refsday[0],axis=(0,3));assert int((~stable).sum())==271
    wood0=Image.new('RGBA',C);table,tmask=banquet(old[0][0]);basket,bmask=rives(old[0][0]);water,wmask=fontaine(old[0][0]);
    assert np.all(wmask|stable) and not (wmask&tmask).any()
    wood0.alpha_composite(basket);wood0.alpha_composite(table)
    # Tiny shadows tie the unchanged object coordinates to the parquet. No gameplay collision is implied.
    oo=np.any([tmask,bmask,wmask],axis=0);pre=gaussian_filter(np.roll(np.roll(oo.astype(float),2,0),1,1),1.06)*.36*floor*~oo
    furniture_shadow=Image.new('RGBA',C,(37,24,19,0));furniture_shadow.putalpha(Image.fromarray(np.rint(pre*255).astype(np.uint8)));sx=np.array(furniture_shadow);sx[sx[...,3]==0]=0;furniture_shadow=Image.fromarray(sx)
    shot(furniture_shadow,L/'Ombres-mobilier.png')
    protect=np.logical_or.reduce([bboxmask(a) for a in [*WINDOWS,EST]])
    odoc=[];changes={};
    for j,(name,base) in enumerate(zip(PAL,(day,night))):
        cf=name.lower();D0=L/name;D0.mkdir(exist_ok=True);shot(base,D0/'01-Salle-bois.png');
        sh=np.asarray(base)[...,3]>0
        before=base.copy();before.alpha_composite(furniture_shadow);mats=ambience(wood0,j);shot(mats,D0/'02-Table-et-corbeilles.png');
        # One pixel for one pixel: the objects live at their exact native positions.
        before.alpha_composite(mats);water_seq=[fontaine(old[j][k],j)[0] for k in range(4)];assert len({im.tobytes() for im in water_seq})==4
        wa=Image.new('RGBA',(C[0]*4,C[1]));
        for k,im in enumerate(water_seq):wa.alpha_composite(im,(k*C[0],0))
        shot(wa,D0/'03-Source-4poses.png');
        off,poses,cav=lit_fixtures(q,j,fl);assert c_mask(cav).sum()==cav.sum()
        at=Image.new('RGBA',(4*SW,SH));fls=Image.new('RGBA',at.size)
        for k,(m,fl0) in enumerate(poses):at.alpha_composite(m,(k*SW,0));fls.alpha_composite(fl0,(k*SW,0))
        shot(off,D0/'Foyer-eteint.png');shot(at,D0/'Foyer-allume-4poses.png');shot(fls,D0/'Braises-et-feu-4poses.png');
        nc=connection(q,j);shot(nc,D0/'Raccord-sous-traverse.png');screens=[];protege=protect&~wmask
        full=shadow.copy();full.alpha_composite(nc,(x0,y0-NECK));full.alpha_composite(off,(x0,y0));shot(full,D0/'Foyer-en-place-eteint.png')
        full=shadow.copy();full.alpha_composite(nc,(x0,y0-NECK));full.alpha_composite(poses[0][0],(x0,y0));shot(full,D0/'Foyer-en-place-allume.png')
        for k in [-2,-1,0,1,2,3]:
            f=max(0,k);table_source=before.copy();table_source.alpha_composite(water_seq[f]);
            view=base.copy();view.alpha_composite(furniture_shadow)
            if k!=-2:view.alpha_composite(shadow)
            if k>=0:view=screen(view,lights[f],.53 if j==0 else .92)
            view.alpha_composite(mats);view.alpha_composite(water_seq[f]);
            if k>=-1:
                view.alpha_composite(nc,(x0,y0-NECK));view.alpha_composite(off if k==-1 else poses[f][0],(x0,y0))
            solid=np.asarray(view);bv=np.asarray(table_source);assert np.array_equal(solid[protege],bv[protege])
            # The entire native table, fountain incl. all animated pixels, and side baskets keep their arrangement.
            assert np.array_equal(solid[tmask|wmask|bmask],bv[tmask|wmask|bmask]);assert np.array_equal(solid[...,3],np.asarray(base)[...,3])
            edited=np.any(solid!=bv,axis=2);wallspan=bboxmask((167,76,334,242));assert not (edited&~wallspan).any()
            if k>=0:
                screens.append(view.copy());changes[name+'-'+str(f)]={'pixels':int(edited.sum()),'parquet_eclaire':int(((fall>.018)&floor&edited&~c_mask(np.asarray(q)[...,3]>0)).sum())}
            elif k==-1:shot(view,PNS/f'Refectoire-{name}-Foyer-Eteint.png')
            tag='Avant' if k==-2 else 'Eteint' if k==-1 else str(k)
            shot(view,W/f'{name}-{tag}-transparent.png');proof=Image.new('RGBA',C,MATE[j]);proof.alpha_composite(view);shot(proof.convert('RGB'),W/f'{name}-{tag}.png')
        # Native-resolution clean still and lossless APNG. PNG in the root is the still shown directly to the user.
        shot(screens[0],PNS/f'Refectoire-EoS-{name}.png');path=PNS/f'Refectoire-EoS-{name}-Anime.png';screens[0].save(path,save_all=True,append_images=screens[1:],duration=[DUR]*4,loop=0,disposal=0,blend=0)
        odoc.append({'periode':name,'parquet':f'Calques/{name}/01-Salle-bois.png','ameublement':f'Calques/{name}/02-Table-et-corbeilles.png','eau':f'Calques/{name}/03-Source-4poses.png','foyer_eteint':f'Calques/{name}/Foyer-eteint.png','foyer_4poses':f'Calques/{name}/Foyer-allume-4poses.png','raccord':f'Calques/{name}/Raccord-sous-traverse.png','ancres_raccord':[x0,y0-NECK],'etats':f'Plans/Refectoire-EoS-{name}-Anime.png','facteur_reflets':.53 if not j else .92})
    for i,im in enumerate(lights):shot(im,L/f'Reflets-pose-{i+1}.png')
    aa=[h(BASE/'PNG'/p/'G01P06.png') for p in PAL];vv=[{'fichier':p.name,'sha256':h(p),'source':u} for p,u in [(RF/'G01P06A-Jour.apng','https://projectpokemon.org/home/gallery/image/77579-g01p06apng/'),(RF/'G01P06B-Nuit.apng','https://projectpokemon.org/home/gallery/image/77580-g01p06bpng/'),(AP,'https://projectpokemon.org/home/gallery/image/77578-g01p05cpng/')]]
    proof={'statut':'PASS','id':'G01P06','echelle':'1×','dimensions_px':list(C),'montage':'bois Destiny sur géométrie G01P06, meuble et fontaine à leurs coordonnées EoS','foyer':{'ancre':[x0,y0],'dimension':list(q.size),'nombre':1,'trame_4x1':True,'raccord_ancre':[x0,y0-NECK],'raccord_taille':[SW,NECK],'zone_foyer_int':list(map(int,Image.fromarray(cav).getbbox())),'bbox_detourage_etude':list(keybox),'etude_sha256':h(ART)},'zones_preservees':{'vitres':g['vitres'],'seuil_est':g['seuils'][0],'passage':list(EST),'table':list(map(int,Image.fromarray(tmask).getbbox())),'fontaine':list(map(int,Image.fromarray(wmask).getbbox())),'sol_poly':g['contour_sol']},'textures_protegees_identiques_au_plan_boise_avant_foyer':True,'memes_positions_table_corbeilles_fontaine':True,'variations_eau_originale_px':int((~stable).sum()),'pixels':changes,'recomposition':odoc,'duree_pose_ms':DUR,'source':vv,'base_sha256_jour_nuit':aa,'bouche_decoupee_par_masque':True}
    jsonout(ROOT/'Releve-G01P06.json',proof);print('G01P06 · un foyer dans la travée centrale ; 8 vues allumées et 2 éteintes ; le mobilier, la source et l’accès est sont protégés.')
    return proof

def c_mask(m):
    a=np.zeros(C[::-1],bool);a[y0:y0+SH,x0:x0+SW]=m;return a

if __name__=='__main__':build()
