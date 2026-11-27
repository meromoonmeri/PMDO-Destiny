#!/usr/bin/env python3
"""Refresh the active preview after precise vegetation fitting, leaving the archive intact."""
from pathlib import Path
from collections import Counter
import importlib.util,hashlib,json
import numpy as np
import Video

S=Path(__file__).resolve().parent

def load(name,file):
 spec=importlib.util.spec_from_file_location(name,S/file);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
L=load('pmd','Lumiere-PMD.py');V=load('verdure','Ajuster-verdure.py')
FILE=L.G/'Guilde-Destiny-Bourgeons-PMD.html';BACKUP=V.CACHE/'Bourgeons-avant.html'

def swap(s,a,b):
 assert s.count(a)==1,(s.count(a),a)
 return s.replace(a,b,1)


def main():
 h,d,t=L.page(FILE)
 if 'verdure' in d:
  assert BACKUP.exists(),'Recréer d’abord le montage de référence via Assembler.py.'
  h,d,t=L.page(BACKUP)
 else:
  V.CACHE.mkdir(parents=True,exist_ok=True);BACKUP.write_bytes(FILE.read_bytes())
 report=V.run(d,L);cnt=Counter(s['salle'] for s in report['poteaux']);br=Counter(s['salle'] for s in report['poteaux'] if s['rameau']);pixels=0;four_phases=[];alpha=[]
 _,before,_=L.page(BACKUP)
 d['verdure']={r['id']:{'poteaux':cnt[r['label']],'rameaux':br[r['label']]} for r in d['rooms'] if cnt[r['label']]}
 for key in ('rooms','ornements','nuits','lumieres','etoffes','catalog','canon','tints'):assert d[key]==before[key],key
 for r in d['rooms']:
  id=r['id'];a=d['lianes'][id];p=before['lianes'][id];changed=id in d['verdure'];assert a['v']==p['v'];assert (a!=p)==changed
  exp=L.night_frames(r,d);assert len({f.tobytes() for f in exp})==4
  four_phases.append(r['label'])
  for s in a['points']:
   for light,emission in s['images']:alpha.append(int(L.decode(light[2])[...,3].max()))
  if r['n']==3:glass=exp
  if changed:
   old=L.night_frames(r,before);pixels+=int(np.any(exp[2]!=old[2],axis=2).sum());guard=L.extract_alpha(d,r)
   assert all(np.array_equal(n[guard],p[guard]) for n,p in zip(exp,old,strict=True))
 assert max(alpha)<=25
 d['reference']['salon']=L.pack(glass[2]);src,_=L.ref_frames();Video.build(src,glass,verdure=True)
 d['film']=dict(webm=L.uri(Video.VIDEO.read_bytes(),'video/webm'),mp4=L.uri(Video.MP4.read_bytes(),'video/mp4'),poster=L.uri(Video.POSTER.read_bytes(),'image/webp'))
 h=swap(h,'<title>Destiny · Bourgeons — lumière PMD</title>','<title>Destiny · Bourgeons — verdure ajustée</title>')
 h=swap(h,'Les teintes et le rythme viennent de la falaise nocturne de Grodoudou, avec des reflets tamisés sur les feuilles et le bois proche.', 'Les lianes ajustées suivent le bois des poteaux, avec quelques ronces courtes au pied. Les bourgeons gardent la lumière tamisée inspirée de la falaise de Grodoudou.')
 h=swap(h,'Voir les bourgeons dans le Grand Salon','Voir les lianes ajustées dans le Grand Salon')
 h=swap(h,'Sans son · détail à 4 s','Sans son · poteaux en gros plan à 4 s')
 h=swap(h,'</style>','.badges-verdure{margin-left:auto;color:#dbe6cb;background:#26362a;border:1px solid #475c49;border-radius:4px;padding:1px 4px;font-size:9px;white-space:nowrap}\n.atlas-card-meta{flex-wrap:wrap}\n</style>')
 t=swap(t,'    open.append(scene,label,meta);panel.append(open);', '''    const fitted=data.verdure[r.id];
    if(fitted){const chip=make('span','badges-verdure','Verdure ajustée');chip.title=`${fitted.poteaux} poteau${fitted.poteaux===1?'':'x'}${fitted.rameaux?' · ronce au pied':''}`;meta.append(chip);}
    open.append(scene,label,meta);panel.append(open);''')
 t=swap(t,'En Nuit, regarde la base des lianes et les premières planches. Les ornements muraux facultatifs n’émettent pas de lumière.', 'Les cartes « Verdure ajustée » indiquent les poteaux repris. En Nuit, seuls les bourgeons émettent.')
 result=h+L.MARK+json.dumps(d,separators=(',',':'),ensure_ascii=False).replace('</','<\\/')+'</script>'+t
 FILE.with_suffix('.tmp').write_text(result,encoding='utf8');FILE.with_suffix('.tmp').replace(FILE)
 report.update(salles_ajustees=list(d['verdure']),salles_hors_retouche_identiques=15-len(d['verdure']),images_nuit_par_salle=4,reflets_alpha_max_255=max(alpha),emetteurs_bourgeons=30,pixels_retouches_nuit_3=pixels,anciens_plans_sha256=hashlib.sha256(BACKUP.read_bytes()).hexdigest(),jeu_modifie=False)
 L.jsonout(L.OUT/'Verdure/Index-ajustements.json',report)
 print(f'PASS · {len(d["verdure"])} salles affinées, {report["poteaux_repris"]} poteaux repris, {report["rameaux_courts"]} ronces, 30 bourgeons · {FILE.stat().st_size:,} o',flush=True)

if __name__=='__main__':main()
