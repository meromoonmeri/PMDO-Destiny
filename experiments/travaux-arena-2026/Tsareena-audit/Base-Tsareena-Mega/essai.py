from PIL import Image,ImageDraw
from pathlib import Path
p=Path(__file__).parent;r=p.parent;src=Image.open(r/'refs-spritecollab/Walk-Anim.png').convert('RGBA');out=Image.new('RGBA',(256,896));st=[]
# On revoit la direction avant-droite seulement. Les jambes et le corps source sont conservés sans altération.
for n in range(4):
 original=src.crop((n*32,56,(n+1)*32,112)).resize((64,112),Image.Resampling.NEAREST)
 dx,dy=[(0,0),(2,2),(0,0),(-2,4)][n];canvas=Image.new('RGBA',(64,112));d=ImageDraw.Draw(canvas)
 # pans de robe derrière le sprite source
 def poly(pts,c):d.polygon([(x+dx,y+dy) for x,y in pts],fill=c)
 # Two independent robe panels, opening freely around the original legs.
 poly([(27,39),(31,42),(27,54),(25,62),(22,67),(18,70),(13,70),(12,67),(16,60),(19,52),(22,44)],'#170c19')
 poly([(27,41),(29,42),(25,53),(23,61),(20,66),(17,68),(14,68),(17,61),(20,53),(23,46)],'#6e3b5d')
 poly([(23,47),(25,45),(22,57),(18,65),(16,66),(19,56)],'#864868')
 poly([(38,40),(43,40),(47,48),(49,56),(53,63),(56,67),(55,70),(48,70),(44,66),(41,60),(39,52)],'#170c19')
 poly([(40,42),(43,42),(46,49),(47,57),(51,64),(54,67),(53,68),(49,68),(46,64),(43,58)],'#693957')
 poly([(42,45),(44,47),(47,58),(51,65),(50,67),(46,62)],'#834664')
 # replacement of original small crown only, retaining body, legs and green hair
 ori=original.copy();ImageDraw.Draw(ori).rectangle((24+dx,3+dy,39+dx,13+dy),fill=(0,0,0,0));canvas.alpha_composite(ori)
 d=ImageDraw.Draw(canvas)
 def poly2(pts,c):d.polygon([(x+dx,y+dy+3) for x,y in pts],fill=c)
 poly2([(25,5),(28,5),(28,2),(33,2),(33,0),(40,0),(40,2),(44,2),(44,4),(47,4),(47,11),(44,11),(44,13),(40,13),(40,12),(36,12),(36,13),(31,13),(31,12),(26,12),(24,10),(24,6)],'#141115')
 poly2([(26,5),(29,5),(29,3),(34,3),(34,2),(39,2),(39,3),(43,3),(43,5),(45,5),(45,10),(42,10),(42,11),(39,10),(36,11),(33,10),(30,11),(27,10),(26,9)],'#729442')
 poly2([(29,4),(33,4),(33,3),(39,3),(39,4),(42,4),(42,5),(44,5),(44,7),(42,7),(42,6),(39,6),(39,9),(37,9),(37,6),(34,6),(34,9),(32,9),(32,6),(29,6)],'#b7df70')
 for x,y in [(28,5),(33,4),(39,4),(43,6),(37,8)]: d.rectangle((x+dx,y+dy+3,x+dx+1,y+dy+4),fill='#f5d85d')
 poly2([(30,10),(32,10),(33,12),(31,12)],'#ac4562');poly2([(40,9),(42,9),(43,11),(41,12)],'#ac4562')
 # longer outward lash at visible outer corner; do not touch eye
 d.line([(41+dx,29+dy),(44+dx,28+dy),(46+dx,27+dy)],fill='#a7385a',width=2)
 canvas.save(p/f'avant-droite-{n+1:02}-retouche.png');out.alpha_composite(canvas,(n*64,112))
 # assert legs y >= 54 identical where source present
 a,b=original.load(),canvas.load(); assert all(a[x,y]==b[x,y] for y in range(54,78) for x in range(64) if a[x,y][3])
out.save(p/'Walk-Anim-avant-droite-PARTIEL.png')
print('4 frames de la direction avant-droite, pixels des jambes source conservés')
