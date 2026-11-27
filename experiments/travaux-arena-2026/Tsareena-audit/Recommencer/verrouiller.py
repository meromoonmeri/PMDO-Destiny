from PIL import Image,ImageDraw
from pathlib import Path
import numpy as np,hashlib
p=Path(__file__).parent
source=p.parent/'revision-corpulence/repos-trois-quart-01.png'
proposal=p/'marche-proposition-02-brute.png'
a=Image.open(source).convert('RGB'); b=Image.open(proposal).convert('RGB')
if a.size!=b.size: raise ValueError('Tailles différentes : recalage manuel requis, arrêt.')
mask=Image.new('L',a.size,0); d=ImageDraw.Draw(mask)
# Région des jambes : inclut aussi un peu de robe/fond, donc audit visuel indispensable.
d.polygon([(405,786),(661,786),(683,982),(614,982),(614,1102),(396,1102),(396,974)],fill=255)
out=Image.composite(b,a,mask);out.save(p/'marche-essai-verrouille.png');mask.save(p/'masque-jambes.png')
A=np.asarray(a);O=np.asarray(out);M=np.asarray(mask)>0
print('source sha256:',hashlib.sha256(source.read_bytes()).hexdigest())
print('pixels modifiés dans masque:',np.count_nonzero(np.any(A!=O,axis=2)&M))
print('pixels modifiés hors masque:',np.count_nonzero(np.any(A!=O,axis=2)&~M))
assert not np.any(A[~M]!=O[~M])
