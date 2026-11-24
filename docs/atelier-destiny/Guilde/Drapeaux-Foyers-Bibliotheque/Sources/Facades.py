#!/usr/bin/env python3
"""Two light pools on grass and two falloffs on actual lower facade material."""
from Commun import *
from scipy.ndimage import gaussian_filter
sys.path.insert(0,str(OLD/'Sources'))
from Falaise import A0,carte,obj,decor
D=ROOT/'Cliff-lumiere'; C=D/'Calques'; SOURCE=OLD/'Falaise'; B=OLD/'Braseros'; SZ=(480,520)


def surface():
    native=np.asarray(Image.open(SOURCE/'Cliff-nuit-sans.png').convert('RGBA'))
    b=Image.new('RGBA',SZ);b.alpha_composite(obj('Object','Guilde_HD_Nuit')[0],(109,24));ba=np.asarray(b)[...,3].astype(float)/255
    fg=np.asarray(decor('nuit'))[...,3].astype(float)/255
    fl=carte('nuit')['obstacles'];z=np.array([[q['Tags'] for q in col] for col in fl],dtype=int).T
    cap=(z==0)*1.+(z==2)*.52; cap=np.asarray(Image.fromarray(np.repeat(np.repeat(cap,8,axis=0),8,axis=1).astype(np.float32)))
    walk=gaussian_filter(cap,1.75);return native,ba,fg,walk


def light(src,wood,fg,walk,phase):
    Y,X=np.indices(src.shape[:2]).astype(float);al=src[...,:3].astype(float);L=al@np.array([.2126,.7152,.0722]);smooth=gaussian_filter(L,.95);gx=np.gradient(smooth,axis=1);gy=np.gradient(smooth,axis=0)
    v=ss(137,213,Y)*(1-ss(279,289,Y));is_wood=(.24+.76*ss(12,76,L))*v*wood
    # Mulch and grass end at the platform edge computed from the native geometry.
    is_grass=fg*(1-wood)*walk*ss(234,259,Y)*(1-ss(329,352,Y));
    wall=np.zeros(L.shape);ground=np.zeros(L.shape);shadow=np.zeros(L.shape)
    for which,(lx,ly) in enumerate([(170,302),(310,302)]):
        dx=X-lx;dy=Y-ly;fl=[1.0,.92,.85,.96][(phase+(1 if which else 0))%4]
        # Face irradiance is strongest at the carved posts/roots level. The far
        # crown is below the light horizon. The doorway rim casts a soft recess.
        dist=((dx-(4 if which==0 else -4))/126)**2+((Y-259)/123)**2
        occl=1-(.42*np.exp(-((X-240)/18)**2)*ss(180,201,Y)*(1-ss(255,272,Y)))
        normal=np.clip(1+(gx*(np.sign(dx)*-.03)+gy*.018),.69,1.35)
        wall+=clip(1-dist)**1.65*occl*normal*fl
        bean=clip(1-(dx/103)**2-((dy+10)/58)**2)**1.9
        core=clip(1-(dx/44)**2-((dy+6)/30)**2)**1.7
        step_occl=1-.28*np.exp(-((X-240)/26)**2)*np.exp(-((Y-268)/13)**2)
        ground+=(.73*bean+.35*core)*step_occl*fl
        # A small contact shadow grounds each tripod (per-channel darkening).
        shadow+=.24*clip(1-(dx/17)**2-((dy+1)/5.8)**2)**1.5
    heat=(al*(1-is_grass[...,None]*shadow[...,None]))
    heat+=((1-al/255.)**.73)*(np.minimum(1.24,wall)[...,None]*is_wood[...,None]*np.array([123,77,29])+np.minimum(1.15,ground)[...,None]*is_grass[...,None]*np.array([94,62,24]))
    pix=np.clip(np.rint(heat),0,255).astype('uint8');pix=np.dstack((pix,src[...,3]));m=np.any(pix!=src,axis=2);pix[~m]=0;pix[m,3]=255
    return Image.fromarray(pix),is_wood,is_grass


def main():
    dst=D;dst.mkdir(exist_ok=True);C.mkdir(exist_ok=True)
    old=json.loads((OLD/'Releve-Cliff.json').read_text());native,wall,fore,walk=surface();meta=[];diff=[]
    for k in range(4):
        rel,wm,gm=light(native,wall,fore,walk,k);q=rel.getbbox();png(rel.crop(q),C/f'reflets-{k+1}.png')
        b=rel.copy();base=Image.fromarray(native);base.alpha_composite(rel)
        for t in old['trépieds']:
            x,y=t['pose_pied'];ax,ay=t['pied_dans_image_nuit'];m=Image.open(B/f"{t['cote']}-nuit-{k+1}.png").convert('RGBA');b.alpha_composite(m,(x-ax,y-ay))
        if k==0:
            shades=rel.convert('RGBA');cut=base.crop((68,124,412,352));png(cut.resize((1032,684),Image.Resampling.NEAREST),W/'Cliff-reflets-seuls.png')
        bb=b.getbbox();name=f'nuit-{k+1}.png';png(b.crop(bb),C/name)
        final=Image.fromarray(native);final.alpha_composite(b);png(final,dst/f'Cliff-nuit-{k+1}.png')
        src=Image.fromarray(native);prev=Image.open(SOURCE/f'Cliff-nuit-{k+1}.png').convert('RGBA');a=np.asarray(final);o=np.asarray(prev);y,x=np.indices(a.shape[:2]);dy=(a[...,:3].astype(float)-o[...,:3])@np.array([.2126,.7152,.0722]);changed=np.any(a!=native,axis=2)
        active=(np.asarray(rel)[...,3]>0);d=(y>=172)&(y<=256)&(wm>.27)&(abs(x-240)<111)&active;g=(y>=272)&(gm>.54)&active
        assert not changed[:137].any() and not changed[352:].any() and not (changed & (fore<.05)).any()
        diff.append({'pose':k+1,'pixels_de_surface_eclaires':int(active.sum()),'pixels_facade_concernes':int((active&(wall>.95)).sum()),'hausse_lum_facade_vs_edition_precedente':round(float(np.mean(dy[d])),2),'hausse_lum_sol_vs_edition_precedente':round(float(np.mean(dy[g])),2),'falaise_haute_ciel_mer_intacts':True})
        meta.append({'x':bb[0],'y':bb[1],'png':f'Cliff-lumiere/Calques/{name}','x_reflets':q[0],'y_reflets':q[1],'reflets':f'Cliff-lumiere/Calques/reflets-{k+1}.png'})
    data={'surface':'bois bas et racines isolés par alpha natif ; herbe et marches par tags de sol ; occultation douce du renfoncement de la porte','poses':meta,'verification':diff,'fps':6,'source_cliff':old['source_nuit']}
    write_json(dst/'Releve-Lumiere.json',data);print(diff[0]);
    v=Image.open(dst/'Cliff-nuit-1.png');png(v.crop((65,134,415,352)).resize((1050,654),Image.Resampling.NEAREST),W/'Cliff-lumiere-test.png')

if __name__=='__main__':main()
