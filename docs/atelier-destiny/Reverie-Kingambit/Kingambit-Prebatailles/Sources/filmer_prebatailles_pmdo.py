#!/usr/bin/env python3
"""Banc PMDO 0.8.12 : installation isolée, vrai moteur et capture X11/Pulse.
Lancer sous xvfb-run. Le parcours QA saute les étages 1–2, pas les événements des finales.
Il enchaîne les essais APRÈS BeginBattleEvent ; aucune greffe ne touche la base source.
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
import time

D=Path.home()/'.cache/spawns-kingambit'
QA=D/'prebatailles'
BASE=D/'runtime12/jeu/PMDO'
S=D/'source/game'
SAVE=D/'profil/SAVE/SAVE.rssv'
EVENT_REL=Path('Data/Script/origin/event_single.lua')
START_REL=Path('Data/Script/origin/ground/test_grounds/init.lua')
MARK='KINGAMBIT_PB '
LUA='''
-- HARNAIS QA, pas dans le dépôt produit : mêmes modules que dans Destiny.
local prebattle=require 'origin.dojo_kingambit_prebatailles'
local groupe=require 'origin.dojo_kingambit_troupes'
local essais=$ROWS
local n=1
local function check(a)
  local e=essais[n]
  local s=_ZONE.CurrentZone.CurrentMapID.Segment
  local m=_ZONE.CurrentMap
  local team=m.MapTeams[0].Players
  assert(e and e[1]==s and e[2]==a.Type and team.Count==3)
  for i=0,2 do
    assert(team[i].CurrentForm.Species==e[i+3] and team[i].CurrentForm.Form==0)
  end
  return team,e
end
SINGLE_CHAR_SCRIPT.DestinyDojoTroupeMasquer=groupe.Masquer
local intro=prebattle.Apres(function(o,c,x,a)
  if x.User==nil then PrintInfo('KINGAMBIT_PB ENTREES '..a.Type) end
  groupe.Jouer(o,c,x,a)
  if x.User~=nil then return end
  check(a)
  local v=RogueEssence.Dungeon.DungeonScene.Instance.ViewRect
  PrintInfo('KINGAMBIT_PB WOOSH '..a.Type..' viewport='..v.Width..'x'..v.Height..' decor='..v.X..','..v.Y)
end)
function SINGLE_CHAR_SCRIPT.DestinyDojoTroupeJouer(o,c,x,a)
  intro(o,c,x,a)
  if x.User~=nil then return end
  check(a)
  PrintInfo('KINGAMBIT_PB FIN '..a.Type)
end
function SINGLE_CHAR_SCRIPT.KingambitQAPreBattle(o,c,x,a)
  if x.User~=nil then return end
  local ok,err=pcall(function()
    local team,e=check(a)
    assert(not _DATA.Save.CutsceneMode)
    assert(_ZONE.CurrentMap.Status:ContainsKey('map_clear_check'))
    local pos={{7,3},{5,4},{9,4}}
    for i=0,2 do assert(team[i].CharLoc.X==pos[i+1][1] and team[i].CharLoc.Y==pos[i+1][2]) end
    PrintInfo('KINGAMBIT_PB COMBAT '..a.Type..' count=3 map_clear_check forme=0 '..team[0].CurrentForm.Species)
    GAME:WaitFrames(16)
    n=n+1
    if not essais[n] then PrintInfo('KINGAMBIT_PB ALL DONE '..#essais);return end
    GAME:ContinueDungeon('dojo_kingambit_dedales',essais[n][1],2,0)
  end)
  if not ok then PrintInfo('KINGAMBIT_PB ECHEC '..tostring(err)) end
end
'''
START='''local q={}
function q.Enter(map)
  if q.started then return end
  q.started=true
  GAME:FadeIn(1)
  GAME:WaitFrames(22)
  GAME:EnterDungeon('dojo_kingambit_dedales',$SEGMENT,2,0,RogueEssence.Data.GameProgress.DungeonStakes.Progress,false,false)
end
q.GameLoad=q.Enter
return q
'''


def call(cmd,**kw):return sp.check_output(cmd,text=True,**kw)


def rows():
    r=json.loads((D/'export/Registre-des-boss.json').read_text())
    # The .rsmap is the authority for species ordering, including mixed-species cadets.
    for i,z in enumerate(r):
        m=json.loads((S/'Data/Map'/f"dojo_kingambit_dedales_{z['type']}.rsmap").read_text(encoding='utf-8-sig'))
        a=m['Object']['MapTeams'][0]['Players']
        r[i]=dict(id=z['type'],slot=i,species=[u['BaseForm']['Species'] for u in a])
    return r


def prepare(root,rs):
    c=root/'PMDO';profile=root/'profil'
    if c.is_dir():shutil.rmtree(c)
    if profile.is_dir():shutil.rmtree(profile)
    sp.run(['cp','-a','--reflink=auto',str(BASE),str(c)],check=True)
    for part in ('Particle','BG'):
        for f in (D/'cyclones/Content'/part).glob('Kingambit_Entree*.dir'):
            shutil.copyfile(f,c/'Content'/part/f.name)
    for p in (QA/'Content').rglob('Kingambit_Prebataille_*'):
        shutil.copyfile(p,c/p.relative_to(QA))
    for f in ('dojo_kingambit_troupes.lua','dojo_kingambit_prebatailles.lua'):
        shutil.copyfile(S/'Data/Script/destiny'/f,c/'Data/Script/origin'/f)
    # Supprime la greffe QA précédente UNIQUEMENT dans la copie.
    ev=c/EVENT_REL; original=ev.read_text(encoding='utf-8').split("\nlocal qa=require 'origin.dojo_kingambit_troupes'",1)[0]
    ru='{'+','.join('{'+str(x['slot'])+','+','.join(json.dumps(j) for j in [x['id'],*x['species']])+'}' for x in rs)+'}'
    ev.write_text(original+'\n'+LUA.replace('$ROWS',ru),encoding='utf-8')
    (c/START_REL).write_text(START.replace('$SEGMENT',str(rs[0]['slot'])),encoding='utf-8')
    for r in rs:
        f=c/'Data/Map'/f"dojo_kingambit_dedales_{r['id']}.rsmap"
        source=S/'Data/Map'/f.name
        assert f.read_bytes()==source.read_bytes(),f
        j=json.loads(f.read_text(encoding='utf-8-sig'))
        starts=j['Object']['MapEffect']['OnMapStarts']
        assert [x['Key']['str'][0] for x in starts]==[-15,-11,-9,-5]
        starts.append({'Key':{'str':[10]},'Value':{'$type':'RogueEssence.Dungeon.SingleCharScriptEvent, RogueEssence','Script':'KingambitQAPreBattle','ArgTable':'{Type="'+r['id']+'"}'}})
        f.write_text(json.dumps(j,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    (profile/'SAVE').mkdir(parents=True);shutil.copyfile(SAVE,profile/'SAVE/SAVE.rssv')
    return c,profile


def tail(profile):
    return ''.join(f.read_text(encoding='utf-8',errors='replace') for f in (profile/'LOG').glob('*.txt'))


def stop(p):
    if p is None or p.poll() is not None:return
    p.terminate()
    try:p.wait(timeout=4)
    except sp.TimeoutExpired:p.kill();p.wait(timeout=4)


def keys():
    for k in ('Return','Return','Return','x','x'):
        sp.run(['xdotool','keydown',k],check=True);time.sleep(.14)
        sp.run(['xdotool','keyup',k],check=True);time.sleep(.84 if k=='Return' else .46)


def capture(root,c,profile,rs,sound):
    s=root/'audio.sock';s.unlink(missing_ok=True)
    pa=game=vid=None
    env={**os.environ,'SDL_AUDIODRIVER':'dummy'}
    try:
        if sound:
            env.update(SDL_AUDIODRIVER='pulseaudio',PULSE_SERVER='unix:'+str(s),PULSE_SINK='kingambit_probe')
            with (root/'pulse.log').open('w') as f:
                pa=sp.Popen(['pulseaudio','-n','--daemonize=no','--exit-idle-time=-1','--use-pid-file=false',
                     '-L',f'module-native-protocol-unix socket={s} auth-anonymous=1',
                     '-L','module-null-sink sink_name=kingambit_probe rate=48000 channels=2'],stdout=f,stderr=sp.STDOUT)
            for _ in range(30):
                if s.exists():break
                if pa.poll() is not None:break
                time.sleep(.1)
            assert s.exists(),(root/'pulse.log').read_text()
            sp.run(['pactl','info'],env=env,check=True,stdout=sp.DEVNULL)
        with (root/'Moteur.log').open('w') as f:
            game=sp.Popen([str(c/'PMDO'),'-appdata',str(profile)+'/', '-lang','en','-nolog'],cwd=c,env=env,stdout=f,stderr=sp.STDOUT)
        window=call(['xdotool','search','--sync','--onlyvisible','--name','Mystery Dungeon'],timeout=12).splitlines()[0]
        geom=dict(re.findall(r'^(\w+)=(-?\d+)$',call(['xdotool','getwindowgeometry','--shell',window]),re.M))
        assert set(geom)>={'X','Y','WIDTH','HEIGHT'}
        w,h=map(int,(geom['WIDTH'],geom['HEIGHT']));assert (w,h)==(640,480),(w,h,geom)
        # Les deux sources sont horodatées par la même horloge Unix. L'origine
        # d'entrée de x11grab (journal FFmpeg) fait foi, pas le lancement de Popen.
        cmd=['ffmpeg','-hide_banner','-loglevel','info','-nostats','-y','-copyts','-start_at_zero',
             '-thread_queue_size','256','-probesize','32','-analyzeduration','0','-f','x11grab','-draw_mouse','0',
             '-framerate','30','-video_size',f'{w}x{h}','-i',os.environ['DISPLAY']+f".0+{geom['X']},{geom['Y']}"]
        if sound:cmd+=['-thread_queue_size','256','-isync','0','-probesize','32','-analyzeduration','0',
                       '-f','pulse','-fragment_size','4096','-i','kingambit_probe.monitor']
        cmd+=['-c:v','libx264','-threads','2','-preset','ultrafast','-crf','16','-pix_fmt','yuv420p']
        if sound:cmd+=['-c:a','aac','-b:a','160k','-af','aresample=async=1:first_pts=0']
        cmd+=['-movflags','+faststart',str(root/'Brut.mp4')]
        with (root/'ffmpeg.log').open('w') as trace:
            t0=time.time(); vid=sp.Popen(cmd,env=env,stdin=sp.PIPE,stdout=trace,stderr=sp.STDOUT)
        (root/'T0.txt').write_text(str(t0))
        time.sleep(.85);keys()
        target=f'ALL DONE {len(rs)}'; begin=time.monotonic()
        prev=set()
        while time.monotonic()-begin<max(17,len(rs)*6):
            log=tail(profile)
            for k in re.findall(r'KINGAMBIT_PB COMBAT (\w+)',log):
                if k not in prev:print('PASS moteur',k,flush=True);prev.add(k)
            fault=[x for x in log.splitlines() if any(q in x for q in ('KINGAMBIT_PB ECHEC','Woosh de prébataille :','Son de prébataille :','Introduction de troupe :'))]
            assert not fault,'\n'.join(fault)
            if MARK+target in log:break
            if game.poll() is not None or vid.poll() is not None:raise RuntimeError('Arrêt de la capture : '+tail(profile)[-3500:])
            time.sleep(.25)
        else:raise TimeoutError('Finales non terminées : '+tail(profile)[-3500:])
        time.sleep(.38);vid.communicate(b'q\n',timeout=6);assert vid.returncode==0
        marks=[line for line in log.splitlines() if MARK in line or 'Version: 0.8.12' in line]
        (root/'Journal-PMDO.txt').write_text('\n'.join(marks)+'\n',encoding='utf-8')
        trace=(root/'ffmpeg.log').read_text()
        first=re.search(r"Input #0, x11grab[^\n]*\n\s*Duration: N/A, start: ([0-9.]+)",trace)
        assert first,trace[:2800]
        start_video=float(first[1]); assert abs(start_video-t0)<2,(start_video,t0)
        (root/'T0-video.txt').write_text(str(start_video)+'\n')
        p=re.compile(r'^\[([\d/:. ]+)\].*?KINGAMBIT_PB (ENTREES|WOOSH|FIN|COMBAT) (\w+)')
        data={x['id']:dict(x) for x in rs}
        for line in marks:
            m=p.match(line)
            if m:data[m[3]][m[2].lower()]=datetime.strptime(m[1],'%Y/%m/%d %H:%M:%S.%f').timestamp()-start_video
        for r in data.values():
            assert r['entrees']<r['woosh']<r['fin']<=r['combat']
            assert r['fin']-r['woosh']>1.32
        (root/'Captures.json').write_text(json.dumps(list(data.values()),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(f'{len(data)} finales / vidéo native et traces prêtes.',flush=True)
    finally:
        stop(vid);stop(game);stop(pa);s.unlink(missing_ok=True)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--type',nargs='+');ap.add_argument('--sans-son',action='store_true');a=ap.parse_args()
    assert os.environ.get('DISPLAY'),'lancer sous xvfb-run'
    a.out.mkdir(parents=True,exist_ok=True)
    r=rows()
    if a.type:r=[next(x for x in r if x['id']==t) for t in a.type]
    c,p=prepare(a.out,r);capture(a.out,c,p,r,not a.sans_son)


if __name__=='__main__':main()
