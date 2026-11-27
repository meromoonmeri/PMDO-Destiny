#!/usr/bin/env python3
"""Prototype V2 : palettes extraites des sols PMDO, animation montée/retombée, garde eau."""
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,io,struct,copy,json,shutil,csv,math
H=Path.home();G=H/'.cache/destiny-test/game/PMDO-Destiny';P=H/'Capacites-Z/Prototypes/Eruption-Geo-Sismique/Generation-PMDO';P.mkdir(parents=True,exist_ok=True)
# Couleurs de références ; association la plus proche à partir des vrais échantillons de sols.
anchors={'terre':(141,102,64),'sable':(221,176,104),'foret':(156,150,74),'verdure':(75,133,77),'pierre':(139,137,132),'neige':(208,230,221),'volcan':(130,73,53),'sombre':(86,53,91),'bleute':(84,129,164)}
# Index de texture directement dans les fichiers .tile (TileIndexNode suivi de PNG).
def getframe(obj):
 if isinstance(obj,dict):
  if isinstance(obj.get('Frames'),list) and obj['Frames']:
   t=obj['Frames'][0]
   if 'Sheet' in t and 'TexLoc' in t:return t
  for x in obj.values():
   r=getframe(x)
   if r:return r
 if isinstance(obj,list):
  for x in obj:
   r=getframe(x)
   if r:return r
 return None
indices={}
def sample(t):
 sheet=t['Sheet'];loc=t['TexLoc'];p=G/'Content/Tile'/(sheet+'.tile')
 if not p.exists():return None
 if sheet not in indices:
  with p.open('rb') as f:
   size,count=struct.unpack('<ii',f.read(8))
   if count<0 or count>100000:raise ValueError('index invalide')
   indices[sheet]={(x,y):pos for x,y,pos in struct.iter_unpack('<iiq',f.read(count*16))}
 pos=indices[sheet].get((loc['X'],loc['Y']))
 if not pos:return None
 with p.open('rb') as f:f.seek(pos);n=struct.unpack('<q',f.read(8))[0];data=f.read(n)
 im=Image.open(io.BytesIO(data)).convert('RGBA');a=np.array(im);rgb=a[:,:,:3][a[:,:,3]>200]
 if len(rgb)<12:return None
 return tuple(int(x) for x in np.median(rgb,axis=0))
entries={};missing=[];rows=[]
for p in (G/'Data/AutoTile').glob('*.json'):
 try:
  obj=json.loads(p.read_text(encoding='utf-8-sig'))['Object']['Tiles']; t=getframe(obj);color=sample(t) if t else None
  if color is None:missing.append(p.stem);continue
  # Pondération raisonnable pour les écarts entre canaux ; pas de classification par nom de biome.
  nearest=min(anchors,key=lambda k:sum((color[i]-anchors[k][i])**2 for i in range(3)))
  entries[p.stem]=nearest;rows.append((p.stem,*color,nearest,t['Sheet']))
 except (OSError,ValueError,KeyError,struct.error):missing.append(p.stem)
with (P/'correspondance-palettes-auto.csv').open('w',encoding='utf-8',newline='') as f:
 w=csv.writer(f);w.writerow(['autotile','rouge','vert','bleu','palette','source_tileset']);w.writerows(sorted(rows))
(P/'autotiles-sans-echantillon.txt').write_text('\n'.join(sorted(missing)))
def cut(name,size):
 im=Image.open(P/name).convert('RGB');im.thumbnail((size,size),Image.Resampling.NEAREST);a=np.array(im);b=a.astype('int16');mask=(b[:,:,1]>125)&(b[:,:,1]>b[:,:,0]+45)&(b[:,:,1]>b[:,:,2]+45);out=Image.fromarray(np.dstack((a,np.where(mask,0,255).astype('uint8'))),'RGBA');return out.crop(out.getbbox())
def tint(im,color,light):
 a=np.array(im).astype('float32');lum=(a[:,:,0]*.299+a[:,:,1]*.587+a[:,:,2]*.114)/255
 mult=light[0]+lum*light[1];out=np.empty_like(a);out[:,:,:3]=np.clip(mult[:,:,None]*np.array(color)[None,None,:],0,255);out[:,:,3]=a[:,:,3];return Image.fromarray(out.astype('uint8'),'RGBA')
def bank(name,frames,N):
 sheet=Image.new('RGBA',(N*len(frames),N*8));
 for row in range(8):
  for i,f in enumerate(frames):sheet.alpha_composite(f,(i*N,row*N))
 sheet.save(P/(name+'.png'));b=io.BytesIO();sheet.save(b,format='PNG');png=b.getvalue();f=P/(name+'.dir');f.write_bytes(struct.pack('<q',len(png))+png+struct.pack('<iiii',N,N,4,len(frames)));shutil.copy2(f,G/'Content/Particle'/f.name)
