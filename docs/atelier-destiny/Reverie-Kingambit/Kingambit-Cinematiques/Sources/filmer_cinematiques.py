#!/usr/bin/env python3
"""Contrôles et vidéo PMDO 0.8.12 sous Xvfb. Les greffes de sonde restent dans le clone.
Dépendances locales : banc Kingambit-Prebatailles, sauvegarde de test, Xvfb, xdotool,
PulseAudio et FFmpeg. Les finales gardent leurs événements natifs -15/-11/-9/-5.
"""
from __future__ import annotations

import argparse
from datetime import datetime
import json
import os
from pathlib import Path
import re
import shutil
import subprocess as sp
import sys
import time

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parents[1]/'Kingambit-Prebatailles/Sources'))
import filmer_prebatailles_pmdo as qa

D=qa.D
S=D/'source'
ORIGIN=Path('Data/Script/origin')
ADD=Path('game/Data/Script/destiny')
MARK='KINGAMBIT_SCENE '
DANGER=('KINGAMBIT_PB ECHEC','[ERROR]', '[WARN]', 'LuaScriptException', 'Woosh de prébataille :',
        'Introduction de troupe :', 'Lumières du dojo :', 'Dialogue du dojo :', 'Entrée du dojo :',
        'Mécanisme de la trappe :')


def blob(rel):
    p=S/rel
    return p.read_bytes() if p.is_file() else sp.check_output(['git','-C',str(S),'show','HEAD:'+str(rel)])


def rajouter(c,root):
    for p in (root/'game/Content').rglob('*.dir'):
        shutil.copyfile(p,c/p.relative_to(root/'game'))
    for p in (root/ADD).glob('dojo_kingambit_*.lua'):
        (c/ORIGIN/p.name).write_text(p.read_text(encoding='utf-8').replace("'destiny.","'origin."),encoding='utf-8')
    for x in ('Marowak Dojo.ogg',):
        rel=Path('Content/Music')/x
        (c/rel).write_bytes(blob(Path('game')/rel))


def grep1(pat,s):
    r=re.search(pat,s);assert r,(pat,s[-1500:]);return r


def marque(text):
    return 'PrintInfo(\''+MARK+text+'\')'


def remplacer(s,ancien,nouveau):
    assert s.count(ancien)==1,(ancien,s.count(ancien));return s.replace(ancien,nouveau)


def installer_finales(c,lot,rs,manquante):
    rajouter(c,lot)
    if manquante:
        (c/'Content/BG'/f"Kingambit_Signaux_{rs[0]['id']}.dir").unlink()
    ev=c/qa.EVENT_REL;s=ev.read_text(encoding='utf-8')
    # Les deux fonctions passées sont les mêmes que dans destiny/event.lua.
    a=s.index('local intro=prebattle.Apres(');b=s.index('function SINGLE_CHAR_SCRIPT.KingambitQAPreBattle',a)
    s=s[:a]+'''local cine=require 'origin.dojo_kingambit_cinematiques'
local intro=cine.Avec(groupe.Jouer,prebattle.Jouer)
SINGLE_CHAR_SCRIPT.DestinyDojoTroupeJouer=function(o,c,x,a)
  if x.User~=nil then return end
  local m=_ZONE.CurrentMap
  local c0=m.ViewCenter
  local joueur=RogueEssence.Dungeon.DungeonScene.Instance.FocusedCharacter
  local dir0=joueur.CharDir
  local b0=SOUND:GetCurrentSong()
  PrintInfo('KINGAMBIT_SCENE DEPART '..a.Type)
  intro(o,c,x,a)
  assert(joueur.CharDir==dir0 and tostring(m.ViewCenter)==tostring(c0))
  local b1=SOUND:GetCurrentSong()
  assert(b1==(b0=='' and m.Music or b0), 'musique non restituée : '..tostring(b1))
  check(a)
  PrintInfo('KINGAMBIT_SCENE FIN '..a.Type)
end
'''+s[b:]
    s=s.replace("PrintInfo('KINGAMBIT_PB COMBAT '","PrintInfo('KINGAMBIT_SCENE COMBAT '").replace("PrintInfo('KINGAMBIT_PB ALL DONE '","PrintInfo('KINGAMBIT_SCENE ALL DONE '")
    # Assez de temps pour voir le HUD d'un vrai combat avant le segment suivant.
    s=s.replace('GAME:WaitFrames(16)\n    n=n+1','GAME:WaitFrames(45)\n    n=n+1')
    ev.write_text(s,encoding='utf-8')
    f=c/ORIGIN/'dojo_kingambit_cinematiques.lua';s=f.read_text(encoding='utf-8')
    for line,l,r in [
        ('  UI:WaitShowDialogue(plan.noir)','VOIX','VOIX_FIN'),
        ('  UI:WaitShowDialogue(plan.replique)','PORTRAIT','PORTRAIT_FIN'),
        ('  GAME:FadeIn(12)','LUMIERES',''),
        ('    woosh(owner,char,context,args)','RACCORD',''),
    ]:
        s=remplacer(s,line,'  '+marque(l)+'\n'+line+ ('\n  '+marque(r) if r else ''))
    f.write_text(s,encoding='utf-8')


