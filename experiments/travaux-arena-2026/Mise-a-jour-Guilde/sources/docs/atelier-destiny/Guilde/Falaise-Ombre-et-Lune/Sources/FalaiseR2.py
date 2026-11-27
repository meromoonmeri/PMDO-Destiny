#!/usr/bin/env python3
"""Cliff 0.7.7 – recover the grass behind the clipped sprite, project a new shadow,
place the moon at the screenshot's registered point, and retain 12 ocean / 4 fire poses.
No game assets are written; the source renderer only reads the authenticated inputs.
"""
from pathlib import Path
from functools import cache
from hashlib import sha256
import io,json,sys,base64,re
import numpy as np
from PIL import Image,ImageOps
from scipy import ndimage as nd

ROOT=Path(__file__).resolve().parents[1];G=ROOT.parent; CF=G/'Comptoirs-et-Falaise';DF=G/'Drapeaux-Foyers-Bibliotheque';SRC=G/'Guilde-Destiny-Drapeaux-Foyers-Bibliotheque.html';W=Path.home()/'.cache/ombre-ciel-cliff';W.mkdir(exist_ok=True)
sys.path.insert(0,str(CF/'Sources'));sys.path.insert(0,str(DF/'Sources'))
from Falaise import A as NATIVE,SZ,P,obj,carte,out_layer,render
from Facades import light,surface

H,WID=SZ[::-1];SKH=152;PAD=48;Y,X=np.indices((H,WID));U,V=np.indices((SKH,WID))[::-1]; MOON=(399,117);HOME=(109,24)


def get_hash(p):return sha256(Path(p).read_bytes()).hexdigest()
def dump(p,data):p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def decode(a):return Image.open(io.BytesIO(base64.b64decode(a.split(',')[-1]))).convert('RGBA')
def save(b,name):
    p=ROOT/name;p.parent.mkdir(exist_ok=True,parents=True);b.save(p,optimize=True);return str(p.relative_to(ROOT))
def tmp(b,n):b.save(W/n,optimize=True)
def clip(a):return np.clip(a,0,1)
def smooth(a,b,v):q=clip((v-a)/(b-a));return q*q*(3-2*q)
def ink(a):return tuple(bytes.fromhex(a))
def rgba(a,alpha):
    q=np.empty((*alpha.shape,4),np.uint8);q[...,3]=alpha;q[...,:3]=a;q[alpha==0]=0;return Image.fromarray(q)
def paint_mask(color,opacity):return rgba(color,np.rint(255*clip(opacity)).astype(np.uint8))
def full(sprite,origin=(0,0),size=SZ):p=Image.new('RGBA',size);p.alpha_composite(sprite,origin);return p

@cache
def terrain(p):
    t=Image.new('RGBA',SZ)
    for k,d in enumerate(carte(p)['Layers'][1:],1):
        if d['Visible']:t.alpha_composite(out_layer(p,k))
    return t

@cache
def turf():
    a=np.asarray(terrain('jour'));r,g,b=a[...,:3].astype(float).transpose(2,0,1)
    # Strictly the turf relief on the upper rock; no smoothing on the cliff or the stone stairs.
    upper=(Y>=156)&(Y<353)
    light=(g>=r+5)&(g>=b+23)&(r>89)&(g>115)&(a[...,3]==255)&upper
    rough=(g>=r-1)&(g>=b+21)&(r>72)&(g>98)&(a[...,3]==255)&upper
    m=(nd.binary_closing(light,np.ones((3,3)))|light)&rough
    L,n=nd.label(m);ct=np.bincount(L.ravel());ct[0]=0;take=np.argsort(-ct)[:4];assert ct[take[0]]>31000
    m&=np.isin(L,take[ct[take]>=30]);dist=nd.distance_transform_edt(m)
    assert not m[353:].any() and not m[354:,209:273].any()
    return m,dist


