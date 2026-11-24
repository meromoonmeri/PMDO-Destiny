"""Validate audible samples, timing and the actual encoded yellow/red frames."""
from array import array
from hashlib import sha256
from io import BytesIO
from pathlib import Path
from PIL import Image
from math import sqrt
import json, subprocess
ROOT=Path(__file__).resolve().parents[1];V=ROOT/'Carte-Miracle-En-Action.mp4';D=json.loads((ROOT/'Calques/Animation.json').read_text());fps=D['fps'];hz=48000

def run(*a):return subprocess.check_output(a)
def raw_audio(p):
    a=array('f');a.frombytes(run('ffmpeg','-v','error','-i',str(p),'-map','0:a:0','-ar',str(hz),'-ac','2','-f','f32le','-'));return a

def rms(xs):return sqrt(sum(x*x for x in xs)/len(xs))
def color(t,name):
    out=run('ffmpeg','-v','error','-i',str(V),'-vf',f'select=eq(n\\,{t})','-frames:v','1','-f','image2pipe','-pix_fmt','rgb24','-vcodec','png','-')
    img=Image.open(BytesIO(out));sx=36+(76-4)*3;sy=129+(276-144-4)*3
    region=img.crop((sx,sy,sx+24,sy+24))
    return sum(1 for r,g,b in region.getdata() if (r>173 and g>138 and b<87 if name=='jaune' else r>133 and g<76 and b<76))

def check():
    info=json.loads(run('ffprobe','-v','error','-show_streams','-show_format','-of','json',str(V)));v,a=info['streams'];
    assert (v['codec_name'],v['width'],v['height'],v['nb_frames'])==('h264',1280,864,'804')
    assert a['codec_name']=='aac' and a['sample_rate']==str(hz) and a['channels']==2 and abs(float(a['duration'])-804/fps)<.003
    red=color(408,'rouge');yellow=color(400,'jaune');assert red>24 and yellow>24,(red,yellow)
    aud=raw_audio(V);between=lambda start,end:aud[round(hz*start)*2:round(hz*end)*2]
    quiet=rms(between(0,400/fps-.07));gap=rms(between(8.5,9.4));assert quiet<.0002 and gap<.0002
    refs={}
    for k,t in [('me',400),('bgm',571)]:
        c=raw_audio(ROOT/D['audio'][k]['1']['fichier']);pos=round(t/fps*hz);n=round(hz*(.95 if k=='me' else 1.3))
        original=c[:n*2:4]; matched=aud[pos*2:(pos+n)*2:4]
        corr=sum(x*y for x,y in zip(original,matched))/sqrt(sum(x*x for x in original)*sum(y*y for y in matched))
        assert corr>.94 and rms(matched)>.015,(k,corr,rms(matched))
        refs[k]={'tick':t,'seconde':round(t/fps,4),'correlation_pcm_reencode':round(corr,6),'rms':round(rms(matched),6)}
    out={'statut':'PASS','frames':804,'format':'H.264 + AAC stéréo','resolution':[1280,864],'fps':fps,'duree':round(804/fps,4),
         'pixels_repere_jaune_f400':yellow,'pixels_repere_rouge_f408':red,'silence_rms_avant_me':quiet,'silence_rms_entre_scenes':gap,
         'sons':refs,'sha256':sha256(V.read_bytes()).hexdigest()}
    (ROOT/'Verification-de-la-video.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))

if __name__=='__main__':check()
