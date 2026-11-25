from pathlib import Path
from functools import cache
from hashlib import sha256
import base64,io,json,re,sys
import numpy as np
from PIL import Image
from scipy.ndimage import label
ROOT=Path(__file__).resolve().parents[1]; G=ROOT.parent; W=Path.home()/'.cache/destiny-feux-rayons'; OLD=G/'Comptoirs-et-Falaise'
REF=ROOT/'Reference'; BASE=G/'Guilde-Destiny-Comptoirs-et-Falaise.html'; OUT=G/'Guilde-Destiny-Drapeaux-Foyers-Bibliotheque.html'
BIB='guilde_destiny_cuisine'; REFEC='guilde_destiny_refectoire'; ACC='guilde_destiny_accueil'
P=('jour','aube','crepuscule','nuit')
DIRS=[('Down','Face','↓'),('DownRight','Avant droit','↘'),('Right','Profil droit','→'),('UpRight','Arrière droit','↗'),('Up','Dos','↑'),('UpLeft','Arrière gauche','↖'),('Left','Profil gauche','←'),('DownLeft','Avant gauche','↙')]

def zap(n):return (ROOT/n).resolve()
def b64(p):return base64.b64encode(Path(p).read_bytes()).decode()
def dec(b):return Image.open(io.BytesIO(base64.b64decode(b.split(',')[-1]))).convert('RGBA')
def filehash(path):return sha256(Path(path).read_bytes()).hexdigest()
def png(img,path):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);img.save(path,optimize=True);return path

def write_json(path,data):Path(path).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')

@cache
def atelier():return json.loads(re.search(r'<script id="donnees"[^>]*>(.*?)</script>',BASE.read_text(),re.S)[1])

def room(k):return next(r for r in atelier()['rooms'] if r['id']==k)

def key(im):
    rgb=np.array(im.convert('RGB'));r,g,b=rgb.astype(int).transpose(2,0,1);matte=~((r>130)&(b>132)&(g+81<np.minimum(r,b)))
    a,n=label(matte);cnt=np.bincount(a.ravel());cnt[0]=0; biggest=a==cnt.argmax(); assert 120<int(np.count_nonzero(biggest))
    rgba=np.dstack((rgb,biggest.astype('uint8')*255));rgba[~biggest]=0
    im=Image.fromarray(rgba);return im.crop(im.getbbox())

def pixel_photo(n,size,colors=0):
    src=key(Image.open(REF/f'{n}-etude-IA.png'));im=src.resize(size,Image.Resampling.NEAREST)
    if colors:
        rgb=im.convert('RGB').quantize(colors=colors,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE).convert('RGB');rgb.putalpha(im.getchannel('A'));a=np.array(rgb);a[a[...,3]==0]=0;return Image.fromarray(a)
    return im

def clip(x):return np.clip(x,0,1)
def ss(lo,hi,x):
    f=clip((x-lo)/(hi-lo));return f*f*(3-2*f)

# Warp each column to the tangent of the circular wooden wall. No antialiasing and
# no arbitrary perspective crop: every pixel has an integer address on the plan.
def tangente(im,width,delta):
    b=np.array(im.resize((width,im.height),Image.Resampling.NEAREST));shift=np.rint(np.linspace(0,delta,width)).astype(int)
    shift-=shift.min();out=np.zeros((b.shape[0]+int(shift.max()),width,4),dtype='uint8')
    for i,s in enumerate(shift):out[s:s+b.shape[0],i]=b[:,i]
    return Image.fromarray(out)

@cache
def palette_for(rid,phase):
    d=atelier();index=room(rid)['nuit'];return d['nuits'][index]['lut'] if phase==3 else d['lumieres'][index][phase]['lut']

def roomtone(im,rid,phase):
    t=np.array(im.convert('RGBA'));lut=palette_for(rid,phase)
    if lut:
        for q in range(3):t[...,q]=np.asarray(lut[q],dtype='uint8')[t[...,q]]
    t[t[...,3]==0]=0;return Image.fromarray(t)