@cache
def clean(p):
    base=terrain(p);a=np.array(base);m,dist=turf();rgb=a[...,:3].astype(float);wt=nd.gaussian_filter(m.astype(float),1.48);pp=np.zeros_like(rgb)
    for i in range(3):
        # Suppress single-pixel chroma/luma alternation without sampling cliff or stair colour.
        v=nd.gaussian_filter(rgb[...,i]*m,1.48)/np.maximum(.006,wt)
        med=nd.median_filter(rgb[...,i],size=3)
        pp[...,i]=.84*v+.16*med
    rate=smooth(.5,2.8,dist)*.955;out=np.rint(rgb+(pp-rgb)*rate[...,None]).clip(0,255).astype(np.uint8)
    # The dither was the defect, not the grass slope. Keep very low-frequency native colour variation.
    fixed=a.copy();fixed[m,:3]=out[m];assert np.array_equal(fixed[...,3],a[...,3]) and np.array_equal(fixed[~m],a[~m]);q=Image.fromarray(fixed)
    diff=np.any(fixed!=a,axis=2);patch=rgba(fixed[...,:3],diff.astype(np.uint8)*255)
    return q,patch

@cache
def house(p):return full(obj('Object','Guilde_HD_'+p.capitalize())[0],HOME)

@cache
def footing():
    building=np.asarray(house('jour'))[...,3]>=128
    low=np.where(building,Y,np.zeros_like(Y)).max(axis=0)
    # Every column has its own contact (trunk and root feet project behind the front step).
    useful=low>178;cols=np.flatnonzero(useful);z0=nd.gaussian_filter1d(np.interp(np.arange(WID),cols,low[cols]).astype(float),3.4)
    surf=building & useful[None,:] & (Y>z0[None,:]-16)
    surf=nd.binary_closing(surf,np.ones((4,4)))|surf
    # The shadow grows from actual floor touches, not from the edges of the old .dir.
    foot=nd.shift(surf.astype(np.uint8),(3,1),order=0)>0
    return building,foot,z0


@cache
def projected(p):
    contact_shape,foot,z0=footing();m,dist=turf();yy,xx=np.where(contact_shape);h=np.maximum(0,z0[xx]-yy)
    idx=P.index(p)
    # Moon at the right -> opposite direction at night. Footprint at the base never moves.
    dx,dy,alpha,reach,contact_op=[(.307,.24,.29,1.0,.37),(.36,.208,.27,.98,.383),(-.323,.22,.25,.94,.36),(-.228,.201,.172,.90,.41)][idx]
    xj=np.clip(np.rint(xx+dx*h).astype(int),0,WID-1);yj=np.clip(np.rint(z0[xx]+dy*h).astype(int),0,H-1)
    samples=np.zeros((H,WID),bool);samples[yj,xj]=True
    cast=nd.binary_fill_holes(nd.binary_closing(samples,np.ones((5,5))))
    cast|=nd.binary_dilation(samples,iterations=1)
    neat=nd.gaussian_filter(cast.astype(float),1.75);far=nd.gaussian_filter(cast.astype(float),4.0)
    roll=smooth(258,338,Y)
    # Near a lateral drop the projected crown trails off, rather than leaving a finger on the lip.
    edge=smooth(83,133,X)*smooth(398,359,X)*smooth(.6,8.4,dist)
    beam=(.65*neat+.35*far)*(1-roll*.57)*alpha*reach*edge
    d1=nd.distance_transform_edt(~foot)
    # Narrow contact under the step edges, then a continuous penumbra. The turf, not a sprite
    # rectangle, is the receiver. Under the lowest step the shadow runs out into the grass.
    base=(contact_op*np.exp(-(d1/3.28)**1.42)+.143*np.exp(-(d1/7.15)**1.79)+.042*np.exp(-(d1/12.7)**2))*(.16+.84*smooth(.5,7,dist))
    opacity=(1-(1-clip(base))*(1-clip(beam)))*m;opacity[opacity<1/255]=0
    color=[(39,54,35),(38,46,47),(39,42,39),(13,24,24)][idx]
    sh=paint_mask(color,opacity);a=np.asarray(sh)[...,3]
    old=np.asarray(obj('Object','Guilde_HD_Ombre_'+p.capitalize())[0])[...,3]
    assert (old[-1]>0).sum()==58 and not any([a[0].any(),a[-1].any(),a[:,0].any(),a[:,-1].any()])
    assert np.any(a[287:320]>9) and not a[355:].any() and a[~m].max()==0
    return sh,{'ancienne_derniere_ligne_opaque':int((old[-1]>0).sum()),'ancienne_fin_sprite_y':HOME[1]+old.shape[0]-1,'nombre_apres_ancienne_limite':int(np.count_nonzero(a[286:])), 'origine':[0,0],'bbox_alpha':list(sh.getbbox()),'pixel_ombre':int((a>0).sum())}

