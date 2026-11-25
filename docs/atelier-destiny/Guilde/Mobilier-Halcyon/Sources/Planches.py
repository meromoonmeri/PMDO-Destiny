#!/usr/bin/env python3
"""Planche de comparaison des teintes et présentoir d'ensemble, en pixels nets."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from io import BytesIO
import base64,json

S=Path(__file__).resolve().parent
O=S.parent
SHOW=['banquet','comptoir-cloche','coffre-haut','bureau-rouleau','maitre','banniere','plante-haute','banc-metano','lit-paille','missions']
DEMO=['coffre-haut','plante-haute','banquet','nappe-sol','tonneau']
C={'fond':'#151d19','head':'#232b21','clair':'#fff2d9','pale':'#d0c3a9','accent':'#eecc8e','bord':'#465145','stage':'#2d362c','badge':'#3d3b2c'}
FONT=Path('/usr/share/fonts/truetype/dejavu')

def font(size,face='sans'):
    file={'sans':'DejaVuSans.ttf','serif':'DejaVuSerif.ttf','mono':'DejaVuSansMono.ttf','bold':'DejaVuSans-Bold.ttf'}[face]
    return ImageFont.truetype(str(FONT/file),size)

def pix(im, w, h, max_scale=2):
    f=min(max_scale,w/im.width,h/im.height)
    return im.resize((max(1,round(im.width*f)),max(1,round(im.height*f))),Image.Resampling.NEAREST)

def read(p):return json.loads(p.read_text(encoding='utf-8'))

def plateau(planche,index,wood):
    keys=index['palettes'];models={a['id']:a for a in index['models']};mut={(m['modele'],m['palette']):m for m in index['variantes']}
    w0,h0=1840,1490;image=Image.new('RGB',(w0,h0),C['fond']);g=ImageDraw.Draw(image)
    g.rounded_rectangle((28,25,w0-29,207),radius=10,fill=C['head'],outline=C['bord'],width=2)
    g.text((53,47),'D E S T I N Y    /    A T E L I E R  H A L C Y O N',font=font(17,'mono'),fill=C['accent'])
    g.text((49,69),'Le meuble, en dix teintes.',font=font(59,'serif'),fill=C['clair'])
    g.text((53,149),'490 variantes · 49 modèles · couleurs testées sur le parquet de Destiny',font=font(21),fill=C['pale'])
    g.text((53,176),'Guilde de Halcyon : 420 variantes   /   Auberge de Metano : 70 variantes',font=font(16),fill=C['pale'])
    # Cartouche de comparaison avant/après, avec le grand tapis sur le bois du Réfectoire.
    for k,(p,label) in enumerate([('source','ORIGINAL'),('lierre','LIERRE'),('minuit','MINUIT')]):
        x=1295+k*171
        g.rounded_rectangle((x,43,x+157,182),radius=6,fill='#151a16',outline=C['bord'])
        bg=wood.crop((12+k*24,7,165+k*24,113));image.paste(bg,(x+2,45))
        ref=models['maitre'];a=Path(ref['source_png']) if p=='source' else Path(mut[('maitre',p)]['png']);im=pix(Image.open(O/a),115,94)
        image.paste(im,(x+79-im.width//2,98-im.height//2),im)
        g.text((x+79,163),label,anchor='mm',font=font(13,'mono'),fill=C['pale'])
    x0,y0=226,226; cw,ch,gap=154,101,6
    g.text((39,251),'DIX NUANCIERS',font=font(17,'mono'),fill=C['accent'])
    g.text((39,279),'Bois · textile · métal',font=font(14),fill=C['pale'])
    for i,p in enumerate(keys):
        x=x0+i*(cw+gap)
        g.rounded_rectangle((x,y0,x+cw,y0+70),radius=5,fill=C['stage'],outline=C['bord'])
        g.text((x+12,y0+9),str(i+1).zfill(2),font=font(12,'mono'),fill='#bfad85')
        g.text((x+12,y0+25),p['nom'],font=font(21,'serif'),fill=C['clair'])
        for j,k in enumerate(('bois','tissu','metal')):
            g.rectangle((x+12+j*44,y0+57,x+50+j*44,y0+62),fill='#'+p[k][3])
    for j,key in enumerate(SHOW):
        m=models[key];y=308+j*(ch+7)
        g.rounded_rectangle((29,y,217,y+ch),radius=6,fill='#242c23',outline=C['bord'])
        words=m['nom'].split();rows=['']
        for word in words:
            value=(rows[-1]+' '+word).strip()
            if g.textlength(value,font=font(17,'bold'))>169 and rows[-1]:rows.append(word)
            else:rows[-1]=value
        g.multiline_text((40,y+15),'\n'.join(rows),font=font(17,'bold'),fill=C['clair'],spacing=3)
        source='Metano' if m['origine']=='metano' else 'Guilde'
        g.text((40,y+ch-24),f'{m["rect"][2]} × {m["rect"][3]} px  /  {source}',font=font(12,'mono'),fill=C['pale'])
        uno=wood.crop((36,11,36+cw-3,11+ch-3))
        if j%2:uno=ImageEnhance.Brightness(uno).enhance(.93)
        for i,p in enumerate(keys):
            x=x0+i*(cw+gap);g.rectangle((x,y,x+cw,y+ch),fill='#5c543e')
            image.paste(uno,(x+2,y+2))
            spr=Image.open(O/mut[(key,p['id'])]['png']);a=pix(spr,cw-14,ch-13)
            image.paste(a,(x+(cw-a.width)//2,y+(ch-a.height)//2),a)
    g.line((29,1400,w0-30,1400),fill=C['bord'],width=2)
    g.text((35,1416),'DÉTAILS 1× ET INDEX DE PROVENANCE DANS LE KIT',font=font(16,'mono'),fill=C['accent'])
    g.text((35,1444),'Silhouettes et décors : Halcyon de Palika · D4yz et Edan Momu crédités au dépôt. Recoloration par matière, alpha d’origine conservé.',font=font(17),fill=C['pale'])
    image.save(planche,optimize=True)

def main():
    index=read(O/'Index.json');text=(O.parent/'Guilde-Destiny-Mobilier-Halcyon.html').read_text(encoding='utf-8');j=json.loads(text.split('<script id="donnees" type="application/json">',1)[1].split('</script>',1)[0]);base=Image.open(BytesIO(base64.b64decode(j['halcyon']['bois']))).convert('RGB');base=Image.blend(base,Image.new('RGB',base.size,'#423623'),.24)
    plateau(O/'Planche-10-Palettes.png',index,base)
    print('Planche comparée : 10 modèles × 10 palettes')

if __name__=='__main__':main()
