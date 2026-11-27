from PIL import Image,ImageDraw
from pathlib import Path
p=Path(__file__).parent
# Work only below the already-drawn skirt, keep head/body unchanged.
src=Image.open(p/'face-marche-02-bras-essai.png').convert('RGB');out=src.copy();box=(295,1025,505,1230);region=src.crop(box);bg=src.getpixel((0,100));ImageDraw.Draw(out).rectangle(box,fill=bg);scaled=region.resize((region.width,158),Image.Resampling.NEAREST);out.paste(scaled,(box[0],box[1]));out.save(p/'face-marche-02-bras-pas-court.png')
