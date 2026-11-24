#!/usr/bin/env python3
"""Découpe une capsule par type depuis X11/Pulse ; vérifie le blanc, pas un blanc ajouté au montage."""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor
import io
import json
from pathlib import Path
import re
import subprocess as sp

import numpy as np
from PIL import Image
from scipy.signal import fftconvolve

FPS=30

def cmd(*args):return sp.check_output(list(map(str,args)))
def jsonread(path):return json.loads(path.read_text(encoding='utf-8'))
def frame_at(source,t):
    b=cmd('ffmpeg','-nostdin','-v','error','-ss',f'{t:.5f}','-i',source,
          '-frames:v','1','-f','image2pipe','-codec:v','png','-')
    return Image.open(io.BytesIO(b)).convert('RGB')


def frames(src,start,d):
    b=cmd('ffmpeg','-nostdin','-v','error','-ss',f'{start:.5f}','-i',src,'-an','-t',f'{d:.5f}',
          '-vf','scale=320:240:flags=neighbor','-f','rawvideo','-pix_fmt','rgb24','-')
    return np.frombuffer(b,dtype=np.uint8).reshape(-1,240,320,3)


def pcm(src):
    return np.frombuffer(cmd('ffmpeg','-nostdin','-v','error','-i',src,'-vn','-f','f32le','-ac','1','-ar','12000','-'),dtype='<f4')


def audio_check(heard,cue,t):
    n=12000; x=round((t+.85)*n); y=round((t+1.5)*n)+len(cue); a=heard[x:y]
    corr=fftconvolve(a,cue[::-1],mode='valid')/np.sqrt(np.maximum(1e-7,fftconvolve(a*a,np.ones(len(cue)),mode='valid'))*np.sum(cue*cue))
    ind=int(np.argmax(corr)); ratio=float(corr[ind]); time=(x+ind)/n-t
    return ratio,time


def consecutive(indices):
    return np.split(indices,np.where(np.diff(indices)>1)[0]+1) if len(indices) else []


def review(src,cap,sound,cue,ref=False):
    start=cap['woosh']-.22
    stop=cap['woosh']+3.16 if ref else cap['combat']+.30
    seq=frames(src,start,stop-start)
    clock=np.arange(len(seq))/FPS-.22
    coverage=(seq.min(axis=3)>=247).mean(axis=(1,2))
    chunks=consecutive(np.where((coverage>=.997)&(clock>2.30))[0]); assert chunks,(cap['id'],coverage.max())
    white=max(chunks,key=len); assert len(white)>=4,(cap['id'],white)
    i_peak=int(round((1.98+.22)*FPS)); active=seq[i_peak]
    still=seq[1];delta=(np.abs(active.astype(np.int16)-still).max(axis=2)>35).mean()
    assert delta>.055,(cap['id'],delta)
    if not ref:
        # Imminence du combat : HUD revenu, aucun reste blanc dans le décor.
        restore=(np.abs(seq[-2].astype(np.int16)-still).max(axis=2)>40).mean()
        # Les tuiles de Glace sont déjà claires sans effet ; compare au témoin.
        assert restore<.16 and abs(coverage[-2]-coverage[1])<.025,(cap['id'],restore,coverage[1],coverage[-2])
        at_fade=max(i_peak+1,white[0]-9)
        assert seq[at_fade:white[0]].mean() > still.mean()+18
    else:restore=None
    # Référence : 62 ticks ; la variante ajoute quatre ticks d'amorce.
    # Marge de capture : ~0,11 s pour l'horloge son/vidéo et le tick du log.
    corr,t=audio_check(sound,cue,cap['woosh'])
    nominal=(62 if ref else 66)/60
    assert corr>.42 and abs(t-nominal)<.15,(cap['id'],corr,t)
    me=dict(id=cap['id'],nb_images_blanches=len(white),t_blanc=round(float(white[0]/FPS),3),
            t_balayage=round(i_peak/FPS,3),t_reprise=None if ref else round(float(np.where(clock>cap['combat']-cap['woosh']+.056)[0][0]/FPS),3),
            part_ecran_modifiee=round(float(delta),3),part_modifiee_apres=round(float(restore),3) if restore is not None else None,
            correlation_woosh_natif=round(corr,3),t_son_par_rapport_lua=round(t,3),
            passage_combat=None if ref else cap['woosh']<cap['fin']<=cap['combat'])
    return start,stop,me


