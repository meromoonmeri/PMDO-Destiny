from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import gzip,ijson,json,io,struct,hashlib,re,zipfile
R=Path('/home/user/chantier-chemins-reverie');S=R/'base';D=R/'calques-publies-png';D.mkdir(exist_ok=True)
sheets={};cache={}
def tile(fr):
 name=fr.get('Sheet','');xy=fr['TexLoc'];key=(name,xy['X'],xy['Y'])
 if not name:return None
 if key in cache:return cache[key]
 if name not in sheets:
  b=(S/'game/Content/Tile'/f'{name}.tile').read_bytes();size,n=struct.unpack_from('<ii',b);assert size==8,(name,size);index={}
  for i in range(n):
   x,y,off=struct.unpack_from('<iiq',b,8+i*16);index[(x,y)]=off
  sheets[name]=(b,index)
 b,idx=sheets[name];off=idx[(xy['X'],xy['Y'])];size=struct.unpack_from('<q',b,off)[0];im=Image.open(io.BytesIO(b[off+8:off+8+size])).convert('RGBA');assert im.size==(8,8);cache[key]=im;return im
p=S/'payload/reverie_centre.rsground.gz';comp=Image.new('RGBA',(1600,4000));stats=[]
with gzip.open(p,'rb') as f:
 if f.read(3)!=b'\xef\xbb\xbf':f.seek(0)
 for i,l in enumerate(ijson.items(f,'Object.Layers.item')):
  piece=Image.new('RGBA',(1600,4000)); count=0
  for x,col in enumerate(l['Tiles']):
   for y,cell in enumerate(col):
    for anim in cell.get('Layers',[]):
     frames=anim.get('Frames',[])
     if frames:
      im=tile(frames[0])
      if im is not None:piece.alpha_composite(im,(8*x,8*y));comp.alpha_composite(im,(8*x,8*y));count+=1
  name=re.sub('[^A-Za-z0-9]+','_',l['Name']).strip('_');piece.save(D/f'{i+1:02}_{name}.png',optimize=True);stats.append({'nom':l['Name'],'niveau':l['Layer'],'tuiles':count,'bbox':piece.getbbox()});print('Rendu',i+1,l['Name'],count,flush=True)
comp.save(R/'reverie-0.5.0-rendu-phase0.png',optimize=True)
(R/'calques-publies-statistiques.json').write_text(json.dumps({'source_commit':'a2db214dc89e675347f670f26594df92158fc9d9','phase':'première image, sans PNJ','couches':stats,'banques':list(sheets)},ensure_ascii=False,indent=2))
print('Banques utilisées:',list(sheets),flush=True)
boxes={'C01':(168,1563,213,1600),'C02':(145,1265,178,1323),'C03':(1058,2574,1078,2602),'C04':(935,1160,980,1202),'C05':(78,2927,120,2958),'C06':(678,2927,720,2958),'C07':(1425,580,1494,620),'C08':(1202,2020,1240,2080),'C09':(770,1160,845,1194),'C10':(640,2568,736,2605)}
# Remettre les repères au centre de découpes plus larges, sans interpolation.
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',16);small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',12)
out=Image.new('RGB',(1120,5*250+80),'#202832');dr=ImageDraw.Draw(out);dr.text((20,12),'Réverie 0.5.0 — points à inspecter sur les chemins',font=font,fill='white')
for k,(name,(x1,y1,x2,y2)) in enumerate(boxes.items()):
 cx=(x1+x2)//2;cy=(y1+y2)//2;size=140;area=comp.crop((cx-size//2,cy-size//2,cx+size//2,cy+size//2));background=Image.new('RGBA',area.size,'#11151b');background.alpha_composite(area);area=background.convert('RGB').resize((210,210),Image.Resampling.NEAREST)
 x=20+(k%2)*550;y=56+(k//2)*250;out.paste(area,(x,y));dr.text((x+220,y+4),name+'   x '+str(x1)+'–'+str(x2),font=font,fill='#ffcf68');dr.text((x+220,y+31),'y '+str(y1)+'–'+str(y2),font=small,fill='white');dr.text((x+220,y+51),'Zone approximative :',font=small,fill='white');dr.text((x+220,y+70),'à confirmer en jeu',font=small,fill='white')
out.save(R/'planche-chemins-zones-C01-C10.png',optimize=True)
with zipfile.ZipFile(R/'calques-Reverie-0.5.0-phase0-REFERENCE.zip','w',zipfile.ZIP_DEFLATED) as z:
 for f in sorted(D.glob('*.png')):z.write(f,f.name)
 z.write(R/'calques-publies-statistiques.json','statistiques.json')
 z.writestr('LISEZ-MOI.txt','Exports de la carte publiée 0.5.0, phase 0, sans personnages. 11 fichiers aux dimensions de la géographie Réverie. Ce sont les calques actuels et non une séparation sémantique parfaite : certaines tuiles sont composites et quatre calques sont vides. Images de référence seulement, pas des ressources à réimporter sans reconstruire les animations ni valider les priorités.\n')
with zipfile.ZipFile(R/'calques-Reverie-0.5.0-phase0-REFERENCE.zip') as z:assert z.testzip() is None
print('Rendu et archive calques terminés',flush=True)
