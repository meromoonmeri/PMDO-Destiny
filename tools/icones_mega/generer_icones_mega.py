#!/usr/bin/env python3
"""48 pierres personnalisées + 6 liaisons de baies. PMDO 0.8.12.
Item.Sprite = DirSheet au sol, Item.Icon et index = glyphe de police en menu.
Aucun changement de mécanique, de forme, de nom ou de disponibilité.
Les six descriptions vides de baies indiquent l'effet déjà présent.
"""
from __future__ import annotations
import argparse
from copy import deepcopy
from dataclasses import dataclass
from hashlib import sha256
import io
import json
import math
from pathlib import Path
import re
import struct
import subprocess as sp

from PIL import Image, ImageDraw
import numpy as np

HERE=Path(__file__).resolve().parent
PUA=0xe340
BASE_ICON=0xe0a0
FONT_NAMES=('text.font','text.zh-hans.font')
BERRIES=(('aspear','Willia'),('cheri','Ceriz'),('chesto','Maron'),('pecha','Pêcha'),('persim','Kika'),('rawst','Fraive'))
POLY={
    'ronde':[(3,2),(10,2),(12,4),(12,9),(10,12),(3,12),(1,9),(1,5)],
    'prisme':[(4,1),(9,1),(12,4),(12,9),(9,12),(6,13),(2,10),(1,6),(2,3)],
    'lance':[(6,1),(8,1),(12,4),(13,7),(10,11),(7,13),(3,10),(1,6),(3,3)],
    'écu':[(3,2),(10,2),(12,4),(12,8),(10,11),(7,13),(4,12),(2,9),(1,6)],
    'delta':[(6,1),(8,1),(12,6),(13,9),(11,12),(3,12),(1,9),(2,6)],
}


@dataclass(frozen=True)
class Model:
    slot:int
    id:str
    dex:int
    species:str
    fr:str
    form:int
    silhouette:str
    base:str
    trim:str
    mark:str
    motif:str
    mask:tuple[str,...]


def models(file):
    seen=set()
    for ln in file.read_text(encoding='utf-8').splitlines():
        if not ln.strip() or ln.startswith('#'):continue
        i,key,dex,spc,fr,form,sh,p,q,c,label,drawing=ln.split('|')
        pixels=tuple(x.strip() for x in drawing.split('/'))
        assert len(pixels)==5 and all(re.fullmatch(r'[.+#o]{5}',x) for x in pixels),ln
        assert key not in seen and sh in POLY;seen.add(key)
        yield Model(int(i),'mega_'+key,int(dex),spc,fr,int(form),sh,p,q,c,label,pixels)


def color(raw):return tuple(bytes.fromhex(raw))
def mix(a,b,t):return tuple(round((1-t)*x+t*y) for x,y in zip(a,b))
def png(im):
    b=io.BytesIO();im.save(b,format='PNG',compress_level=6);return b.getvalue()
def put(f,raw):f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(raw)
def rgba(c):return (*c,255)
def sha(raw):return sha256(raw).hexdigest()
def jsonb(b):return json.loads(b.decode('utf-8-sig'))


