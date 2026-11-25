#!/usr/bin/env python3
"""Install the optional visual layers in the offline preview, never in game data."""
import hashlib
import json
from pathlib import Path

import Fabriquer as F

HERE=Path(__file__).resolve().parent


def swap(s,a,b):
    assert s.count(a)==1,a
    return s.replace(a,b,1)


def block(s,where,file,fmt):
    key=file.rsplit('.',1)[1]
    a,b=(fmt.format(f'Chaines/{key}/{p}') for p in ('debut','fin'))
    new=a+'\n'+(HERE/file).read_text(encoding='utf8').rstrip()+'\n'+b+'\n'
    if a not in s:
        return swap(s,where,new+where)
    lead,rest=s.split(a,1);_,after=rest.split(b+'\n',1)
    return lead+new+after


def digest(d):
    return hashlib.sha256(json.dumps({k:v for k,v in d.items() if k!='chaines_accueil'},ensure_ascii=False).encode()).hexdigest()


def main():
    head,d,t=F.page();before=digest(d)
    assert 'seuil_accueil' in d and 'verdure' in d
    assert (len(d['rooms']),sum(len(r['gates']) for r in d['rooms']),sum(bool((r['south'] or {}).get('band')) for r in d['rooms']))==(15,29,7)
    first='chaines_accueil' not in d
    d['chaines_accueil'],proof=F.build(d)
    assert digest(d)==before
    if first:
        head=swap(head,'<title>Destiny · Bourgeons — le seuil de l’Accueil</title>','<title>Destiny · Bourgeons — les chaînes de l’Accueil</title>')
        t=swap(t,'phase:0,seuil:true,','phase:0,seuil:true,chaines:true,')
        t=swap(t,'const vines=lianesAt(r,p,lianes), doorstep=seuilAt(r,p);','const vines=lianesAt(r,p,lianes), doorstep=seuilAt(r,p), rails=chainesAt(r,p);')
        t=swap(t,'  drawPicture(c,r.m[p][1],0,0);','  drawPicture(c,r.m[p][1],0,0);\n  for(const [x,y,b] of rails)drawPicture(c,b,x,y);')
        t=swap(t,'...doorstep.map(q=>q[2]),...items.map','...doorstep.map(q=>q[2]),...rails.map(q=>q[2]),...items.map')
        t=swap(t,'...seuilAt(r,i).map(q=>q[2]),...items.map','...seuilAt(r,i).map(q=>q[2]),...chainesAt(r,i).map(q=>q[2]),...items.map')
        t=swap(t,'updateFilm();updateSeuil();','updateFilm();updateSeuil();updateChaines();')
        t=swap(t,"  if(s.page==='atlas')paintSeuil();","  if(s.page==='atlas'){paintSeuil();paintChaines();}")
        t=swap(t,"    if(s.page==='atlas')paintSeuil(true);","    if(s.page==='atlas'){paintSeuil(true);paintChaines(true);}")
        t=swap(t,'ni l’habillage du seuil.','ni les décors fixes de l’Accueil.')
        t=swap(t,'setupSeuil();setupAtlas();','setupChaines();setupSeuil();setupAtlas();')
    head=block(head,'</style>','Panneau.css','/* {} */')
    head=block(head,'<!-- Accueil/section/debut -->','Panneau.html','<!-- {} -->')
    t=block(t,'setupChaines();setupSeuil();','Panneau.js','// {}')
    html=head+F.MARK+json.dumps(d,separators=(',',':'),ensure_ascii=False).replace('</','<\\/')+'</script>'+t
    tmp=F.PREVIEW.with_suffix('.part');tmp.write_text(html,encoding='utf8');tmp.replace(F.PREVIEW)
    proof['donnees_heritees_sha256']=before
    (F.OUT/'Index-tilesheet.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print('PASS · Tilesheet 8 sprites et deux barrières placées dans l’aperçu ·',F.PREVIEW.stat().st_size,'octets')


if __name__=='__main__':
    main()
