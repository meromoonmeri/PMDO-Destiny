#!/usr/bin/env python3
"""Make a true sliding portcullis atlas, clipped by the existing wooden arch."""
import argparse
import base64
import hashlib
import json
from io import BytesIO
from pathlib import Path

import numpy as np
from PIL import Image

OUT = Path(__file__).resolve().parents[1]
ROOT = OUT.parent
HTML = ROOT/'Guilde-Destiny-Bourgeons-PMD.html'
MARK = '<script id="donnees" type="application/json">'
ID = 'guilde_destiny_accueil'
NEXT = 'guilde_destiny_missions'
MASTER = OUT/'Maitres/Grille-metal.png'
ATLAS = OUT/'Tilesheet-Grille-Escalier.png'
X,Y,W,H = 224,64,64,80
RECT = [X,Y,W,H]
VIEW = dict(x=200, y=54, w=112, h=96)
BAS = 135                 # last row covered by the feet is y134; y135 is the stair riser
HAUT = 69                 # tip of the original aperture
GATE_X = 228
WIDTH, HEIGHT = 56,66
OFFSETS = [0,1,3,6,10,15,21,27,34,41,48,54,59,63,65,66]
FPS = 15
# Interior wood edge, measured by scanline on the 512 x 384 Accueil map.
EDGES = [(69,252,261),(71,246,267),(74,242,270),(78,238,274),(83,235,278),
         (88,234,280),(93,233,280),(98,232,280),(103,232,281),(111,232,280),
         (119,231,281),(128,231,282),(134,230,283)]
VARIANTS = {
    'fermee':('G01P01A2-Entree-fermee.png','G01P01A2','77345','5e8f9b94482389a60aeb28033a8d467d4c86fd8341dcd2db443d08aad8f1e62a'),
    'ouverte':('G01P01A-Entree-ouverte.png','G01P01A','77344','9ff9001a7ed4fb9272bd5c38b9abfb4f45b6525c318130a43a0b05db5e0fbf84'),
}


def page():
    head,rest=HTML.read_text(encoding='utf8').split(MARK,1)
    body,tail=rest.split('</script>',1)
    return head,json.loads(body),tail


def decode(p):
    return Image.open(BytesIO(base64.b64decode(p.rsplit(',',1)[-1]))).convert('RGBA')


def pack(img):
    buf=BytesIO();img.save(buf,'PNG',optimize=True)
    return 'data:image/png;base64,'+base64.b64encode(buf.getvalue()).decode('ascii')


def save(path,im):
    path.parent.mkdir(parents=True,exist_ok=True);im.save(path,'PNG',optimize=True)


