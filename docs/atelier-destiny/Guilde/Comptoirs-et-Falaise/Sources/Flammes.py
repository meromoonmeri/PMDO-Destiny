#!/usr/bin/env python3
"""Détourage des deux trépieds G01P01A / G01P01C, sans redessiner les pixels de flamme."""
from collections import Counter
import hashlib,io,json,struct,zlib
import numpy as np
from PIL import Image
from scipy.ndimage import binary_fill_holes
from Falaise import W,A0,O,P,SZ,carte
BR=O/'Braseros'; B=O/'Falaise'; ref=O.parent/'Bourgeons-PMD/Reference/G01P01C-Falaise-Nuit.png'
dayref=O/'Reference/G01P01A-Falaise-Jour.png'; WS=B/'Calques'
# Native coordinates used on the preview, at the end of the centre leg.
POSE=[(170,302),(310,302)]
BOX=[(149,87,185,154),(293,87,329,154)]; ANCHOR=[(18,65),(18,65)]; FPS=6
DAY_METAL={(71,63,47),(79,71,63),(95,87,71),(119,111,103)}
FIRE={(231,47,0),(231,79,0),(231,103,0),(231,119,0),(231,159,0),(231,199,23),(231,223,15),(231,231,183)}
METAL={(151,143,111),(95,95,79),(39,39,39),(119,111,103),(127,127,79),(71,63,47),(55,47,31),(71,55,39),(31,31,31),(47,39,31),(103,95,71),(95,71,71),(119,111,87),(79,79,63)}

def rgba(src,mask):
    a=np.dstack([src,mask.astype('uint8')*255]);a[~mask]=0;return Image.fromarray(a)

def maskcolors(a,colors):
    z=a.astype(np.int32);key=z[...,0]*65536+z[...,1]*256+z[...,2];return np.isin(key,[r*65536+g*256+b for r,g,b in colors])

def exact_apng(frames,dst):
    """Put exact 1/6 s fractions in each fcTL header instead of rounding milliseconds."""
    buf=io.BytesIO();frames[0].save(buf,format='PNG',save_all=True,append_images=frames[1:],duration=167,loop=0,disposal=0,blend=0)
    raw=buf.getvalue();out=bytearray(raw[:8]);i=8
    while i<len(raw):
        size,n=struct.unpack_from('>I4s',raw,i);data=raw[i+8:i+8+size];i+=12+size
        if n==b'fcTL':data=data[:20]+struct.pack('>HH',1,FPS)+data[24:]
        out.extend(struct.pack('>I',len(data))+n+data+struct.pack('>I',zlib.crc32(n+data)))
    dst.write_bytes(out)


