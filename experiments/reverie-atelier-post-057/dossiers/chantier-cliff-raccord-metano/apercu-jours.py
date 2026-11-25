from PIL import Image, ImageDraw
from pathlib import Path
import numpy as np
R=Path('/home/user/chantier-cliff-raccord-metano');sea=Image.open(R/'source-jour-phase00.png').convert('RGBA');terrain=Image.open(R/'cliff-corrige-transparent.png');cloud=Image.open('/home/user/apercu-cliff-guilde-ambiances/assets/pmu-nuage-1.png').convert('RGBA')
for phase in ['jour','crepuscule']:
 im=Image.new('RGBA',(480,520));draw=ImageDraw.Draw(im)
 for y in range(152):
  t=y/151
  if phase=='jour': col=(int(95+25*t),int(155+35*t),int(241+5*t),255)
  else: col=(int(55+160*t),int(56+40*t),int(110+10*t),255)
  draw.line((0,y,479,y),fill=col)
 # Nuage PMU entier pour ces images fixes : seule l'animation nuit est PMD.
 im.alpha_composite(cloud,(24,38));im.alpha_composite(cloud,(260,70))
 ocean=sea.crop((0,128,312,240));band=sea.crop((0,216,312,240))
 if phase=='crepuscule':
  def tint(img):
   a=np.array(img);a[:,:,:3]=(a[:,:,:3].astype(float)*[.70,.57,.68]).astype('uint8');return Image.fromarray(a)
  ocean=tint(ocean);band=tint(band);t=tint(terrain)
 else:t=terrain
 for x in [0,312]:im.paste(ocean,(x,152))
 for y in range(264,520,24):
  for x in [0,312]:im.paste(band,(x,y))
 im.alpha_composite(t,(0,104));im.convert('RGB').save(R/f'cliff-{phase}-fixe.png')
