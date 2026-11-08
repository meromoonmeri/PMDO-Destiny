import gzip,json,sys,gc,copy
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
R=Path('/home/user/chantier-corrections-bassin-55');P=Path('/home/user/chantier-corrections-bassin-53-54');journal=json.loads((R/'journal-55.json').read_text());
for i,name in enumerate(['reverie_etang.rsground.gz','reverie_etang_Dev.rsground.gz']):
 before=json.loads(gzip.decompress((P/'candidat/payload'/name).read_bytes()).decode('utf-8-sig'));after=json.loads(gzip.decompress((R/'candidat/payload'/name).read_bytes()).decode('utf-8-sig')); b=next(l for l in before['Object']['Layers'] if l['Name']=='Base')['Tiles'];a=next(l for l in after['Object']['Layers'] if l['Name']=='Base')['Tiles'];
 for change in journal['cartes'][i]['modifications']:
  x,y=change['x'],change['y'];assert b[x][y]==change['avant'] and a[x][y]==change['apres'];a[x][y]=copy.deepcopy(change['avant'])
 assert before==after, 'Comparaison intégrale échouée';print(name,'PASS',len(journal['cartes'][i]['modifications']),'cases Base ; tout le reste identique')
 del before,after,a,b;gc.collect()
code=(R/'audit-calques.py').read_text().split('regions=')[0]
def get_context(path):
 newcode=code.replace("p=P/'candidat/payload/reverie_etang.rsground.gz'",f"p=Path({str(path)!r})").replace("sheets[n]=SheetReader(P/'banques'/(n+'.tile'))", "sheets[n]=SheetReader((R/'banques' if n=='Reverie_Correction_Herbe_55' else P/'banques')/(n+'.tile'))")
 ctx={};exec(newcode,ctx);return ctx
old=get_context(P/'candidat/payload/reverie_etang.rsground.gz');new=get_context(R/'candidat/payload/reverie_etang.rsground.gz');
for name,box in {'souche':(159,259,177,270),'fleurs':(144,279,156,292),'ouest':(98,255,112,283),'est':(162,264,173,279),'bas':(107,305,119,317)}.items():
 a=old['render'](box);b=new['render'](box);assert a.size==b.size
 mult=5; w,h=a.size;output=Image.new('RGB',(w*2*mult,h*mult+42),'#161f18');d=ImageDraw.Draw(output);font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',16);d.text((6,10),'Avant : candidat 53–54',font=font,fill='white');d.text((w*mult+6,10),'Après : candidat 55',font=font,fill='white');output.paste(a.resize((w*mult,h*mult),Image.Resampling.NEAREST),(0,42),a.resize((w*mult,h*mult),Image.Resampling.NEAREST));output.paste(b.resize((w*mult,h*mult),Image.Resampling.NEAREST),(w*mult,42),b.resize((w*mult,h*mult),Image.Resampling.NEAREST));output.save(R/f'avant-apres-{name}.png')
 print(name,'pixels différents visiblement',sum(1 for i,j in zip(a.getdata(),b.getdata()) if i!=j))
