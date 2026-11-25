from pathlib import Path
import json,requests,zipfile,concurrent.futures,hashlib,io,sys,struct
import numpy as np
from PIL import Image
R=Path('/home/user/chantier-raccords-et-pmu');M=Path('/home/user/PMU-Destiny-module');sys.path.insert(0,str(M));import pmu_core as c
P=json.loads((M/'manifest-banques.json').read_text())['pages'];pairs=json.loads(Path('/home/user/chantier-ressources-pmu/inventaire-paires-animees.json').read_text())['paires'];src=Path('/home/user/chantier-ressources-pmu/sauvegarde-travail-local-ressources.zip');C='ee39156a24f350b67e81740478be8505f4ff1a05'
def bank(p):
 r=requests.get(f'https://raw.githubusercontent.com/meromoonmeri/PMDO-Destiny/{C}/game/Content/Tile/{p["nom"]}.tile',timeout=120);r.raise_for_status();data=r.content;assert hashlib.sha256(data).hexdigest()==p['sha256_tile'];assert struct.unpack_from('<i',data)[0]==8;return p['nom'],data
archive=R/'candidat-banques-et-15-objets-pmu.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=5) as z:
 with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
  for name,data in ex.map(bank,P):z.writestr(f'game/Content/Tile/{name}.tile',data)
 with zipfile.ZipFile(src) as input:
  names=[n for n in input.namelist() if n.startswith('travail/game/Content/Object/PMU_') and n.endswith('.dir')];assert len(names)==15
  for name in names:z.writestr(name.removeprefix('travail/'),input.read(name))
  for name in input.namelist():
   if name.startswith('travail/art/pmu/objets-source/') and name.endswith('.png'):z.writestr(name.removeprefix('travail/'),input.read(name))
  z.writestr('game/Data/Ground/pmu_fleurs_animees_dev.rsground',input.read('travail/game/Data/Ground/pmu_fleurs_animees_dev.rsground'))
 z.writestr('manifest-banques.json',(M/'manifest-banques.json').read_text());z.writestr('preuve-15-objets.json',Path('/home/user/apercu-global-reverie/preuve-15-objets.json').read_text());
 z.writestr('LISEZ-MOI.txt','CANDIDAT LOCAL NON INSTALLE. 40 banques PMDO du commit Destiny v0.5.7 déjà présentes en dépôt ; 5 objets et 10 fleurs localement préparés, non validés en moteur. La carte fleurs est un catalogue dev non raccordé. Ne jamais écraser un projet sans sauvegarde et comparaison ; il faut régénérer les index avec les outils PMDO et tester dans une copie. Ce paquet NE contient PAS tous les objets entiers ni toutes les animations PMU. Voir le rapport du chantier. Aucun personnage PMU.\n')
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
print('40 banques et 15 objets, CRC OK',archive.stat().st_size,hashlib.sha256(archive.read_bytes()).hexdigest(),flush=True)
# All valid pairs, exposed strictly as single-cell fragments for dev auditing;
# the tuples cannot establish object boundaries and are kept out of game/Content/Object.
valid=[p for p in pairs if p['references_valides']];invalid=[p for p in pairs if not p['references_valides']];assert len(valid)==4058 and len(invalid)==22
zpath=R/'fragments-animes-pmu-4058-non-assembles.zip';manifest=[];blank=Image.new('RGBA',(32,32))
with zipfile.ZipFile(zpath,'w',zipfile.ZIP_DEFLATED,compresslevel=5) as z:
 for p in valid:
  name=f'PMU_FragmentAnim_{p["base_set"]:02}_{p["base_tile"]:05}_{p["anime_set"]:02}_{p["anime_tile"]:05}'
  frame1=c.image_tile(p['base_set'],p['base_tile']) if p['base_tile'] else blank;frame2=c.image_tile(p['anime_set'],p['anime_tile']) if p['anime_tile'] else blank;assert frame1 and frame2
  im=Image.new('RGBA',(64,32));im.paste(frame1,(0,0));im.paste(frame2,(32,0));arr=np.array(im,dtype=np.uint16);arr[:,:,:3]=(arr[:,:,:3]*arr[:,:,3:4])//255;pm=Image.fromarray(arr.astype(np.uint8));b=io.BytesIO();pm.save(b,format='PNG');png=b.getvalue();directory=struct.pack('<q',len(png))+png+struct.pack('<iiii',32,32,0,2)
  # Format, dimensions, every premultiplied pixel, and two-frame sequence.
  ln=struct.unpack_from('<q',directory)[0];assert struct.unpack_from('<iiii',directory,8+ln)==(32,32,0,2);assert Image.open(io.BytesIO(directory[8:8+ln])).convert('RGBA').tobytes()==pm.tobytes()
  z.writestr('fragments-non-assembles/'+name+'.dir',directory);manifest.append({'id':name,**p,'sha256_dir':hashlib.sha256(directory).hexdigest()})
 z.writestr('inventaire-fragments.json',json.dumps({'nombre':len(manifest),'elements':manifest,'paires_invalides_non_converties':invalid},ensure_ascii=False,separators=(',',':')))
 z.writestr('LISEZ-MOI.txt','Ces 4058 fichiers DirSheet représentent chacun DEUX CASES de 32x32 et non des objets complets. Ils sont volontairement hors game/Content/Object : ne pas installer en bloc comme mobilier/cascades. Les 22 paires dont une référence manque sont listées séparément. Échelle native conservée ; cadence 250 ms indicative définie au placement, pas dans le fichier. Aucun test moteur ni validation artistique.\n')
with zipfile.ZipFile(zpath) as z:assert z.testzip() is None
print('4058 fragments à 2 phases contrôlés, 22 paires non convertibles, CRC OK',zpath.stat().st_size,hashlib.sha256(zpath.read_bytes()).hexdigest(),flush=True)
