#!/usr/bin/env python3
"""Traînées Kingambit : masques de Pre_Battle + 18 sources générées par image.
Proche du défaut : tuile 256×64, pas de panneau ni de sceau central.
Le défilement, le blanc et le retour sont gérés en jeu par le module Lua.
"""
from __future__ import annotations
import argparse
from dataclasses import dataclass
from hashlib import sha256
import io
import json
from pathlib import Path
import struct

import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import label, find_objects, maximum_filter, binary_fill_holes

ROOT=Path(__file__).resolve().parent
W,H=256,64
NAME='Kingambit_Prebataille_PMD_'


@dataclass(frozen=True)
class Type:
    id:str
    titre:str
    boss:str
    motif:str
    note:str
    accent:str
    fonce:str
    coeur:str
    largeur:int
    hauteur:int
    torsion:float
    vitesse:tuple[int,...]


TYPES=(
    Type('normal','Normal','Lockpin','Échos d’ivoire','Deux filaments droits se doublent sans déformer le balayage.','#ecd293','#9f7049','#fff6df',68,7,.0,(360,360,360,360,360)),
    Type('fire','Feu','Braségali','Pointes de braise','Des jets courts de flamme prennent de la vitesse vers le bord.','#ff9b58','#a52e27','#fff1af',76,10,1.8,(336,366,396,426,450)),
    Type('water','Eau','Tortank','Crêtes d’écume','Des vagues basses roulent dans les lignes en contre-courant.','#66e2eb','#246bb8','#d5fff9',79,10,2.7,(318,336,354,366,378)),
    Type('grass','Plante','Jungko','Filets de feuilles','De petites feuilles effilées accrochent les courbes du sillage.','#c4e77f','#49893d','#f0ffc7',64,11,2.0,(330,360,366,378,396)),
    Type('electric','Électrik','Élecsprint','Sauts d’étincelles','Les pointes cassent en zigzag, puis les derniers filets accélèrent.','#f6d55e','#a56a21','#fff4b2',73,9,2.1,(408,444,492,468,510)),
    Type('ice','Glace','Oniglali','Échardes de givre','Des échardes rigides et claires filent le long des traits bleu froid.','#a3ebff','#4783b4','#ecffff',76,9,.8,(396,414,426,438,450)),
    Type('fighting','Combat','Lucario','Chevrons d’impact','Les lames d’impact se doublent et se resserrent autour de leurs pointes.','#ffad86','#a5383a','#ffe1b8',56,12,1.2,(330,390,426,450,468)),
    Type('poison','Poison','Ectoplasma','Bulles de miasme','Les filets ondulent sans s’épaissir et laissent des bulles dans leur sillage.','#e6a2f5','#8b438f','#ffd8fa',67,10,3.0,(294,306,330,342,366)),
    Type('ground','Sol','Laggron','Failles de sable','Des strates se décalent par petits à-coups et projettent des grains.','#e5b778','#9b5734','#ffe4aa',75,9,2.5,(294,312,330,336,360)),
    Type('flying','Vol','Dracaufeu','Plumes d’alizé','Les plumes longues et pâles se mêlent aux balayages les plus rapides.','#a0efe7','#387695','#eefffb',81,10,1.6,(390,420,444,468,486)),
    Type('psychic','Psy','Alakazam','Réfraction','Des pointes en losange se dédoublent comme un reflet de prisme.','#e8b0fc','#7b4a9a','#ffdfff',64,10,1.0,(336,378,390,414,426)),
    Type('bug','Insecte','Dardargnan','Rafales d’essaim','Trois traits courts, nervurés, se croisent par salves rapprochées.','#d7ef87','#607830','#f8ffd5',53,8,.9,(372,414,378,432,450)),
    Type('rock','Roche','Tyranocif','Pierres taillées','Des flèches de schiste très basses se brisent en fragments brefs.','#d8b58e','#806158','#ffdfbf',60,11,2.4,(294,300,324,342,360)),
    Type('ghost','Spectre','Branette','Veilleuses fuyantes','Les lueurs indigo se creusent d’ombres entre deux bandes.','#a7b1f5','#595093','#e8eaff',68,10,2.3,(300,336,348,372,384)),
    Type('dragon','Dragon','Altaria','Sillage d’écailles','Les courbes du dragon généré deviennent de fines queues violettes, sans portrait central.','#c9a8ff','#6850a9','#f1e6ff',69,11,2.2,(342,372,396,420,450)),
    Type('dark','Ténèbres','Démolosse','Entailles nocturnes','Une lisière grenat laisse des croissants courts sur des filets d’ombre.','#eaa0b3','#753c5c','#f7ccdf',75,9,1.8,(330,354,384,426,450)),
    Type('steel','Acier','Métalosse','Rails d’argent','Les extrémités de la mâchoire générée deviennent des rails à rivets, par paires.','#bceaf3','#596e88','#f0ffff',65,10,.0,(324,384,384,432,432)),
    Type('fairy','Fée','Gardevoir','Poudre d’étoiles','De petits éclats rose et or filent en tête des lignes, à la manière du woosh Dazzling.','#f6b1d9','#a3548f','#fff3cf',75,8,.6,(336,366,396,414,438)),
)


