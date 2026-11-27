from pathlib import Path
from PIL import Image,ImageDraw
import json,base64,io,collections
P=Path(__file__).resolve().parent;root=P.parent;h=(root/'Apercu-actuel/index.html').read_text();data=json.loads(h.split('<script id="donnees" type="application/json">')[1].split('</script>')[0]);catalog=data['catalog'];
# Motif brodé à pixels : œuf central et ailes symétriques, fil écru clair.
logo=Image.new('RGBA',(45,23));d=ImageDraw.Draw(logo);thread='#fff7e4';shadow='#d6cdb9';accent='#ffffff'
d.polygon([(17,7),(13,6),(9,3),(4,1),(1,1),(2,6),(4,9),(6,10),(6,13),(9,15),(10,17),(14,19),(18,17)],fill=thread)
# Aile droite symétrique
left=logo.crop((0,0,21,23));logo.alpha_composite(left.transpose(Image.Transpose.FLIP_LEFT_RIGHT),(24,0));d=ImageDraw.Draw(logo)
d.polygon([(22,3),(19,4),(17,8),(16,13),(17,17),(19,20),(22,21),(25,20),(27,17),(28,13),(27,8),(25,4)],fill=thread)
# Piqûres gris clair évoquant le fil, sans couleurs d'emblème non blanches.
d.line([(4,4),(11,9),(16,10)],fill=shadow,width=1);d.line([(6,9),(12,13),(16,13)],fill=shadow,width=1);d.line([(10,16),(15,17)],fill=shadow,width=1)
d.line([(40,4),(33,9),(28,10)],fill=shadow,width=1);d.line([(38,9),(32,13),(28,13)],fill=shadow,width=1);d.line([(34,16),(29,17)],fill=shadow,width=1)
d.line([(22,5),(20,8),(19,12),(19,16)],fill=accent,width=1);d.line([(25,8),(26,12),(26,16),(24,19)],fill=shadow,width=1)
logo.resize((450,230),Image.Resampling.NEAREST).save(P/'embleme-blanc-zoom.png')
# Les 20 tapis du nuancier PMU déjà présent + 12 tapis PMU de forme/couleur variée.
base=[a for a in catalog if a.get('collection')=='pmu100' and a['category']=='tapis']
extra=['Guilde_PMU_Cpt_129','Guilde_PMU_Cpt_135','Guilde_PMU_Cpt_136','Guilde_PMU_Cpt_131','Guilde_PMU_Cpt_134','Guilde_PMU_Cpt_140','Guilde_PMU_DecA_210','Guilde_PMU_DecA_218','Guilde_PMU_DecA_217','Guilde_PMU_DecB_272','Guilde_PMU_DecB_270','Guilde_PMU_DecB_271','Guilde_PMU_DecB_282','Guilde_PMU_DecB_280']
base.extend(next(a for a in catalog if a['id']==i) for i in extra)
result=[];examples=[]
for a in base:
 raw=base64.b64decode(a['m'][0].split(',')[-1]);im=Image.open(io.BytesIO(raw)).convert('RGBA');w,h=im.size
 # Logo à plat au centre du tapis, sans toucher aux franges / bordures.
 mw=min(45,max(25,int(w*.40)));mh=max(12,round(mw*23/45*.75));mark=logo.resize((mw,mh),Image.Resampling.NEAREST)
 cx=w//2;cy=h//2
 # Un très discret point d'ombre sous le fil permet de lire la broderie sur tissu clair.
 shade=Image.new('RGBA',mark.size,(48,37,26,110));shade.putalpha(mark.getchannel('A').point(lambda x:100 if x else 0));im.alpha_composite(shade,(cx-mw//2,cy-mh//2+1));im.alpha_composite(mark,(cx-mw//2,cy-mh//2))
 out=io.BytesIO();im.save(out,format='PNG',optimize=True)
 id='tapis-brode-'+a['id'].replace('_','-').lower();name=a['label']+' · emblème blanc'
 result.append({'id':id,'label':name,'category':'tapis','collection':'tapisbrodes','w':w,'h':h,'wall':False,'previewOnly':True,'m':[base64.b64encode(out.getvalue()).decode()]})
 (P/(id+'.png')).write_bytes(out.getvalue())
 if len(examples)<8 and (not a['id'].startswith('pmu100') or a['id'].endswith('sauge')):examples.append((name,im))
(root/'tapis-brodes.json').write_text(json.dumps(result,ensure_ascii=False,separators=(',',':')));print(len(result))
# Vérification visuelle locale, exemples séparés en vignette.
sheet=Image.new('RGB',(620,480),'#24352c');d=ImageDraw.Draw(sheet)
for i,(name,im) in enumerate(examples[:8]):
 x=(i%3)*205;y=(i//3)*160;sheet.paste(im,(x+(200-im.width)//2,y+15),im);d.text((x+2,y+130),name[:28],fill='white')
sheet.save(P/'verifier-exemples.png')