def prepare(raw):
    a=np.asarray(Image.open(raw).convert('RGB'),dtype=np.int16)
    r,g,b=a.transpose(2,0,1)
    matte=~((r>98)&(b>96)&(r-g>37)&(b-g>30));a[~matte]=0
    im=Image.fromarray(np.dstack((a.astype(np.uint8),matte.astype(np.uint8)*255)))
    im=im.crop(im.getbbox()).resize((WIDTH,HEIGHT),Image.Resampling.BOX)
    a=np.array(im);a[...,3]=np.where(a[...,3]>=120,255,0)
    a[...,:3]=(np.round(a[...,:3].astype(float)/3).clip(0,85)*3).astype(np.uint8)
    a[a[...,3]==0]=0
    # Six visible slats through the bottom, one solid crossbrace through the middle.
    line=a[-4,:,3]>0
    assert np.count_nonzero(line & ~np.r_[False,line[:-1]])==6
    assert (a[HEIGHT//2,:,3]>0).sum()>=WIDTH-2
    save(MASTER,Image.fromarray(a))


def mask():
    rows=np.arange(Y,Y+H)
    ym,l,r=np.asarray(EDGES).T
    xl=np.rint(np.interp(rows,ym,l)).astype(int)
    xr=np.rint(np.interp(rows,ym,r)).astype(int)
    x=np.arange(X,X+W)
    return (rows[:,None]>=HAUT)&(rows[:,None]<BAS)&(x>=xl[:,None])&(x<xr[:,None])


def build_frames(im):
    supported=mask();frames=[]
    y=np.arange(Y,Y+H)
    # The part of the same grate inside the curved opening is darker than its feet.
    depth=np.interp(y,[HAUT,90,113,BAS],[.65,.77,.91,1])[:,None,None]
    for lift in OFFSETS:
        raw=Image.new('RGBA',(W,H));raw.paste(im,(GATE_X-X,BAS-HEIGHT-lift-Y))
        a=np.array(raw);a[~supported]=0;a[...,:3]=np.rint(a[...,:3]*depth).astype(np.uint8)
        frames.append(a)
    # Verify motion, rather than opacity fading: the material's lower edge follows the offset.
    assert all(int(np.nonzero(a[...,3])[0].max())+Y==BAS-1-k for a,k in zip(frames[:-1],OFFSETS[:-1],strict=True))
    assert len({f.tobytes() for f in frames})==len(frames)
    assert not frames[-1].any()
    return frames


def build(d):
    r=next(q for q in d['rooms'] if q['id']==ID)
    g=next(q for q in r['gates'] if q['id']=='EscalierNord')
    back=next(q for q in d['rooms'] if q['id']==NEXT)
    rev=next(q for q in back['gates'] if q['dest']==ID)
    assert (r['w'],r['h'],g['rect'],g['dest'],rev['id'])==(512,384,[232,104,48,16],NEXT,'EscalierSud')
    protect=np.array(decode(r['front']))[Y:Y+H,X:X+W,3]
    assert not protect[mask()].any()
    im=Image.open(MASTER).convert('RGBA');assert im.size==(WIDTH,HEIGHT)
    frames=build_frames(im)
    sheets=[]
    for n in range(4):
        cfg=d['nuits'][r['nuit']] if n==3 else d['lumieres'][r['nuit']][n]
        lut=np.asarray(cfg['lut'],dtype=np.uint8)
        sheet=Image.new('RGBA',(W*4,H*4))
        for i,f in enumerate(frames):
            a=f.copy()
            for k in range(3):a[...,k]=lut[k,a[...,k]]
            a[a[...,3]==0]=0
            pic=Image.fromarray(a);sheet.paste(pic,(i%4*W,i//4*H))
            if n==0 and i in (0,5,9,15):
                label={0:'Fermee',5:'Levee-15px',9:'Levee-41px',15:'Ouverte'}[i]
                save(OUT/'Calques'/f'{label}.png',pic)
        if n==0:save(ATLAS,sheet)
        sheets.append(pack(sheet))
    references={};src={}
    for state,(filename,code,num,sha) in VARIANTS.items():
        path=OUT/'Reference'/filename;assert hashlib.sha256(path.read_bytes()).hexdigest()==sha
        a=Image.open(path).convert('RGBA');assert a.size==(480,408)
        references[state]=pack(a.crop((210,106,270,154)))
        src[state]=dict(carte=code,url=f'https://projectpokemon.org/home/gallery/image/{num}-{code.lower()}png/',sha256=sha)
    links=[(r['id'],g['id']),(back['id'],rev['id'])]
    gate=dict(id=ID,dest=NEXT,vues=VIEW,rect=RECT,colonnes=4,positions=OFFSETS,ips=FPS,
              calques=sheets,liens=links,reference=references)
    proof=dict(planche=ATLAS.name,dimensions=[4*W,4*H],case=[W,H],tuile=8,
               images=[dict(index=k,case=[k%4*W,k//4*H,W,H],levee_px=h,passage_autorise=k==len(OFFSETS)-1)
                       for k,h in enumerate(OFFSETS)], cadence=FPS,duree_ouverture_ms=round(1000*(len(OFFSETS)-1)/FPS),
               salle=ID,origine_case=[X,Y],bord_marche_y=BAS,haut_visible_y=HAUT,
               nord=dict(id=g['id'],rect=g['rect'],destination=NEXT),retour=rev['id'], reference=src,
               source='Grille générée, découpée et déplacée verticalement dans le masque de l’arche de Destiny.',
               guidage='Décor et navigation de l’aperçu uniquement',pixel_jeu_modifie=False)
    (OUT/'Index-Tilesheet.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    return gate,proof


if __name__=='__main__':
    q=argparse.ArgumentParser();q.add_argument('--generee',type=Path);args=q.parse_args()
    if args.generee:prepare(args.generee)
    _,d,_=page();g,p=build(d)
    print(f'PASS · {len(OFFSETS)} images, course {OFFSETS[-1]} px · {p["dimensions"]}')
