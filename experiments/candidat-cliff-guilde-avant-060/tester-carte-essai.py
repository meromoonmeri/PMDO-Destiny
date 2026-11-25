from pathlib import Path
from PIL import Image,ImageChops
import sys,json
R=Path(__file__).resolve().parent;C=R/'candidat-isole';sys.path.insert(0,'/home/user/destiny-reference/tools');from preview_maps import SheetReader
p=C/'Data/Ground/guilde_cliff_essai_jour.rsground';o=json.loads(p.read_text())['Object'];sheet=C/'Content/Tile/Destiny_GuildeCliff_Essai_Jour_059.tile';r=SheetReader(sheet)
scene=Image.new('RGBA',(480,520));cells=0
for layer in o['Layers']:
 for x,col in enumerate(layer['Tiles']):
  for y,t in enumerate(col):
   for sub in t['Layers']:
    f=sub['Frames'][0];assert f['Sheet']==sheet.stem;pos=f['TexLoc'];tile=r.get_tile(pos['X'],pos['Y']);assert tile is not None
    scene.alpha_composite(tile.convert('RGBA'),(x*8,y*8));cells+=1
r.close();ref=Image.open(R/'rapports/apercu-candidat-jour.png').convert('RGBA');assert scene.tobytes()==ref.tobytes(), 'La recomposition du Ground diffère du montage.'
print('PASS :',cells,'cellules recomposées, image identique octet pour octet ; ceci ne valide pas le moteur.')