def draw_gem(m,n):
    """Le relief du cabochon, sa taille (forme de coupe) et sa gravure sont distincts.
    On dessine directement aux deux tailles natives, sans rétrécir la gravure.
    """
    assert n in (11,14)
    p,q,g=[color(x) for x in (m.base,m.trim,m.mark)]
    black=(29,26,44); slate=(63,53,78); pearl=(249,244,229)
    rim0=mix(p,black,.72); rim1=mix(q,slate,.40)
    light=mix(q,pearl,.43); dark=mix(p,black,.39); spark=mix(q,pearl,.69)
    im=Image.new('RGBA',(n,n));s=Image.new('1',(n,n));d=ImageDraw.Draw(s)
    pts=[(round(x*(n-1)/13),round(y*(n-1)/13)) for x,y in POLY[m.silhouette]]
    d.polygon(pts,fill=1); a=np.asarray(s,dtype=bool); f=im.load()
    def inside(x,y):return 0<=x<n and 0<=y<n and a[y,x]
    unit=n/14
    for y in range(n):
        for x in range(n):
            if not inside(x,y):continue
            neigh=[inside(x-1,y),inside(x+1,y),inside(x,y-1),inside(x,y+1)]
            # Contour sombre : lisibilité sur sol clair et menu PMD sombre.
            if not all(neigh):
                col=rim0 if x+y>6*unit else mix(rim0,rim1,.2)
            elif x+y < 7.6*unit:
                col=light
            elif (x-y>2.9*unit and y<9.3*unit) or (x-y<-3.8*unit and y>6.9*unit):
                col=mix(q,p,.59) if x+y<14*unit else mix(q,rim0,.44)
            elif x+y > 19*unit:
                col=dark
            elif (x+y)>15.0*unit:
                col=mix(p,q,.37) if m.silhouette in ('ronde','lance') else mix(p,black,.28)
            else:
                col=mix(p,q,.17)
            f[x,y]=rgba(col)
    # Gravure incrustée en 5x5 : les + suivent la couleur de veine, les o le reflet.
    x0=(n-5)//2+int(n==14);y0=(n-5)//2+int(n==14)
    bright=sum(g)>390
    brightside=mix(g,pearl,.17) if bright else mix(g,black,.17)
    inks={'#':brightside,'+':mix(g,q,.40),'o':mix(q,pearl,.54) if not bright else mix(q,black,.30)}
    rendered=0
    for y,row in enumerate(m.mask):
        for x,c in enumerate(row):
            xx,yy=x+x0,y+y0
            if c in inks and inside(xx,yy):f[xx,yy]=rgba(inks[c]);rendered+=1
    assert rendered>=sum(c!='.' for r in m.mask for c in r)-1,(m.id,n,rendered)
    # Petits reflets blancs hors gravure, plus un retour de couleur sur la tranche.
    for xp,yp,is_spark in ((.31,.22,True),(.24,.30,False),(.73,.77,False)):
        x,y=round(xp*(n-1)),round(yp*(n-1))
        if not ((x0<=x<x0+5) and (y0<=y<y0+5)) and all(inside(x+dx,y+dy) for dx,dy in ((0,0),(1,0),(-1,0),(0,1),(0,-1))):
            f[x,y]=rgba(spark if is_spark else light)
    return im


