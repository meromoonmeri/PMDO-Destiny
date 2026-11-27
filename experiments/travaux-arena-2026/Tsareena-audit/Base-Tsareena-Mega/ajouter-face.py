from PIL import Image,ImageDraw
from pathlib import Path
p=Path(__file__).parent; ref=Image.open(p.parent/'refs-spritecollab/Walk-Anim.png').convert('RGBA');sheet=Image.open(p/'Walk-Anim-avant-droite-PARTIEL.png')
for i in range(4):
 sprite=ref.crop((i*32,0,(i+1)*32,56)).resize((64,112),Image.Resampling.NEAREST)
 dx,dy=[(0,0),(0,2),(0,0),(0,2)][i];coat=Image.new('RGBA',(64,112));d=ImageDraw.Draw(coat)
 def poly(pts,c):d.polygon([(x+dx,y+dy) for x,y in pts],fill=c)
 # Purple panels frame the legs rather than joining into a trouser-like shape.
 poly([(25,39),(30,41),(27,52),(25,60),(21,66),(17,70),(12,70),(10,68),(13,62),(16,55),(19,46)],'#171019')
 poly([(24,42),(28,42),(25,52),(23,59),(19,65),(16,68),(13,68),(16,61),(19,54),(21,47)],'#693959')
 poly([(21,47),(24,44),(21,56),(17,64),(15,66),(18,56)],'#854866')
 poly([(35,41),(40,39),(46,46),(49,55),(52,62),(55,68),(53,70),(48,70),(44,66),(40,60),(38,52)],'#171019')
 poly([(36,42),(40,42),(43,47),(45,54),(48,61),(51,68),(48,68),(45,65),(41,59),(39,52)],'#693959')
 poly([(40,44),(43,47),(46,56),(49,64),(48,66),(44,59)],'#854866')
 # preserve base legs and body; replace the small original crown at the top only
 original=sprite.copy();d0=ImageDraw.Draw(original);bx=[(32,2,47,13),(34,6,49,17),(32,2,47,13),(30,4,45,15)][i];d0.rectangle(bx,fill=(0,0,0,0));coat.alpha_composite(original);d=ImageDraw.Draw(coat)
 # simplified crown lowered to sit on the hair
 def poly(pts,c):d.polygon([(x+dx,y+dy+3) for x,y in pts],fill=c)
 poly([(25,6),(27,3),(32,3),(32,1),(38,1),(38,3),(43,3),(46,6),(46,12),(42,14),(38,13),(34,14),(30,13),(26,14),(23,11),(23,7)],'#151015')
 poly([(25,6),(28,4),(33,4),(33,3),(37,3),(37,4),(42,4),(44,6),(44,10),(41,12),(38,11),(35,12),(32,11),(28,12),(25,10)],'#6e9144')
 poly([(27,6),(30,5),(34,5),(34,4),(38,4),(38,5),(41,5),(43,6),(43,7),(40,7),(40,9),(38,9),(38,7),(34,7),(34,10),(32,10),(32,7),(28,7)],'#b2dc6e')
 for x,y in [(27,6),(33,5),(39,5),(42,7)]:d.rectangle((x+dx,y+dy+3,x+dx+1,y+dy+4),fill='#f1d65f')
 poly([(29,10),(31,10),(32,12),(30,13)],'#aa3f60');poly([(39,10),(41,10),(42,12),(40,13)],'#aa3f60')
 # extend lashes without altering eyes
 d.line([(18+dx,29+dy),(16+dx,27+dy)],fill='#ac3e5c',width=2);d.line([(42+dx,29+dy),(45+dx,27+dy)],fill='#ac3e5c',width=2)
 a,b=sprite.load(),coat.load();assert all(a[x,y]==b[x,y] for y in range(54,80) for x in range(64) if a[x,y][3])
 coat.save(p/f'face-{i+1:02}-retouche.png');sheet.alpha_composite(coat,(i*64,0))
sheet.save(p/'Walk-Anim-face-avant-droite-PARTIEL.png'); print('Face + avant-droite : 8 cases / 32 ; jambes source intactes')
