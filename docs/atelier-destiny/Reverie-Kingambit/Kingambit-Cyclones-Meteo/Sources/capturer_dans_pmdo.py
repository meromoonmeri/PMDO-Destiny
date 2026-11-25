#!/usr/bin/env python3
"""Banc isolé et réversible. Capture l'intro réelle et l'activation au sac dans PMDO.

À lancer avec xvfb-run sur une copie de la base d'essai PMDO 0.8.12 utilisée par le
précédent lot. Le seul rôle du Lua QA : poser le joueur dans l'arène, lui donner
la bonne pierre, et horodater l'action. Le test n'est jamais appliqué à Destiny.
"""
from datetime import datetime
from pathlib import Path
import glob, json, os, re, shutil, subprocess as sp, time

D=Path.home()/'.cache/spawns-kingambit'; C=D/'runtime12/jeu/PMDO'; T=D/'cyclones'; N=T/'natif'
BASE=D/'export/Mega/Addon/Mega_Stones_Reverie'; G=C/'Data/Script/origin'; S=D/'source/game'
CASES=[(9,'flying','charizard','mega_charizardite_x'),(14,'dragon','altaria','mega_altarianite'),(2,'water','blastoise','mega_blastoisinite'),(1,'fire','blaziken','mega_blazikenite')]
LOG={k:'[{ts}]' for _,k,_,_ in CASES}
WRAP='''
-- Trace d'essai uniquement, hors du patch de quête et de l'addon livré.
local original_compat=BATTLE_SCRIPT.CancelIfWrongMon
function BATTLE_SCRIPT.CancelIfWrongMon(o,c,x,a)
  original_compat(o,c,x,a)
  if not x.CancelState.Cancel then PrintInfo('KINGAMBIT_FX MEGA_ACTION '..x.User.BaseForm.Species) end
end
local original_mega=BATTLE_SCRIPT.Mega_Evolve
function BATTLE_SCRIPT.Mega_Evolve(o,c,x,a)
  original_mega(o,c,x,a)
  PrintInfo('KINGAMBIT_FX MEGA_FORM '..x.User.CurrentForm.Species..' '..x.User.CurrentForm.Form)
end
'''
AFTER='''
local intro_kingambit=SINGLE_CHAR_SCRIPT.DestinyDojoTroupeJouer
function SINGLE_CHAR_SCRIPT.DestinyDojoTroupeJouer(o,c,x,a)
  intro_kingambit(o,c,x,a)
  if not x or x.User~=nil then return end
  local p=GAME:GetPlayerPartyMember(0)
  DUNGEON:CharSetAction(p,RogueEssence.Dungeon.CharAnimIdle(p.CharLoc,Direction.Down))
end
'''
START='''local q={}
function q.Enter(map)
  if q.started then return end
  q.started=true
  local ch=GAME:GetPlayerPartyMember(0)
  ch:Promote(RogueEssence.Dungeon.MonsterID('$POKEMON',0,ch.BaseForm.Skin,ch.BaseForm.Gender))
  ch.Nickname=''
  GAME:GivePlayerItem('$PIERRE',1,false,'')
  GAME:FadeIn(1)
  GAME:WaitFrames(25)
  GAME:EnterDungeon('dojo_kingambit_dedales',$SEGMENT,2,0,RogueEssence.Data.GameProgress.DungeonStakes.Progress,false,false)
end
q.GameLoad=q.Enter
return q
'''

def call(*cmd,**kw):return sp.check_output(cmd,text=True,**kw)

def tap(k,dt=.27):
    sp.run(['xdotool','keydown',k],check=True);time.sleep(.125)
    sp.run(['xdotool','keyup',k],check=True);time.sleep(dt)

def readlog(profile):
    return ''.join(p.read_text(encoding='utf-8',errors='replace') for p in (profile/'LOG').glob('*.txt'))

def wait_log(profile,text,proc,t=10):
    start=time.monotonic()
    while time.monotonic()-start<t:
        log=readlog(profile)
        if text in log:return log
        if proc.poll() is not None:break
        time.sleep(.095)
    raise RuntimeError(f'Marqueur absent {text}: {readlog(profile)[-3800:]}')

def relative(log,text,why):
    row=next((r for r in log.splitlines() if text in r),None)
    assert row and row[0]=='[',(text,why)
    return datetime.strptime(row[1:row.index(']')],'%Y/%m/%d %H:%M:%S.%f').timestamp()