def extract():
    day=Image.open(dayref);night=Image.open(ref)
    assert night.n_frames==4 and night.size==(480,408) and day.size==night.size
    decoded=[]
    for k in range(4):
        night.seek(k);d=night.info.get('duration');assert abs(d-1000/FPS)<0.01
        decoded.append((night.convert('RGB'),d))
    meta=[]; result={}
    for side,box in enumerate(BOX):
        name=('ouest','est')[side]; dr=np.asarray(day.convert('RGB').crop(box));y=np.arange(box[1],box[3])[:,None];metal=maskcolors(dr,DAY_METAL)&(y>=110);metal=binary_fill_holes(metal)
        assert 480<=metal.sum()<=600
        dm=rgba(dr,metal); a0=dm.getbbox();dm.crop(a0).save(BR/f'{name}-eteint.png',optimize=True)
        phases=[]; nf=[]
        for k,(nat,d) in enumerate(decoded):
            src=np.array(nat.crop(box));fire=maskcolors(src,FIRE)&(y<129)
            bowl=metal&(y>=130)
            # The daylight palette supplies the tripod outline. The flame partly covers
            # the bowl, so look up the exact dark/night rim colours inside its contour.
            for yy in range(121-box[1],130-box[1]):
                xs=np.flatnonzero(metal[yy]);lo,hi=int(xs.min()),int(xs.max())+1
                bowl[yy,lo:hi]=maskcolors(src[yy,lo:hi],METAL)
            # At the source, a rock hides a few pixels on the east tripod.
            # Borrow only those metal pixels from the homologous west leg.
            occluded=bowl&(y>=140)&(src[...,0]>140)&~maskcolors(src,{(143,143,95),(215,151,95),(215,167,95)}) if side else np.zeros(bowl.shape,bool)
            src[occluded]=np.asarray(nat.crop(BOX[0]))[occluded]
            m=fire|bowl;assert (m&fire).sum()==fire.sum() and fire.sum()>480,(name,k,int(fire.sum()))
            nf.append(rgba(src,m));phases.append({'phase':k,'duree_ms':round(d,4),'pixels_flamme':int(fire.sum()),'pixels_trépied':int((bowl&~fire).sum()),'pixels_metal_masques_source':int(occluded.sum())})
        bb=tuple(fn(x.getbbox()[i] for x in nf) for i,fn in enumerate([min,min,max,max]));sizes=[]
        for k,im in enumerate(nf):
            sp=im.crop(bb);sp.save(BR/f'{name}-nuit-{k+1}.png',optimize=True);sizes.append(len(np.unique(np.asarray(sp).reshape(-1,4),axis=0)))
            assert (np.array(sp)[...,:3][np.array(sp)[...,3]>0]!=0).any()
        exact_apng([im.crop(bb) for im in nf],BR/f'{name}-boucle-nuit.png')
        meta.append({'cote':name,'fenetre_source':list(box),'pose_pied':list(POSE[side]),'pied_dans_image_nuit':[ANCHOR[side][0]-bb[0],ANCHOR[side][1]-bb[1]],'pied_dans_image_jour':[ANCHOR[side][0]-a0[0],ANCHOR[side][1]-a0[1]],'phases':phases,'palette_verifiee':sizes})
        result[name]=[dm,nf]
    return result,meta

def ground_mask(p):
    n=np.asarray(Image.open(A0/f'{p}-decor.png'));y,x=np.indices(SZ[::-1]);return (n[...,3]>250)&(y>228)&(y<346)

def layers(p,k,detailed):
    y,x=np.indices(SZ[::-1]);m=ground_mask(p)
    shadow=Image.new('RGBA',SZ);cast=Image.new('RGBA',SZ);sprites=Image.new('RGBA',SZ)
    for half,((bx,by),side) in enumerate(zip(POSE,('ouest','est'))):
        phase=p=='nuit';pig=[1,.68,.88,.76][P.index(p)];contact=((x-bx)/18)**2+((y-(by-2))/7)**2
        sh=np.round(255*np.clip(1-contact,0,1)**1.5*.36*m).astype(np.uint8);mp=Image.new('RGBA',SZ,(22,18,16,0));mp.putalpha(Image.fromarray(sh));shadow.alpha_composite(mp)
        if phase:
            f=[1.0,.90,.83,.94][k]
            dx=(x-bx);dy=y-(by-23);h=np.maximum(0,1-(dx/65)**2-(dy/49)**2)**2
            g=np.maximum(0,1-((x-(bx+(-3,3)[half]))/36)**2-((y-(by-4))/23)**2)**1.6
            # Warm local reflected light, not a canvas overlay. The outer edge of
            # the cliff, sea and sky are untouched, as is the centre of the steps.
            no_portal=np.minimum(1,np.maximum(0,(abs(x-240)-23)/17))
            amp=np.minimum(.23, (.12*h+.155*g)*f)*m*no_portal
            color=(253,160,67);hlo=Image.new('RGBA',SZ,color+(0,));hlo.putalpha(Image.fromarray(np.round(amp*255).astype('uint8')));cast.alpha_composite(hlo)
        a,t=detailed[side]; sp=t[k] if phase else a
        if not phase and p!='jour':
            rgb=np.array(sp);rgb[...,:3]=np.minimum(255,np.round(rgb[...,:3]*np.array(([1.05,.99,1.11] if p=='aube' else [.85,.75,.80])))).astype('uint8');sp=Image.fromarray(rgb)
        j=(bx-ANCHOR[half][0],by-ANCHOR[half][1]); sprites.alpha_composite(sp,j)
    shadow.alpha_composite(cast);shadow.alpha_composite(sprites)
    return shadow

