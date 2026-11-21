#!/usr/bin/env python3
"""Banc isolé PMDO 0.8.12 (Linux, Xvfb, xdotool, ImageMagick, Pillow, numpy).
La sauvegarde de test doit ouvrir test_grounds, pas une sauvegarde de joueur.
Lancer avec xvfb-run -a -s '-screen 0 960x720x24 -nolisten tcp' python …
"""
from pathlib import Path
import argparse, json, os, re, shutil, subprocess as sp, time
import numpy as np
from PIL import Image

HERE=Path(__file__).resolve().parent
MOD='Mega_Stones_Reverie'
SCRIPTS=Path('Data/Script')
MAP=SCRIPTS/'origin/ground/test_grounds/init.lua'
MODES={'foyer-fr':(True,False,True,'fr'), 'ensemble-fr':(True,True,False,'fr'),
       'ensemble-en':(True,True,False,'en'), 'ensemble-zh-hans':(True,True,False,'zh-hans'),
       'addon-fr':(False,True,False,'fr'),'destiny-zh-hans':(True,False,False,'zh-hans')}
TEXT_FIELDS={'fr':'description_fr','en':'description_par_defaut'}
VARIANTS={'mega_charizardite_x':'Dracaufeu-X','mega_charizardite_y':'Dracaufeu-Y',
          'mega_mewtwonite_x':'Mewtwo-X','mega_mewtwonite_y':'Mewtwo-Y'}


def lua(value):
    if isinstance(value,bool):return ['false','true'][value]
    if isinstance(value,list):return '{'+','.join(map(lua,value))+'}'
    return json.dumps(value,ensure_ascii=False)


def qt_tap(key):
    sp.run(['xdotool','keydown',key],check=True)
    time.sleep(.105)
    sp.run(['xdotool','keyup',key],check=True)


