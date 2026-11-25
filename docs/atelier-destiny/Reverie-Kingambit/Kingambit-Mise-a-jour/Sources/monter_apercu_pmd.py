#!/usr/bin/env python3
"""Monte la référence et les 18 capsules jouées par PMDO en un MP4 chapitré.
Les cartels sont hors du jeu ; aucun rééclairage ni effet ajouté dans la fenêtre.
"""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import subprocess as sp
import tempfile

from PIL import Image, ImageDraw, ImageFont

W,H=1280,720
GX,GY=52,120
GW,GH=640,480
CARD=(725,120,1228,600)
FONTDIR=Path('/usr/share/fonts/truetype/dejavu')


def cmd(*a):return sp.check_output(list(map(str,a)))


def font(n,weight='regular'):
    filename={'regular':'DejaVuSans.ttf','bold':'DejaVuSans-Bold.ttf','mono':'DejaVuSansMono.ttf'}[weight]
    return ImageFont.truetype(str(FONTDIR/filename),n)


def card(p,r,tex=None):
    im=Image.new('RGB',(W,H),'#111826'); d=ImageDraw.Draw(im)
    accent=r['couleur']; i=r['numero'];ref=i==0
    def txt(x,y,s,n=18,fill='#f1efe8',face='regular'):d.text((x,y),s,font=font(n,face),fill=fill)
    def wrapped(x,y,msg,n,width,fill,face='regular'):
        acc=''; f=font(n,face)
        def put(j):d.text((x,j),acc,font=f,fill=fill)
        for token in msg.split():
            candidate=(acc+' '+token).strip()
            if acc and d.textlength(candidate,font=f)>width:put(y);y+=n+7;acc=token
            else:acc=candidate
        if acc:put(y)
    d.line((52,88,1228,88),fill='#3b495f')
    d.rounded_rectangle((52,36,60,67),3,fill=accent)
    txt(75,34,'DOJO KINGAMBIT',28,face='bold')
    txt(380,48,'/  WOOSHES FAÇON PMD',15,'#c3cfe0','mono')
    d.rounded_rectangle((1066,37,1228,68),5,fill='#263144',outline='#4a5771')
    txt(1081,44,'PMDO 0.8.12',16,'#e0e5ee','mono')
    d.rectangle((GX-2,GY-2,GX+GW+1,GY+GH+1),outline='#506077',width=2)
    d.rounded_rectangle(CARD,11,fill='#1b2536',outline='#3e4c61')
    d.rounded_rectangle((752,144,892 if ref else 870,174),5,fill='#2c374d')
    txt(765,150,'RÉFÉRENCE' if ref else f'{i:02d} / 18',15,accent,'mono')
    txt(752,201,'PMDO PAR DÉFAUT' if ref else r['type'].upper(),24,accent,'bold')
    txt(750,241,r['boss'],48,face='bold')
    d.line((752,321,1202,321),fill='#475971');d.rectangle((752,320,811,323),fill=accent)
    txt(751,344,r['titre'],27,face='bold')
    wrapped(752,387,r['note'],19,437,'#c7d2e2')
    if tex and not ref:
        tile=tex/(r['id']+'-accent.png')
        if tile.exists():
            f=Image.open(tile).convert('RGBA'); f=f.resize((f.width*2,f.height*2),Image.Resampling.NEAREST)
            im.paste(f,(1196-f.width,160-f.height//2),f)
    d.line((752,505,1202,505),fill='#475971')
    txt(752,525,'BALAYAGE   →   BLANC'+('' if ref else '   →   COMBAT'),15,accent,'mono')
    txt(752,552,'Référence capturée dans la scène de Drattak.' if ref else 'Fondu blanc joué par le moteur, sans coupe.',16,'#bfcce0')
    d.line((52,638,1228,638),fill='#3b495f')
    txt(52,658,'CAPTURE EN JEU  /  IMAGE ET SON DU MOTEUR',14,'#b6c4d9','mono')
    for j in range(19):
        x=886+j*18
        d.rounded_rectangle((x,666,x+10,670),2,fill=accent if j==i else '#495a72')
    im.save(p,optimize=True)


def one(r,clips,out,tex):
    i=r['numero'];p=out/f'clip-{i:02d}.mp4';img=out/f'cartel-{i:02d}.png'
    card(img,r,tex)
    cmd('ffmpeg','-nostdin','-hide_banner','-v','error','-y','-threads','1','-i',clips/r['video'],
        '-loop','1','-framerate','30','-i',img,'-filter_complex_threads','1','-filter_complex',
        f'[1:v][0:v]overlay={GX}:{GY}:shortest=1:format=yuv420[v]',
        '-map','[v]','-map','0:a:0','-t',f"{r['duration']:.5f}",'-c:v','libx264','-threads','2',
        '-preset','fast','-crf','20','-pix_fmt','yuv420p','-c:a','aac','-ar','48000','-b:a','128k',p)
    duration=float(cmd('ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',p))
    return p,round(duration*1000)


def main():
    a=argparse.ArgumentParser(description=__doc__)
    for k in ('index','clips','textures','out'):a.add_argument('--'+k,type=Path,required=k!='textures')
    t=a.parse_args();r=json.loads(t.index.read_text(encoding='utf-8'))
    assert [x['numero'] for x in r]==list(range(19))
    t.out.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='woosh-film-') as tmp:
        w=Path(tmp)
        with ThreadPoolExecutor(max_workers=3) as pool:parts=list(pool.map(lambda x:one(x,t.clips,w,t.textures),r))
        seq=w/'concat.txt';seq.write_text(''.join(f"file '{p.name}'\n" for p,_ in parts),encoding='utf-8')
        at=0;meta=[';FFMETADATA1','title=Kingambit — les 18 wooshes de boss façon PMD']
        for x,(_,d) in zip(r,parts):
            meta+=['[CHAPTER]','TIMEBASE=1/1000',f'START={at}',f'END={at+d}',f"title={x['numero']:02d}. {x['type']} — {x['boss']}"]
            at+=d
        m=w/'meta.ff';m.write_text('\n'.join(meta)+'\n',encoding='utf-8')
        cmd('ffmpeg','-nostdin','-v','error','-y','-f','concat','-safe','0','-i',seq,'-i',m,
            '-map','0:v:0','-map','0:a:0','-map_metadata','1','-map_chapters','1','-c','copy','-movflags','+faststart',t.out)
    manifest=json.loads(cmd('ffprobe','-v','error','-show_streams','-show_chapters','-show_format','-of','json',t.out))
    assert len(manifest['chapters'])==19 and {s['codec_type'] for s in manifest['streams']}>={'video','audio'}
    cmd('ffmpeg','-nostdin','-v','error','-xerror','-threads','2','-i',t.out,'-f','null','-')
    print(f"MP4 : 19 chapitres, {manifest['format']['duration']} s, {t.out.stat().st_size:,} octets. Décodage OK.",flush=True)

if __name__=='__main__':main()
