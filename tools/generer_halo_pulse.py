#!/usr/bin/env python3
"""Anime les trois calques *existants* du halo Destiny, sans recréer leur dessin.

Exemple : python tools/generer_halo_pulse.py --source game/Content/BG --output game/Content/BG
Format DirSheet 0.8.12 : Int64 longueur PNG, PNG, Int32 largeur/hauteur/type/nombre.
Le fichier source est conservé ; l'image de la frame 0 est identique à la source.
"""
from __future__ import annotations
import argparse, io, math, struct
from pathlib import Path
from PIL import Image

LAYERS=('Halo_Fond','Halo_Anneau','Halo_Shine')

def load_dir(path):
 data=path.read_bytes(); length=struct.unpack_from('<q',data,0)[0]
 assert 0<length<=len(data)-24
 img=Image.open(io.BytesIO(data[8:8+length])).convert('RGBA')
 width,height,dirs,frames=struct.unpack_from('<iiii',data,8+length)
 assert (img.width,img.height,dirs,frames)==(width,height,0,1),path
 return img

def frames_for(img,opaque):
 out=[]
 for i in range(16):
  factor=0.60+0.40*math.cos(2*math.pi*i/16)
  if i==0:out.append(img.copy());continue
  r,g,b,a=img.split()
  if opaque:
   r=r.point(lambda x:round(x*factor));g=g.point(lambda x:round(x*factor));b=b.point(lambda x:round(x*factor))
  else:
   a=a.point(lambda x:round(x*factor))
  out.append(Image.merge('RGBA',(r,g,b,a)))
 return out

def write_dir(path,images):
 w,h=images[0].size;atlas=Image.new('RGBA',(w*4,h*4))
 for i,im in enumerate(images):atlas.paste(im,((i%4)*w,(i//4)*h))
 b=io.BytesIO();atlas.save(b,format='PNG',optimize=True);raw=b.getvalue()
 path.write_bytes(struct.pack('<q',len(raw))+raw+struct.pack('<iiii',w,h,0,len(images)))

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--source',type=Path,required=True);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
 args.output.mkdir(parents=True,exist_ok=True)
 for name in LAYERS:
  im=load_dir(args.source/(name+'.dir'));frames=frames_for(im,name=='Halo_Fond')
  assert frames[0].tobytes()==im.tobytes()
  dst=args.output/(name+'_Pulse.dir');write_dir(dst,frames)
  print(dst,'16 images, maximum identique à la source')

if __name__=='__main__':main()
