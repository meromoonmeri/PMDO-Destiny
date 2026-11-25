#!/usr/bin/env python3
"""Replace side chains with a functional preview-only portcullis."""
import hashlib
import json
from pathlib import Path

import Fabriquer as F

HERE=Path(__file__).resolve().parent
TITLE='<title>Destiny · Bourgeons — le seuil de l’Accueil</title>'


def swap(s,a,b):
    assert s.count(a)==1,a
    return s.replace(a,b,1)


def insert(s,anchor,file,fmt):
    k=file.rsplit('.',1)[1]
    a,b=(fmt.format(f'Grille/{k}/{p}') for p in ('debut','fin'))
    new=a+'\n'+(HERE/file).read_text(encoding='utf8').rstrip()+'\n'+b+'\n'
    if a not in s:return swap(s,anchor,new+anchor)
    x,z=s.split(a,1);_,y=z.split(b+'\n',1)
    return x+new+y


def strip(s,key,fmt):
    a,b=(fmt.format(f'Chaines/{key}/{p}') for p in ('debut','fin'))
    x,z=s.split(a,1);_,y=z.split(b+'\n',1)
    return x+y


def without_side_chains(h,t):
    h=strip(strip(h,'css','/* {} */'),'html','<!-- {} -->')
    h=swap(h,'<title>Destiny · Bourgeons — les chaînes de l’Accueil</title>',TITLE)
    t=strip(t,'js','// {}')
    swaps=[
      ('phase:0,seuil:true,chaines:true,','phase:0,seuil:true,'),
      (', rails=chainesAt(r,p);',';'),
      ('\n  for(const [x,y,b] of rails)drawPicture(c,b,x,y);',''),
      ('...rails.map(q=>q[2]),',''),
      ('...chainesAt(r,i).map(q=>q[2]),',''),
      ('updateFilm();updateSeuil();updateChaines();','updateFilm();updateSeuil();'),
      ("  if(s.page==='atlas'){paintSeuil();paintChaines();}","  if(s.page==='atlas')paintSeuil();"),
      ("    if(s.page==='atlas'){paintSeuil(true);paintChaines(true);}","    if(s.page==='atlas')paintSeuil(true);"),
      ('ni les décors fixes de l’Accueil.','ni l’habillage du seuil.'),
      ('setupChaines();setupSeuil();','setupSeuil();'),
    ]
    for a,b in swaps:t=swap(t,a,b)
    return h,t


def signature(d):
    return hashlib.sha256(json.dumps({k:v for k,v in d.items() if k!='grille_accueil'},ensure_ascii=False).encode()).hexdigest()


def main():
    h,d,t=F.page()
    assert 'seuil_accueil' in d and 'verdure' in d
    if 'chaines_accueil' in d:
        h,t=without_side_chains(h,t);del d['chaines_accueil']
    first='grille_accueil' not in d
    before=signature(d)
    d['grille_accueil'],report=F.build(d)
    assert signature(d)==before
    assert (len(d['rooms']),sum(len(r['gates']) for r in d['rooms']),sum(bool((r['south'] or {}).get('band')) for r in d['rooms']))==(15,29,7)
    if first:
        h=swap(h,TITLE,'<title>Destiny · Bourgeons — la grille de l’Accueil</title>')
        h=swap(h,'<div id="accesses"></div></div>', '<div id="accesses"></div><div class="grille-editor-tools" id="grille-editor-tools" hidden><button class="soft grille-lever" id="grille-editor-lever" type="button" aria-controls="accesses"><span>Lever la grille</span></button><small id="grille-editor-status" role="status" aria-live="polite">Fermée · passage bloqué</small></div></div>')
        old="  $('accesses').replaceChildren(...r.gates.map((g,i)=>{const to=gameMap.get(g.dest);const p=to?button('portal',(i+1)+' · '+to.label,()=>selectRoom(to.id)):make('span','portal-out',(i+1)+' · Falaise');p.title=g.id;return p;}));"
        swaps=[
          (old,"  $('accesses').replaceChildren(...portesPour(r));"),
          ('items=dataFor(r),lianes=s.lianes,ms=clock.ms}=opts;', 'items=dataFor(r),lianes=s.lianes,ms=clock.ms,gateFrame=lift.frame}=opts;'),
          ('const vines=lianesAt(r,p,lianes), doorstep=seuilAt(r,p);', 'const vines=lianesAt(r,p,lianes), doorstep=seuilAt(r,p), gate=grilleAt(r,p);'),
          ('  drawPicture(c,r.m[p][1],0,0);','  drawPicture(c,r.m[p][1],0,0);\n  drawGrille(c,gate,gateFrame);'),
          ('...doorstep.map(q=>q[2]),...items.map','...doorstep.map(q=>q[2]),...(gate?[gate]:[]),...items.map'),
          ('const r=s.room,i=s.phase,v=viewport(),items=[...dataFor()],lianes=s.lianes,ms=clock.ms,mode=s.mode;const bits=', 'const r=s.room,i=s.phase,v=viewport(),items=[...dataFor()],lianes=s.lianes,ms=clock.ms,mode=s.mode,gateFrame=lift.frame,gate=grilleAt(r,i);const bits='),
          ('...seuilAt(r,i).map(q=>q[2]),...items.map','...seuilAt(r,i).map(q=>q[2]),...(gate?[gate]:[]),...items.map'),
          ('drawScene(out.getContext(\'2d\'),r,i,v,{items,lianes,ms});','drawScene(out.getContext(\'2d\'),r,i,v,{items,lianes,ms,gateFrame});'),
          ('updateFilm();updateSeuil();','updateFilm();updateSeuil();updateGrille();'),
          ("  if(s.page==='atlas')paintSeuil();","  if(s.page==='atlas'){paintSeuil();paintGrille();}"),
          ("    if(s.page==='atlas')paintSeuil(true);","    if(s.page==='atlas'){paintSeuil(true);paintGrille(true);}"),
          ('ni l’habillage du seuil.','ni la grille ni l’habillage du seuil.'),
          ('setupSeuil();setupAtlas();','setupGrille();setupSeuil();setupAtlas();'),
        ]
        for a,b in swaps:t=swap(t,a,b)
    h=insert(h,'</style>','Panneau.css','/* {} */')
    h=insert(h,'<!-- Accueil/section/debut -->','Panneau.html','<!-- {} -->')
    t=insert(t,'setupGrille();setupSeuil();','Panneau.js','// {}')
    out=h+F.MARK+json.dumps(d,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+'</script>'+t
    tmp=F.HTML.with_suffix('.part');tmp.write_text(out,encoding='utf8');tmp.replace(F.HTML)
    report['donnees_lumieres_plans_seuil_sud_sha256']=before
    (F.OUT/'Index-Tilesheet.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(f'PASS · grille guillotine intégrée, {len(d["grille_accueil"]["positions"])} images, anciennes rambardes retirées de l’aperçu · {F.HTML.stat().st_size:,} o')


if __name__=='__main__':main()
