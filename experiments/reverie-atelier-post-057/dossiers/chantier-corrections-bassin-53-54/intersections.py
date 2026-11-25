exec(open('/home/user/chantier-corrections-bassin-53-54/rendu-audit.py').read().split('# Full selection')[0])
from collections import Counter
regions={'droite':(162,263,172,278),'gauchehaut':(99,255,108,267),'gauche1':(102,265,112,277),'gauche2':(102,278,112,292)}
for n,box in regions.items():
 cl=render(box,['Cliffs']);ob=render(box,['Objects']);top=render(box,['Objects Anim','Objects Over','Objects Over Anim','Fringe']);c=Counter()
 for o,cc,t in zip(ob.getdata(),cl.getdata(),top.getdata()):
  if o[3] and cc[3] and t[3]==0:c[o]+=1
 print(n, sum(c.values()),c.most_common(25))
