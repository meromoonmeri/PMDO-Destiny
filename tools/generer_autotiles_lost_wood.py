#!/usr/bin/env python3
"""Construit les autotiles Lost Wood 24 px à partir de matières générées.

Le modèle a produit deux matières, pas les masques de raccord. Les 47 cas
AutoTileAdjacent sont calculés ici selon RogueEssence ; aucun pixel des
références natives n'est copié. Les anciens placements/index sont conservés.
"""
from pathlib import Path
import collections, io, json, math, struct, zlib, os
from PIL import Image, ImageEnhance

ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT/'game'
SOURCE = ROOT/'art/lost_wood_sources'
# Les définitions actives utilisent maintenant le DTEF aux lucioles. Garder
# les définitions historiques permet de reconstruire sans les remplacer.
ORIGINAL_DEFINITIONS = SOURCE/'autotiles_originaux'
OUT = Path(os.environ.get('DESTINY_AUTOTILE_OUT', ROOT/'build/lost_wood_generation'))
OUT.mkdir(parents=True, exist_ok=True)

# Recalage à l'échelle des pixels d'un étage. Le lissage ne touche jamais au
# découpage en cellules de 24 px : il rend uniquement les matières périodiques.
def periodic(path, crop, brightness=1.0):
    image = Image.open(path).convert('RGB').resize((192,192), Image.Resampling.NEAREST).crop(crop)
    image = image.resize((48,48), Image.Resampling.NEAREST)
    image = ImageEnhance.Brightness(image).enhance(brightness)
    out = Image.new('RGB',(24,24))
    pix = image.load(); dst=out.load()
    for y in range(24):
        # La fonction rejoint exactement sa valeur d'origine à x/y=24.
        wy = y/24
        for x in range(24):
            wx=x/24
            weights=((1-wx)*(1-wy),wx*(1-wy),(1-wx)*wy,wx*wy)
            source=(pix[x+24,y+24],pix[x,y+24],pix[x+24,y],pix[x,y])
            dst[x,y]=tuple(round(sum(c[i]*w for c,w in zip(source,weights))) for i in range(3))
    # Mêmes pixels sur chaque bord : toute variante conserve cette bordure.
    p=out.load()
    for i in range(24):
        p[23,i]=p[0,i]
        p[i,23]=p[i,0]
    p[23,23]=p[0,0]
    return out

ground = periodic(SOURCE/'matiere_sol.png', (72,12,120,60), 1.45)
canopy = periodic(SOURCE/'matiere_canopée.png', (60,0,108,48), 1.50)
ground_alts = [ground, periodic(SOURCE/'matiere_sol.png',(60,24,108,72),1.45), periodic(SOURCE/'matiere_sol.png',(48,36,96,84),1.45)]
canopy_alts = [canopy, periodic(SOURCE/'matiere_canopée.png',(48,0,96,48),1.50), periodic(SOURCE/'matiere_canopée.png',(72,72,120,120),1.50)]
roots = periodic(SOURCE/'guide_lost_wood.png',(28,28,54,54),1.90)
ground.save(OUT/'matiere_sol_24px.png');canopy.save(OUT/'matiere_canopée_24px.png')

def alternative(base, other):
    # Les quatre bords restent identiques ; seule la matière intérieure change.
    out=base.copy();p=out.load();a=base.load();b=other.load()
    for y in range(24):
        for x in range(24):
            distance=min(x,y,23-x,23-y)
            t=max(0,min(1,(distance-1)/5))
            p[x,y]=tuple(round(a[x,y][i]*(1-t)+b[x,y][i]*t) for i in range(3))
    return out

def ground_variant(index):
    out=alternative(ground,ground_alts[index%len(ground_alts)])
    # Détails dessinés par-dessus la matière générée, jamais sur les bordures.
    # Une touffe et quelques pétales évoquent le sol des donjons PMD.
    if index:
        pixels=out.load()
        if index==1:
            for dx,dy,c in [(-2,-2,(44,98,59)),(0,-3,(53,111,67)),(2,-2,(44,98,59)),(-1,-1,(65,122,66)),(0,0,(40,87,53)),(1,-1,(65,122,66)),(0,1,(37,72,44))]:
                pixels[11+dx,12+dy]=c
        else:
            for dx,dy,c in [(0,-1,(162,167,120)),(-1,0,(154,169,140)),(1,0,(154,169,140)),(0,1,(135,155,125)),(0,0,(215,185,89)),(1,2,(36,86,50))]:
                pixels[13+dx,13+dy]=c
    return out

# Bits du moteur : D,G,H,Droite puis les diagonales BG,HG,HD,BD.
# Interpolation locale continue entre les centres de cellules ; le seuil est
# relevé pour laisser un petit rebord de sol au contact des pièces praticables.
def field(code,x,y):
    dirs=[bool(code & (1<<i)) for i in range(4)]
    xdir=1 if x<12 else 3
    ydir=2 if y<12 else 0
    dindex={(1,0):0,(1,2):1,(3,2):2,(3,0):3}[(xdir,ydir)]
    # Sur un bord commun, les deux cases évaluent exactement le même champ.
    ax=.5 if x in (0,23) else abs((x+0.5-12)/24)
    ay=.5 if y in (0,23) else abs((y+0.5-12)/24)
    dx=1 if dirs[xdir] else 0; dy=1 if dirs[ydir] else 0
    diag=1 if (code & (1<<(dindex+4))) else 0
    return (1-ax)*(1-ay)+ax*(1-ay)*dx+(1-ax)*ay*dy+ax*ay*diag

def blend(a,b,t):
    return tuple(round(a[i]*(1-t)+b[i]*t) for i in range(3))

