from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,struct,io,base64,html
R=Path(__file__).resolve().parent;W=R/'travail/game/Data/Ground';P=Path('/home/user/PMU-Destiny-module/Planches_PNG');O=R/'apercu-integrations-pmu';O.mkdir(exist_ok=True)
names=[('maison_equipe_falaise','Maison de l’équipe · Daycliff','Auberge PMU s1506'),('reverie_rock_home','Maison de pierre','PMU s1142'),('reverie_fire_home','Maison feu','PMU s1143'),('reverie_grass_home','Maison plante','PMU s1144'),('reverie_normal_home','Maison normale','PMU s1145'),('reverie_water_home','Maison aquatique','PMU s1146'),('reverie_electric_home','Maison électrique','PMU s1373')]
sheets={};png=(R/'Hay_Bed.dir').read_bytes();n=struct.unpack_from('<q',png)[0];bed=Image.open(io.BytesIO(png[8:8+n])).convert('RGBA')
assert bed.size==(40,40)
def get(s):
 if s not in sheets:sheets[s]=Image.open(P/(s+'.png')).convert('RGBA')
 return sheets[s]
images=[]
for code,title,ref in names:
 data=json.loads((W/(code+'.rsground')).read_text(encoding='utf-8-sig'))['Object']; layers=data['Layers'];w=len(data['obstacles']);h=len(data['obstacles'][0]);im=Image.new('RGBA',(w*8,h*8),(0,0,0,255))
 for index,layer in enumerate(layers):
  if index==3 and code=='maison_equipe_falaise':
   for obj in data['Entities'][0]['GroundObjects']:
    if obj['ObjectAnim']['AnimIndex']=='Hay_Bed':
     c=obj['Collider'];o=obj['DrawOffset'];im.alpha_composite(bed,(c['X']-o['X'],c['Y']-o['Y']))
  sheet_layer=Image.new('RGBA',im.size)
  for x,col in enumerate(layer['Tiles']):
   for y,cell in enumerate(col):
    for a in cell['Layers']:
     if a['Frames']:
      f=a['Frames'][0];s=f['Sheet']
      if s:
       xy=f['TexLoc'];tile=get(s).crop((xy['X']*8,xy['Y']*8,xy['X']*8+8,xy['Y']*8+8));sheet_layer.alpha_composite(tile,(x*8,y*8))
  im.alpha_composite(sheet_layer)
 f=O/(code+'.png');im.save(f);images.append((code,title,ref,im,f));print(code,im.size)
# Planche à taille native divisée par deux, sans interpolation.
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',16); bold=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',20)
board=Image.new('RGB',(1000,4*300+100),'#f4f7f3');d=ImageDraw.Draw(board);d.text((20,14),'Intérieurs PMU · intégrations locales (jour)',font=bold,fill='#19364a');d.text((20,43),'Recomposition des cartes et des lits · pas une capture en jeu',font=font,fill='#536b70')
for i,(code,title,ref,im,f) in enumerate(images):
 x=20+(i%3)*330;y=85+(i//3)*300;d.text((x,y),title,font=font,fill='#19364a');d.text((x,y+21),ref,font=font,fill='#536b70');mini=im.resize((320,240),Image.Resampling.NEAREST);board.paste(mini,(x,y+47))
board=board.crop((0,0,1000,985));board.save(R/'apercu-interieurs-pmu-integres.png')
blocks=[]
for code,title,ref,im,f in images:
 uri='data:image/png;base64,'+base64.b64encode(f.read_bytes()).decode();blocks.append('<article><header><div class="label">'+html.escape(ref)+'</div><h2>'+html.escape(title)+'</h2></header><a href="'+uri+'" download="'+code+'.png"><img src="'+uri+'" alt="'+html.escape(title)+' : recomposition des cinq calques"></a><p>Cliquer pour enregistrer l’image à taille native.</p></article>')
page='''<!doctype html><html lang="fr"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Intérieurs PMU · aperçu local</title><style>body{margin:0;background:#f3f7f3;color:#19364a;font:16px/1.5 system-ui}main{max-width:1400px;margin:auto;padding:40px 24px 70px}h1{font-size:clamp(34px,5vw,58px);line-height:1.08;margin:12px 0}h2{font-size:21px;margin:6px 0}.over,.label{color:#297566;font-weight:750;text-transform:uppercase;letter-spacing:.12em;font-size:12px}.lead{max-width:900px;color:#586f72;font-size:18px}.notice{padding:18px;background:#fff2db;border:1px solid #efd8aa;border-radius:12px;margin:25px 0}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(340px,1fr));gap:20px}article{background:white;border:1px solid #dce7df;border-radius:14px;overflow:hidden}header,p{padding:12px 16px;margin:0}article p{font-size:13px;color:#667c7b}article img{image-rendering:pixelated;width:100%;height:auto;display:block;background:#000}footer{margin-top:35px;color:#657a79;font-size:13px}@media(max-width:500px){.grid{grid-template-columns:1fr}main{padding:25px 14px}}</style><main><div class="over">Réverie &amp; Daycliff · cartes en cours</div><h1>Les intérieurs PMU préparés</h1><p class="lead">Sept cartes issues des fichiers locaux : la maison de l’équipe sur Daycliff et six maisons de Réverie.</p><div class="notice"><b>État réel :</b> recomposition statique des cinq calques et, pour Daycliff, des deux lits placés. Ce n’est pas une capture du jeu : personnages, mouvements, collisions, son et nuit ne sont pas montrés ni validés. La hutte, l’auberge de Réverie, Draco et la fusion des secteurs ne sont pas encore intégrés.</div><div class="grid">'''+''.join(blocks)+'''</div><footer>Graphismes : sources historiques PMU-Client et PMU-Server 2014. Les objets de lit Daycliff viennent du jeu Destiny. Droits des graphismes individuels à vérifier avant redistribution. Cadence des animations PMU non confirmée.</footer></main></html>'''
(R/'apercu-interieurs-pmu.html').write_text(page,encoding='utf8');print('Aperçus créés')
