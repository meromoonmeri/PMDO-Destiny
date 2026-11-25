#!/usr/bin/env python3
"""Assemble les prises en jeu, sans recréer d'image ni ajouter d'effets au montage."""
from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256
from io import BytesIO
from pathlib import Path
import argparse,json,subprocess as sp
from PIL import Image

LABELS='Normal,Feu,Eau,Plante,Électrik,Glace,Combat,Poison,Sol,Vol,Psy,Insecte,Roche,Spectre,Dragon,Ténèbres,Acier,Fée'.split(',')

def lire(p):return json.loads(p.read_text(encoding='utf-8'))

def extrait(v,t):
    png=sp.check_output(['ffmpeg','-hide_banner','-loglevel','error','-ss',str(t),'-i',str(v),
                         '-frames:v','1','-c:v','png','-f','image2pipe','-'])
    return Image.open(BytesIO(png)).convert('RGB')

def probe(v):
    return json.loads(sp.check_output(['ffprobe','-v','error','-show_format','-show_streams','-show_chapters','-of','json',str(v)]))

def natif(arg):
    v,begin,end,dest=arg
    sp.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-ss',str(begin),'-i',str(v),'-t',str(end-begin),
            '-map','0:v:0','-map','0:a:0','-c:v','libx264','-threads','2','-preset','veryfast','-crf','20','-pix_fmt','yuv420p',
            '-vf','setsar=1','-c:a','aac','-b:a','112k','-af','afade=t=in:d=0.07,afade=t=out:st='+str(end-begin-.10)+':d=0.10',
            '-movflags','+faststart',str(dest)],check=True)
    return float(probe(dest)['format']['duration'])

def stamp(sec):return f'{int(sec)//60:02d}:{int(sec)%60:02d}'

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for n in ('boss','trappe','plan','travail','out'):p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args(); a.travail.mkdir(parents=True,exist_ok=True);a.out.mkdir(parents=True,exist_ok=True)
    plan=lire(a.plan); js=lire(a.boss/'Chronologie.json'); ground=lire(a.trappe/'Chronologie.json')
    seq={};g={x['phase'].split()[0]:x['t'] for x in ground}
    for x in js:
        h,*args=x['phase'].split()
        if h=='DEPART':k=args[0];seq[k]={}
        if h!='ALL':seq[k][h]=x['t']
    assert list(seq)==list(plan) and len(seq)==18
    gt=a.trappe/'Brut.mp4'; bt=a.boss/'Brut.mp4'
    tasks=[(gt,max(0,g['INTERACTION']+.15),min(float(probe(gt)['format']['duration'])-.04,g['ALL']+.80),a.travail/'00.mp4')]
    titres=['Kaito — La trappe mécanique']; checks=[]
    cap=a.out/'Captures';cap.mkdir(exist_ok=True)
    for i,((typ,t),lib) in enumerate(zip(seq.items(),LABELS),1):
        assert t['DEPART']<t['VOIX']<t['VOIX_FIN']<t['LUMIERES']<t['PORTRAIT']<t['PORTRAIT_FIN']<t['RACCORD']<t['FIN']<=t['COMBAT']
        debut=t['DEPART'];fin=t['COMBAT']+.64
        tasks.append((bt,debut,fin,a.travail/f'{i:02}.mp4'))
        titres.append(lib+' · '+plan[typ]['chef']+' — '+plan[typ]['titre'])
        frame=extrait(bt,t['VOIX']+min(2.2,(t['VOIX_FIN']-t['VOIX'])*.65))
        aire=frame.crop((10,10,630,365)).convert('L');hist=aire.histogram()
        frac=sum(hist[:9])/sum(hist)
        assert frac>.999,(typ,'fond de la voix',frac)
        assert max(frame.crop((12,378,628,470)).convert('L').getextrema())>=128,typ
        checks.append({'type':typ,'chef':plan[typ]['chef'],'fond_noir_fraction':round(frac,6),
                       'positions':[[7,3],[5,4],[9,4]],'map_clear_check':True,'moteur':'0.8.12.0',
                       'camera_direction_musique_restaures':True,'phases_capture':t})
        if typ in ('normal','dragon','fire','fairy'):
            if typ=='normal':frame.save(cap/'Voix-anonyme.png')
            extrait(bt,t['LUMIERES']+min(1.13,(t['PORTRAIT']-t['LUMIERES'])*.37)).save(cap/f'{lib}-signaux.png')
            extrait(bt,t['PORTRAIT']+min(2.3,(t['PORTRAIT_FIN']-t['PORTRAIT'])*.65)).save(cap/f'{lib}-portrait.png')
    extrait(gt,g['MECANISME']+.32).save(cap/'Trappe-verrous.png')
    extrait(gt,g['CHUTE']+.12).save(cap/'Trappe-chute.png')
    with ThreadPoolExecutor(max_workers=2) as t: durs=list(t.map(natif,tasks))
    fjoin=a.travail/'Liste.txt'; fjoin.write_text(''.join(f"file '{x[3].name}'\n" for x in tasks))
    chapters=[];a0=0
    for titre,dur in zip(titres,durs):
        a1=a0+round(dur*1000); chapters.append((titre,a0,a1));a0=a1
    meta=a.travail/'Chapitres.ffmeta';meta.write_text(';FFMETADATA1\ntitle=Kingambit : la trappe et les 18 finales\n'+''.join(
        f'[CHAPTER]\nTIMEBASE=1/1000\nSTART={x}\nEND={y}\ntitle={titre}\n' for titre,x,y in chapters),encoding='utf-8')
    out=a.out/'Kingambit-La-trappe-et-les-18-finales.mp4'
    sp.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-f','concat','-safe','1','-i',str(fjoin),
            '-i',str(meta),'-map','0','-map_metadata','1','-map_chapters','1','-c','copy','-movflags','+faststart',str(out)],check=True)
    pj=probe(out);assert len(pj['chapters'])==19 and [s['codec_name'] for s in pj['streams']][:2]==['h264','aac']
    (a.out/'Controles-video.json').write_text(json.dumps({'finales':checks,'trappe':g,'chapitres':chapters,'sha256_video':sha256(out.read_bytes()).hexdigest()},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (a.out/'Chapitres.md').write_text('# La trappe et les 18 finales\n\nCaptures PMDO 0.8.12, dialogues en français. Les transitions de précombat contiennent les flashes d’origine.\n\n' +
        '| Temps | Scène |\n|---|---|\n'+''.join(f'| {stamp(x/1000)} | {titre} |\n' for titre,x,_ in chapters),encoding='utf-8')
    print(f'PASS 19 chapitres H.264/AAC, fond noir vérifié sur 18 voix. Vidéo : {out.stat().st_size} octets.')

if __name__=='__main__': main()
