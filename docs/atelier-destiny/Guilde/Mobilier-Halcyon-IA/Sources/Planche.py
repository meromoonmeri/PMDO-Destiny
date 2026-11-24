#!/usr/bin/env python3
"""Présente les trois dessins retenus, leurs sprites 1× et leurs teintes dérivées."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from io import BytesIO
import json,base64
O=Path(__file__).resolve().parents[1];G=O.parent
j=json.loads((O/'Index.json').read_text());vs={(v['modele'],v['palette']):v for v in j['variantes']};ps=j['palettes'];stems=j['modeles']
P=G/'Guilde-Destiny-Mobilier-Halcyon-IA.html';d=json.loads(P.read_text().split('<script id="donnees" type="application/json">')[1].split('</script>',1)[0]);wood=Image.open(BytesIO(base64.b64decode(d['halcyon']['bois']))).convert('RGB')

def font(px,f='serif'):
    return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/'+{'serif':'DejaVuSerif.ttf','sans':'DejaVuSans.ttf','mono':'DejaVuSansMono.ttf'}[f],px)

def scale(im,w,h,method=Image.Resampling.NEAREST):
    s=min(w/im.width,h/im.height);return im.resize((round(im.width*s),round(im.height*s)),method)

def compose(bg,sprite,box,method=Image.Resampling.NEAREST):
    x,y,w,h=box;m=scale(sprite,w,h,method);bg.paste(m,(x+(w-m.width)//2,y+(h-m.height)//2),m)

def fond(w,h):
    return Image.blend(wood.resize((w,h),Image.Resampling.NEAREST),Image.new('RGB',(w,h),'#2f281b'),.28)

W,H=1510,890;back=Image.new('RGB',(W,H),'#17201b');g=ImageDraw.Draw(back)
g.text((27,21),'D E S T I N Y    /    É D I T I O N   H A L C Y O N   I A',font=font(16,'mono'),fill='#e9c78d')
g.text((24,45),'Les trois créations retenues',font=font(59),fill='#fff0d6')
g.text((28,119),'Trois images générées à partir des sprites de Halcyon • Détourage transparent et déclinaisons Destiny',font=font(19,'sans'),fill='#d2c3a5')
for i,m in enumerate(stems):
    x=27+i*490;y=169;c=473
    q=vs[(m['id'],m['palette'])];a=Image.open(O/q['png']);p=next(k for k in ps if k['id']==m['palette']);hd=Image.open(O/m['hd']);
    g.rounded_rectangle((x,y,x+c,y+452),radius=9,fill='#252d24',outline='#505645',width=2)
    g.text((x+14,y+13),f'{i+1:02}   /   {p["nom"].upper()}',font=font(14,'mono'),fill='#efd09b')
    g.text((x+13,y+37),m['titre'],font=font(29),fill='#fff1d3')
    back.paste(fond(c-25,292),(x+12,y+81));compose(back,hd,(x+27,y+93,c-55,266),Image.Resampling.LANCZOS)
    g.rectangle((x+12,y+81,x+c-13,y+373),outline='#a47648',width=1)
    g.text((x+14,y+390),'IMAGE GÉNÉRÉE · DÉTOURÉE',font=font(13,'mono'),fill='#ead4a5')
    g.text((x+14,y+415),f'Sprite adapté : {a.width} × {a.height} px',font=font(14,'sans'),fill='#d3c6a9')
    for k,key in enumerate(('bois','tissu','metal')):g.rounded_rectangle((x+c-106+29*k,y+415,x+c-84+29*k,y+430),radius=2,fill='#'+p[key][3])
    g.text((x+1,641),'Aperçu des teintes sur le sprite 1×',font=font(16,'sans'),fill='#ead4ac')
    for k,t in enumerate(ps):
        im=Image.open(O/vs[(m['id'],t['id'])]['png']);u=x+(k%5)*95;v=672+k//5*72
        g.rounded_rectangle((u,v,u+90,v+66),radius=5,fill='#2d352b',outline=('#ebc88d' if t['id']==m['palette'] else '#4f5b49'))
        compose(back,im,(u+4,v+3,83,43));g.text((u+45,v+54),t['nom'],anchor='mm',font=font(11,'sans'),fill='#f4e7ca')
g.line((26,835,W-26,835),fill='#58604b',width=2)
g.text((27,849),'3 générations sélectionnées   ·   27 variations de couleur dérivées   ·   Sans modification du jeu',font=font(17,'sans'),fill='#ddd0b1')
back.save(O/'Planche-Creations-IA.png',optimize=True)
print('Comparatif des créations IA et des teintes fini')
