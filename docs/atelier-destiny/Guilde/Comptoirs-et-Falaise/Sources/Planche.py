#!/usr/bin/env python3
from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import base64,io,json
from Implantation import ROOT,base

FT='/usr/share/fonts/truetype/dejavu/'
serif=lambda n:ImageFont.truetype(FT+'DejaVuSerif.ttf',n)
mono=lambda n:ImageFont.truetype(FT+'DejaVuSansMono.ttf',n)
sans=lambda n:ImageFont.truetype(FT+'DejaVuSans.ttf',n)
heavy=lambda n:ImageFont.truetype(FT+'DejaVuSans-Bold.ttf',n)
cream='#f3dfb7';dim='#c3b29a';gold='#d8a565';line='#5e4d38'

def pix(im,n):return im.resize((round(im.width*n),round(im.height*n)),Image.Resampling.NEAREST)
def text(d,xy,s,f,c=cream,anchor=None):d.text(xy,s,font=f,fill=c,anchor=anchor)
def asset_png(b):return Image.open(io.BytesIO(base64.b64decode(b.split(',')[-1]))).convert('RGBA')
def frame(r,base_data,im,xy):
    v=Image.new('RGBA',(r['w'],r['h']),tuple(base_data['balade_nuit']['fonds'][r['id']]['rgb'][0])+(255,));v.alpha_composite(asset_png(r['base']));v.alpha_composite(im,tuple(xy));v.alpha_composite(asset_png(r['front']));box=v.getbbox();return v

def main():
    R=json.loads((ROOT/'Index-Comptoirs.json').read_text())['orientations']; photos=[]
    for v in R:photos.append(Image.open(ROOT/v['png']).convert('RGBA'))
    d0=base();situ=json.loads((ROOT/'Implantations.json').read_text())
    page=Image.new('RGB',(1472,1250),'#171d1d');dr=ImageDraw.Draw(page)
    text(dr,(47,40),'ATELIER DESTINY   ///   FICHE DE MOBILIER 01',mono(16),gold)
    text(dr,(42,65),'Le comptoir à cloche',serif(65));text(dr,(47,150),'Noyer · pierre mate · cloche en laiton',sans(23),dim)
    dr.rounded_rectangle((1182,54,1427,160),radius=12,fill='#26302a',outline='#617464',width=1)
    text(dr,(1200,78),'8',serif(50),'#f7d598');text(dr,(1260,86),'ORIENTATIONS',mono(14),'#c4dfce');text(dr,(1260,112),'PNG 1×',mono(16),cream)
    dr.line((47,205,1427,205),fill='#556756',width=1)
    text(dr,(47,225),'01 / LES HUIT VUES',heavy(18),gold);text(dr,(958,225),'02 / LE SEUIL EXTÉRIEUR',heavy(18),gold)
    cardW=211;gap=12;top=258;cardH=242
    for i,(v,im) in enumerate(zip(R,photos)):
        lx=47+(i%4)*(cardW+gap);ty=top+(i//4)*(cardH+13)
        dr.rounded_rectangle((lx,ty,lx+cardW,ty+cardH),radius=10,fill='#28241f',outline=line,width=1)
        text(dr,(lx+13,ty+13),v['flèche'],sans(24),gold);text(dr,(lx+cardW-13,ty+20),f'{i+1:02d}',mono(13),dim,anchor='ra')
        # Checker clipped to the rendering area only; the individual PNGs have true alpha.
        b=Image.new('RGB',(cardW-24,149),'#312d26');dd=ImageDraw.Draw(b)
        for y in range(0,149,9):
            for x in range(0,b.width,9):
                if (x//9+y//9)%2:dd.rectangle((x,y,min(b.width-1,x+8),min(148,y+8)),fill='#383128')
        vimg=pix(im,2);b.paste(vimg,((b.width-vimg.width)//2,(b.height-vimg.height)//2),vimg);page.paste(b,(lx+12,ty+43))
        text(dr,(lx+13,ty+200),v['direction'],heavy(17));text(dr,(lx+13,ty+222),v['nom'],sans(13),dim)
        text(dr,(lx+cardW-13,ty+226),f"{v['w']}×{v['h']}",mono(11),gold,anchor='ra')
    lx=958;im=Image.open(ROOT/'Falaise/Cliff-nuit-1.png').convert('RGB');im=pix(im,0.852)
    dr.rounded_rectangle((lx,top,1427,top+497),radius=10,fill='#212434',outline='#565775',width=1)
    page.paste(im,(lx+(469-im.width)//2,top+7));dr.rectangle((lx,711,1427,755),fill='#212434');dr.line((lx+1,711,1426,711),fill='#565775')
    text(dr,(lx+13,723),'G01P01C · 2 braseros · 6 i/s',mono(16),'#e8d5b5')
    text(dr,(47,795),'03 / SUR LE PARQUET DE LA GUILDE',heavy(18),gold)
    text(dr,(1426,801),'24 implantations vérifiées · aucun passage déplacé',sans(15),dim,anchor='ra')
    for j,(room,dirn,cut) in enumerate([('Accueil','Down',(84,128,305,269)),('Réfectoire','UpLeft',(120,118,380,271)),('Cuisine','DownRight',(213,87,418,245))]):
        rr=next(r for r in d0['rooms'] if r['label']==room);a=next(i for i,v in enumerate(R) if v['direction']==dirn);xy=next(v['haut_gauche'] for v in situ if v['salle']==room and v['direction']==dirn)
        source=frame(rr,d0,photos[a],xy).convert('RGB').crop(cut);x=47+j*465;y=829
        dr.rounded_rectangle((x,y,x+450,y+286),radius=10,fill='#28241f',outline=line);body=Image.new('RGB',(430,222),'#221d1a');n=min(body.width/source.width,body.height/source.height);src=pix(source,n);body.paste(src,((430-src.width)//2,(222-src.height)//2));page.paste(body,(x+10,y+10));
        text(dr,(x+15,y+247),room,heavy(22));text(dr,(x+433,y+257),dirn,mono(15),gold,anchor='ra')
    dr.line((47,1151,1427,1151),fill='#556756')
    text(dr,(47,1176),'SPRITES À L’ÉCHELLE 2× SUR CETTE PLANCHE · FICHIERS INDIVIDUELS EN 1×',mono(15),dim)
    text(dr,(47,1205),'Destiny 0.7.7 · étude d’après Halcyon · trépieds extraits de l’extérieur de Grodoudou',sans(15),'#c1b79f')
    page.save(ROOT/'Planche-Comptoirs.png',optimize=True)
    # Pack entries in explicit, equally sized cells so pivots remain deterministic.
    a=Image.new('RGBA',(4*96,2*80));m=[]
    for i,(v,im) in enumerate(zip(R,photos)):
        x=(i%4)*96+(96-im.width)//2;y=(i//4)*80+(80-im.height)//2;a.alpha_composite(im,(x,y));m.append({'direction':v['direction'],'rect':[x,y,im.width,im.height],'pivot_dans_sprite':v['pivot']})
    a.save(ROOT/'Atlas-Comptoirs-1x.png',optimize=True)
    (ROOT/'Cases-Atlas.json').write_text(json.dumps(m,indent=2)+'\n')

if __name__=='__main__':main()
