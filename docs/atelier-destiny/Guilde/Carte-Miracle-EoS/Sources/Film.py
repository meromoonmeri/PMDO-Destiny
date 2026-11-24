"""Render the exact same scene clock and sprites as the offline player into a short H.264/AAC film.
Requires Node.js, Pillow and ffmpeg. Use --trajet saline for the short scene taken from the game's script.
"""
from __future__ import annotations
from argparse import ArgumentParser
from array import array
from fractions import Fraction
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import json, math, subprocess, sys, tempfile, wave

ROOT=Path(__file__).resolve().parents[1];S=ROOT/'Sources';D=json.loads((ROOT/'Calques/Animation.json').read_text())
W,H=1280,864
SX,SY=36,129; WIDTH,HEIGHT=768,576
RX=839; RIGHT=1243
PAPER='#fff0cd'; GOLD='#f1cf8d'; MUTED='#bdc4ad'; DIM='#96a591'; INK='#162621'; EDGE='#536250'
SANS='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'; BOLD=SANS.replace('.ttf','-Bold.ttf');SERIF=SANS.replace('Sans','Serif');SB=SERIF.replace('.ttf','-Bold.ttf');MONO=SANS.replace('Sans','SansMono')
FONTS={}
def font(n,f=SANS):
    if (n,f) not in FONTS:FONTS[n,f]=ImageFont.truetype(f,n)
    return FONTS[n,f]
def txt(d,s,x,y,n=15,fill=PAPER,f=SANS,anchor='lt'):
    d.text((x,y),s,fill=fill,font=font(n,f),anchor=anchor)
def linewrap(d,s,width,n=16,f=SANS):
    acc=[];l=''
    for word in s.split():
        next=(l+' '+word).strip()
        if d.textlength(next,font=font(n,f))>width and l:acc.append(l);l=word
        else:l=next
    if l:acc.append(l)
    return acc

def paragraph(d,s,x,y,width,n=16,leading=24,fill=MUTED):
    for l in linewrap(d,s,width,n):txt(d,l,x,y,n,fill);y+=leading
    return y

def icon(d,x,y,r=13):
    d.ellipse((x-r,y-r,x+r,y+r),outline=GOLD,width=1)
    for i in range(4):
        dx=round(math.sin(math.pi*i/2));dy=round(math.cos(math.pi*i/2));d.line((x+dx*r,y+dy*r,x+dx*(r+4),y+dy*(r+4)),fill=GOLD,width=1)
    d.polygon([(x+8,y-8),(x+3,y+3),(x-8,y+8),(x-3,y-3)],outline=GOLD)
    d.polygon([(x+8,y-8),(x+3,y+3),(x-3,y-3)],fill=GOLD)

IMAGES={}
def picture(meta):
    p=meta['fichier'];
    if p not in IMAGES:IMAGES[p]=Image.open(ROOT/p).convert('RGBA')
    return IMAGES[p]

def frame_map(s,full=False):
    c=s['cam'] if not full else dict(x=0,y=0,w=504,h=336);x,y,w,h=c['x'],c['y'],c['w'],c['h'];box=(x,y,x+w,y+h)
    a=picture(D['terrain']).crop(box);a.alpha_composite(picture(D['masques'][str(s['level'])]).crop(box))
    for o in s['sprites']:
        m=(D['reperes'] if o['family']=='reperes' else D['brume_mobile'] if o['family']=='brume' else D['pikachu']['poses'])[str(o['pose'])]
        dx,dy=m['coin_relatif'];a.alpha_composite(picture(m),(o['x']+dx-x,o['y']+dy-y))
    a=a.convert('RGB')
    if s['black']:a=Image.blend(a,Image.new('RGB',a.size,'black'),s['black'])
    return a

def background():
    plate=Image.new('RGB',(W,H));d=ImageDraw.Draw(plate)
    for y in range(H):
        q=y/(H-1);col=(int(44-24*q),int(62-32*q),int(51-25*q));d.line((0,y,W,y),fill=col)
    for r in range(120,650,35):d.ellipse((W-r*1.62,-r*.65,W+r*1.62,r*.87),outline='#52604b',width=1)
    d.rectangle((0,116,W,H),fill='#14251f');d.line((36,26,W-36,26),fill='#7c7f5b',width=1)
    icon(d,53,54);txt(d,'ARCHIVES DE LA GUILDE',78,47,13,GOLD,BOLD);txt(d,'NINTENDO DS  /  EXPLORATEURS DU CIEL',W-38,48,12,MUTED,MONO,'rt')
    title='La Carte Miracle';txt(d,title,36,70,40,PAPER,SERIF)
    xx=36+d.textlength(title,font=font(40,SERIF))+18
    txt(d,'en mouvement',xx,75,32,GOLD,SERIF)
    d.rounded_rectangle((SX-6,SY-6,SX+WIDTH+5,SY+HEIGHT+5),radius=4,fill='#0d1a16',outline=EDGE,width=1)
    d.rounded_rectangle((RX,SY,RIGHT,H-55),radius=12,fill='#1c3028',outline=EDGE,width=1)
    d.line((36,H-37,RIGHT,H-37),fill='#4b5f4e')
    txt(d,'PMDO DESTINY  /  RECONSTITUTION DOCUMENTAIRE',36,H-27,10,DIM,MONO)
    txt(d,'POKÉMON DONJON MYSTÈRE',RIGHT,H-27,10,DIM,MONO,'rt')
    return plate

