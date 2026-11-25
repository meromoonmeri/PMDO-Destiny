"""Lay out the final generated island cutouts at ×3 on a separate pure-magenta sheet."""
from pathlib import Path
from PIL import Image
import json
import numpy as np

root=Path(__file__).resolve().parents[1]; N=Image.Resampling.NEAREST
meta={a['id']:a for a in json.loads((root/'Atlas.json').read_text())['archipels']}
canvas=Image.new('RGB',(840,560),(255,0,255));area=0
for name,cx,cy in (('volcans',210,140),('petales',630,140),('amethystes',210,420),('coraux',630,420)):
 z=meta[name];raw=Image.open(root/'Calques'/z['file']).convert('RGBA');im=raw.resize((raw.width*3,raw.height*3),N)
 mask=im.getchannel('A');area+=int(np.count_nonzero(np.asarray(mask)));canvas.paste(im,(cx-im.width//2,cy-im.height//2),mask)
a=np.array(canvas);assert int(np.count_nonzero(np.any(a!=[255,0,255],axis=-1)))==area
out=root/'Archipels-Destiny-Magenta.png';canvas.save(out,optimize=True);print(out.name,canvas.size)