def touche(k='Return', duree=.075):
    sp.run(['xdotool','keydown',k],check=True);time.sleep(duree)
    sp.run(['xdotool','keyup',k],check=True)


def pulse(root):
    socket=root/'audio.sock';socket.unlink(missing_ok=True)
    with (root/'pulse.log').open('w') as f:
        p=sp.Popen(['pulseaudio','-n','--daemonize=no','--exit-idle-time=-1','--use-pid-file=false',
          '-L',f'module-native-protocol-unix socket={socket} auth-anonymous=1',
          '-L','module-null-sink sink_name=kingambit_scene rate=48000 channels=2'],stdout=f,stderr=sp.STDOUT)
    env={**os.environ,'SDL_AUDIODRIVER':'pulseaudio','PULSE_SERVER':'unix:'+str(socket),'PULSE_SINK':'kingambit_scene'}
    for i in range(42):
        if socket.exists() and sp.run(['pactl','info'],env=env,stdout=sp.DEVNULL,stderr=sp.DEVNULL).returncode==0:
            return p,socket,env
        if p.poll() is not None:break
        time.sleep(.10)
    qa.stop(p)
    raise RuntimeError((root/'pulse.log').read_text())


def encoder(root,window,env):
    geom=dict(re.findall(r'^(\w+)=(-?\d+)$',qa.call(['xdotool','getwindowgeometry','--shell',window]),re.M))
    assert (geom['WIDTH'],geom['HEIGHT'])==('640','480'),geom
    source=os.environ['DISPLAY']+f".0+{geom['X']},{geom['Y']}"
    cmd=['ffmpeg','-hide_banner','-loglevel','info','-nostats','-y','-copyts','-start_at_zero',
      '-thread_queue_size','256','-probesize','32','-analyzeduration','0','-f','x11grab','-draw_mouse','0',
      '-framerate','30','-video_size','640x480','-i',source,
      '-thread_queue_size','256','-isync','0','-probesize','32','-analyzeduration','0',
      '-f','pulse','-fragment_size','4096','-i','kingambit_scene.monitor',
      '-c:v','libx264','-threads','2','-preset','ultrafast','-crf','17','-pix_fmt','yuv420p',
      '-c:a','aac','-b:a','128k','-af','aresample=async=1:first_pts=0','-movflags','+faststart',str(root/'Brut.mp4')]
    with (root/'ffmpeg.log').open('w') as f:
        return sp.Popen(cmd,env=env,stdin=sp.PIPE,stdout=f,stderr=sp.STDOUT)


