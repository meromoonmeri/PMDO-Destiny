#!/usr/bin/env python3
"""Découpe 18 séquences natives : pixels de jeu et son Pulse réellement enregistrés.
Ajoute des cartels hors de la vue du jeu, puis les chapitres. Ne recompose pas les VFX.
"""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import io
import json
import math
import subprocess as sp

from PIL import Image,ImageDraw,ImageFont
import numpy as np
from scipy.signal import fftconvolve
from dessiner_prebatailles_kingambit import COSTUMES,POSES,TICKS,seal,NEAR

W,H=1280,720
X,Y=61,117
WW,HH=640,480
FONTS=Path('/usr/share/fonts/truetype/dejavu')
TITLE='Les-18-prebatailles-dans-PMDO.mp4'
MONO='DejaVuSansMono.ttf'


def cmd(*args,**k):return sp.check_output([str(q) for q in args],**k)


def font(size,bold=False,mono=False):
    name=MONO if mono else ('DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf')
    return ImageFont.truetype(str(FONTS/name),size)


def wrap(txt,dr,f,lim):
    out=[];l=''
    for word in txt.split():
        test=(l+' '+word).strip()
        if l and dr.textlength(test,font=f)>lim:out.append(l);l=word
        else:l=test
    if l:out.append(l)
    return out


def titlecard(i,work):
    k=COSTUMES[i]; accent=k.trim
    p=Image.new('RGB',(W,H),'#101823');d=ImageDraw.Draw(p)
    def text(x,y,t,n=22,col='#f2f1ed',bold=False,mono=False):d.text((x,y),t,font=font(n,bold,mono),fill=col)
    d.rectangle((X-2,Y-2,X+WW+1,Y+HH+1),outline='#43556a',width=2)
    d.line((61,89,1219,89),fill='#344153',width=1)
    d.rectangle((61,37,65,66),fill=accent)
    text(79,34,'DOJO KINGAMBIT',28,bold=True)
    text(386,45,'/  LES 18 PRÉBATAILLES',15,'#a7b9c8',mono=True)
    d.rounded_rectangle((1060,37,1219,67),5,fill='#1d2b3d',outline='#37495f')
    text(1073,44,'PMDO 0.8.12',16,'#cdd9e5',mono=True)
    bx=752
    d.rounded_rectangle((734,Y,1219,Y+HH),12,fill='#162131',outline='#354255',width=1)
    d.rounded_rectangle((762,141,865,170),5,fill='#25344a')
    text(774,147,f'{i+1:02d} / 18',14,accent,mono=True)
    text(768,198,k.type.upper(),23,accent,bold=True)
    text(766,238,k.boss,46,bold=True)
    icon=seal(k).resize((104,104),NEAR)
    d.rounded_rectangle((1081,141,1194,254),13,fill='#111a27',outline='#34455b')
    p.paste(icon,(1085,145),icon)
    d.line((765,312,1187,312),fill='#344356');d.rectangle((765,310,824,313),fill=accent)
    f=font(27,True);l=wrap(k.titre,d,f,416)
    for j,row in enumerate(l):d.text((767,333+j*33),row,font=f,fill='#f0ede3')
    y=342+len(l)*33
    for j,row in enumerate(wrap(k.motif,d,font(19),405)):
        text(768,y+j*26,row,19,'#c7d1df')
    text(766,514,'WOOSH APRÈS L’APPARITION',15,accent,mono=True)
    text(766,544,'Le combat natif prend ensuite la main.',16,'#a8baca')
    d.line((61,638,1219,638),fill='#344153')
    text(61,656,'CAPTURE EN JEU  ·  IMAGE ET SON DU MOTEUR',14,'#a2b3c7',mono=True)
    for j in range(18):
        xx=922+17*j;d.rounded_rectangle((xx,666,xx+10,670),2,fill=accent if i==j else '#46576e')
    ff=work/f'cartel-{i:02d}.png';p.save(ff);return ff


