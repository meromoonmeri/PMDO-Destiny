#!/usr/bin/env python3
"""Assemble la galerie hors ligne et la planche PNG depuis les dessins natifs."""
from base64 import b64encode
from html import escape
from pathlib import Path
import argparse, json
from PIL import Image, ImageDraw, ImageFont

HERE=Path(__file__).resolve().parent


def uri(f):return 'data:image/png;base64,'+b64encode(f.read_bytes()).decode('ascii')


def title(r):return r['pokemon'] or r['nom']


def html(a,rows):
    small=a.gen/'Dessins/Glyphe';ground=a.gen/'Dessins/Objet'
    page=(HERE/'modele-galerie.html').read_text(encoding='utf-8');cards=[]
    for r in rows:
        id=r['id'];f=id+'.png'; label=title(r); motif=r['motif'];tags='baie' if r['genre']=='baie' else 'mega'
        if id.endswith(('_x','_y')):tags+=' xy';flag=f'<b class="form">{id[-1].upper()}</b>'
        elif r['genre']=='delta':flag='<b class="form">Δ</b>'
        else:flag=''
        sub=r['nom'] if r['pokemon'] else 'Baie de Réverie'
        number=f'N°{r["dex"]:03}' if 'dex' in r else 'BAIE'
        with Image.open(ground/f) as im:w,h=im.size
        words=' '.join(map(str,[label,r['nom'],id,r.get('dex',''),number,motif,r.get('espece','')]))
        cards.append(f'''<article class="card" data-cat="{tags}" data-words="{escape(words,quote=True)}" style="--pigment:{r['palette'][0]}">
<div class="art"><span class="index">{number}</span>{flag}<img class="small" src="{uri(small/f)}" alt="Émoticône : {escape(label)}" width="11" height="11" style="height:auto" loading="lazy"><img class="ground" src="{uri(ground/f)}" alt="Sprite : {escape(label)}" width="{w}" height="{h}" style="height:auto" loading="lazy"></div>
<div class="caption"><h3>{escape(label)}</h3><p>{escape(sub)}</p></div>
<details><summary>Description FR</summary><p class="description">{escape(r['description_fr'])}</p><p>{escape(motif)}<br><code>{escape(id)} · {r['code']}</code></p></details></article>''')
    proof=[(a.captures/'ensemble-fr/Description-Dracaufeu-X.png','Sac · Dracaufeu X','La description précise la forme X en français.'),
           (a.captures/'ensemble-fr/Description-Mewtwo-Y.png','Sac · Mewtwo Y','La forme Y est indiquée dans le texte et par l’icône rose.'),
           (a.captures/'foyer-fr/Recompense-Pecha.png','Dialogue · Baie Pêcha','La récompense réelle du script de Réverie, sans l’addon Méga.')]
    figures=[f'<figure><img width="640" height="480" src="{uri(f)}" alt="{escape(t)}" loading="lazy"><figcaption><strong>{escape(t)}</strong><br>{escape(c)}</figcaption></figure>' for f,t,c in proof]
    parts={'X':uri(ground/'mega_charizardite_x.png'),'Y':uri(ground/'mega_charizardite_y.png'),'CARTES':'\n'.join(cards),'CAPTURES':'\n'.join(figures)}
    for k,v in parts.items():page=page.replace('@@'+k+'@@',v)
    assert '@@' not in page and page.count('class="card"')==54
    (a.out/'Les-gemmes-de-Reverie.html').write_text(page,encoding='utf-8')


def png(a,rows):
    W,H=1312,1532
    im=Image.new('RGB',(W,H),'#101720');d=ImageDraw.Draw(im)
    fonts=Path(a.fonts)
    def font(n,b=False,mono=False):
        nm='DejaVuSansMono' if mono else 'DejaVuSans';nm+=('-Bold' if b else '')+'.ttf'
        return ImageFont.truetype(str(fonts/nm),n)
    f21=font(21,True);f18=font(18);f14=font(14,mono=True);warm='#f5d4a2';muted='#adbacb';txt='#f8f2e8'
    d.rectangle((0,0,W,8),fill=warm)
    d.text((34,32),'D E S T I N Y    /    R É V E R I E',fill=warm,font=f14)
    d.text((32,54),'Les gemmes de Réverie',fill=txt,font=font(49,True))
    d.text((34,123),'48 objets Méga · 46 Pokémon · 6 baies   /   Émoticônes 11 × 11 px, ici agrandies ×6',font=f18,fill=muted)
    d.line((34,168,W-34,168),fill='#34475c',width=1)
    for j,r in enumerate(rows):
        is_berry=r['genre']=='baie';pos=j if not is_berry else j-48
        x,y=34+(pos%8)*156,190+(pos//8)*171 if not is_berry else 1326
        d.rounded_rectangle((x,y,x+147,y+155),9,fill='#182331',outline='#2b3b4d',width=1)
        d.rounded_rectangle((x+4,y+4,x+143,y+105),6,fill='#111a27')
        t=r.get('dex');d.text((x+10,y+9),'BAIE' if t is None else f'#{t:03}',font=f14,fill=muted)
        g=Image.open(a.gen/'Dessins/Glyphe'/(r['id']+'.png')).convert('RGBA').resize((66,66),Image.Resampling.NEAREST)
        im.paste(g,(x+41,y+30),g)
        name=title(r);ff=f18 if d.textlength(name,font=f21)>141 else f21
        d.text((x+73,y+116),name,anchor='mt',font=ff,fill=txt)
        if r['genre']=='delta':label='Météorite Delta'
        elif not is_berry:label=r['nom']
        else:label=f'Icon {r["ico"]}'
        d.text((x+73,y+138),label,anchor='mt',font=font(12),fill=muted)
    d.text((34,1284),'BAIES DE RÉVERIE   /   SANS ADDON MÉGA',font=f14,fill=warm)
    d.line((34,1309,W-34,1309),fill='#34475c',width=1)
    d.text((34,1501),'PMDO 0.8.12  ·  Émoticône = sac et dialogues    /    Sprite = objet posé au sol',font=f14,fill=muted)
    im.save(a.out/'Planche-54-icones.png',optimize=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--gen',required=True,type=Path);p.add_argument('--captures',required=True,type=Path)
    p.add_argument('--out',required=True,type=Path);p.add_argument('--fonts',default='/usr/share/fonts/truetype/dejavu')
    a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);rows=json.loads((a.gen/'Registre-icones.json').read_text())['items']
    png(a,rows);html(a,rows)
    print('Planche PNG et galerie HTML autonome (54 objets, 3 captures réelles).')