def capter(root,c,profil,rs,manquante=False,mode='finales'):
    pa=jeu=vid=None; done=False
    try:
        pa,socket,env=pulse(root)
        with (root/'Moteur.log').open('w') as f:
            jeu=sp.Popen([str(c/'PMDO'),'-appdata',str(profil)+'/', '-lang','fr','-nolog'],cwd=c,env=env,stdout=f,stderr=sp.STDOUT)
        win=qa.call(['xdotool','search','--sync','--onlyvisible','--pid',str(jeu.pid)],timeout=16).splitlines()[0]
        vid=encoder(root,win,env)
        limite=time.monotonic()+27
        while 'Lua engine ready' not in qa.tail(profil):
            assert time.monotonic()<limite and jeu.poll() is None,qa.tail(profil)[-2000:]
            time.sleep(.15)
        time.sleep(.65)
        for _ in range(9):
            if 'Loading rsground file: test_grounds' in qa.tail(profil) or MARK in qa.tail(profil):break
            touche('x');time.sleep(.88)
        t0=time.monotonic(); imposer=0;prochain=0;dialogue=None;seen=set();printed=0;action=False
        while time.monotonic()<t0+max(50,len(rs)*20):
            s=qa.tail(profil);lines=s.splitlines();new=lines[printed:];printed=len(lines)
            for line in new:
                if any(t in line for t in DANGER):
                    if not (manquante and 'Lumières du dojo :' in line and 'banque de lumière' in line):
                        raise RuntimeError(line+'\n'+s[-3500:])
                if MARK not in line:continue
                msg=line.split(MARK,1)[1];print(msg,flush=True)
                cmd=msg.split()[0]
                if cmd in ('VOIX','PORTRAIT','CHOIX','CONFIRMER'):
                    dialogue=cmd; prochain=time.monotonic()+({'CHOIX':1.15,'CONFIRMER':6.6}.get(cmd,3.0));imposer=0
                elif cmd.endswith('_FIN') or cmd=='MECANISME':dialogue=None
                if cmd=='CONFIRMER_FIN':assert msg=='CONFIRMER_FIN ok=true',msg
                if cmd=='COMBAT':seen.add(msg.split()[1])
                if cmd=='ALL':done=True
                if cmd=='INTERACTION':action=True;prochain=time.monotonic()+1.2
            assert jeu.poll() is None and vid.poll() is None, s[-3500:]
            if done:break
            if action and time.monotonic()>=prochain:
                action=False;touche('x') # Attack par défaut ; Entrée est seulement Confirm.
            if dialogue and time.monotonic()>=prochain:
                assert imposer<11,('Dialogue non avancé',dialogue,s[-2000:])
                if imposer==0 and dialogue=='CONFIRMER':
                    touche('Up',.17);time.sleep(.28) # « Descendre », et non « Pas maintenant »
                if imposer==0 and dialogue=='CHOIX':
                    page,ligne=divmod(rs[0]['slot'],7)
                    for k in ['Right']*page+['Down']*ligne:
                        touche(k);time.sleep(.10)
                touche();prochain=time.monotonic()+.60;imposer+=1
            time.sleep(.055)
        assert done, 'Délai dépassé : '+qa.tail(profil)[-3600:]
        if mode=='finales':assert seen=={r['id'] for r in rs},seen
        time.sleep(.85);vid.communicate(b'q\n',timeout=6);assert vid.returncode==0
        log=qa.tail(profil);(root/'Journal-complet.txt').write_text(log,encoding='utf-8')
        trace=(root/'ffmpeg.log').read_text(); t=float(grep1(r'Input #0, x11grab[^\n]*\n\s*Duration: N/A, start: ([0-9.]+)',trace)[1])
        pat=re.compile(r'^\[([\d/:. ]+)\].*?'+MARK+r'(.+)')
        marks=[]
        for l in log.splitlines():
            m=pat.match(l)
            if m:marks.append({'t':round(datetime.strptime(m[1],'%Y/%m/%d %H:%M:%S.%f').timestamp()-t,3),'phase':m[2]})
        assert marks and min(x['t'] for x in marks)>0,marks[:4]
        (root/'Chronologie.json').write_text(json.dumps(marks,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        (root/'Journal-PMDO.txt').write_text('\n'.join(l for l in log.splitlines() if MARK in l or 'Version:' in l)+'\n',encoding='utf-8')
    finally:
        for p in (vid,jeu,pa):qa.stop(p)
        (root/'audio.sock').unlink(missing_ok=True)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--lot',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True);p.add_argument('--type',nargs='+')
    p.add_argument('--manquante',action='store_true',help='retrait d’une lumière en copie pour tester le repli')
    a=p.parse_args();assert os.getenv('DISPLAY'),'lancer sous xvfb-run';a.out.mkdir(parents=True,exist_ok=True)
    rs=qa.rows();rs=rs if not a.type else [next(r for r in rs if r['id']==k) for k in a.type]
    qa.QA=D/'prebatailles-pmd/banques'
    c,p=qa.prepare(a.out,rs);installer_finales(c,a.lot,rs,a.manquante)
    capter(a.out,c,p,rs,a.manquante)


if __name__=='__main__': main()
