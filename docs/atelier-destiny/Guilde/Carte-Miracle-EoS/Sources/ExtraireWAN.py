"""Decode EoS static OBJ-atlas WANs `s01p01a1/2`, preserving the pose's anchor."""
from pathlib import Path
from struct import unpack_from
from PIL import Image, ImageOps
import argparse, json, re

def decode(wan):
    b = Path(wan).read_bytes()
    U = lambda at, n=1: unpack_from(f'<{n}I', b, at)
    H = lambda at, n=1: unpack_from(f'<{n}H', b, at)
    assert b[:4] == b'SIR0'
    header, = U(4)
    anim, image = U(header, 2)
    assert H(header + 8) == (0,)
    frame_table, offsets, group_table = U(anim, 3)
    assert offsets == 0 and H(anim + 12) == (1,)
    seq_table, = U(group_table)
    assert seq_table > frame_table and (seq_table-frame_table)%4 == 0
    seq_count, = H(group_table+4)
    image_table, palette_info = U(image, 2)
    assert H(image+10) == (0,)
    colors_at, = U(palette_info)
    ncolors, = H(palette_info+6)
    assert ncolors == 16
    palette = [(0,0,0,0)] + [tuple(b[colors_at + i*4:colors_at + i*4+3])+(255,) for i in range(1,16)]
    atlas = {}
    tile_num = 0
    for p in U(image_table,H(image+14)[0]):
        raw = bytearray()
        while True:
            adr,length,_,_ = unpack_from('<IHHI',b,p)
            p += 12
            if not (adr or length): break
            raw.extend(b[adr:adr+length] if adr else bytes(length))
        atlas[tile_num] = raw
        tile_num += max(1,(len(raw)+127)//128)
    dimensions = [(8,8),(16,16),(32,32),(64,64),(16,8),(32,8),(32,16),(64,32),(8,16),(8,32),(16,32),(32,64)]
    frames = []
    for p in U(frame_table, (seq_table-frame_table)//4):
        chunks = []
        while True:
            index,_,y,x,tile = unpack_from('<h4H', b, p)
            p += 10
            assert index == -1 and not (y & 0x0c00) and not (tile & 0xf000)
            ww,hh = dimensions[(y>>14)*4+(x>>14)]
            data = atlas[tile&1023]
            assert len(data)*2 == ww*hh
            pixels = [p for byte in data for p in (byte&15, byte>>4)]
            out = Image.new('RGBA',(ww,hh))
            out.putdata([palette[pixels[((j//8)*(ww//8)+(i//8))*64+(j%8)*8+i%8]] for j in range(hh) for i in range(ww)])
            if x&0x1000: out=ImageOps.mirror(out)
            if x&0x2000: out=ImageOps.flip(out)
            chunks.append(((x&511)-256,(y&1023)-512,out))
            if x&0x800: break
        left=min(x for x,y,o in chunks); top=min(y for x,y,o in chunks)
        right=max(x+o.width for x,y,o in chunks); down=max(y+o.height for x,y,o in chunks)
        out=Image.new('RGBA',(right-left,down-top))
        for x,y,o in reversed(chunks): out.alpha_composite(o,(x-left,y-top))
        l,t,r,d=out.getbbox(alpha_only=True) or (0,0,1,1)
        frames.append((out.crop((l,t,r,d)), (left+l,top+t)))
    sequences=[]
    for p in U(seq_table,seq_count):
        seq=[]
        while b[p]:
            ticks,flag,f,x,y,_,_=unpack_from('<BBHhhhh',b,p)
            seq.append({'pose':f,'ticks':ticks,'offset':[x,y], 'flags':flag}); p+=12
        sequences.append(seq)
    return frames,sequences

def transitions(data):
    text=Path(data).read_text()
    def blob(start,end):
        src=text.split(start+':',1)[1].split('.global '+end,1)[0]
        return bytes(int(h,16) for h in re.findall(r'0x([0-9a-fA-F]{2})\b',src))
    def arr(start,end):
        x=blob(start,end)
        assert len(x)%24==0
        return [unpack_from('<6i',x,i) for i in range(0,len(x),24)]
    big=arr('ov11_023233E8','ov11_02323490');small=arr('ov11_02323490','ov11_02323730')
    counts=blob('ov11_02323374','ov11_0232337C')[:7]
    assert len(big)==7 and len(small)==sum(counts)
    def tr(x):
        a,b,u,v,t,n=x
        assert t==240 and (n&~0xff)==0x800
        return {'origine':[a,b],'vitesse_8_8':[u,v],'ticks':t,'sequence':n&255,'flags':hex(n)}
    off=0; all=[]
    for level,(main,count) in enumerate(zip(big,counts),2):
        all.append({'palier':level,'banc':tr(main),'petits_nuages':list(map(tr,small[off:off+count]))});off+=count
    return all

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('wan',type=Path);p.add_argument('table',type=Path);p.add_argument('sortie',type=Path);ns=p.parse_args();ns.sortie.mkdir(parents=True,exist_ok=True)
    frames,seq=decode(ns.wan); seq=seq[:9]; used=sorted({f['pose'] for a in seq for f in a}); meta={}
    for i in used:
        o,origin=frames[i];fn=f'Pose-{i:02}.png';o.save(ns.sortie/fn)
        meta[str(i)]={'fichier':fn,'coin_relatif':list(origin),'taille':list(o.size)}
    spec={'taille_carte':[504,336],'taille_ecran_ds':[256,192], 'attente_ticks':30,'transitions':transitions(ns.table),'sequences':seq,'poses':meta}
    (ns.sortie/'Trajectoires.json').write_text(json.dumps(spec,indent=2,ensure_ascii=False)+'\n')
