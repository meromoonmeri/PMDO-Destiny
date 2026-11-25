#!/usr/bin/env python3
"""Montage des vraies captures : écran entier pour l'entrée, zoom entier ×2 pour la Méga."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json, subprocess as sp, math
from PIL import Image, ImageDraw, ImageFont

O=Path(__file__).resolve().parents[1]
D=Path.home()/'.cache/spawns-kingambit';T=D/'cyclones';N=T/'natif';F=T/'montage'
W,H=1280,720; X,Y=68,122
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans'; MONO='/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'
STYLE={
'flying': {'type':'Vol','couleur':'#a0ecf4','boss':'Dracaufeu','mega':'Méga-Dracaufeu X','pierre':'Dracaufite X','effet':'Cyclone des alizés','phases':['Amorce','Ascension','Rafales'],'texte':['Trois colonnes de vent s’élèvent.','Les combattants plongent dans l’œil.'],'motif':'vol-cyclone'},
'dragon': {'type':'Dragon','couleur':'#ccadf3','boss':'Altaria','mega':'Méga-Altaria','pierre':'Altarite','effet':'Vortex draconique','phases':['Cercle','Vortex','Éclats'],'texte':['Les spirales violettes se resserrent.','La troupe bondit au cœur du vortex.'],'motif':'dragon-cyclone'},
'water': {'type':'Eau','couleur':'#81cdf1','boss':'Tortank','mega':'Méga-Tortank','pierre':'Tortankite','effet':'Colonnes sous l’averse','phases':['Averse','Chutes','Ondes'],'texte':['La pluie commence avant la chute.','Les impacts laissent des ronds dans l’eau.'],'motif':'eau-averse'},
'fire': {'type':'Feu','couleur':'#ffb47d','boss':'Braségali','mega':'Méga-Braségali','pierre':'Braségalite','effet':'Colonnes de canicule','phases':['Chaleur','Chutes','Braises'],'texte':['L’air ondule autour des colonnes.','Les braises remontent après l’impact.'],'motif':'feu-braises'},
}

def font(s,b=False,mono=False):return ImageFont.truetype(MONO if mono else FONT+('-Bold' if b else '')+'.ttf',s)

def panel(k,i,mega):
    p=STYLE[k];a=p['couleur'];im=Image.new('RGB',(W,H),'#101820');d=ImageDraw.Draw(im);light='#f2f1ea';mid='#a3b4bf';line='#293b47'
    def text(x,y,s,z,c=light,b=False,m=False):d.text((x,y),s,font=font(z,b,m),fill=c)
    d.rectangle((0,0,W,4),fill=a);d.line((X,93,1212,93),fill=line,width=1)
    text(X,39,'DOJO KINGAMBIT',28,light,True);text(361,48,'/  Réverie',17,mid)
    d.rounded_rectangle((1038,41,1212,68),5,fill='#22323f');text(1051,45,'PMDO  0.8.12',16,'#cfe0e7',False,True)
    d.rectangle((X-1,Y-1,X+640,Y+480),outline='#758b97',width=1)
    d.rectangle((X-1,Y-1,X+42,Y),fill=a);d.rectangle((X-1,Y-1,X,Y+37),fill=a)
    x=755
    pill=f'{i:02} / 04   {p["type"].upper()}';d.rounded_rectangle((x,129,x+219,162),6,fill='#21313d')
    text(x+11,135,pill,18,a,True,True)
    text(x,197,'MÉGA-ÉVOLUTION' if mega else 'APPARITION',16,a,True)
    name=p['mega'] if mega else p['effet'];z=39
    while d.textlength(name,font=font(z,True))>451:z-=1
    text(x,230,name,z,light,True)
    text(x,290,p['pierre']+' · activation depuis le sac' if mega else 'Chef : '+p['boss'],19,mid)
    d.line((x,343,1212,343),fill=line,width=1)
    labs=['Charge','Éclosion','Forme Méga'] if mega else p['phases']
    for j,lab in enumerate(labs):
        o=x+j*151;d.line((o,368,o+137,368),fill=a,width=2);text(o,383,f'0{j+1}',13,a,False,True);text(o,405,lab,18,light,True)
    if mega:
        text(x,488,'Transformation capturée dans le moteur.',17,mid)
        text(x,517,'Le porteur est joué sur le banc de test.',17,mid)
        text(x,566,'ZOOM ×2 SUR LE PORTEUR',14,a,False,True)
    else:
        for j,s in enumerate(p['texte']):text(x,487+j*27,s,17,mid)
        text(x,564,'1 MAÎTRE   +   2 CADETS',14,a,False,True)
    d.line((X,637,1212,637),fill=line,width=1)
    text(X,656,'CAPTURE NATIVE · BANCS DE TEST' if mega else 'CAPTURE NATIVE · AVANT COMBAT',15,mid,False,True)
    text(943,656,'APPARITION   /   MÉGA',15,a,False,True)
    for j in range(4):d.rectangle((1166+j*13,659,1174+j*13,667),fill=a if i==j+1 else '#4e666e')
    dest=F / f'{i:02}-{k}-{"mega" if mega else "intro"}.png';im.save(dest);return dest

def probe(p):return float(sp.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(p)],text=True).strip())

def render(i,case,mega):
    k=case['type']; src=N/case['video'];end=probe(src)
    img=panel(k,i,mega); out=img.with_suffix('.mp4')
    if mega:
        start=max(case['fin']+.8,case['action']-.34)
        until=min(end-.05,case['mega']+1.66)
        delay=max(0,round(1000*(case['mega']-start-3.8)))
        sound=D/'export/Mega/Addon/Mega_Stones_Reverie/Content/Sound/Battle/Mega_Evolution.ogg'
        video='[0:v]crop=320:240:160:222,scale=640:480:flags=neighbor,setpts=PTS-STARTPTS[jeu]'
    else:
        start=max(0,case['intro']-.16);until=min(case['fin']+.53,case['action']-1.05)
        delay=round(1000*(case['intro']-start))
        sound=D/'runtime12/jeu/PMDO/Content/Sound/Battle'/f'Kingambit_Whoosh_{k}.ogg'
        video='[0:v]setpts=PTS-STARTPTS[jeu]'
    n=math.floor((until-start)*30); dur=n/30
    assert case['size']==[640,480] and dur>1.9 and sound.exists()
    filters=f'{video};[1:v][jeu]overlay={X}:{Y}:shortest=1:format=auto,format=yuv420p[image];[2:a]adelay={delay}:all=1,volume={.86 if mega else .78},apad,atrim=duration={dur:.6f},aresample=44100[audio]'
    args=['ffmpeg','-nostdin','-hide_banner','-v','error','-y','-threads','1','-ss',f'{start:.4f}','-i',str(src),'-loop','1','-framerate','30','-i',str(img),'-i',str(sound),'-filter_complex_threads','1','-filter_complex',filters,'-map','[image]','-map','[audio]',
          '-t',f'{dur:.9f}','-c:v','libx264','-threads','1','-preset','veryfast','-crf','17','-pix_fmt','yuv420p','-r','30','-c:a','aac','-ar','44100','-ac','2','-b:a','144k','-movflags','+faststart',str(out)]
    sp.run(args,check=True);return out,dur

def join(entries,dest,slug):
    lst=F/(slug+'.txt'); lst.write_text(''.join(f"file '{path.name}'\nduration {d:.6f}\n" for path,d,label in entries))
    meta=F/(slug+'.ffmeta'); pos=0; data=[';FFMETADATA1','title=Dojo Kingambit — Cyclones, météo et Méga-Évolution']
    for path,d,label in entries:
        end=pos+d;data+=['[CHAPTER]','TIMEBASE=1/1000',f'START={round(pos*1000)}',f'END={round(end*1000)}',f'title={label}'];pos=end
    meta.write_text('\n'.join(data)+'\n',encoding='utf-8')
    sp.run(['ffmpeg','-nostdin','-v','error','-y','-f','concat','-safe','0','-i',str(lst),'-f','ffmetadata','-i',str(meta),'-map','0:v','-map','0:a','-map_metadata','1','-map_chapters','1','-c','copy','-movflags','+faststart',str(dest)],check=True)

def main():
    cases=json.loads((N/'Captures.json').read_text()); assert [c['type'] for c in cases]==list(STYLE)
    F.mkdir(parents=True,exist_ok=True)
    jobs=[(i,case,x) for i,case in enumerate(cases,1) for x in (False,True)]
    with ThreadPoolExecutor(max_workers=2) as ex:out=list(ex.map(lambda x:render(*x),jobs))
    entries=[(p,d,STYLE[c['type']]['mega' if m else 'effet']) for (p,d),(_,c,m) in zip(out,jobs)]
    join(entries,O/'Apercu-Cyclones-Meteo-et-Mega.mp4','tout')
    join(entries[1::2],O/'Les-quatre-Mega-Evolutions.mp4','mega')
    print('Aperçus natifs exportés ; chapitres en secondes :')
    t=0
    for _,d,l in entries:print(f'{t:5.2f}  {l}');t+=d
if __name__=='__main__':main()
