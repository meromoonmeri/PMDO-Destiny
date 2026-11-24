#!/usr/bin/env python3
"""Paint the recess behind the portcullis, within the existing arch at 1×."""
from pathlib import Path
import importlib.util
import numpy as np
from PIL import Image

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('grille_origine',HERE/'Fabriquer.py')
G=importlib.util.module_from_spec(spec);spec.loader.exec_module(G)
# Exclusive right edge. These are interior scanlines, inset from the carved
# outline. Keep the bevel, both jambs and the lower threshold untouched.
OUVERTURE=[(69,253,260),(70,250,263),(71,247,267),(72,245,269),(74,242,270),
           (77,239,273),(79,238,274),(81,236,275),(83,235,277),(86,236,279),
           (89,235,279),(92,234,280),(98,233,280),(103,233,280),
           (110,233,279),(114,233,279)]

def smooth(a):
    a=np.clip(a,0,1);return a*a*(3-2*a)


def assombrir(r,L):
    assert (r['id'],r['w'],r['h'])==(G.ID,512,384)
    a=L.decode(r['base']);base=a.copy();x0,y0,w,h=G.RECT
    y,x=np.indices((h,w));y=y+y0;x=x+x0
    yy,xl,xr=np.array(OUVERTURE).T
    left=np.rint(np.interp(y,yy,xl));right=np.rint(np.interp(y,yy,xr))-1
    d=np.minimum(x-left,right-x)
    m=(y>=yy[0])&(y<=yy[-1])&(d>=0)&G.mask()
    p=a[y0:y0+h,x0:x0+w];rgb=p[...,:3].astype(float)
    # Near the crown only the dark inside paint is permitted, not any of the
    # ochre edge highlights which cross the stair silhouette on a few scanlines.
    m&=(((rgb[...,0]<=108)&(rgb[...,1]<=57))|(y>=92))&(p[...,3]==255)
    # Shadow on the upper treads: retain their brushwork, risers and warm noses.
    t=smooth((y-78.)/36.);center=np.clip(d/10.,0.,1.)
    attenuation=(.54+.46*t)-(.13*(1-t))*(1-center)
    steps=rgb*attenuation[...,None]+(1-t)[...,None]*[1.5,1.6,3.0]
    # The original block joints in the far crown were read as a wall.
    # Replace those joints with a small colour ramp recess, slightly warmer
    # at the first tread. No flat black shape and no texture added to steps.
    level=np.interp(y,[69,72,76,80,83,87,90],[0,1,2,3,4,5,6])
    level=np.rint(np.clip(level-.9*(1-smooth(d/8.))+.24*np.sin((x-224)*.17+y*.19),0,6)).astype(int)
    colors=np.array([[27,13,18],[31,15,21],[34,17,23],[39,20,25],
                     [45,24,28],[51,28,30],[61,34,31]],dtype=float)
    recess=colors[level]
    crown=(1-smooth((y-81)/8.))*smooth((d+1.)/3.)
    blend=steps*(1-crown[...,None])+recess*crown[...,None]
    # Finish on the inside of the old edge. The receding arch still has its
    # original narrow outline, and nothing changes below the upper flight.
    gain=smooth((d+1)/2.7)*smooth((114-y)/6.)
    shade=np.rint(rgb+(blend-rgb)*gain[...,None]).clip(0,255).astype(np.uint8)
    p[m,:3]=shade[m];changed=np.any(a!=base,axis=2)
    mask=np.zeros_like(changed);mask[y0:y0+h,x0:x0+w]=m
    assert 900<changed.sum()<2000 and not changed[~mask].any()
    assert not changed[:69].any() and not changed[114:].any()
    assert not changed[L.decode(r['front'])[...,3]>0].any()
    assert np.array_equal(a[...,3],base[...,3])
    for patch in r['patches']:
        for ax,ay,bit in patch:
            patch_h,patch_w=L.decode(bit).shape[:2]
            assert not changed[ay:ay+patch_h,ax:ax+patch_w].any()
    q=np.zeros((h,w,4),np.uint8);delta=changed[y0:y0+h,x0:x0+w];q[delta]=p[delta]
    ys,xs=np.nonzero(changed)
    proof=dict(salle=r['id'],origine=[x0,y0],dimensions=[w,h],
               emprise=[int(xs.min()),int(ys.min()),int(np.ptp(xs)+1),int(np.ptp(ys)+1)],
               pixels_modifies=int(changed.sum()),hors_arche=0,marches_basses_inchangees_des_y=114,
               lignes_de_cloison_attenuees=True,calque='Ombre-Interieure.png')
    return a,Image.fromarray(q),changed,proof
