from pathlib import Path
import sys,json,io,struct,hashlib
from PIL import Image
sys.path.insert(0,'/home/user/PMU-Destiny-module');import pmu_core as c
R=Path('/home/user/chantier-ressources-pmu');T=Path('/home/user/chantier-apercu-reverie/travail');tree=json.load(open('/home/user/chantier-defauts-46-52/arbre-057.json'));paths={x['path'] for x in tree['tree'] if x['type']=='blob'}
pairs=[(7,3234,3235,'Fleurs_orange_01'),(7,3248,3249,'Fleurs_jaunes_01'),(7,3254,3268,'Fleurs_blanches_01'),(7,3282,3283,'Fleurs_potager_01'),(7,5772,5773,'Fleurs_mauves_01'),(7,2954,2955,'Fleurs_orange_02'),(7,2956,2957,'Fleurs_rose_01'),(7,2968,2969,'Fleurs_cyan_01'),(7,2970,2971,'Fleurs_bleues_01'),(7,5832,5833,'Fleurs_bouquet_01')]
known={(i['base_set'],i['base_tile'],i['anime_set'],i['anime_tile']) for i in json.load(open(R/'inventaire-paires-animees.json'))['paires'] if i['references_valides']}
manifest=[];decos=[]
for i,(s,n,an,nom) in enumerate(pairs):
 assert (s,n,s,an) in known,(s,n,an)
 name='PMU_'+nom;dest='game/Content/Object/'+name+'.dir';assert dest not in paths
 frames=[c.image_tile(s,n),c.image_tile(s,an)];assert all(im and im.size==(32,32) for im in frames) and frames[0].tobytes()!=frames[1].tobytes()
 sheet=Image.new('RGBA',(64,32));sheet.paste(frames[0],(0,0));sheet.paste(frames[1],(32,0))
 # PMDO imports PNG into premultiplied texture and DirSheet saves it.
 premul=Image.frombytes('RGBA',sheet.size,bytes(v for rgba in sheet.getdata() for v in (rgba[0]*rgba[3]//255,rgba[1]*rgba[3]//255,rgba[2]*rgba[3]//255,rgba[3])))
 mem=io.BytesIO();premul.save(mem,format='PNG');pngdata=mem.getvalue();payload=struct.pack('<q',len(pngdata))+pngdata+struct.pack('<iiii',32,32,0,2)
 d=T/dest;d.parent.mkdir(parents=True,exist_ok=True)
 if d.exists():assert d.read_bytes()==payload
 else:d.write_bytes(payload)
 imp=T/'art/pmu/objets-source'/f'{name}.2.png';imp.parent.mkdir(parents=True,exist_ok=True);sheet.save(imp)
 x=32+(i%5)*64;y=64+(i//5)*96
 decos.append({'MapLoc':{'X':x,'Y':y},'ObjectAnim':{'$type':'RogueEssence.Content.ObjAnimData, RogueEssence','AnimIndex':name,'FrameTime':15,'StartFrame':-1,'EndFrame':-1,'AnimDir':0,'Alpha':255,'AnimFlip':0}})
 manifest.append({'nom':name,'source_set':s,'base_tile':n,'anim_tile':an,'trames':2,'duree_frames_60fps':15,'duree_ms_approx':250,'cadence':'globale PMU 2014, MapViewer.OnTick','sha256_dir':hashlib.sha256(payload).hexdigest()})
# A separate developer Ground; no insertion into existing maps.
p=json.loads((c.R/'Cartes_PMU/modele-ground.json').read_text(encoding='utf-8-sig'));o=p['Object'];W,H=40,30
o['Name']['DefaultText']='PMU - Fleurs animees';o['AssetName']='pmu_fleurs_animees_dev';o['Comment']='Catalogue partiel PMU, 10 fleurs en deux phases, 15 frames par phase.';o['Released']=False;o['Music']='';o['TexSize']=1
o['obstacles']=[[{'Bounds':{'X':x*8,'Y':y*8,'Width':8,'Height':8},'Tags':0} for y in range(H)] for x in range(W)]
page,x,y=c.locate(7,4);grid=[]
for cx in range(W):
 col=[]
 for cy in range(H):
  f={'Sheet':page['nom'],'TexLoc':{'X':x//8+(cx%4),'Y':y//8+(cy%4)}}
  col.append({'AutoTileset':'','Associates':[],'Layers':[{'Frames':[f],'FrameLength':60}],'NeighborCode':0})
 grid.append(col)
o['Layers']=[{'Name':'Sol PMU','Layer':0,'Visible':True,'Tiles':grid}]
o['Decorations']=[{'Name':'Fleurs PMU - cadence 15','Layer':0,'Visible':True,'Anims':decos}]
o['Entities']=[{'Name':'Entités','Visible':True,'MapChars':[],'GroundObjects':[],'Spawners':[],'Markers':[{'EntName':'Main_Entrance_Marker','Direction':4,'EntEnabled':True,'triggerType':0,'Collider':{'X':8,'Y':8,'Width':16,'Height':16}}]}]
ground='game/Data/Ground/pmu_fleurs_animees_dev.rsground';assert ground not in paths;d=T/ground;d.parent.mkdir(parents=True,exist_ok=True);d.write_text('\ufeff'+json.dumps(p,ensure_ascii=False,separators=(',',':')),encoding='utf8')
(T/'art/pmu/objets-source/fleurs-animees.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
print('PASS : 10 fleurs, 20 trames 32x32, 10 .dir et PNG .2, 1 Ground séparé, cadence 15 ; aucun Ground existant modifié')