def premult(im):
    a=np.array(im.convert('RGBA'))
    a[...,:3]=((a[...,:3].astype('uint16')*a[...,3:4]+127)//255).astype('uint8')
    return Image.fromarray(a)


def unpremult(im):
    a=np.array(im.convert('RGBA'));alpha=a[...,3:4].astype('uint32');colors=a[...,:3].astype('uint32')
    a[...,:3]=np.clip((colors*255+alpha//2)//np.maximum(1,alpha),0,255).astype('uint8')
    return Image.fromarray(a)


def dirsheet(im):
    w,h=im.size;raw=png(premult(im));return struct.pack('<q',len(raw))+raw+struct.pack('<4i',w,h,0,1)


def read_dir(data):
    n,=struct.unpack_from('<q',data);assert 0<n and n+24==len(data)
    w,h,rot,frames=struct.unpack_from('<4i',data,8+n);assert rot==0 and frames==1
    im=Image.open(io.BytesIO(data[8:8+n])).convert('RGBA');assert im.size==(w,h)
    return unpremult(im)


def berry_glyph(sprite):
    mini=sprite.crop(sprite.getchannel('A').getbbox())
    mini.thumbnail((10,10),Image.Resampling.NEAREST)
    c=Image.new('RGBA',(11,11));c.paste(mini,((11-mini.width)//2,(11-mini.height)//2))
    return c


def parts_font(data):
    n,=struct.unpack_from('<q',data); im=Image.open(io.BytesIO(data[8:n+8])).convert('RGBA')
    total,=struct.unpack_from('<i',data,n+8);start=n+12;end=start+total*16
    rect=data[start:end];m=data[end:end+16];c=data[end+16:]
    assert len(rect)==total*16 and len(c)==total*9 and len(m)==16
    entries={r[0]:r[1:] for r in struct.iter_unpack('<ii?',c)}
    assert len(entries)==total and all(0<=x[0]<total for x in entries.values())
    return im,total,rect,m,c,entries


def extend_font(data,extra):
    im,n,r,m,c,cmap=parts_font(data)
    assert set(extra).isdisjoint(cmap) and all(0xe000<code<=0xf8ff for code in extra)
    assert struct.unpack_from('<4i',m)[1]>=11
    step=13;col=min(im.width//step,64);lines=math.ceil(len(extra)/col)
    result=Image.new('RGBA',(im.width,im.height+lines*step));result.paste(im,(0,0))
    tail_r,tail_c=[],[]
    for i,(code,img) in enumerate(sorted(extra.items())):
        assert img.size==(11,11)
        x,y=i%col*step+1,im.height+i//col*step+1
        result.paste(premult(img),(x,y))
        tail_r.append(struct.pack('<4i',x,y,11,11));tail_c.append(struct.pack('<ii?',code,n+i,True))
    p=png(result);out=struct.pack('<q',len(p))+p+struct.pack('<i',n+len(extra))+r+b''.join(tail_r)+m+c+b''.join(tail_c)
    im2,v,r2,m2,c2,cmap2=parts_font(out)
    assert v==n+len(extra) and m2==m and r2.startswith(r) and c2.startswith(c)
    assert im2.crop((0,0,*im.size)).tobytes()==im.tobytes()
    for cp,img in extra.items():
        no,flag=cmap2[cp];x,y,w,h=struct.unpack_from('<4i',r2,16*no)
        assert flag and (w,h)==(11,11) and im2.crop((x,y,x+w,y+h)).tobytes()==premult(img).tobytes()
    return out,dict(avant=n,apres=v,sha256_source=sha(data),sha256_fusion=sha(out))


def patch_item(data,sprite,slot,berry=False):
    old=jsonb(data);expect=deepcopy(old);expect['Object'].update(Sprite=sprite,Icon=slot)
    text=data.decode('utf-8-sig')
    text,n=re.subn(r'("Sprite"\s*:\s*)"[^"\n]*"',lambda mm:mm[1]+json.dumps(sprite),text,count=1);assert n==1
    text,n=re.subn(r'("Icon"\s*:\s*)-?\d+',lambda mm:mm[1]+str(slot),text,count=1);assert n==1
    if berry:
        ev=[v['Value'] for v in old['Object']['UseEvent']['OnHits']]
        assert len(ev)==1 and ev[0]['$type']=='PMDC.Dungeon.RestoreBellyEvent, PMDC' and ev[0]['Heal']==3
        assert old['Object']['Desc']=={'DefaultText':'','LocalTexts':{}}
        desc={'DefaultText':'Restores 3 Belly.','LocalTexts':{'fr':'Restaure 3 points de satiété.'}}
        expect['Object']['Desc']=desc
        text,n=re.subn(r'("Desc"\s*:\s*)\{\s*"DefaultText"\s*:\s*""\s*,\s*"LocalTexts"\s*:\s*\{\}\s*\}',
                       lambda mm:mm[1]+json.dumps(desc,ensure_ascii=False),text,count=1);assert n==1
    result=(b'\xef\xbb\xbf' if data.startswith(b'\xef\xbb\xbf') else b'')+text.encode()
    assert jsonb(result)==expect
    return result


def mega_index(data,icons):
    source=jsonb(data); expect=deepcopy(source);text=data.decode('utf-8-sig')
    assert set(expect['Object'])-{'$type'}==set(icons)
    for key,slot in icons.items():
        expect['Object'][key]['Icon']=slot
        regex='("'+re.escape(key)+'"'+r'\s*:\s*\{\s*"\$type"\s*:\s*"[^\"]*"\s*,\s*"Icon"\s*:\s*)-?\d+'
        text,n=re.subn(regex,lambda mm:mm[1]+str(slot),text,count=1);assert n==1,key
    out=(b'\xef\xbb\xbf' if data.startswith(b'\xef\xbb\xbf') else b'')+text.encode()
    assert jsonb(out)==expect
    return out


def json_text(data,bom=False,indent=2):return (b'\xef\xbb\xbf' if bom else b'')+(json.dumps(data,ensure_ascii=False,indent=indent)+'\n').encode()


def build(dst,base,out,reference,tsv,catalogue):
    stock_index=jsonb((base/'Data/Item/index.idx').read_bytes())['Object']
    addon=dst/'addons/Mega_Stones_Reverie';staged=out/'AddOn';game=out/'Destiny'
    meta={r['id']:r for r in json.loads(catalogue.read_text(encoding='utf-8'))}
    theme=list(models(tsv));assert len(theme)==48 and [a.slot for a in theme]==list(range(48))
    assert all(a.id in meta and (a.dex,a.species,a.form)==(meta[a.id]['dex'],meta[a.id]['espece'],meta[a.id]['forme']) for a in theme)
    def local(rel):
        p=dst/rel
        if p.is_file():return p.read_bytes()
        if reference and (reference/rel).is_file():return (reference/rel).read_bytes()
        return sp.check_output(['git','-C',str(dst),'show','HEAD:'+rel])
    old_index=local('game/Data/Item/index.idx');gummi=jsonb(old_index)
    mega_keys={m.id for m in theme};berry_keys={'berry_'+a for a,_ in BERRIES}
    old_gummi={k:deepcopy(v) for k,v in gummi['Object'].items() if k not in berry_keys}
    gummi['Object']=deepcopy(old_gummi)
    icons={}; rows=[];fonts={}; glyphs={}
    reserved={p.get('Icon') for group in (stock_index,gummi['Object'],jsonb((addon/'Data/Item/index.idx').read_bytes())['Object'])
              for k,p in group.items() if isinstance(p,dict) and k not in mega_keys and k not in berry_keys}
    assert set(range(PUA-BASE_ICON,PUA-BASE_ICON+54)).isdisjoint(reserved)
    a_dir='Content/Item';a_item='Data/Item';extra=set()
    for m in theme:
        s=PUA+m.slot;slot=s-BASE_ICON;icons[m.id]=slot
        sprite='MegaStone_Meteorite_Delta' if m.species=='rayquaza' else 'MegaStone_'+m.species
        if m.species in ('charizard','mewtwo'):sprite+=('_X' if m.form==1 else '_Y')
        assert sprite not in extra;extra.add(sprite)
        small,large=draw_gem(m,11),draw_gem(m,14);glyphs[s]=small
        put(staged/a_dir/(sprite+'.dir'),dirsheet(large))
        native=(addon/a_item/(m.id+'.json')).read_bytes();put(staged/a_item/(m.id+'.json'),patch_item(native,sprite,slot))
        item=jsonb(native)['Object']
        row=dict(id=m.id,nom=item['Name']['DefaultText'],pokemon=m.fr,espece=m.species,forme=m.form,dex=m.dex,
                 ico=slot,code=f'U+{s:04X}',sprite=sprite,motif=m.motif,palette=['#'+m.base,'#'+m.trim,'#'+m.mark],
                 genre='delta' if m.species=='rayquaza' else 'mega',
                 sprite_sha256=sha((staged/a_dir/(sprite+'.dir')).read_bytes()))
        rows.append(row)
        put(out/'Dessins'/'Glyphe'/(m.id+'.png'),png(small));put(out/'Dessins'/'Objet'/(m.id+'.png'),png(large))
    put(staged/a_item/'index.idx',mega_index((addon/a_item/'index.idx').read_bytes(),icons))
    for j,(short,fr) in enumerate(BERRIES):
        key='berry_'+short;s=PUA+48+j;slot=s-BASE_ICON;sprite='Berry_'+short.title()
        bare=(base/a_item/(key+'.json')).read_bytes();b=jsonb(bare)['Object'];assert b['Sprite']=='' and b['Icon']==3 and b['Released']==False
        assert b['Name']['LocalTexts']['fr']=='Baie '+fr and key not in gummi['Object']
        art=local('game/Content/Item/'+sprite+'.dir');large=read_dir(art);small=berry_glyph(large);glyphs[s]=small
        put(game/a_dir/(sprite+'.dir'),art)
        put(game/a_item/(key+'.json'),patch_item(bare,sprite,slot,berry=True))
        index=deepcopy(stock_index[key]);index['Icon']=slot;gummi['Object'][key]=index
        rows.append(dict(id=key,nom='Baie '+fr,pokemon=None,ico=slot,code=f'U+{s:04X}',sprite=sprite,motif='Sprite Destiny déjà dessiné ; lien et glyphe ajoutés.',palette=['#e9aadd'],genre='baie',sprite_sha256=sha(art)))
        put(out/'Dessins'/'Glyphe'/(key+'.png'),png(small));put(out/'Dessins'/'Objet'/(key+'.png'),png(large))
    assert {k:val for k,val in gummi['Object'].items() if k not in berry_keys}==old_gummi
    put(game/a_item/'index.idx',json_text(gummi,bom=old_index.startswith(b'\xef\xbb\xbf'),indent=1))
    assert len({x.tobytes() for x in glyphs.values()})==54
    for font in FONT_NAMES:
        out_font,synth=extend_font((base/'Content/Font'/font).read_bytes(),glyphs)
        fonts[font]=synth
        for target in (staged,game):put(target/'Content/Font'/font,out_font)
    for row in rows:
        fiches=game if row['genre']=='baie' else staged
        desc=jsonb((fiches/a_item/(row['id']+'.json')).read_bytes())['Object']['Desc']
        row.update(description_fr=desc['LocalTexts'].get('fr'),description_par_defaut=desc['DefaultText'])
    alias=jsonb((base/'Editor/Aliases/Item_Icon.json').read_bytes());alias0=deepcopy(alias)
    alias.update({str(row['ico']):(row['nom'] if row['genre']=='baie' else row['nom']+' — '+row['pokemon']) for row in rows})
    assert len(alias)==len(alias0)+54 and all(alias[k]==v for k,v in alias0.items())
    put(out/'Editeur/Item_Icon.json',json_text(alias))
    put(out/'Registre-icones.json',json_text(dict(items=rows,polices=fonts,icon_base=BASE_ICON,glyph_debut=PUA)))
    print('47 Méga-Gemmes + Météorite Delta, 6 baies. 54 sprites uniques / 54 pictogrammes ; indices et deux polices vérifiés.',flush=True)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--destiny',type=Path,required=True);p.add_argument('--stock',type=Path,help='PMDO 0.8.12, par défaut <destiny>/base')
    p.add_argument('--reference',type=Path,help='Copie de fichiers manquants dans un checkout sparse')
    p.add_argument('--out',type=Path,required=True);p.add_argument('--modeles',type=Path,default=HERE/'Modeles-des-gemmes.tsv')
    p.add_argument('--catalogue',type=Path,default=HERE/'Catalogue-des-pierres.json')
    a=p.parse_args();build(a.destiny,a.stock or a.destiny/'base',a.out,a.reference,a.modeles,a.catalogue)


if __name__=='__main__':main()