def locate(screen,glyph,where):
    """Ne compare que les pixels opaques, à la taille exacte de l'UI.
    Recherche de corrélation exacte, couleur native et de tous les pixels.
    """
    pic=Image.open(screen).convert('RGB'); ico=Image.open(glyph).convert('RGBA')
    scale=pic.width//320;assert pic.size==(320*scale,240*scale)
    im=np.asarray(pic);ic=np.asarray(ico.resize((ico.width*scale,ico.height*scale),Image.Resampling.NEAREST));
    coords=np.argwhere(ic[:,:,3]==255); y,x=coords[len(coords)//2]; clr=ic[y,x,:3]
    xx1,yy1,xx2,yy2=[n*scale for n in where]
    z=im[yy1:yy2,xx1:xx2,:]
    yy,xx=np.nonzero(np.all(z==clr,axis=-1)); ys,xs=yy-y+yy1,xx-x+xx1
    rgb=ic[coords[:,0],coords[:,1],:3]
    for k in range(len(ys)):
        a,b=int(ys[k]),int(xs[k]);
        if yy1<=a<=yy2-ic.shape[0] and xx1<=b<=xx2-ic.shape[1]:
            if np.array_equal(im[a+coords[:,0],b+coords[:,1],:],rgb):return b/scale,a/scale
    return None


def copier(src,dest):
    dest.parent.mkdir(parents=True,exist_ok=True)
    if dest.is_symlink():dest.unlink()
    shutil.copy2(src,dest)


def run(a):
    dest,add,riddle,lang=MODES[a.mode];work=a.out/a.mode; p=work/'profil';game=work/'PMDO';mods=p/'MODS'
    assert not work.exists(),f'Choisir une sortie neuve : {work}'
    work.mkdir(parents=True); modpath=mods/'Destiny'; gen=a.gen
    sp.run(['cp','-as',str(a.runtime.resolve()),str(game)],check=True)
    if dest:
        shutil.copytree(gen/'Destiny',modpath)
        copier(a.destiny/'game/Mod.xml',modpath/'Mod.xml')
        for m in ['reverie_foyers','reverie_foyers_recits','cinematique','reverie_recit','suivi_interieurs','equipe_scene']:
            f=SCRIPTS/'destiny'/(m+'.lua');copier(a.destiny/'game'/f,modpath/f)
    if add:
        shutil.copytree(a.destiny/'addons'/MOD,mods/MOD)
        shutil.copytree(gen/'AddOn',mods/MOD,dirs_exist_ok=True)
    (p/'CONFIG').mkdir(parents=True,exist_ok=True)
    (p/'CONFIG/Config.xml').write_text(f'''<Config>
  <BGM>0</BGM><SE>0</SE><BattleFlow>Normal</BattleFlow><DefaultSkills>Attacks</DefaultSkills>
  <Minimap>100</Minimap><MinimapColor>White</MinimapColor><TextSpeed>1</TextSpeed>
  <Border>0</Border><Window>2</Window><Language>{lang}</Language><InactiveInput>False</InactiveInput>
</Config>''')
    copier(a.save,(p/'SAVE'/('MODS/Destiny' if dest else '')/'SAVE.rssv'))
    rows=json.loads((gen/'Registre-icones.json').read_text())['items']
    rows=[r for r in rows if (dest if r['genre']=='baie' else add)]
    keys=[r['id'] for r in rows]; mega=[k for k in keys if k.startswith('mega_')]; berries=[k for k in keys if k.startswith('berry_')]
    # La dernière page inscrit Pêcha en tête pour ouvrir son résumé.
    if 'berry_pecha' in berries:berries.insert(0,berries.pop(berries.index('berry_pecha')))
    pages=[mega[i:i+8] for i in range(0,len(mega),8)]+([berries+['berry_oran','food_apple']] if berries else [])
    sizes=[]
    for row in rows:
        desc=row[TEXT_FIELDS[lang]] if lang in TEXT_FIELDS else False
        assert desc or lang not in TEXT_FIELDS, (row['id'],lang)
        with Image.open(gen/'Dessins/Objet'/(row['id']+'.png')) as im:sizes.append([row['id'],row['ico'],row['sprite'],*im.size,desc])
    script=(HERE/'banc_icones.lua').read_text(encoding='utf-8')
    for k,v in dict(ROWS=sizes,PAGES=pages,ADDON=add,DESTINY=dest,RIDDLE=riddle,LANG=lang).items():script=script.replace('__'+k+'__',lua(v))
    trial=game/MAP;trial.unlink();trial.write_text(script,encoding='utf-8')
    args=[str(game/'PMDO'),'-asset',str(game)+'/', '-appdata',str(p)+'/', '-lang',lang]
    if dest:args+=['-quest','Destiny']
    if add:args+=['-mod',MOD]
    env=os.environ|{'SDL_AUDIODRIVER':'dummy','LIBGL_ALWAYS_SOFTWARE':'1'}
    qa=[]; window=None; events=0; finish=False; matches=[]
    start=time.monotonic(); last_key=start; delay=1.4; pending=''
    with (work/'Moteur.log').open('w') as stderr:
        proc=sp.Popen(args,cwd=game,env=env,stdout=stderr,stderr=stderr)
        try:
            def snap(fname):
                f=work/fname
                sp.run(['import','-window',window,'-define','png:color-type=2',str(f)],check=True,timeout=4)
                return f
            glyphs=gen/'Dessins/Glyphe'
            while time.monotonic()-start<94 and proc.poll() is None:
                time.sleep(.04)
                if window is None:
                    res=sp.run(['xdotool','search','--onlyvisible','--class','^PMDO$'],text=True,capture_output=True)
                    if res.returncode==0:
                        window=res.stdout.strip().splitlines()[-1]
                        sp.run(['xdotool','windowfocus',window,'mousemove','--window',window,'636','476'],check=True)
                raw=''.join(f.read_text(errors='replace') for f in sorted((p/'LOG').glob('*.txt')))
                qa=re.findall(r'QA_ICONE ([^\n\r]+)',raw)
                if not qa and window and time.monotonic()-last_key>delay:
                    qt_tap('Return');last_key=time.monotonic();delay=.85
                if len(qa)==events:
                    if pending in ('DIALOG','RECIPIENT') and time.monotonic()-last_key>.65:
                        qt_tap('Return');last_key=time.monotonic()
                    continue
                for event in qa[events:]:
                    pending=event.partition(' ')[0]
                    head,_,rest=event.partition(' ')
                    if head=='FAIL':raise RuntimeError(event)
                    if head=='FONT':print(a.mode,event,flush=True)
                    if head in ('DIALOG','CHOICE','RECIPIENT'):
                        time.sleep(.34)
                        if head=='CHOICE':qt_tap('Down');time.sleep(.08)
                        if head=='RECIPIENT':
                            f=snap('Recompense-Pecha.png');spot=locate(f,glyphs/'berry_pecha.png',(8,174,315,240))
                            if spot is None:time.sleep(.38);f=snap(f.name);spot=locate(f,glyphs/'berry_pecha.png',(8,174,315,240))
                            assert spot is not None,'Émoticône Pêcha absente du dialogue'+str(f)
                            matches.append(f'{f.name}: berry_pecha @ {spot}')
                        qt_tap('Return');last_key=time.monotonic();time.sleep(.12)
                    if head=='BAG':
                        time.sleep(.24)
                        n=int(rest);f=snap(f'Sac-{n:02d}.png')
                        for k in pages[n-1]:
                            if k not in keys:continue
                            spot=locate(f,glyphs/(k+'.png'),(19,27,61,174));assert spot is not None,(k,f)
                            matches.append(f'{f.name}: {k} @ {spot}')
                        if a.mode=='ensemble-fr':
                            cursor=0
                            for i,k in enumerate(pages[n-1]):
                                if k not in VARIANTS:continue
                                for _ in range(i-cursor):
                                    qt_tap('Down');time.sleep(.09)
                                cursor=i
                                snap('Description-'+VARIANTS[k]+'.png')
                        print(a.mode,'SAC',n,len(pages[n-1]),flush=True)
                        qt_tap('z')
                    if head=='DONE':
                        assert rest==f'{len(rows)} {len(pages)}'
                        assert len(matches)==len(rows)+int(riddle)
                        if lang in TEXT_FIELDS:
                            seen={e.partition(' ')[2].partition(' ')[0]:e.partition(' ')[2].partition(' ')[2]
                                  for e in qa if e.startswith('DESCRIPTION ')}
                            assert seen=={row['id']:row[TEXT_FIELDS[lang]] for row in rows},'descriptions du moteur'
                        if riddle:assert set(['GIFT_ONE berry_pecha','GIFT_ONCE berry_pecha']).issubset(qa)
                        if 'Version: 0.8.12.0' not in raw:raise RuntimeError('version inattendue')
                        finish=True
                events=len(qa)
                if finish:break
            assert finish,(a.mode,'échec : pas de DONE',qa[-6:])
        finally:
            proc.terminate()
            try:proc.wait(timeout=5)
            except sp.TimeoutExpired:proc.kill();proc.wait()
            (work/'Contrôle.txt').write_text('PMDO Linux 0.8.12.0 / '+a.mode+'\n'+'\n'.join(qa+['CORRESPONDANCE pixel exact:']+matches)+'\n',encoding='utf-8')
    print(f'{a.mode}: PASS {len(rows)} sprites chargés ; {len(matches)} glyphes reconnus pixel par pixel',flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for k in ('runtime','destiny','gen','save','out'):p.add_argument('--'+k,type=Path,required=True)
    p.add_argument('--mode',choices=MODES,required=True)
    run(p.parse_args())