@cache
def sample(id):
    # Island silhouettes taken from the original cliff sky. Recompose – not an upscaled sky edit.
    name,rank={'hauteur':('NUAGES_HAUT',0),'large':('NUAGES_HAUT',2),'voile':('NUAGES_HAUT',3),'petit':('NUAGES_HORIZON',0),'brume':('NUAGES_HAUT',1)}[id]
    im=obj('BG','GUILDE_CLIFF_JOUR_'+name)[0];a=np.array(im);L,n=nd.label(a[...,3]>20);ct=np.bincount(L.ravel());ct[0]=0;m=L==np.argsort(-ct)[rank];q=rgba(a[...,:3],np.where(m,a[...,3],0));return q.crop(q.getbbox())

PALETTES={
 'jour':[['8eabd5','a7c3e5','c9daf0','eaf0f3','fff6dd'],['61b8df','8bcde8','ace0ef','cbecf3','edf6f4']],
 'aube':[['776fac','9683b9','b39bc7','d2acd0','f3c6b9'],['a78fbc','bb9fc5','d5afd0','e8bfca','f7d1c4']],
 'crepuscule':[['666497','876c9f','a482ad','c995b4','efbdaf'],['a4719b','ba86a2','d297a8','e7adae','f5c0b3']],
 'nuit':[['081842','102c58','1c3a67','294b7d','426293'],['142b62','193772','203e7d','2b4885','405a93']],
}

def cloud(p,mode,who,wh,mirror=False,opacity=1.):
    a=sample(who);a=ImageOps.mirror(a) if mirror else a;a=a.resize(wh,Image.Resampling.NEAREST);a=np.array(a);rgb=a[...,:3].astype(float)
    z=rgb@np.array([.22,.64,.14]);R=np.array([ink(k) for k in PALETTES[p][mode]]);colors=np.stack([np.interp(z,[156,180,204,226,246],R[:,i]) for i in range(3)],axis=2)
    # Ramps have subtle breaks but no added dithering. Thin cloud banks keep supporting haze.
    return rgba(np.rint(colors).astype(np.uint8),np.rint(a[...,3]*opacity).astype(np.uint8))


@cache
def nebulas(p):
    high=Image.new('RGBA',(WID+2*PAD,SKH));low=high.copy()
    # Offset shapes break symmetry; the top crown occludes clouds, never the reverse.
    items=[('large',27,22,123,33,False,.98),('hauteur',311,10,153,39,True,.98),('voile',7,70,102,12,False,.70),('voile',392,69,104,12,True,.82),('petit',58,83,42,23,False,.92),('brume',344,47,65,25,True,.54)]
    if p=='nuit':items=[('hauteur',26,24,130,37,False,.96),('large',316,18,137,34,True,.94),('voile',3,74,86,12,True,.70),('voile',408,75,86,13,False,.81)]
    for who,x,y,w,h,f,alpha in items:high.alpha_composite(cloud(p,0,who,(w,h),f,alpha),(x+PAD,y))
    # Horizon banks are lower and shallower, a separate plane drifting more slowly.
    far=[('voile',12,132,122,13,True,.82),('large',42,119,139,22,True,.64),('hauteur',342,134,131,14,False,.68),('voile',370,141,91,10,False,.75)]
    if p=='nuit':far=[('voile',9,136,150,13,True,.86),('large',50,125,101,17,False,.73),('hauteur',340,138,140,12,False,.81),('voile',434,128,66,8,True,.57),('voile',368,143,98,8,False,.73)]
    for who,x,y,w,h,f,alpha in far:low.alpha_composite(cloud(p,1,who,(w,h),f,alpha),(x+PAD,y))
    return high,low