def render_all():
    for d in [BR,B,WS]:d.mkdir(parents=True,exist_ok=True)
    detailed,meta=extract(); frames={}; summary={}
    for p in P:
        phases=range(4) if p=='nuit' else [0];base=Image.open(A0/f'{p}-00.png');base.save(B/f'Cliff-{p}-sans.png',optimize=True)
        frames[p]=[]; diff=[]
        for i in phases:
            ov=layers(p,i,detailed);bb=ov.getbbox();part=ov.crop(bb);name=f'{p}-{i+1}.png';part.save(WS/name,optimize=True);frames[p].append([bb[0],bb[1],name])
            final=base.copy();final.alpha_composite(ov)
            if p=='nuit':final.save(B/f'Cliff-{p}-{i+1}.png',optimize=True)
            else:final.save(B/f'Cliff-{p}.png',optimize=True)
            changed=np.any(np.array(base)!=np.array(final),axis=2);y,x=np.nonzero(changed);diff.append({'pixels':int(changed.sum()),'limites_inclusives':[int(x.min()),int(y.min()),int(x.max()),int(y.max())]})
            assert changed[:,218:263].sum()==0 and changed[:228].sum()==0 and changed[346:].sum()==0
        summary[p]=diff
    # Only the changed pixels in the twelve night ocean poses are stored. PNG
    # preserves the tile colours exactly and all pixels on foreground match.
    orig=np.asarray(Image.open(A0/'nuit-00.png')); patch=Image.new('RGBA',(0,0)); tiles=[];box=None
    for k in range(12):
        src=np.asarray(Image.open(A0/f'nuit-{k:02}.png'));m=np.any(src!=orig,axis=2);out=rgba(src[...,:3],m);tiles.append(out)
        q=out.getbbox()
        if q:box=q if not box else (min(q[0],box[0]),min(q[1],box[1]),max(q[2],box[2]),max(q[3],box[3]))
    l,t,r,b=box;w,h=r-l,b-t;patch=Image.new('RGBA',(w*2,h*6))
    for j,tile in enumerate(tiles):patch.paste(tile.crop(box),(j%2*w,j//2*h))
    patch.save(WS/'Mer-nuit.png',optimize=True)
    r=carte('nuit'); dur=Counter(g['FrameLength'] for col in r['Layers'][0]['Tiles'] for ce in col for g in ce['Layers'] if len(g['Frames'])>1).most_common(1)
    # Check the real walkability tags in every ambience, not image colours.
    tag_check={}
    for p in P:
        o=carte(p)['obstacles'];pts=POSE+[(240,y) for y in range(280,350,8)]
        tag_check[p]=[o[x//8][y//8]['Tags'] for x,y in pts];assert all(t==0 for t in tag_check[p])
    rep={'source_nuit':{'url':'https://projectpokemon.org/home/gallery/image/77577-g01p01cpng/','sha256':hashlib.sha256(ref.read_bytes()).hexdigest()},'source_jour':{'url':'https://projectpokemon.org/home/gallery/image/77344-g01p01apng/','sha256':hashlib.sha256(dayref.read_bytes()).hexdigest()},'trépieds':meta,'fps_braseros':FPS,'fps_mer_apercu':7.5,'mer_frameLength':dur,'atlas_mer':[l,t,w,h,'Mer-nuit.png'],'calques':frames,'differences_vs_cliff_natif':summary,'porte_rect':[224,256,32,16],'arrivee_rect':[224,280,16,16],'sol_aux_pieds_et_axe_central':tag_check}
    (O/'Releve-Cliff.json').write_text(json.dumps(rep,ensure_ascii=False,indent=2)+'\n');return rep

if __name__=='__main__':render_all();print('2 trépieds et 4 poses détourés ; 4 ambiances Cliff comparées avec la carte nue.')
