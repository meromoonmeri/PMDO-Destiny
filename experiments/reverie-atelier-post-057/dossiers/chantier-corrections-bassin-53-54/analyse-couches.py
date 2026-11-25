exec(open('/home/user/chantier-corrections-bassin-53-54/rendu-audit.py').read().split('# Full selection')[0])
from collections import Counter
zones={'est':(164,264,172,275),'gauche1':(100,257,108,266),'gauche2':(103,264,111,279),'gauche3':(103,278,111,292)}
for n,box in zones.items():
 bg=render(box,['Base']);cl=render(box,['Cliffs']);ob=render(box,['Objects']);all=render(box)
 for name,im in [('base',bg),('cliff',cl),('objets',ob),('total',all)]: im.resize((im.width*6,im.height*6),Image.Resampling.NEAREST).save(R/f'couches-{n}-{name}.png')
 print(n,'objets top',Counter(ob.getdata()).most_common(15),'cliff alpha',Counter(cl.getchannel('A').getdata()).most_common(4))