def frame_at(src,t):
    f=cmd('ffmpeg','-nostdin','-hide_banner','-loglevel','error','-ss',f'{t:.6f}','-i',src,
          '-frames:v','1','-f','image2pipe','-vcodec','png','-')
    return Image.open(io.BytesIO(f)).convert('RGB')


def verify(top, rows, atlas_dir, son_dir, src):
    """Un témoin de la pose fondue, et une corrélation du son écouté par Pulse."""
    sr=12000
    def pcm(p):return np.frombuffer(cmd('ffmpeg','-nostdin','-v','error','-i',p,'-vn','-f','f32le','-ac','1','-ar',sr,'-'),dtype='<f4')
    audio=pcm(src)
    report=[];captures=[]
    for cap,row in zip(top,rows):
        k=cap['id']; a=Image.open(atlas_dir/(k+'.png')); pic=row['pic']
        f=a.crop((pic%7*320,pic//7*240,(pic%7+1)*320,(pic//7+1)*240))
        f=np.asarray(f,dtype='float32');opacity=f[...,3:4]/255; ok_mask=opacity[...,0]>.65
        assert ok_mask.sum()>450
        plain=frame_at(src,cap['fin']+.075).resize((320,240),NEAR)
        p=np.asarray(plain,dtype='float32');expect=(f[...,:3]*opacity+p*(1-opacity))[ok_mask]
        t0=cap['woosh']+.057+pic/20-.16
        yuv=cmd('ffmpeg','-nostdin','-v','error','-ss',f'{t0:.6f}','-i',src,'-an','-t','0.49',
                '-vf','scale=320:240:flags=neighbor','-f','rawvideo','-pix_fmt','rgb24','-')
        seq=np.frombuffer(yuv,np.uint8).reshape(-1,240,320,3)
        err=np.mean(np.abs(seq[:,ok_mask].astype('float32')-expect),axis=(1,2))
        best=int(err.argmin()); base=float(np.mean(np.abs(p[ok_mask]-expect)))
        ratio=float(err[best])/max(1,base)
        assert base>18 and ratio<.69,(k,base,ratio)
        snap=frame_at(src,t0+best/30+0.00025)
        quoted=pcm(son_dir/row['son']);b=max(0,round((cap['woosh']-.18)*sr));e=min(len(audio),round((cap['woosh']+.32)*sr)+len(quoted))
        sample=audio[b:e]
        scores=fftconvolve(sample,quoted[::-1],mode='valid')/np.sqrt(np.maximum(1e-6,fftconvolve(sample**2,np.ones(len(quoted)),mode='valid'))*np.sum(quoted**2))
        idx=int(scores.argmax());cc=float(scores[idx]); offset=(b+idx)/sr-cap['woosh']-4/60
        assert cc>.35 and abs(offset)<.21,(k,cc,offset)
        report.append(dict(type=k,duree_woosh_s=round(cap['fin']-cap['woosh'],3),erreur_relative_pose=round(ratio,3),
                           correlation_son=round(cc,3),delai_capture_son=round(offset,3),nb_combattants=3))
        captures.append(snap)
        print(f"PASS capturé {k:8s} image={ratio:.2f}, cue={cc:.2f}, +{offset:.3f}s",flush=True)
    return captures,report


def contact(snaps,rows,path):
    CW,CH=246,208
    m=Image.new('RGB',(CW*6,CH*3+76),'#111b28');d=ImageDraw.Draw(m)
    d.text((16,17),'DOJO KINGAMBIT',font=font(27,True),fill='#f0eee8')
    d.text((313,29),'LES 18 WOOSHES  /  CAPTURES PMDO',font=font(15,mono=True),fill='#a8bbcf')
    for i,(shot,k) in enumerate(zip(snaps,rows)):
        x,y=i%6*CW,i//6*CH+70
        d.text((x+9,y),f"{i+1:02}. {k['type']} · {k['boss']}",font=font(14,True),fill=k['accent'])
        # 0.375x is the same for every thumbnail; the video retains the 2x window.
        m.paste(shot.resize((232,174),Image.Resampling.LANCZOS),(x+7,y+23))
    m.save(path,quality=93,optimize=True)


def make_clip(i,cap,src,work):
    card=titlecard(i,work)
    start=cap['woosh']-.28
    n=math.ceil((cap['combat']+.21-start)*30)
    duration=n/30
    p=work/f'scene-{i:02d}.mp4'
    fadein=.052; fadeout=.082
    cmd('ffmpeg','-nostdin','-v','error','-y','-threads','1','-ss',f'{start:.6f}','-i',src,
         '-loop','1','-framerate','30','-i',card,'-filter_complex_threads','1',
         '-filter_complex',f'[1:v][0:v]overlay={X}:{Y}:shortest=1:format=auto[v]',
         '-map','[v]','-map','0:a:0','-af',f'apad,afade=in:d={fadein},afade=out:st={duration-fadeout:.6f}:d={fadeout}',
         '-r','30','-t',f'{duration:.6f}','-c:v','libx264','-threads','2','-preset','veryfast','-crf','17',
         '-pix_fmt','yuv420p','-c:a','aac','-b:a','144k','-ar','48000',p)
    print(f'Montage {i+1:02}/18 {cap["id"]}',flush=True)
    return p,n


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--banques',type=Path,required=True);ap.add_argument('--captures',type=Path,required=True);ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args(); out=a.out; out.mkdir(parents=True,exist_ok=True);work=a.captures/'montage';work.mkdir(exist_ok=True)
    src=a.captures/'Brut.mp4';marks=json.loads((a.captures/'Captures.json').read_text());rows=json.loads((a.banques/'Index-Prebatailles.json').read_text())
    assert [r['id'] for r in marks]==[x.id for x in COSTUMES]==[r['id'] for r in rows]
    shots,report=verify(marks,rows,a.banques/'Planches',a.banques/'Content/Sound/Battle',src)
    (a.captures/'Controle-audiovisuel.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
    contact(shots,rows,a.captures/'Planche-des-18-dans-PMDO.jpg')
    with ThreadPoolExecutor(max_workers=3) as pool:
        pieces=list(pool.map(lambda args:make_clip(*args,src,work),enumerate(marks)))
    seq=work/'liste.txt';seq.write_text(''.join(f"file {p.name}\n" for p,_ in pieces))
    # Concat uses container durations. Add chapter starts at the encoded boundary.
    meta=work/'chapitres.ffmeta';pos=0;lines=[';FFMETADATA1','title=Dojo Kingambit — les 18 prébatailles']
    for i,((p,n),k) in enumerate(zip(pieces,COSTUMES)):
        duration=round(float(cmd('ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',p))*1000)
        lines+=['[CHAPTER]','TIMEBASE=1/1000',f'START={pos}',f'END={pos+duration}',f'title={i+1:02d}. {k.type} — {k.boss} · {k.titre}']
        pos+=duration
    meta.write_text('\n'.join(lines)+'\n',encoding='utf-8');dest=out/TITLE
    cmd('ffmpeg','-nostdin','-v','error','-y','-f','concat','-safe','0','-i',seq,'-i',meta,
         '-map','0:v:0','-map','0:a:0','-map_metadata','1','-map_chapters','1','-c','copy','-movflags','+faststart',dest)
    con=json.loads(cmd('ffprobe','-v','error','-show_chapters','-show_streams','-of','json',dest))
    assert len(con['chapters'])==18 and any(x['codec_type']=='audio' for x in con['streams'])
    sp.run(['ffmpeg','-nostdin','-hide_banner','-v','error','-xerror','-i',str(dest),'-f','null','-'],check=True)
    print(f'18 chapitres / {pos/1000:.2f} s / décodage OK : {dest}',flush=True)


if __name__=='__main__':main()
