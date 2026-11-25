#!/usr/bin/env python3
"""Quatre entrées PMDO à partir des nouveaux dessins générés et des colonnes approuvées.

python animer_cyclones_meteo.py --base Kingambit-Spawns-et-Mega.zip --out DESTINATION
Dépendances : Pillow, NumPy. Export : planches RGBA et banques DirSheet à ancre centrée.
"""
from __future__ import annotations
from pathlib import Path
from PIL import Image, ImageDraw, ImageOps, ImageFont
from zipfile import ZipFile
from io import BytesIO
import argparse, hashlib, json, math, random, struct
import numpy as np

ROOT = Path(__file__).resolve().parent
TICKS = 4
COUL = {
    'flying': ((43,70,95),(100,160,171),(172,219,217),(242,250,216)),
    'dragon': ((37,24,73),(84,57,151),(143,110,221),(252,222,155)),
    'water': ((41,104,149),(85,160,199),(141,214,230),(226,253,244)),
    'fire': ((148,54,33),(200,87,40),(246,154,62),(255,233,155)),
}
SOURCES = {'flying': ('vol-cyclone', (67,88)), 'dragon': ('dragon-cyclone', (86,80)),
           'water': ('eau-averse',(29,46)), 'fire': ('feu-braises',(24,47))}
size_bank={'flying':(136,180),'dragon':(144,160),'water':(96,384),'fire':(96,384)}

def png(im):
    b=BytesIO();im.save(b,'PNG',optimize=True);return b.getvalue()

def put(p,b):
    p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)

def chroma(p, size):
    a=np.array(Image.open(p).convert('RGBA')); r,g,b,x=a.astype('int16').transpose(2,0,1)
    key=((r>169)&(b>160)&(r-g>109)&(b-g>108)&(r>b-78)&(r<b+76)) | (x<100)
    a[key]=0;a[~key,3]=255
    im=Image.fromarray(a); im=im.crop(im.getbbox()).resize(size,Image.Resampling.NEAREST)
    ar=np.array(im); m=ar[:,:,3]>0
    c=Image.fromarray(ar[m][:,:3][None,...]).quantize(colors=12,dither=Image.Dither.NONE).convert('RGB')
    ar[m,:3]=np.array(c)[0];ar[~m]=0
    return Image.fromarray(ar)

def scaled(im,w,h): return im.resize((max(1,round(w)),max(1,round(h))),Image.Resampling.NEAREST)

def stamp(canvas,obj,x,y,alpha=255):
    if alpha<=0:return
    if alpha<255:
        obj=obj.copy();obj.putalpha(obj.getchannel('A').point([round(k*alpha/255) for k in range(256)]))
    canvas.alpha_composite(obj,(round(x),round(y)))

