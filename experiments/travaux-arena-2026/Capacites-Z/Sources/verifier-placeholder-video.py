#!/usr/bin/env python3
"""Comptage des pixels magenta vif caractérisant le damier de remplacement."""
import sys,subprocess,numpy as np
from pathlib import Path
for f in sys.argv[1:]:
 p=subprocess.Popen(['ffmpeg','-v','error','-i',f,'-vf','fps=20,scale=320:240:flags=neighbor','-pix_fmt','rgb24','-f','rawvideo','-'],stdout=subprocess.PIPE); size=320*240*3; n=0; flagged=[];peak=0
 while True:
  data=p.stdout.read(size)
  if len(data)<size:break
  a=np.frombuffer(data,dtype=np.uint8).reshape((240,320,3));mask=(a[:,:,0]>220)&(a[:,:,1]<50)&(a[:,:,2]>220);count=int(mask.sum());peak=max(peak,count)
  if count>=5:flagged.append((n/20,count))
  n+=1
 p.wait();print(Path(f).name,'frames',n,'max-magenta',peak,'frames-signalees',len(flagged),'exemples',flagged[:6])