@cache
def moon_sprite():
    a=np.array(obj('BG','GUILDE_CLIFF_NUIT_CIEL')[0]); y,x=np.indices(a.shape[:2]);r,g,b=a[...,:3].astype(int).transpose(2,0,1)
    m=(abs(x-240)<35)&(abs(y-66)<35)&(r>125)&(g>119)&(r>b+24)
    s=rgba(a[...,:3],m.astype(np.uint8)*255);box=s.getbbox();assert box[2]-box[0] in range(60,66) and box[3]-box[1] in range(60,66)
    cr=s.crop(box).resize((32,32),Image.Resampling.BOX);rgb=np.array(cr);rgb[rgb[...,3]<128]=0;rgb[rgb[...,3]>0,3]=255
    # A native ivory disc, with the original mottled relief. No accent line from the screenshot.
    return Image.fromarray(rgb),box

@cache
def clear_sky(p):
    a=obj('BG','GUILDE_CLIFF_'+p.upper()+'_CIEL')[0].copy(); old_box=None
    if p=='nuit':
        rgb=np.array(a);ref=np.median(rgb,axis=1).astype('uint8');mask=np.any(rgb!=ref[:,None,:],axis=2);y,x=np.where(mask);old_box=[int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)];assert old_box==[195,21,286,112]
        rgb[mask]=np.broadcast_to(ref[:,None,:],rgb.shape)[mask];a=Image.fromarray(rgb)
    for row in carte(p)['Background']['Layers']:
        bg=row['BG'];name=bg['BGAnim']['AnimIndex'];
        if not name.endswith('ETOILES'):continue
        a.alpha_composite(obj('BG',name)[0],(bg['MapLoc']['X'],bg['MapLoc']['Y']))
    assert a.size==(WID,SKH) and a.getextrema()[3]==(255,255)
    return a,old_box

@cache
def lunar():
    distance=np.hypot(U+.5-MOON[0],V+.5-MOON[1]);halo=(1-smooth(13,27,distance))**1.4*.34
    halo=paint_mask((192,185,152),halo);m,_=moon_sprite();halo.alpha_composite(m,(MOON[0]-16,MOON[1]-16));return halo

@cache
def background(p):return painted_sky(p,0)

def scenery(p,k=0,animated_at=None):
    # Canopy, terrain and shore are still composed by the original cliff addresses.
    sky=background(p) if animated_at is None else painted_sky(p,animated_at)
    z=full(sky,size=SZ);z.alpha_composite(out_layer(p,0,k));z.alpha_composite(stage(p)[0]);return z

@cache
def stage(p):
    clean_grass,_=clean(p);sh,_=projected(p);z=clean_grass.copy();z.alpha_composite(sh);z.alpha_composite(house(p));return z,clean_grass,sh


def cloud_crop(im,dx=0):
    assert abs(dx)<=PAD
    return im.crop((PAD+dx,0,PAD+dx+WID,SKH))

def painted_sky(p,ms):
    s=clear_sky(p)[0].copy();high,low=nebulas(p)
    if p=='nuit':s.alpha_composite(lunar())
    for plane,v in [(high,.003),(low,.0014)]:s.alpha_composite(cloud_crop(plane,int(ms*v)))
    return s


def stats_noise(a,b,m):
    aa=np.asarray(a)[...,:3].astype(float)@np.array([.213,.715,.072]);bb=np.asarray(b)[...,:3].astype(float)@np.array([.213,.715,.072]);before=aa-nd.median_filter(aa,size=3);after=bb-nd.median_filter(bb,size=3);r0=np.sqrt(np.mean(before[m]**2));r1=np.sqrt(np.mean(after[m]**2));assert r1<r0*.35,(r0,r1)
    return [round(float(r0),4),round(float(r1),4)]

def old_layer(old,phase,k=0):
    x,y,b=old['calques'][phase][k];return full(decode(b),(x,y))


