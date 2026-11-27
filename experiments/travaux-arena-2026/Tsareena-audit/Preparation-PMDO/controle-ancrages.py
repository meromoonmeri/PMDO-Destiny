from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
p=Path(__file__).resolve().parent
ref=Image.open(p.parent/'refs-spritecollab/Walk-Anim.png').convert('RGBA')
mega=Image.open(p.parent/'Polish-nettete/Walk-palette15-taille-jeu-ESSAI.png').convert('RGBA')
off=Image.open(p.parent/'refs-spritecollab/Walk-Offsets.png').convert('RGBA')
sh=Image.open(p.parent/'refs-spritecollab/Walk-Shadow.png').convert('RGBA')
W,H=32,56;scale=4; names=['Face','Avant-droite','Droite','Arrière-droite','Dos','Arrière-gauche','Gauche','Avant-gauche']
for r,name in enumerate(names):
 out=Image.new('RGB',(4*2*W*scale, H*scale+54),'#c6d8bf');d=ImageDraw.Draw(out);d.text((6,5),f'{name} - normal | Méga ; repères NORMAUX reportés, non validés',fill='#1f3323')
 for f in range(4):
  box=(f*W,r*H,(f+1)*W,(r+1)*H)
  for which,img in enumerate((ref,mega)):
   x=(f*2+which)*W*scale; y=32
   cell=img.crop(box).resize((W*scale,H*scale),Image.Resampling.NEAREST);out.paste(cell,(x,y),cell)
   # Repères de la référence uniquement : l'utilisation sur Méga n'est qu'un diagnostic.
   for layer in (off,sh):
    mark=layer.crop(box);pix=mark.load()
    for py in range(H):
     for px in range(W):
      c=pix[px,py]
      if c[3] and (layer is off or c[:3]==(255,255,255)):
       xx=x+px*scale+scale//2; yy=y+py*scale+scale//2
       ink=(255,255,255) if c[:3]==(0,0,0) else c[:3]
       d.rectangle((xx-2,yy-2,xx+2,yy+2),fill=(20,20,20),outline=ink,width=1)
  d.text(((f*2)*W*scale+4,H*scale+35),f'image {f+1}',fill='#1f3323')
 out.save(p/f'controle-ancrages-direction-{r}.png')
print('8 contrôles visuels générés. Aucun offset ni ombre n’a été créé ou validé pour Méga.')