def take(q,kind,species,stone,loader):
    profile=N/'profils'/kind; profile.mkdir(parents=True,exist_ok=True)
    for b in ('LOG','SAVE'):
        target=profile/b
        if target.exists():shutil.rmtree(target)
        target.mkdir()
    (profile/'MODS').mkdir(exist_ok=True)
    mod=profile/'MODS/Mega_Stones_Reverie'
    if mod.exists():shutil.rmtree(mod)
    shutil.copytree(BASE,mod)
    with (mod/'Data/Script/megastones/event_battle.lua').open('a',encoding='utf-8') as file:file.write(WRAP)
    shutil.copy2(D/'profil/SAVE/SAVE.rssv',profile/'SAVE/SAVE.rssv')
    loader.write_text(START.replace('$SEGMENT',str(q)).replace('$POKEMON',species).replace('$PIERRE',stone),encoding='utf-8')
    pr=None;ff=None
    try:
        with (N/(kind+'.stdout.log')).open('w') as stdout:
            pr=sp.Popen([str(C/'PMDO'),'-appdata',str(profile)+'/', '-mod','Mega_Stones_Reverie','-lang','en','-nolog'],cwd=C,stdout=stdout,stderr=sp.STDOUT,env={**os.environ,'SDL_AUDIODRIVER':'dummy'})
        time.sleep(1.05)
        win=call('xdotool','search','--sync','--onlyvisible','--name','Mystery Dungeon',timeout=10).splitlines()[0]
        geom=dict(re.findall(r'^(\w+)=(\d+)$',call('xdotool','getwindowgeometry','--shell',win),re.M))
        w,h=geom['WIDTH'],geom['HEIGHT'];loc=os.environ['DISPLAY']+f".0+{geom['X']},{geom['Y']}"
        t0=time.time()
        ff=sp.Popen(['ffmpeg','-v','error','-y','-f','x11grab','-draw_mouse','0','-framerate','30','-video_size',f'{w}x{h}','-i',loc,'-c:v','libx264','-threads','1','-preset','ultrafast','-crf','17','-pix_fmt','yuv420p',str(N/f'{kind}.mp4')],stdin=sp.PIPE)
        time.sleep(.95)
        for k in ('Return','Return','Return','x','x'):tap(k,.92 if k=='Return' else .7)
        end=wait_log(profile,'KINGAMBIT_QA end '+kind,pr,13)
        assert 'count=3' in end and 'Introduction de troupe :' not in end,kind
        time.sleep(.43)
        for k in ('Escape','Down','x','x','x','x'):tap(k,.29)
        wait_log(profile,'KINGAMBIT_FX MEGA_ACTION '+species,pr,6)
        log=wait_log(profile,'KINGAMBIT_FX MEGA_FORM '+species+' 1',pr,10)
        time.sleep(1.85)
        log=readlog(profile)
        assert 'JsonSerializationException' not in log and 'Error loading chara' not in log and 'Introduction de troupe :' not in log,kind
        t_intro=relative(log,'KINGAMBIT_QA start '+kind,'intro')-t0
        t_end=relative(log,'KINGAMBIT_QA end '+kind,'fin')-t0
        t_action=relative(log,'KINGAMBIT_FX MEGA_ACTION '+species,'action')-t0
        t_mega=relative(log,'KINGAMBIT_FX MEGA_FORM '+species,'forme')-t0
        assert t_intro>0 and t_end>t_intro and t_action>t_end and t_mega>t_action
        print(f'PASS {kind} : 3 combattants, activation de {stone}, sprite Méga {species} forme 1.',flush=True)
        (N/f'{kind}.journal.txt').write_text('\n'.join(s for s in log.splitlines() if 'KINGAMBIT' in s or 'Version: 0.8.12' in s or 'Queued mod' in s)+'\n',encoding='utf-8')
        return dict(type=kind,species=species,stone=stone,video=kind+'.mp4',intro=t_intro,fin=t_end,action=t_action,mega=t_mega,size=[int(w),int(h)])
    finally:
        if ff is not None:
            try:ff.communicate(b'q\n',timeout=5)
            except sp.TimeoutExpired:ff.terminate();ff.wait(timeout=4)
        if pr is not None:
            pr.terminate()
            try:pr.wait(timeout=6)
            except sp.TimeoutExpired:pr.kill();pr.wait(timeout=4)

def main():
    assert os.environ.get('DISPLAY') and (C/'PMDO').is_file()
    N.mkdir(parents=True,exist_ok=True)
    loader=G/'ground/test_grounds/init.lua'; event=G/'event_single.lua'; script=G/'dojo_kingambit_troupes.lua'
    targets={loader:None,event:None,script:S/'Data/Script/destiny/dojo_kingambit_troupes.lua'}
    for f in (T/'Content').rglob('*.dir'):targets[C/f.relative_to(T)]=f
    originals={q:q.read_bytes() if q.exists() else None for q in targets}
    assert 'KINGAMBIT_QA' in event.read_text()
    try:
        for q,p in targets.items():
            if p is not None:
                q.parent.mkdir(exist_ok=True,parents=True);shutil.copyfile(p,q)
        with event.open('a',encoding='utf-8') as out:out.write(AFTER)
        result=[]
        for k in CASES:
            result.append(take(*k,loader))
            (N/'Captures.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    finally:
        for q,b in originals.items():
            if b is None:q.unlink(missing_ok=True)
            else:q.write_bytes(b)
if __name__=='__main__':main()