def centre(canvas,obj,x,y,alpha=255):
    stamp(canvas,obj,canvas.width//2+x-obj.width//2,canvas.height//2+y-obj.height//2,alpha)

def drawings(im):
    d=ImageDraw.Draw(im);cx,cy=im.width//2,im.height//2
    def coords(pts):return [(round(cx+x),round(cy+y)) for x,y in pts]
    def line(p,c,width=1):d.line(coords(p),fill=c,width=width)
    def arc(x,y,rx,ry,lo,hi,c,width=1):
        if rx>0 and ry>0:d.arc(coords(((x-rx,y-ry),(x+rx,y+ry))),lo,hi,fill=c,width=width)
    def point(x,y,c,k=1):
        if k==1:d.point(coords(((x,y),)),fill=c)
        else:d.polygon(coords(((x-k,y),(x,y-1),(x+k,y),(x,y+1))),fill=c)
    return line,arc,point

def witha(c,a):return (*c,max(0,min(255,round(a))))

def split_torsion(im,f,rad,k):
    """Cisaillement différent pour la paroi arrière et les rubans au premier plan."""
    w,h=im.size; out=Image.new('RGBA',(w+18,h)); d0=Image.new('RGBA',out.size)
    for y in range(h):
        yrel=y/max(1,h-1); shift=round(math.sin(f*.49+yrel*math.tau*1.1)*(2+5*(1-yrel))*rad)
        if k=='dragon':shift+=round(math.cos(f*.41-yrel*6)*(2+1.5*yrel))
        strip=im.crop((0,y,w,y+1));d0.paste(strip,(9+shift,y))
    a=np.array(d0); rows=np.arange(h)[:,None]; cols=np.arange(w+18)[None,:];
    # L'alternance suit la spirale, elle ne coupe pas simplement l'image en deux rectangles.
    rr=rows/max(1,h-1)
    ring=np.sin(rr*(16 if k=='flying' else 17.5)+(cols-(w+18)/2)*.10+f*.17)
    behind=(ring<-.12)|((rr>.68)&(np.abs(cols-(w+18)/2)<w*.11))
    ar=a.copy(); af=a.copy(); ar[~behind]=0; af[behind]=0
    return Image.fromarray(ar),Image.fromarray(af)

def vortex(k,m,f):
    W,H=size_bank[k];s=Image.new('RGBA',(W,H));a=s.copy();c=COUL[k];dr=k=='dragon'; base=(f==0 or f==23)
    if base:return s,a
    ls,arc,ps=drawings(s);la,aa,pa=drawings(a)
    growth=[0,.16,.24,.34,.45,.59,.73,.88,.98,1.02,1.08,1.04,.98,1.02,1.05,1.08,1.01,.90,.78,.65,.48,.34,.23,0][f]
    fade=[0,125,152,192,208,226,241,246,252,255,255,255,250,245,231,213,192,164,137,111,82,62,37,0][f]
    vert=max(.16,min(1.,growth+(f-5)*.04));r=(11+growth*(26 if dr else 21))*(1 if f<17 else 1+(f-16)*.09)
    phi=(f*(26 if dr else -23))%360
    # Trace au sol. Trois sections tournent autour des pieds même avant que le cône se lève.
    for j in range(3):
        q=(phi+j*120)%360
        arc(0,4,r-j*2,3+r*.30-j*.7,q,q+74,witha(c[1+j%3],fade),1+(j==0))
        if f>2: aa(0,6,r*.82,3+r*.23,q+53,q+88,witha(c[2+j%2],fade*.78))
    if f>=2:
        w=(m.width*(.74 if dr else .79))*(.66+growth*.35)
        height=m.height*(.89 if dr else .88)*vert
        m1=scaled(m,w,height)
        if f>=17:
            w+=min(10,(f-16)*2);m1=scaled(m1,w,height*.80)
        back,front=split_torsion(m1,f,1 if not dr else .73,k)
        rise=0 if f<16 else (f-15)*(1.8 if not dr else .9)
        y=3-m1.height/2-rise
        cx=(math.sin(f*.71)*3 if not dr else math.cos(f*.59)*4)
        centre(s,back,cx,y,fade)
        # À l'apparition, la partie avant ouvre un œil à mi-hauteur et la base se résorbe.
        if f>=(10 if not dr else 12):
            arr=np.array(front)
            X,Y=np.meshgrid(np.linspace(-1,1,front.width),np.linspace(0,1,front.height))
            hole=(X*(1.9 if dr else 2.2))**2+((Y-.82)*4.7)**2 < .90
            arr[hole,3]=np.minimum(arr[hole,3],46 if dr else 66)
            front=Image.fromarray(arr)
        centre(a,front,cx,y,fade)
    # Bandes obliques dessinées sur le tourbillon ; leur vitesse et leur profondeur diffèrent.
    for j in range(7 if dr else 6):
        z=(f*.50*(-1 if not dr else 1)+j*math.tau/7)
        h=((j*17+f*(5 if not dr else 3))%77)/77
        vx=math.cos(z)*r*(.36+h*.70);vy=-4-h*vert*(54 if dr else 69)+math.sin(z)*8
        ell=4+7*(j%3)/2+growth*4
        p=witha(c[2+(j%5==0)],fade*(.79 if dr else .87))
        fn=la if math.sin(z)>=0 else ls
        fn(((vx-ell,vy+1),(vx-ell*.28,vy),(vx+ell*.55,vy-3)),p,1+(j%4==0 and f<16))
        if f>=13:
            vx*=1+(f-12)*.12;vy+=(f-12)*(1.9 if dr else -2.15)
            fn(((vx-ell*.62,vy+1),(vx+1,vy),(vx+3,vy-3)),witha(c[1+j%3],fade))
    for j in range(14 if dr else 10):
        rng=random.Random(901+j); lag=j%4
        t=f-lag-2
        if t<0:continue
        z=rng.uniform(0,math.tau)+f*.45*(1 if dr else -1)
        rad=(10+rng.randrange(16))*(.54+.5*growth)+(max(0,f-13))*1.4
        yy=-3-(j%6)*7*vert-t*.62 if not dr else -5-(j%4)*7*vert-max(0,f-10)*1.5
        p=pa if math.sin(z)>0 else ps; x=math.cos(z)*rad;y=yy+math.sin(z)*7
        p(x,y,witha(c[3 if j%4==0 else 1+j%2],fade),2 if (j%5==0 and t<15) else 1)
    return s,a

def old_cols(z,k,layer):
    rel=f'Planches/Particle/Kingambit_Entree_{k}_{layer}.png'; im=Image.open(BytesIO(z.read(rel))).convert('RGBA')
    w,h=size_bank[k];assert im.size==(4*w,4*h)
    return [im.crop((i%4*w,i//4*h,i%4*w+w,i//4*h+h)) for i in range(16)]

def colonne(k,m,f,s,a):
    if f==0 or f==15:return s,a
    p=COUL[k]; ls,rs,gs=drawings(s);la,ra,ga=drawings(a)
    if k=='water':
        # Ondes de pluie dès les premières gouttes, puis éclaboussures d'impact au pied.
        for j in range(5):
            age=(f+j*3)%10
            if age==9: continue
            x=[-25,23,-32,13,-8][j]; y=[16,7,-5,20,-13][j]
            radius=1.0+age*.76;rs(x,y,radius,max(1,radius*.33),0,359,witha(p[(j+1)%4],104*(1-age/10)))
        if 4<=f<=13:
            for j in range(13):
                z=(j*2.4);t=f-4-j%3
                if t<0:continue
                x=math.cos(z)*(4+t*2.65+j%6); y=6+math.sin(z)*(2+t*.42)-t*(1.8-t*.17)
                la(((x+1,y-3),(x,y),(x-1,y+1)),witha(p[2+(j%4==0)],210-t*14))
    else:
        # Cisaillement à l'intérieur de la colonne, silhouette toujours ancrée hors champ.
        if f<=11:
            b=a.copy();a=Image.new('RGBA',a.size); w,h=a.size
            for y in range(h):
                offset=round(2.1*math.sin(y*.17+f*.9)+1.3*math.sin(y*.29-f*.6))
                a.paste(b.crop((0,y,w,y+1)),(offset,y))
            la,ra,ga=drawings(a)
        # Filets d'air chaud de part et d'autre ; les braises se détachent et montent.
        for j,d in enumerate((-1,1)):
            t=f-j
            if not 1<=t<=13:continue
            sc=.43+min(6,t)*.082
            b=scaled(m,m.width*sc,m.height*sc); b=b if j==0 else ImageOps.mirror(b)
            x=d*(17+t*.65)+math.sin(t*.64+j*2)*3
            centre(a,b,x,-8-t*4.5, min(185,32+t*26,(14-t)*46))
        for j in range(16):
            rng=random.Random(661+j); t=f-j%4-1
            if not 0<=t<12:continue
            y=7-t*(4.1+j%3)-rng.randrange(8);x=(-1)**j*(7+rng.randrange(18)+t*.85)+math.sin(t*.76+j)*3
            if t<8 and j%3==0:la(((x-1,y+2),(x,y),(x+1,y-3)),witha(p[1+j%3],191-t*9))
            else:ga(x,y,witha(p[1+j%3],187-t*11),1+(t<6 and j%5==0))
    return s,a

def edge_stamp(im,obj,x,y,a):
    x%=im.width;y%=im.height
    for dx in (0,-im.width):
        for dy in (0,-im.height):stamp(im,obj,x+dx,y+dy,a)

def weather(k,f,m):
    w,h=160,120; p=COUL[k]
    env=(0,.16,.27,.42,.54,.65,.74,.84,.94,1,1,1,1,.97,.94,.91,.87,.81,.74,.67,.57,.47,.37,.27,.15,0)[f]
    im=Image.new('RGBA',(w,h));
    if env==0:return im
    if k=='water':
        im.paste(witha((42,95,145),31*env),(0,0,w,h))
        bands=[scaled(m,m.width*x,m.height*x) for x in (.61,.78,1.08)]
        for j in range(5):
            rng=random.Random(727+j); x=(rng.randrange(w)-f*(3+j%3));y=(rng.randrange(h)+f*(9+j%5))
            edge_stamp(im,bands[j%3],x,y,(85+j%4*23)*env)
    else:
        im.paste(witha((255,155,74),34*env),(0,0,w,h))
        # Deux bancs de mirage en fines marches (réfraction stylisée, sans shader).
        for j in range(9):
            x0=(j*27+f*4)%w; y0=(h//3+j*11+(f*3+j)%9)%h
            b=Image.new('RGBA',(35,8)); dr=ImageDraw.Draw(b);le=16+(j%4)*6
            for q,c in ((0,p[2]),(1,p[0])):
                dr.line([(x,3+int(1.8*math.sin(x*.20+f*.74+j))+q) for x in range(le)],fill=witha(c,(27 if q==0 else 22)*env))
            edge_stamp(im,b,x0,y0,255)
        for j in range(6):
            rng=random.Random(733+j);s=(.26+j%3*.12);chip=scaled(m,m.width*s,m.height*s)
            edge_stamp(im,chip,rng.randrange(w)+round(math.sin(f*.4+j)*4)+f*(2+j%2),rng.randrange(h)-f*(3+j%3),(58+j%4*17)*env)
    dr=ImageDraw.Draw(im)
    for j in range(29 if k=='water' else 28):
        rng=random.Random(1083+j); q=j%5
        x=(rng.randrange(w)+((-1 if k=='water' else 1)*(3+(q%3))*f))%w
        y=(rng.randrange(h)+((9+q*2) if k=='water' else -(3+q))*f)%h
        for dx in (0,w,-w):
            for dy in (0,h,-h):
                xx,yy=x+dx,y+dy
                if k=='water': dr.line(((xx+q//2,yy-3-q),(xx-1,yy+1)),fill=witha(p[1+j%3],env*(49+j%4*20)))
                elif q>=3: dr.line(((xx,yy),(xx+(j%2),yy-2)),fill=witha(p[2+(j%5==0)],env*(87+j%3*23)))
                else:dr.point((xx,yy),fill=witha(p[1+j%3],env*(77+j%3*20)))
    return im

def bank(out,rel,frames,cols):
    w,h=frames[0].size;n=len(frames); rows=(n+cols-1)//cols
    assert frames[0].getbbox() is None and frames[-1].getbbox() is None
    canvas=Image.new('RGBA',(w*cols,h*rows))
    for i,im in enumerate(frames):canvas.paste(im,(i%cols*w,i//cols*h))
    f=Path(rel);put(out/'Planches'/f.with_suffix('.png'),png(canvas))
    # PMDO stocke le Texture2D déjà prémultiplié dans ses .dir. Conserver
    # l'alpha droit dans les planches éditables, le convertir pour le rendu natif.
    rgba=np.array(canvas,dtype='uint16')
    rgba[:,:,:3]=(rgba[:,:,:3]*rgba[:,:,3:4]+127)//255
    b=png(Image.fromarray(rgba.astype('uint8')))
    page=struct.pack('<q',len(b))+b+struct.pack('<iiii',w,h,0,n)
    put(out/'Content'/f.with_suffix('.dir'),page)
    return {'banque':f.name,'dossier':f.parent.name,'cellule_px':[w,h],'ancre_px':[w//2,h//2],
            'colonnes':cols,'lignes':rows,'poses':n,'ticks_par_pose':TICKS,'sha256':hashlib.sha256(page).hexdigest()}

def main():
    p=argparse.ArgumentParser();p.add_argument('--base',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--bruts',type=Path,default=ROOT/'dessins-generes'); args=p.parse_args();out=args.out
    info={}
    with ZipFile(args.base) as z:
        for k,(name,dim) in SOURCES.items():
            path=args.bruts/(name+'.png');m=chroma(path,dim);put(out/'Motifs-détourés'/(name+'.png'),png(m));
            assert 30 < np.count_nonzero(np.array(m)[:,:,3]) < m.width*m.height*.96
            if k in ('flying','dragon'):
                seq=[vortex(k,m,f) for f in range(24)]; labels=[{'phase':'amorce','poses':[0,5]},{'phase':'vortex','poses':[6,15]},{'phase':'dislocation','poses':[16,23]}]
            else:
                ss,aa=(old_cols(z,k,l) for l in ('Sol','Air'))
                seq=[colonne(k,m,f,ss[f],aa[f]) for f in range(16)]; labels=[{'phase':'chute','poses':[0,4]},{'phase':'impact et sortie','poses':[5,10]},{'phase':'dissipation','poses':[11,15]}]
            n='Kingambit_Entree_'+k+'_';calques={}
            for i,l in enumerate(('Sol','Air')):calques[l]=bank(out,'Particle/'+n+l,[s[i] for s in seq],6 if len(seq)==24 else 4)
            if k in ('fire','water'):calques['Ecran']=bank(out,'BG/'+n+'Ecran',[weather(k,f,m) for f in range(26)],6)
            info[k]={'dessin':path.name,'dessin_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'phases':labels,'calques':calques}
    put(out/'Index-Cyclones-Meteo.json',(json.dumps(info,ensure_ascii=False,indent=2)+'\n').encode());print('4 entrées : 10 banques PMDO, 4 sources IA, 2 nappes écran.')
if __name__=='__main__':main()