def time(t):
    v=t/D['fps']; return f'{int(v)//60:02}:{(v%60):04.1f}'

def decorate(plate,s,plan):
    d=ImageDraw.Draw(plate);unlock=s['part']=='deblocage';T=plan['T'];U=plan['U'];x=RX+22;xr=RIGHT-22;wide=xr-x
    d.rectangle((SX,SY,SX+WIDTH-1,SY+HEIGHT-1),outline='#f1d39d',width=1)
    for xx,yy,ss,sy in [(SX,SY,1,1),(SX+WIDTH-1,SY,-1,1),(SX,SY+HEIGHT-1,1,-1),(SX+WIDTH-1,SY+HEIGHT-1,-1,-1)]:
        d.line((xx+ss*14,yy,xx,yy,xx,yy+sy*14),fill='#ffe6b5',width=2)
    txt(d,'ÉCRAN SUPÉRIEUR  /  256 × 192',SX,SY+HEIGHT+14,10,MUTED,MONO)
    txt(d,f'S01P01A    PALIER {s["level"]}',SX+WIDTH,SY+HEIGHT+14,10,MUTED,MONO,'rt')
    d.rounded_rectangle((SX,742,SX+WIDTH,808),radius=5,fill='#f2e6c3'); d.polygon([(SX+16,759),(SX+22,765),(SX+16,771),(SX+10,765)],fill='#ad8950')
    txt(d,s['kind'],SX+32,752,18,'#312517',SB)
    txt(d,s['caption'],SX+32,778,14,'#3b3323',SANS)
    d.line((x,190,xr,190),fill='#52614f')
    txt(d,'01' if unlock else '02',x,149,29,GOLD,SERIF)
    txt(d,'DÉBLOCAGE' if unlock else 'VOYAGE',x+54,156,14,GOLD,BOLD)
    txt(d,'Île Blizzard' if unlock else T['nom'],x,210,34,PAPER,SERIF)
    if unlock:
        txt(d,'SCÈNE DU JEU  /  P01P01A',x,258,11,GOLD,MONO)
        paragraph(d,'Les nuages se lèvent sur la Région Gelée. Le jingle retentit quand le point rouge et jaune apparaît.',x,287,wide,16)
        d.rounded_rectangle((x,379,xr,538),radius=9,fill='#14261f',outline='#53604c');txt(d,'REPÈRES CANONIQUES',x+14,395,12,GOLD,BOLD)
        for i,(pose,label) in enumerate([(2,'Jaune fixe'),(9,'Jaune atténué'),(4,'Rouge')]):
            ax=x+16+i*112; dd=picture(D['reperes'][str(pose)]).resize((32,32),Image.Resampling.NEAREST)
            plate.paste(dd,(ax+4,428),dd);txt(d,label,ax,467,12,MUTED)
        txt(d,'Un seul repère, plusieurs poses.',x+14,505,13,PAPER)
        if s['t']>=U['jingle']:
            d.rounded_rectangle((x,566,xr,616),radius=6,fill='#edcf8e')
            txt(d,'♪',x+13,577,23,'#2b2115',BOLD);txt(d,'Fanfare de déblocage · ME 06',x+43,583,14,'#2b2115',BOLD)
        else:
            d.rounded_rectangle((x,566,xr,616),radius=6,fill='#2c4034',outline='#61705b')
            txt(d,'Fanfare au signal du repère',x+13,584,14,MUTED,BOLD)
    else:
        desc='SCÈNE DU JEU  /  G01P04A' if T['canonique'] else 'TRAJET RECOMPOSÉ'
        txt(d,desc,x,258,11,GOLD,MONO)
        txt(d,'Bourg-Trésor → '+T['nom'],x,286,15,PAPER,BOLD)
        paragraph(d,'Déplacement de la scène du jeu.' if T['canonique'] else 'Deux points natifs et la marche du héros.',x,314,wide,15,23)
        # A wide shot of the same moment makes the character's move visible even
        # while the camera follows it in the main 256 × 192 window.
        mini=frame_map(s,full=True).resize((348,232),Image.Resampling.NEAREST)
        cent=x+(wide-mini.width)//2;plate.paste(mini,(cent,358))
        d.rectangle((cent-1,357,cent+mini.width,590),outline='#c4a878',width=1)
        txt(d,'CARTE ENTIÈRE  /  SUIVI DU TRAJET',x,606,10,MUTED,MONO)
    d.line((x,658,xr,658),fill='#50644e')
    t=s['global'];tall=plan['total'];boundary=U['ticks'];prog=(t+1)/tall
    txt(d,time(t),x,679,12,GOLD,MONO);txt(d,time(tall),xr,679,12,MUTED,MONO,'rt')
    d.rounded_rectangle((x,707,xr,711),radius=2,fill='#607365');d.rounded_rectangle((x,707,x+max(3,int(wide*prog)),711),radius=2,fill=GOLD)
    bx=x+round(wide*boundary/tall);d.line((bx,703,bx,716),fill=PAPER,width=1)
    txt(d,'NUAGES & JINGLE',x,731,10,MUTED,MONO);txt(d,'VOYAGE',xr,731,10,MUTED,MONO,'rt')