crack0=cut('fissures-source.png',128);spike0=cut('pointe-source.png',60);overview=Image.new('RGB',(800,9*100),(35,32,30));d=ImageDraw.Draw(overview)
for pi,(palette,col) in enumerate(anchors.items()):
 crack=tint(crack0,col,(.12,.60));spike=tint(spike0,col,(.30,.95));frames=[];N=144
 for i in range(24):
  size=min(128,16+i*13);alpha=220 if i<17 else max(0,220-(i-16)*30);part=crack.resize((size,size),Image.Resampling.NEAREST);part.putalpha(part.getchannel('A').point(lambda x:x*alpha//255));f=Image.new('RGBA',(N,N));f.alpha_composite(part,((N-size)//2,(N-size)//2));frames.append(f)
 bank('GeoV2_Fissure_'+palette,frames,N)
 # Dessin de la roche sans écrasement vertical : son sommet monte depuis la ligne de sol.
 frames=[];N=80;body=spike.resize((34,48),Image.Resampling.NEAREST)
 for i in range(22):
  f=Image.new('RGBA',(N,N));base=54
  # Fissure au pied de chaque roche, dans la même animation que l'impact.
  if i<21:
   local_size=min(58,18+i*9); local_crack=crack.resize((local_size,max(8,local_size//2)),Image.Resampling.NEAREST)
   fade=210 if i<16 else max(0,210-(i-15)*35)
   local_crack.putalpha(local_crack.getchannel('A').point(lambda x:x*fade//255))
   f.alpha_composite(local_crack,((N-local_size)//2,base-local_crack.height//2))
  d2=ImageDraw.Draw(f)
  if i<7:reveal=min(48,(i+1)*7)
  elif i<14:reveal=48
  else:reveal=max(0,48-(i-13)*6)
  if reveal:
   # révélation du sommet à sa taille réelle, comme une colonne montant du sol
   top=body.crop((0,0,34,reveal));top.putalpha(top.getchannel('A').point(lambda x:x*(255 if i<15 else max(0,255-(i-14)*26))//255));f.alpha_composite(top,(23,base-reveal))
  if 3<=i<=19:
   for j in range(7):
    x=40+((j*19+i*7)%45)-22;y=base-((j*13+i*4)%24);color=tuple(min(255,int(q*(.75+0.1*(j%3)))) for q in col);d2.rectangle((x,y,x+1+(j%2),y+1),fill=(*color,max(0,210-max(0,i-14)*30)))
  frames.append(f)
 bank('GeoV2_Pointe_'+palette,frames,N)
 # Fiche de contrôle sur fond approximatif : pointe naissance, pic, retrait.
 draw=ImageDraw.Draw(overview);draw.rectangle((0,pi*100,799,pi*100+99),fill=tuple(int(v*.78) for v in col));draw.text((3,pi*100+3),palette,fill=(255,255,255))
 for j,k in enumerate([2,8,15,20]):
  f=frames[k];overview.paste(f,(100+j*100,pi*100+10),f)
overview.save(P/'v2-palettes-apparition-roches.png')
# Lua table de correspondance pré-calculée d'après les ressources réelles connues.
lua=['-- Échantillons de terrain calculés depuis les ressources PMDO disponibles.','local GEO_V2_PALETTES = {']
for k,v in sorted(entries.items()):lua.append('  ['+json.dumps(k)+'] = '+json.dumps(v)+',')
lua+=['}', '''function BATTLE_SCRIPT.GeoSismiqueV2_Preparer(owner, ownerChar, context, args)
 local map = _ZONE.CurrentMap
 local tile = map:GetTile(context.User.CharLoc)
 local terrain = tile.Data.ID
 if terrain == 'water' or terrain == 'water_poison' then
  _DUNGEON:LogMsg('Impossible de provoquer cette éruption depuis l’eau !')
  context.CancelState.Cancel = true
  PrintInfo('[GEO V2 EAU] refus terrain='..terrain..' pp-inchanges')
  return
 end
 local key = tile.Data.TileTex.AutoTileset
 if key == '' then
  if map.TextureMap:ContainsKey(terrain) then
   local tex = map.TextureMap[terrain]
   if tex then key = tex.AutoTileset end
  end
 end
 local pal = GEO_V2_PALETTES[key] or 'terre'
 context.HitboxAction.PreActions[0].Emitter.Anim.Anim.AnimIndex = 'GeoV2_Fissure_'..pal
 context.Data.HitFX.Emitter.Anim.Anim.AnimIndex = 'GeoV2_Pointe_'..pal
 PrintInfo('[GEO V2 BIOME] autotile='..tostring(key)..' palette='..pal..' terrain='..terrain)
end
''']
(H/'Capacites-Z/Sources/eruption-geo-v2-evenement.lua').write_text('\n'.join(lua))
def read(n):return json.loads((G/'Data/Skill'/f'{n}.json').read_text(encoding='utf-8-sig'))
z=json.loads((P/'tectonic_rage-test-only.json').read_text());a=z['Object'];a['HitboxAction']['PreActions'][0]['Emitter']['Anim']['Anim']['AnimIndex']='GeoV2_Fissure_terre';a['Data']['HitFX']['Emitter']['Anim']['Anim']['AnimIndex']='GeoV2_Pointe_terre';a['Data']['HitFX']['Delay']=36
a['Data']['BeforeTryActions'].append({'Key':{'str':[0]},'Value':{'$type':'RogueEssence.Dungeon.BattleScriptEvent, RogueEssence','Script':'GeoSismiqueV2_Preparer','ArgTable':'{}'}})
s=json.dumps(z,ensure_ascii=False,indent=2);(P/'tectonic_rage-v2-test-only.json').write_text(s);(G/'Data/Skill/tectonic_rage.json').write_text(s)
p=G/'Data/Script/origin/event_battle.lua';bak=H/'.cache/destiny-test/event-battle-avant-geo-v2.lua'
if not bak.exists():shutil.copy2(p,bak)
# Toujours repartir de la sauvegarde originale pour permettre une régénération sûre.
shutil.copy2(bak,p)
with p.open('a',encoding='utf-8') as f:f.write('\n'+(H/'Capacites-Z/Sources/eruption-geo-v2-evenement.lua').read_text())
print('Cartographie de',len(entries),'autotiles ;',len(missing),'sans échantillon ; 9 palettes ; 24/22 poses')
