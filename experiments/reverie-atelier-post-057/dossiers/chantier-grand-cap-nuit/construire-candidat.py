#!/usr/bin/env python3
"""Candidat séparé : Grand Cap historique + APNG V24P01A, sans raccord de jeu."""
from pathlib import Path
from PIL import Image,ImageChops
import json,struct,io,hashlib,copy,sys
R=Path('/home/user/chantier-grand-cap-nuit'); sys.path.insert(0,'/home/user/destiny-reference/tools');from preview_maps import SheetReader
original=json.loads((R/'grand-cap-nuit-original.rsground').read_text(encoding='utf-8-sig'));obj=original['Object'];assert len(obj['Layers'])==6 and len(obj['Layers'][0]['Tiles'])==150
w,h=1200,880;tile_w=312;upper=168; assert upper+128==296
src=Image.open(R/'V24P01A-original-anime.png'); assert src.n_frames==12 and src.size==(312,240)
frames=[];reference=[]
for i in range(12):
 src.seek(i); ref=src.convert('RGBA');reference.append(ref.copy())
 frame=Image.new('RGBA',(tile_w,h),(0,0,79,255))
 # Prolonger le ciel par sa partie haute étoilée (sans dupliquer le banc
 # de nuages d'horizon), en décalant les bandes de pixels natifs.
 band_sky=ref.crop((0,0,312,16))
 for y in range(0,upper,16):
  dec=((y//16)*37)%312
  frame.paste(band_sky,(dec,y));frame.paste(band_sky,(dec-312,y))
 # Image complète intacte : ciel + horizon + mer, avec horizon à y=296.
 frame.paste(ref,(0,upper))
 # Prolonger la mer par ses 24 dernières lignes natives, sur la même phase.
 band=ref.crop((0,216,312,240))
 for y in range(408,h,24):frame.paste(band,(0,y))
 assert frame.crop((0,168,312,408)).tobytes()==ref.tobytes()
 frames.append(frame)
# DirSheet PMDO : bande horizontale, 12 cases 312x880, RotateType.None=0.
atlas=Image.new('RGBA',(tile_w*12,h));
for i,fr in enumerate(frames):atlas.paste(fr,(i*tile_w,0))
out=io.BytesIO();atlas.save(out,format='PNG',optimize=True);png=out.getvalue();(R/'candidat/Content/BG/GrandCap_V24P01A_Nuit.dir').write_bytes(struct.pack('<q',len(png))+png+struct.pack('<iiii',312,880,0,12))
# Ne retoucher que le fond : enlever le calque 0 opaque, remplacé par MapBG.
doc=copy.deepcopy(original);o=doc['Object'];old=o['Layers'].pop(0)
bg=o['Background'];bg['MapLoc']={'X':0,'Y':0}; bg['BGAnim']={'AnimIndex':'GrandCap_V24P01A_Nuit','FrameTime':8,'StartFrame':0,'EndFrame':11,'AnimDir':-1,'Alpha':255,'AnimFlip':0};bg['BGMovement']={'X':0,'Y':0};bg['Parallax']='1, 1';bg['RepeatX']=True;bg['RepeatY']=False
# Identifiant de carte neuf pour ne pas remplacer un Ground existant.
o['AssetName']='grand_cap_panoramique_nuit';o['Name']={'DefaultText':'Grand Cap panoramique — nuit','LocalTexts':{'fr':'Grand Cap panoramique — nuit'}}
o['Comment']='Candidat Grand Cap nocturne ; fond V24P01A, 12 phases ; aucun raccordement installé.'
p=R/'candidat/Data/Ground/grand_cap_panoramique_nuit.rsground';p.write_text(json.dumps(doc,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
# Vérifier qu'aucune donnée hors fond et identité n'est modifiée.
a=copy.deepcopy(original);b=copy.deepcopy(doc)
a['Object']['Layers'].pop(0)
for field in ['Background','AssetName','Name','Comment']:a['Object'].pop(field,None);b['Object'].pop(field,None)
assert a==b
# Rendu hors moteur : terrain natif, sans PNJ et sans simulation de la caméra.
reader=SheetReader(R/'candidat/Content/Tile/Metano_Town_Base_Night.tile'); terrain=Image.new('RGBA',(w,h),(0,0,0,0));missing=[];n=0
for lay in o['Layers']:
 if not lay.get('Visible',True):continue
 for x,col in enumerate(lay['Tiles']):
  for y,t in enumerate(col):
   for sub in t.get('Layers',[]):
    for f in sub.get('Frames',[])[:1]:
     if f.get('Sheet')!='Metano_Town_Base_Night':missing.append(f.get('Sheet'));continue
     tex=f['TexLoc'];im=reader.get_tile(tex['X'],tex['Y']);
     if im is None:missing.append(str(tex));continue
     terrain.alpha_composite(im,(x*8,y*8));n+=1
reader.close();assert not missing,missing[:20];terrain.save(R/'apercu/terrain-grand-cap-nuit.png')
views=[]
for frame in frames:
 bg=Image.new('RGBA',(w,h))
 for x in range(0,w,tile_w):bg.paste(frame,(x,0))
 bg.alpha_composite(terrain);views.append(bg.convert('RGB'))
views[0].save(R/'apercu/grand-cap-nuit-phase-01.png',optimize=True)
views[0].save(R/'apercu/grand-cap-nuit-anime.png',format='PNG',save_all=True,append_images=views[1:],duration=[133.333]*12,loop=0,disposal=0,blend=0,optimize=True)
views[0].resize((960,704),Image.Resampling.NEAREST).save(R/'apercu/grand-cap-nuit-anime.gif',save_all=True,append_images=[f.resize((960,704),Image.Resampling.NEAREST) for f in views[1:]],duration=130,loop=0,optimize=True,disposal=2)
proof={'source_apng_sha256':hashlib.sha256((R/'V24P01A-original-anime.png').read_bytes()).hexdigest(),'original_ground_sha256':hashlib.sha256((R/'grand-cap-nuit-original.rsground').read_bytes()).hexdigest(),'frames':12,'frame_ms_original':133.333333,'ticks_proposes':8,'horizon_original_haut':128,'horizon_adapte':296,'scroll_background':{'repeat_x':True,'repeat_y':False,'parallax':'1, 1'},'frame_1x_pixels_inchanges':True,'terrain_couleurs_non_modifiees':True,'geometry_collisions_entities_remaining_layers_unchanged':True,'terrain_tiles_rendues':n,'missing_tiles':missing,'tests_moteur':False,'raccordement_escalier':False,'limites':'Rendu statique/animation hors moteur ; répétition de la source, raccords et comportement caméra à valider en jeu.'}
(R/'preuves.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2));print(json.dumps(proof,ensure_ascii=False,indent=2))