def rgb(col):return np.array(tuple(bytes.fromhex(col[1:])),np.float32)


def lire_dir(path):
    b=path.read_bytes()
    n,=struct.unpack_from('<q',b)
    w,h,d,f=struct.unpack_from('<4i',b,n+8)
    assert len(b)==n+24 and (w,h,d,f)==(W,H,0,4),path
    a=np.asarray(Image.open(io.BytesIO(b[8:n+8])).convert('RGBA'))
    return [a[:H,i*W:(i+1)*W] for i in range(4)]


def couper(path,kind):
    im=Image.open(path).convert('RGB')
    # Les deux premiers essais étaient des illustrations larges. On n'en
    # prélève que l'extrémité décorative, sans faire apparaître de blason.
    if kind.id=='dragon':im=im.crop((0,0,round(.62*im.width),im.height))
    if kind.id=='steel':im=im.crop((round(.64*im.width),0,im.width,im.height))
    a=np.asarray(im.resize((768,round(768*im.height/im.width)),Image.Resampling.LANCZOS))
    intensity=a.max(2)
    mask=intensity>27
    z,n=label(mask,np.ones((3,3),np.uint8)); sizes=np.bincount(z.ravel()); sizes[0]=0
    mask=(sizes[z]>=9)
    hard=binary_fill_holes(mask)
    soft=maximum_filter(mask,size=3)
    opacity=np.where(hard,np.clip((intensity.astype(np.float32)-12)/23,.4,1),
                     np.clip((intensity.astype(np.float32)-9)/30,0,.7)*soft)
    nonzero=Image.fromarray(np.rint(255*opacity).astype(np.uint8));box=nonzero.getbbox();assert box,path
    raw=Image.fromarray(np.dstack((a,np.asarray(nonzero))))
    sprite=raw.crop(box).resize((kind.largeur,kind.hauteur),Image.Resampling.LANCZOS)
    q=np.array(sprite)
    # Regroupe les couleurs en pas de pixel, en retenant la matière du dessin.
    q[...,:3]=np.clip(np.rint(q[...,:3].astype('float32')/8)*8,0,255).astype('uint8')
    q[...,3]=np.where(q[...,3]<23,0,np.minimum(255,(q[...,3].astype(np.int32)+8)//16*16)).astype('uint8')
    assert (q[...,3]>150).sum()>kind.largeur*.78,(path,box)
    return Image.fromarray(q)


# Plafond du générateur : ces six traitements partent d'une texture existante.
# Ils gardent sa matière et remplacent la géométrie / ponctuation du sillage.
ADAPTATIONS={'flying':'ice','psychic':'electric','bug':'grass','rock':'ground',
             'ghost':'poison','dark':'fire'}


def adapter(src,k):
    w,h=src.size
    a=np.array(src); yy,xx=np.indices((h,w))
    v=a[...,:3].max(2).astype(np.float32)/255
    low,mid,hi=rgb(k.fonce),rgb(k.accent),rgb(k.coeur)
    pigment=low+(mid-low)*np.clip(v*1.4,0,1)[...,None]+(hi-mid)*np.clip((v-.65)*2.1,0,.75)[...,None]
    a[...,:3]=np.rint(pigment).clip(0,255).astype(np.uint8)
    def layer(im, gain):
        im.putalpha(im.getchannel('A').point(lambda b:round(b*gain)));return im
    b=Image.new('RGBA',src.size)
    p=Image.fromarray(a)
    d=ImageDraw.Draw(b)
    c=lambda x,g=255:(*tuple(map(int,x)),g)
    if k.id=='flying':
        b.alpha_composite(p,(-5,0));d=ImageDraw.Draw(b)
        for x,y,gain in ((w-26,4,235),(26,6,160)):
            d.polygon([(x-11,y),(x-7,y-3),(x+9,y-3),(x+15,y-2),(x+7,y+2),(x-5,y+3)],c(low,gain))
            d.polygon([(x-9,y),(x+2,y-2),(x+12,y-2),(x+4,y+1),(x-5,y+2)],c(mid,gain))
            d.line([(x-9,y+2),(x+11,y-2)],fill=c(hi,gain));d.point([(x-1,y),(x+6,y-1)],fill=c(hi,gain))
    elif k.id=='psychic':
        echo=p.resize((w-12,h-3),Image.Resampling.NEAREST)
        b.alpha_composite(layer(echo,.57),(0,0));b.alpha_composite(p,(6,2));d=ImageDraw.Draw(b)
        for x,y,r in ((w-14,4,7),(w-37,5,4),(w-55,3,2)):
            poly=[(x-r*2,y),(x,y-r//2-1),(x+r*2,y),(x,y+r//2+1)]
            d.polygon(poly,fill=c(low,225),outline=c(mid,234));d.line((x-r*2+1,y,x+r*2-2,y),fill=c(hi,224))
    elif k.id=='bug':
        for x,y,n,g in ((0,4,28,.60),(11,2,33,.77),(24,0,30,1)):
            sr=p.resize((n,h-3),Image.Resampling.LANCZOS);b.alpha_composite(layer(sr,g),(x,y))
        d=ImageDraw.Draw(b)
        for x,y in ((w-12,2),(w-27,4),(w-41,6)):
            d.polygon([(x-5,y-2),(x+6,y),(x-5,y+2),(x-2,y)],c(mid,225));d.line((x-4,y-1,x+4,y),c(hi,205))
    elif k.id=='rock':
        a[...,3][((xx+yy//2)%17>=14)&(xx>w//5)]=0
        b=Image.fromarray(a);d=ImageDraw.Draw(b)
        for x,y,r in ((w-8,5,5),(w-23,7,6),(w-40,3,4),(7,7,2)):
            d.polygon([(x-r,y),(x-r//2,y-2),(x+1,y-3),(x+r,y),(x+1,y+2)],fill=c(mid,244),outline=c(low,218))
            d.line((x-r//2,y-2,x+r,y),fill=c(hi,224))
    elif k.id=='ghost':
        a[...,3]=(a[...,3].astype(np.float32)*np.where(((xx//8)%4==1)&(yy>3),.32,.91)).astype(np.uint8)
        b=Image.fromarray(a);d=ImageDraw.Draw(b)
        for x,y,r in ((w-16,4,5),(w-40,6,3),(16,3,2)):
            d.polygon([(x-r*3,y+2),(x-r,y),(x,y-3),(x+r,y),(x+r//2,y+2),(x-r,y+1)],c(low,190))
            d.line([(x-r*2,y+2),(x-r,y),(x,y-1),(x+r//2,y)],fill=c(mid,215),width=2)
            d.point([(x,y-1),(x+1,y)],fill=c(hi,214))
    elif k.id=='dark':
        b.alpha_composite(layer(p,.7));d=ImageDraw.Draw(b)
        for x,y,r in ((w-16,3,8),(w-44,5,5)):
            d.polygon([(x-r*3,y+3),(x-r,y+1),(x,y-2),(x+r,y-2),(x+r//2,y+2),(x-r,y+3)],c(low,232))
            d.line([(x-r*3,y+3),(x-r,y+1),(x,y-2),(x+r,y-2)],fill=c(mid,226),width=1)
            d.point([(x+r,y-2),(x-1,y-2),(x-r,y)],fill=c(hi,228))
    return b


def forme(k, x, y, n):
    # Formes périodiques : le contour se raccorde au défilement horizontal.
    step=2*np.pi*x/W+n*.8+(y//15)*1.8
    if k.id in {'ground','rock'}:
        phase=(x+(y//5)*6+n*9)%64//8
        return np.rint(k.torsion*np.array([-1,-1,-.36,.70,.70,.04,.52,-.30])[phase]).astype(np.int32)
    if k.id=='electric':
        tri=4*np.abs(((x+3*y+n*18)%64)/64-.5)-1
        return np.rint(k.torsion*tri).astype(np.int32)
    if k.id=='fighting':
        return np.rint(k.torsion*4*(.25-np.abs((x%64)/64-.5))).astype(np.int32)
    return np.rint(k.torsion*np.sin(step*(1 if k.id in {'flying','water','dragon'} else 2))).astype(np.int32)


def texturer(tile,k,i,accent):
    y,x=np.indices((H,W))
    a=tile[np.clip(y-forme(k,x,y,i),0,H-1),x].copy()  # 4 textures natives, silhouettes adaptées
    a[(y<2)|(y>=H-2),3]=0
    source=a.astype(np.float32)
    opa=source[...,3]; t=np.minimum(1.,source[...,0]/np.maximum(1,opa)*1.10)
    low,middle,high=rgb(k.fonce),rgb(k.accent),rgb(k.coeur)
    # Liseré teinté, cœur brillant de la fusaïole, comme Pre_Battle.
    ramp=low+(middle-low)*np.minimum(1.,t*2.7)[...,None]
    ramp+=(high-middle)*np.clip((t-.32)*1.22,0,.88)[...,None]
    b=np.dstack((np.round(ramp).clip(0,255).astype(np.uint8),(opa*.94).astype(np.uint8)))
    base=Image.fromarray(b)
    if k.id in {'normal','psychic','steel','fighting'}:
        double=np.roll(b,3 if k.id in {'psychic','fighting'} else 5,axis=0)
        double[:6,:,3]=0;double[-4:,:,3]=0
        double[...,3]=(double[...,3].astype(np.float32)*(.31 if k.id=='psychic' else .24)).astype(np.uint8)
        halo=Image.fromarray(double);halo.alpha_composite(base);base=halo
    # Monte les détails générés sur les filaments, pas au centre en blason.
    # Un 3e point bref pour l'essaim, sinon 2 textures courtes et espacées.
    labels,num=label(tile[...,3]>=145,np.ones((3,3),np.uint8))
    boxes=[p for p in find_objects(labels) if p and p[1].stop-p[1].start>22]
    boxes.sort(key=lambda p:p[1].stop-p[1].start,reverse=True)
    assert len(boxes)>=3,(k.id,i)
    positions=[]
    candidates=(boxes[:5] if i%2==0 else boxes[1:6])
    for box in candidates:
        center_x=(box[1].start+box[1].stop)//2
        row=(box[0].start+box[0].stop)//2
        if any(abs(row-r)<11 for _,r in positions):continue
        positions.append((center_x,row))
        if len(positions)==(3 if k.id=='bug' else 2):break
    for j,(px,py) in enumerate(positions):
        off=int(forme(k,np.array(px),np.array(py),i))
        scale=(1.0 if j==0 else (.77 if j==1 else .58))
        sr=accent.resize((round(accent.width*scale),max(3,round(accent.height*scale))),Image.Resampling.LANCZOS)
        sr.putalpha(sr.getchannel('A').point(lambda a:round(a*(.94-.10*j))))
        at=(px-round(sr.width*.47),min(H-sr.height-2,max(2,py+off-sr.height//2)))
        for e in (-W,0,W):base.alpha_composite(sr,(at[0]+e,at[1]))
    return base


def bank(p,frames):
    sheet=Image.new('RGBA',(4*W,2*H))
    for j,f in enumerate(frames):sheet.paste(f,(j%4*W,j//4*H))
    a=np.array(sheet)
    a[...,:3]=((a[...,:3].astype('uint16')*a[...,3:4]+127)//255).astype('uint8')
    buf=io.BytesIO();Image.fromarray(a).save(buf,'PNG',compress_level=7)
    b=buf.getvalue();p.write_bytes(struct.pack('<q',len(b))+b+struct.pack('<4i',W,H,0,len(frames)))
    return sheet


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--pmdo',type=Path,required=True,help='Dossier PMDO, contenant Content/BG/Pre_Battle.dir')
    ap.add_argument('--images',type=Path,default=ROOT/'Images')
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--type',nargs='+',choices=[k.id for k in TYPES]);a=ap.parse_args()
    src=a.pmdo/'Content/BG/Pre_Battle.dir'; native=lire_dir(src)
    dst=a.out/'Content/BG';review=a.out/'Textures';dst.mkdir(parents=True,exist_ok=True);review.mkdir(exist_ok=True)
    index=[]
    for k in TYPES:
        if a.type and k.id not in a.type:continue
        origin=ADAPTATIONS.get(k.id,k.id)
        pic=a.images/(origin+'.png');motif=couper(pic,k)
        if origin!=k.id:motif=adapter(motif,k)
        strips=[texturer(s,k,i,motif) for i,s in enumerate(native)]
        result=dst/(NAME+k.id+'.dir')
        atlas=bank(result,strips+[s.transpose(Image.Transpose.FLIP_LEFT_RIGHT) for s in strips]);atlas.save(review/(k.id+'.png'))
        motif.save(review/(k.id+'-accent.png'))
        index.append(dict(id=k.id,type=k.titre,boss=k.boss,titre=k.motif,note=k.note,couleur=k.accent,
                          vitesse=k.vitesse,texture=result.name,sha256=sha256(result.read_bytes()).hexdigest(),
                          image_source=pic.name,adaptation=origin!=k.id,image_sha256=sha256(pic.read_bytes()).hexdigest()))
        print(f'{k.id:8s} | {result.stat().st_size:6,} octets | {motif.width}×{motif.height} px',flush=True)
    (a.out/'Index-Illustrations.json').write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':main()