def positions(route):
    runner="""const E=require(process.argv[1]), D=require(process.argv[2]), P=E.makePlan(D,'film',process.argv[3]); console.log(JSON.stringify({P,frames:Array.from({length:P.total},(_,i)=>E.frame(D,P,i))}));"""
    return json.loads(subprocess.check_output(['node','-e',runner,str(S/'Moteur.js'),str(ROOT/'Calques/Animation.json'),route]))

def sound(p,dest):
    hz=48000;fps=D['fps'];N=int(round(p['total']/fps*hz)); mix=array('h',[0])*(N*2)
    for e in p['events']:
        source=ROOT/D['audio'][e['key']]['1']['fichier'];raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(source),'-map','0:a:0','-ar',str(hz),'-ac','2','-f','f32le','-']);clip=array('f');clip.frombytes(raw)
        a=int(round(e['at']/fps*hz));b=int(round(e['until']/fps*hz));ramp=None if e['fadeAt'] is None else e['fadeAt']/fps*hz
        for j in range(min(len(clip)//2,b-a,N-a)):
            v=.92*e['gain']
            if ramp is not None and a+j>ramp:v*=max(0,(b-a-j)/(b-ramp))
            for k in range(2):mix[(a+j)*2+k]+=round(32767*v*clip[j*2+k])
    if sys.byteorder=='big': mix.byteswap()
    with wave.open(str(dest),'wb') as wav:wav.setnchannels(2);wav.setsampwidth(2);wav.setframerate(hz);wav.writeframes(mix.tobytes())

def main():
    ap=ArgumentParser(description=__doc__);ap.add_argument('--trajet',default='blizzard',choices=['saline','blizzard']);ap.add_argument('--sortie',type=Path);ap.add_argument('--image',type=int,help='Write one PNG frame rather than a video');args=ap.parse_args()
    data=positions(args.trajet);plan=data['P'];frames=data['frames'];root=background()
    def render(s):
        plate=root.copy();plate.paste(frame_map(s).resize((WIDTH,HEIGHT),Image.Resampling.NEAREST),(SX,SY));decorate(plate,s,plan);return plate
    if args.image is not None:
        render(frames[args.image]).save(args.sortie or ROOT/'Carte-Miracle-Image.png');return
    with tempfile.TemporaryDirectory() as tmp:
        audio=Path(tmp)/'bande.wav';sound(plan,audio);rate=str(Fraction(str(D['fps'])))
        dest=args.sortie or ROOT/'Carte-Miracle-En-Action.mp4'
        opts=['ffmpeg','-hide_banner','-v','warning','-y','-f','rawvideo','-pixel_format','rgb24','-video_size',f'{W}x{H}',
              '-framerate',rate,'-i','pipe:0','-i',str(audio),'-map','0:v:0','-map','1:a:0','-c:v','libx264','-preset','fast','-crf','18',
              '-threads','4','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-movflags','+faststart','-metadata','title=La Carte Miracle en mouvement',str(dest)]
        p=subprocess.Popen(opts,stdin=subprocess.PIPE)
        try:
            for f in frames:p.stdin.write(render(f).tobytes())
        finally:p.stdin.close()
        assert p.wait()==0
        print(f'{dest.name}: {len(frames)} images, {len(frames)/D["fps"]:.03f} s, {dest.stat().st_size:,} octets')

if __name__=='__main__':main()