def wall_variant(code,index):
    result=Image.new('RGB',(24,24)); dst=result.load(); a=ground.load()
    leaf_variant=alternative(canopy,canopy_alts[index%len(canopy_alts)])
    b=leaf_variant.load()
    for y in range(24):
      for x in range(24):
        # Le relief des feuilles irrégularise la silhouette des raccords.
        leaf=canopy.getpixel((x,y))
        rough=max(-.025,min(.025,(leaf[1]-65)*.0006))
        f=field(code,x,y)+rough
        if f < .70:
            c=a[x,y]
        elif f < .74:
            # Pied de berge : ombre progressive depuis la terre.
            c=blend(a[x,y], (44,41,27), (f-.70)/.04*.72)
        elif f < .82:
            # Racines extraites de l'image créée, avec une lisière ocre.
            r=roots.getpixel((x,y))
            c=blend(r,(91,68,35),.30)
        elif f < .86:
            c=blend(roots.getpixel((x,y)), b[x,y], (f-.82)/.04)
        else:
            c=b[x,y]
        # Quelques éclats de feuilles, uniquement à l'intérieur des variantes.
        if index and f>.88 and 3<x<20 and 3<y<20 and ((x*7+y*11+index*5)%71==0):
            c=blend(c,(71,117,74),.30)
        dst[x,y]=c
    return result

# Une seule palette commune aux deux matières et à toutes les bordures :
# deux cases voisines ne changent pas de couleur selon la variante choisie.
training=Image.new('RGB',(72,48))
training.paste(ground_variant(0),(0,0));training.paste(canopy,(24,0));training.paste(roots,(48,0))
training.paste(wall_variant(0x03,0),(0,24));training.paste(ground_variant(1),(24,24));training.paste(ground_variant(2),(48,24))
PALETTE=training.quantize(colors=64,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE)

def png_bytes(im):
    # PNG indexé conforme (64 couleurs). Réduire le chunk PLTE, pas la qualité
    # à chaque case : Pillow écrit sinon systématiquement 256 entrées.
    indexed=im.convert('RGB').quantize(palette=PALETTE,dither=Image.Dither.NONE)
    buf=io.BytesIO();indexed.save(buf,format='PNG',optimize=True,bits=8)
    raw=buf.getvalue();out=bytearray(raw[:8]);offset=8
    while offset<len(raw):
        length=struct.unpack_from('>I',raw,offset)[0];kind=raw[offset+4:offset+8]
        payload=raw[offset+8:offset+8+length];offset+=length+12
        if kind==b'PLTE':payload=payload[:64*3]
        out+=struct.pack('>I',len(payload))+kind+payload+struct.pack('>I',zlib.crc32(kind+payload)&0xffffffff)
    return bytes(out)

def pad_png_to(png, size):
    # Chunk auxiliaire valide, AVANT IEND, pour conserver les positions natives.
    missing = size-len(png)
    if missing<12: raise ValueError(f'PNG trop grand pour l’enveloppe native: {len(png)} vs {size}')
    payload=b'\0'*(missing-12);chunk_type=b'npAD'
    chunk=struct.pack('>I',len(payload))+chunk_type+payload+struct.pack('>I',zlib.crc32(chunk_type+payload)&0xffffffff)
    assert png[-12:]==b'\0\0\0\0IEND\xaeB`\x82'
    result=png[:-12]+chunk+png[-12:]
    assert len(result)==size
    # Vraie relecture, pas uniquement vérification de signature.
    with Image.open(io.BytesIO(result)) as check:check.load();assert check.size==(24,24)
    return result

def build(kind):
    n='LostWoodFloor' if kind=='floor' else 'LostWoodWall'
    original=(GAME/'Content/Tile'/f'{n}.tile').read_bytes()
    ts,count=struct.unpack_from('<ii',original);assert ts==24
    positions={}
    for i in range(count):
        x,y,pos=struct.unpack_from('<iiq',original,8+i*16);positions[(x,y)]=pos
    dest=bytearray(original)
    doc=json.loads((ORIGINAL_DEFINITIONS/f'lost_wood_{kind}.json').read_text(encoding='utf-8-sig'))
    definitions=doc['Object']['Tiles'];atlas=Image.new('RGBA',(192,(max(y for x,y in positions)+1)*24),(0,0,0,0)); used=set(); info=[]
    for key,variants in definitions.items():
        if not key.startswith('Tilex'):continue
        code=int(key[5:],16)
        for index,variant in enumerate(variants):
            assert len(variant)==1 and len(variant[0]['Frames'])==1
            frame=variant[0]['Frames'][0];assert frame['Sheet']==n
            loc=frame['TexLoc'];xy=(loc['X'],loc['Y']);assert xy in positions and xy not in used
            used.add(xy);pos=positions[xy];length=struct.unpack_from('<q',original,pos)[0]
            im=ground_variant(index) if kind=='floor' else wall_variant(code,index)
            png=pad_png_to(png_bytes(im),length)
            dest[pos+8:pos+8+length]=png
            with Image.open(io.BytesIO(png)) as decoded:atlas.paste(decoded.convert('RGBA'),(xy[0]*24,xy[1]*24))
            info.append({'case':key,'variante':index,'x':xy[0],'y':xy[1]})
    assert used==set(positions) and len(info)==count
    assert bytes(dest[:8+count*16])==original[:8+count*16]
    assert len(dest)==len(original)
    (OUT/f'{n}.tile').write_bytes(dest)
    atlas.save(OUT/f'{n}_24.png')
    (OUT/f'{n}_correspondance.json').write_text(json.dumps(info,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(kind,count,'cas',len([k for k in definitions if k.startswith('Tilex')]),'taille',len(dest),'index préservé')

if __name__=='__main__':
    build('floor');build('wall')
