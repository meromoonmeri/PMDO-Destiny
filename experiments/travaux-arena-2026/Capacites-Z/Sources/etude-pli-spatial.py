#!/usr/bin/env python3
"""Étude hors jeu : déformer les pixels d'une capture PMDO, sans calque dessiné.

La capture est fixe. Cette étude ne modifie ni le moteur ni la capacité. L'algorithme
utilise seulement l'image reçue et peut donc servir sur n'importe quel décor ;
il ne prouve pas que le rendu en temps réel est intégré ou performant.
"""
from pathlib import Path
import math, subprocess
import cv2
import numpy as np

H = Path.home(); P = H/'Capacites-Z/Prototypes/Psycho-Pulverisation-EX/Generation-PMDO'
source = P/'Gardevoir-Psycho-Pulverisation-EX-8-directions-son.mp4'
image = P/'pli-spatial-capture-source.png'
out = P/'Psycho-pli-spatial-etude-hors-jeu-60ips-son.mp4'
subprocess.run(['ffmpeg','-v','error','-y','-ss','0','-i',str(source),'-frames:v','1',str(image)],check=True)
frame = cv2.imread(str(image), cv2.IMREAD_COLOR)
h,w = frame.shape[:2]
# Centre sur le personnage ; zone elliptique, raccordée progressivement au décor.
cx,cy = 480,355
rx,ry = 175,150
x0,x1 = max(0,cx-rx),min(w,cx+rx+1)
y0,y1 = max(0,cy-ry),min(h,cy+ry+1)
y,x = np.mgrid[y0:y1,x0:x1].astype(np.float32)
nx=(x-cx)/rx; ny=(y-cy)/ry
r=np.sqrt(nx*nx+ny*ny)
mask=np.clip(1-r*r,0,1)**2
# Lancé hors jeu : flux vidéo calculé puis associé à la bande-son existante.
cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','bgr24','-s',f'{w}x{h}','-r','60','-i','pipe:0','-i',str(source),'-t','4','-map','0:v:0','-map','1:a:0','-c:v','libx264','-crf','19','-pix_fmt','yuv420p','-c:a','aac','-b:a','128k','-movflags','+faststart',str(out)]
proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
for n in range(240):
    t=n/60
    envelope=math.sin(math.pi*min(1,max(0,t/4)))**1.3
    pulse=math.sin(2*math.pi*t/1.25)
    # Déformation par coordonnées inverses : aucune couleur ajoutée.
    fold=mask*envelope
    sx=x + fold*(30*nx*math.cos(t*3.2) + 23*np.sin(ny*5.5+t*4.0))
    sy=y + fold*(23*ny*pulse + 13*np.sin(nx*5.2-t*3.1))
    # Échantillonnage discret pour respecter les contours du pixel art.
    warped=cv2.remap(frame,sx.astype(np.float32),sy.astype(np.float32),cv2.INTER_NEAREST,borderMode=cv2.BORDER_REPLICATE)
    result=frame.copy();result[y0:y1,x0:x1]=warped
    proc.stdin.write(result.tobytes())
proc.stdin.close()
if proc.wait(): raise RuntimeError('Échec encodage')
print(out)