def cut(src,path,start,stop):
    d=round((stop-start)*FPS)/FPS
    cmd('ffmpeg','-nostdin','-hide_banner','-loglevel','error','-y','-threads','2','-ss',f'{start:.5f}','-i',src,
        '-t',f'{d:.5f}','-map','0:v:0','-map','0:a:0','-af',f'afade=in:d=0.052,afade=out:st={d-.10:.5f}:d=0.1',
        '-c:v','libx264','-threads','2','-preset','fast','-crf','20','-pix_fmt','yuv420p','-c:a','aac','-b:a','112k',
        '-movflags','+faststart',path)
    out=json.loads(cmd('ffprobe','-v','error','-show_format','-show_streams','-of','json',path))
    assert [s['codec_type'] for s in out['streams']]==['video','audio']
    assert (out['streams'][0]['width'],out['streams'][0]['height'])==(640,480)
    cmd('ffmpeg','-nostdin','-v','error','-xerror','-threads','2','-i',path,'-f','null','-')
    return round(float(out['format']['duration']),3)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for flag in ('natif','reference','banques','pmdo','out'):ap.add_argument('--'+flag,type=Path,required=True)
    a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    clips=a.out/'Clips';clips.mkdir(exist_ok=True)
    raw=a.natif/'Brut.mp4';van=a.reference/'Brut.mp4'
    heard=pcm(raw);van_sound=pcm(van);cue=pcm(a.pmdo/'Content/Sound/Battle/EVT_Battle_Transition.ogg')[:16800]
    marks=jsonread(a.natif/'Captures.json');index=jsonread(a.banques/'Index-Illustrations.json')
    assert [r['id'] for r in marks]==[r['id'] for r in index]
    log=(a.natif/'Journal-PMDO.txt').read_text()
    assert log.count(' COMBAT ')==len(marks) and log.count('map_clear_check')==len(marks)
    assert not re.search(r'error|exception|échec|warning',log,re.I)
    ref=jsonread(a.reference/'Captures.json')[0]
    r0=dict(id='vanilla',type='Référence PMDO',boss='Drattak',titre='Woosh par défaut',couleur='#c4b8ff',
            note='Les lignes bleues et le fondu blanc de COMMON.BossTransition, capturés dans la scène de Drattak. Le clip s’arrête au blanc.')
    jobs=[(0,r0,ref,van,van_sound,True)]+[(i+1,r,c,raw,heard,False) for i,(r,c) in enumerate(zip(index,marks))]
    def one(job):
        i,k,c,src,track,is_ref=job
        start,stop,analysis=review(src,c,track,cue,is_ref)
        stem=f'{i:02d}-'+('Reference-PMDO' if is_ref else k['type'].replace('É','E').replace('è','e').replace('é','e'))
        file=clips/(stem+'.mp4');duration=cut(src,file,start,stop)
        post=clips/(k['id']+'.jpg');frame_at(src,start+analysis['t_balayage']).save(post,quality=88,optimize=True)
        print(f"PASS {k['id']:8} : {analysis['nb_images_blanches']:2d} images blanches, corrélation son {analysis['correlation_woosh_natif']:.2f}, {duration:.2f} s",flush=True)
        return dict(**k,numero=i,video=file.name,poster=post.name,duration=duration,**{q:v for q,v in analysis.items() if q!='id'})
    with ThreadPoolExecutor(max_workers=3) as pool:rows=list(pool.map(one,jobs))
    (a.out/'Capsules.json').write_text(json.dumps(rows,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')


if __name__=='__main__':main()