def tripods(ov,k):
    t=json.loads((CF/'Releve-Cliff.json').read_text())['trépieds'];all=[]
    for row in t:
        x,y=row['pose_pied'];u,v=row['pied_dans_image_nuit'];f=Image.open(CF/'Braseros'/f'{row["cote"]}-nuit-{k+1}.png').convert('RGBA');ov.alpha_composite(f,(x-u,y-v));all.append((x-u,y-v,f))
    return all


def delta_atlas(p,mer_rect,base):
    x0,y0,w,h=mer_rect;z=Image.new('RGBA',(w*2,h*6));a=np.asarray(base);diff=[]
    fo=np.asarray(stage(p)[0])[...,3]
    for k in range(12):
        im=scenery(p,k);b=np.asarray(im);m=np.any(a!=b,axis=2);assert not (m & (fo==255)).any();assert not m[:SKH].any()
        s=rgba(b[...,:3],m.astype(np.uint8)*255);assert not m[:y0].any() and not m[:,0:x0].any() and not m[:,x0+w:].any() and not m[y0+h:].any()
        z.paste(s.crop((x0,y0,x0+w,y0+h)),((k%2)*w,k//2*h));diff.append(int(m.sum()))
    return z,diff


def mdata():
    s=SRC.read_text();a=re.search(r'(<script id="donnees"[^>]*>)(.*?)(</script>)',s,re.S);return s,a,json.loads(a[2])

def passes(p):
    doc=carte(p);raw=json.dumps({'relief':doc['obstacles'],'entites':doc['Entities']},sort_keys=True).encode()
    def rect(o):return [o['Collider'][key] for key in ('X','Y','Width','Height')]
    ent=doc['Entities'][0];return {'sha256_entites_obstacles':sha256(raw).hexdigest(),'sha256_rsground':get_hash(NATIVE/f'Data/Ground/guilde_cliff_{p}.rsground'),'porte':rect(next(x for x in ent['GroundObjects'] if x['EntName']=='PorteGuilde')),'entrees':{x['EntName']:rect(x) for x in ent['Markers']}}


def build():
    s,a,d=mdata();old=d['cliff'];assert old['taille']==list(SZ) and old['porte']==[224,256,32,16] and get_hash(SRC)=='005bc65efd4b88102eb0bedc3c484e51dd20750b2f7a99fd7d2caf02662676d5'
    od={p:{'calques':{},'ombres':{},'mer':{},'feux':[]} for p in P};_,wood,fore,walk=surface();m,dist=turf();pos=old['mer']['rect'];mo,src_m=moon_sprite()
    geometry={p:passes(p) for p in P};assert len({q['sha256_entites_obstacles'] for q in geometry.values()})==1
    save(mo,'Calques/Lune-disque.png');save(lunar(),'Calques/nuit/Lune-et-halo.png')
    for i,p in enumerate(P):
        k=od[p];z,fix,shadow=stage(p);base=scenery(p);old0=decode(old['bases'][i]);oldsky,old_lune_rect=clear_sky(p);high,low=nebulas(p)
        assert np.array_equal(np.asarray(old0),np.asarray(render(p)))  # the screenshots belong to this exact base
        roof=house(p).crop((0,0,WID,SKH));old_at=terrain(p);_,patch=clean(p);_,k['ombres']=projected(p)
        pfix=np.asarray(patch)[...,3]>0;k['pixels_herbe_nettoyes']=int(pfix.sum());m1=m&(dist>3)&(Y>=268)&(Y<342)
        k['bruit_luminance_avant_apres']=stats_noise(old_at,fix,m1)
        assert np.array_equal(np.asarray(fix)[~m],np.asarray(old_at)[~m]);assert np.array_equal(np.asarray(base)[np.asarray(house(p))[...,3]==255],np.asarray(house(p))[np.asarray(house(p))[...,3]==255]);
        oldshade=np.asarray(obj('Object','Guilde_HD_Ombre_'+p.capitalize())[0])[...,3]
        assert oldshade[-1,131]>0 and not np.any(np.array(shadow)[np.array(terrain(p))[...,3]==0,3])
        assert not np.any(np.array(patch)[(Y>355),3]);fol=f'Calques/{p}'
        k['calques']={'herbe':save(patch,f'{fol}/Herbe-nettoyee.png'),'ombre':save(shadow,f'{fol}/Ombre-projetee.png'),'ciel_fixe':save(oldsky,f'{fol}/Ciel-fixe.png'),'nuages_cime':save(high,f'{fol}/Nuages-cime.png'),'nuages_horizon':save(low,f'{fol}/Nuages-horizon.png'),'cime_occlusion':save(roof,f'{fol}/Cime-au-premier-plan.png'),'terrain':save(z,f'{fol}/Plateau-et-batiment.png')}
        if p=='nuit':k['calques']['lune']='Calques/nuit/Lune-et-halo.png'
        k['nu']=save(base,f'Plans/Cliff-{p}-sans-braseros.png');k['ancien_soleil_lune_bbox']=old_lune_rect
        sea,changes=delta_atlas(p,pos,base);k['mer']={'rect':pos,'images':12,'fps':7.5,'png':save(sea,f'{fol}/Mer-12-poses.png'),'pixels_par_pose':changes};assert len(set(changes))>6
        tmp(old0,f'Avant-{p}-sans.png')
        if p!='nuit':
            rr=old_layer(old,i);k['feux'].append(save(rr,f'{fol}/Braseros-eteints.png'));q=base.copy();q.alpha_composite(rr);save(q,f'Plans/Cliff-{p}.png')
            before=old0.copy();before.alpha_composite(rr);tmp(before,f'Avant-{p}-0.png')
        else:
            for idx in range(4):
                flare,wall,grass=light(np.asarray(base),wood,fore,walk,idx);fx=flare.copy();tp=tripods(fx,idx)
                z2=base.copy();z2.alpha_composite(fx);aa=np.asarray(z2);zz=np.asarray(base);changed=np.any(aa!=zz,axis=2);assert not changed[:137].any() and not changed[352:].any()
                for x,y,f in tp:
                    q=np.asarray(f);b=aa[y:y+f.height,x:x+f.width];assert np.array_equal(q[q[...,3]==255],b[q[...,3]==255])
                e=old['calques'][3][idx];before=old0.copy();before.alpha_composite(decode(e[2]),(e[0],e[1]));tmp(before,f'Avant-nuit-{idx}.png')
                k['feux'].append(save(fx,f'{fol}/Braseros-et-lumiere-{idx+1}.png'));k.setdefault('reflets_seuls',[]).append(save(flare,f'{fol}/Reflets-braseros-{idx+1}.png'))
                save(z2,f'Plans/Cliff-nuit-{idx+1}.png')
    p9=G.parent/'uploads/image-9.png';p8=G.parent/'uploads/image-8.png'
    # Registered image-9: the crop starts on the cliff at x=326, y=67; its last 24px are UI.
    ref={'cible_lune':list(MOON),'cible_bbox_capture':[54,38,92,63],'origine_capture_9':[326,67],'ancienne_lune_box_source':list(src_m),'nouvelle_lune_bbox':[MOON[0]-16,MOON[1]-16,MOON[0]+16,MOON[1]+16],'origin_capture_8':[210,267],'capture_sha256':[get_hash(p8),get_hash(p9)]}
    rep={'statut':'PASS','format_px':list(SZ),'porte':old['porte'],'geometrie_native':geometry,'nuages_origine_px':[-PAD,0],'raies_coupees_corrigees_a_y':286,'reperage':ref,'base_sha256':get_hash(SRC),'couches':od,'comparatif':'seulement herbe, ombre et ciel sont retravaillés ; chemin, 12 poses de mer et 4 poses couleur des braseros conservés','vitesse_nuages_px_s':[3,1.4]}
    dump(ROOT/'Releve-Cliff-R2.json',rep);print('PASS · ombre reconnectée sans bord tronqué, herbe corrigée, lune',MOON,'et 12 poses de mer par ambiance.')
    for p in ('jour','nuit'):
        b=Image.open(ROOT/'Plans'/('Cliff-jour.png' if p=='jour' else 'Cliff-nuit-1.png')).convert('RGBA');tmp(b,f'Examen-{p}.png')
    return rep

if __name__=='__main__':build()
