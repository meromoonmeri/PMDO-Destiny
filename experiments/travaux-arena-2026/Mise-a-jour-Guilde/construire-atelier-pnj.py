from pathlib import Path
import html
from PIL import Image
from io import BytesIO
import base64,json,hashlib
P=Path(__file__).resolve().parent;path=P/'sources/docs/atelier-destiny/Guilde/Guilde-Destiny-Bourgeons-PMD.html';s=path.read_text();mark='<script id="donnees" type="application/json">';head,rest=s.split(mark,1);raw,tail=rest.split('</script>',1);data=json.loads(raw);root=P/'personnages-sources';index=json.loads((root/'index.json').read_text());assert len(index)==15 and not any('error' in x for x in index)
data['catalog'].extend(json.loads((P/'banque-complementaire.json').read_text(encoding='utf8')))
data['catalog'].extend(json.loads((P/'tapis-brodes.json').read_text(encoding='utf8'))) 
for nom,titre in [('secours','Tableau mural · Quêtes de secours'),('exploration','Tableau mural · Exploration')]:
 raw=(P/'Tableaux-quetes'/f'{nom}-mural-v2-sprite.png').read_bytes()
 im=Image.open(BytesIO(raw))
 data['catalog'].append({'id':f'tableau-mural-{nom}-verdure-v1','label':titre,'category':'panneaux','collection':'tableaux','w':im.width,'h':im.height,'wall':True,'previewOnly':True,'m':[base64.b64encode(raw).decode()]})
for nom,titre in [('monde','Carte du monde Destiny · Épinglée'),('reverie','Carte de Réverie · Épinglée')]:
 raw=(P/'Tableaux-quetes'/f'carte-{nom}-sprite.png').read_bytes()
 im=Image.open(BytesIO(raw))
 data['catalog'].append({'id':f'carte-murale-{nom}-destiny','label':titre,'category':'panneaux','collection':'cartes','w':im.width,'h':im.height,'wall':True,'previewOnly':True,'m':[base64.b64encode(raw).decode()]})
for nom,titre in [('cafe-spinda','Kiosque café · Inspiré de Spinda'),('accueil-missions','Kiosque accueil et missions'),('reserve-guilde','Kiosque de Canarticho · Réserve de la Guilde')]:
 raw=(P/'Kiosques-guilde'/('canarticho-vide-nearest-sprite.png' if nom=='reserve-guilde' else f'{nom}-sprite.png')).read_bytes()
 im=Image.open(BytesIO(raw))
 data['catalog'].append({'id':f'kiosque-{nom}-guilde','label':titre,'category':'meubles','collection':'kiosques','w':im.width,'h':im.height,'wall':False,'previewOnly':True,'m':[base64.b64encode(raw).decode()]})
raw=(P/'Kiosques-guilde'/'carte-monde-grande-sprite.png').read_bytes()
im=Image.open(BytesIO(raw))
data['catalog'].append({'id':'carte-murale-monde-destiny-grande','label':'Grande carte murale du monde Destiny','category':'panneaux','collection':'cartes','w':im.width,'h':im.height,'wall':True,'previewOnly':True,'m':[base64.b64encode(raw).decode()]})
for cote in ['gauche','droite']:
 raw=(P/'Rideaux-missions'/f'rideau-{cote}-perspective-sprite.png').read_bytes()
 im=Image.open(BytesIO(raw))
 data['catalog'].append({'id':f'rideau-guilde-missions-{cote}','label':f'Rideau {cote} · Salle des missions','category':'panneaux','collection':'rideauxmissions','w':im.width,'h':im.height,'wall':True,'previewOnly':True,'m':[base64.b64encode(raw).decode()]})
raw=(P/'Fontaine-missions'/'Fontaine-image-01.png').read_bytes()
sheet=(P/'Fontaine-missions'/'Tilesheet-Fontaine-8-images.png').read_bytes()
data['catalog'].append({'id':'fontaine-verdure-missions','label':'Fontaine à eau et verdure · 8 images','category':'meubles','collection':'fontaine','w':112,'h':80,'wall':False,'previewOnly':True,'m':[base64.b64encode(raw).decode()]})
data['etoffes']['fontaine-verdure-missions']={'s':'data:image/png;base64,'+base64.b64encode(sheet).decode(),'n':8,'c':8,'dt':160}
raw=(P/'Tapis-missions'/'Tapis-des-missions-sprite.png').read_bytes()
data['catalog'].append({'id':'tapis-circulaire-missions-embleme','label':'Tapis circulaire · Salle des missions · Emblème blanc','category':'tapis','collection':'tapisbrodes','w':144,'h':80,'wall':False,'previewOnly':True,'m':[base64.b64encode(raw).decode()]})
for nom,titre in [('comptoir-cloche','Comptoir à cloche · Guilde'),('table-buche','Table en bûche · Auberge Réverie'),('siege-buche','Petit siège en bûche · Auberge Réverie')]:
 raw=(P/'Ensemble-missions'/('comptoir-simple-halcyon-54x28.png' if nom=='comptoir-cloche' else f'{nom}-sprite.png')).read_bytes()
 im=Image.open(BytesIO(raw))
 data['catalog'].append({'id':f'ensemble-missions-{nom}','label':titre,'category':'meubles','collection':'boismissions','w':im.width,'h':im.height,'wall':False,'previewOnly':True,'m':[base64.b64encode(raw).decode()]})
for item in json.loads((P/'Trente-nouveautes'/'index.json').read_text(encoding='utf8')):
 raw=(P/'Trente-nouveautes'/item['file']).read_bytes()
 data['catalog'].append({'id':item['id'],'label':item['label'],'category':'panneaux' if item['wall'] else 'meubles','collection':'nouveautesguilde','w':item['w'],'h':item['h'],'wall':item['wall'],'previewOnly':True,'m':[base64.b64encode(raw).decode()]})
raw=(P/'Cheminee-refectoire'/'cheminee-frame-01.png').read_bytes()
sheet=(P/'Cheminee-refectoire'/'cheminee-tilesheet.png').read_bytes()
data['catalog'].append({'id':'cheminee-refectoire-reverie','label':'Cheminée du réfectoire · inspirée de la maison de feu','category':'panneaux','collection':'chemineerefectoire','w':48,'h':83,'wall':True,'previewOnly':True,'m':[base64.b64encode(raw).decode()]})
data['etoffes']['cheminee-refectoire-reverie']={'s':'data:image/png;base64,'+base64.b64encode(sheet).decode(),'n':6,'c':6,'dt':167}
raw=(P/'Bureau-maitre'/'drapeau-embleme-sprite.png').read_bytes()
im=Image.open(BytesIO(raw))
data['catalog'].append({'id':'bureau-maitre-drapeau-guilde','label':'Drapeau mural · Emblème de la Guilde','category':'panneaux','collection':'bureaumaitre','w':im.width,'h':im.height,'wall':True,'previewOnly':True,'m':[base64.b64encode(raw).decode()]})
raw=(P/'Cheminee-refectoire'/'generee-image-01.png').read_bytes()
sheet=(P/'Cheminee-refectoire'/'generee-tilesheet.png').read_bytes()
data['catalog'].append({'id':'cheminee-refectoire-generee','label':'Cheminée générée · Réfectoire · 4 poses de flammes','category':'panneaux','collection':'chemineerefectoire','w':48,'h':71,'wall':True,'previewOnly':True,'m':[base64.b64encode(raw).decode()]})
data['etoffes']['cheminee-refectoire-generee']={'s':'data:image/png;base64,'+base64.b64encode(sheet).decode(),'n':4,'c':4,'dt':170}
for item in json.loads((P/'Salon-chaleureux'/'index.json').read_text(encoding='utf8')):
 raw=(P/'Salon-chaleureux'/item['file']).read_bytes()
 data['catalog'].append({'id':item['id'],'label':item['label'],'category':item['category'],'collection':'salonchaleureux','w':item['w'],'h':item['h'],'wall':item['wall'],'previewOnly':True,'m':[base64.b64encode(raw).decode()]})
for item in json.loads((P/'Cartes-dortoirs'/'index.json').read_text(encoding='utf8')):
 raw=(P/'Cartes-dortoirs'/item['file']).read_bytes()
 data['catalog'].append({'id':item['id'],'label':item['label'],'category':'panneaux','collection':'cartesdortoirs','w':item['w'],'h':item['h'],'wall':True,'previewOnly':True,'m':[base64.b64encode(raw).decode()]})
for item in index:
 num=item['id'];w=item['w'];h=item['h'];im=Image.open(root/f'{num:04d}'/'Idle-Anim.png').convert('RGBA');assert im.height==8*h and im.width>=w
 for direction in range(8):
  frame=im.crop((0,direction*h,w,(direction+1)*h));box=frame.getbbox();assert box
  frame=frame.crop(box);b=BytesIO();frame.save(b,format='PNG',optimize=True)
  data['catalog'].append({'id':f'pnj-{num:04d}-{direction}','label':item['label'],'category':'personnages','collection':'pnj','w':frame.width,'h':frame.height,'wall':False,'previewOnly':True,'pnj':True,'species':num,'direction':direction,'m':[base64.b64encode(b.getvalue()).decode()]})

# Sources exactes de l'aperçu validé : plans natifs, sans prétendre à une intégration runtime.
cliff=P/'sources/docs/atelier-destiny/Guilde/Falaise-Ombre-et-Lune/Plans'
scene={}
for phase in ('jour','aube','crepuscule'):
 scene[phase]=['data:image/png;base64,'+base64.b64encode((cliff/f'Cliff-{phase}.png').read_bytes()).decode()]
scene['nuit']=['data:image/png;base64,'+base64.b64encode((cliff/f'Cliff-nuit-{i}.png').read_bytes()).decode() for i in range(1,5)]
data['falaise_apercu']=scene

def replace(s,a,b):
 n=s.count(a)
 if n!=1:raise ValueError('Attendu exactement une occurrence, trouvé '+str(n)+': '+a[:100])
 return s.replace(a,b,1)
head=replace(head,'<title>Destiny · Bourgeons — la grille de l’Accueil</title>','<title>Destiny · Guilde — meubles et PNJ</title>')
head=replace(head,'<option value="drapeaux" selected>Drapeaux et tentures · 24</option><option value="pmu100">100 variantes PMU</option><option value="origine">Banque d’origine · 33</option>','<option value="tous" selected>Tous les meubles et objets · 1 225</option><option value="origine">Mobilier d’origine · 33</option><option value="drapeaux">Drapeaux et tentures · 24</option><option value="pmu100">100 variantes PMU</option><option value="cartesdortoirs">Cartes murales des dortoirs · 4</option><option value="salonchaleureux">Réfectoire chaleureux · 8</option><option value="bureaumaitre">Drapeaux du bureau · 1</option><option value="chemineerefectoire">Cheminée réfectoire · 2</option><option value="nouveautesguilde">Nouveaux meubles de Guilde · 13</option><option value="boismissions">Comptoir et bûches · 3</option><option value="fontaine">Fontaine animée · 1</option><option value="rideauxmissions">Rideaux salle des missions · 2</option><option value="tapisbrodes">Tapis · emblème blanc · 35</option><option value="kiosques">Kiosques de la Guilde · 3</option><option value="tableaux">Tableaux de missions · 2</option><option value="cartes">Cartes murales Destiny · 3</option><option value="creations40">Nos créations · 40 objets</option><option value="halcyon">Halcyon &amp; Metano · 490 teintes</option><option value="halcyonia">Créations Halcyon IA · 30 teintes</option><option value="pmucomplet">PMU Destiny · 327 objets</option><option value="natifcomplet">Objets natifs · 102 objets</option><option value="comptoirs">Comptoir et étendard · 2</option><option value="pnj">PNJ · 15 Pokémon</option>')
head=replace(head,'<label>Palette<select id="palette-pmu">','<label id="pnj-direction-wrap" hidden>Orientation des nouveaux PNJ<select id="pnj-direction"><option value="0">Face</option><option value="1">Avant-droite</option><option value="2">Droite</option><option value="3">Arrière-droite</option><option value="4">Dos</option><option value="5">Arrière-gauche</option><option value="6">Gauche</option><option value="7">Avant-gauche</option></select></label><label>Palette<select id="palette-pmu">')
head=replace(head,'<h2>Mobilier PMU</h2>','<h2>Mobilier &amp; PNJ</h2>')
head=replace(head,'<button id="tab-work"','<button type="button" id="ouvrir-falaise" class="soft">🏡 Falaise jour / nuit</button><button id="tab-work"')
head=replace(head,'<button id="tab-work"','<button type="button" id="poser-rideaux-missions" class="soft">🪟 Accrocher les rideaux</button><button id="tab-work"')
head=replace(head,'<button id="tab-work"','<button type="button" id="poser-fontaine-missions" class="soft">⛲ Fontaine des missions</button><button id="tab-work"')
head=replace(head,'<button id="tab-work"','<button type="button" id="poser-cartes-dortoirs" class="soft">🗺️ Cartes des dortoirs</button><button id="tab-work"')
head=replace(head,'<button id="tab-work"','<button type="button" id="amenager-refectoire" class="soft">🍵 Aménager le réfectoire</button><button id="tab-work"')
head=replace(head,'<button id="tab-work"','<button type="button" id="poser-drapeaux-bureau" class="soft">🏳️ Drapeaux du bureau</button><button id="tab-work"')
head=replace(head,'<button id="tab-work"','<button type="button" id="poser-cheminee-refectoire" class="soft">🔥 Cheminée du réfectoire</button><button id="tab-work"')
head=replace(head,'<button id="tab-work"','<button type="button" id="poser-bois-missions" class="soft">🪵 Comptoir et bûches</button><button id="tab-work"')
head=replace(head,'<div id="catalog" class="catalog" aria-label="Objets disponibles"></div>','<div id="catalog" class="catalog" aria-label="Mobilier et personnages disponibles"></div><p style="font-size:11px;line-height:1.4;color:#b9c8b4">Tous les objets existants sont ici, par collection. 1 108 références de la banque orientable sont montrées avec leur vue de base, plus nos 40 créations ; les 20 autres créations prévues n’existent pas encore. PNJ sans dialogue. Enregistre ton plan JSON. Sprites : <a href="https://github.com/PMDCollab/SpriteCollab" target="_blank" rel="noopener">SpriteCollab</a> · CC BY-NC 4.0.</p>')
# Quand le pied d'un PNJ est dans l'ouverture, il est dessiné avant le kiosque ; le plateau masque son bas.
tail=replace(tail,"function ordered(items){return [...items].sort((a,b)=>Number(assets.get(b.meuble).category==='tapis')-Number(assets.get(a.meuble).category==='tapis'));}","""function ordered(items){
  const out=[...items].sort((a,b)=>Number(assets.get(b.meuble).category==='tapis')-Number(assets.get(a.meuble).category==='tapis'));
  const kiosks=out.filter(o=>o.meuble==='kiosque-reserve-guilde-guilde');
  for(const kiosk of kiosks){
    const k=assets.get(kiosk.meuble);
    const inside=out.filter(o=>{const a=assets.get(o.meuble);if(!a.pnj)return false;const cx=o.x+a.w/2,foot=o.y+a.h;return cx>kiosk.x+k.w*.27&&cx<kiosk.x+k.w*.73&&foot>kiosk.y+k.h*.37&&foot<kiosk.y+k.h*.80;});
    for(const npc of inside){const i=out.indexOf(npc);out.splice(i,1);out.splice(out.indexOf(kiosk),0,npc);}
  }
  return out;
}""")
# Dans la fenêtre centrale, le clic traverse le kiosque pour sélectionner le PNJ.
tail=replace(tail,"return t.x>=o.x&&t.y>=o.y&&t.x<o.x+a.w&&t.y<o.y+a.h;","if(o.meuble==='kiosque-reserve-guilde-guilde'&&t.x>o.x+a.w*.25&&t.x<o.x+a.w*.75&&t.y>o.y+a.h*.27&&t.y<o.y+a.h*.64)return false;return t.x>=o.x&&t.y>=o.y&&t.x<o.x+a.w&&t.y<o.y+a.h;")
# Le marqueur exact du centre est conservé en jeu ; exception de maquette pour visualiser la fontaine par-dessus lui.
tail=replace(tail,"r.mark.some(m=>overlaps(shape,m))","r.mark.some(m=>!(a.id==='fontaine-verdure-missions'&&r.id==='guilde_destiny_missions'&&m[0]===280&&m[1]===256)&&overlaps(shape,m))")
tail=replace(tail,"data.etoffes[a.id]?'étoffe animée'","data.etoffes[a.id]?'objet animé'")
tail=replace(tail,"collection:'drapeaux',palette:'tout'","collection:'tous',palette:'tout',pnjDirection:0")
tail=replace(tail,"(a.collection??'origine')===s.collection","(s.collection==='tous'?a.collection!=='pnj':(a.collection??'origine')===s.collection)")
tail=replace(tail,"(s.category==='tout'||s.category===a.category)&&(!term||normalized(a.label).includes(term))", "(s.collection==='pnj'||s.category==='tout'||s.category===a.category)&&(s.collection!=='pnj'||a.direction===s.pnjDirection)&&(!term||normalized(a.label).includes(term))")
tail=replace(tail,"$('palette-pmu').disabled=s.collection==='origine';s.category='tout';cancel();updatePalette();refresh();", "$('palette-pmu').disabled=!['drapeaux','pmu100'].includes(s.collection);$('pnj-direction-wrap').hidden=s.collection!=='pnj';$('filters').hidden=s.collection==='pnj';s.category='tout';cancel();updatePalette();refresh();")
tail=replace(tail,"$('palette-pmu').onchange=()=>{s.palette=$('palette-pmu').value;cancel();updatePalette();refresh();};", "$('palette-pmu').onchange=()=>{s.palette=$('palette-pmu').value;cancel();updatePalette();refresh();};\n$('pnj-direction').onchange=()=>{s.pnjDirection=Number($('pnj-direction').value);cancel();updatePalette();refresh();};")
old="panel.append(make('span','inspect-coords','X '+o.x+' · Y '+o.y));const actions=make('div','inspect-actions');"
new="""panel.append(make('span','inspect-coords','X '+o.x+' · Y '+o.y));
    const existing=assets.get(o.meuble);
    if(existing.pnj){
      const label=make('label','','Orientation du PNJ');const select=make('select');select.setAttribute('aria-label','Orientation du PNJ sélectionné');
      ['Face','Avant-droite','Droite','Arrière-droite','Dos','Arrière-gauche','Gauche','Avant-gauche'].forEach((name,i)=>{const op=make('option','',name);op.value=String(i);select.append(op)});select.value=String(existing.direction);
      select.onchange=()=>{const target=assets.get('pnj-'+String(existing.species).padStart(4,'0')+'-'+select.value);const x=Math.round(o.x+(existing.w-target.w)/2),y=o.y+existing.h-target.h;const issue=why(s.room,target,x,y);if(issue){toast(issue,true);refresh();return;}setRoomItems(dataFor().map(t=>t.id===o.id?{...t,meuble:target.id,x,y}:t));};
      label.append(select);panel.append(label);
    }
    const actions=make('div','inspect-actions');"""
tail=replace(tail,old,new)
tail=replace(tail,"a.previewOnly?'variante d’atelier':'sprite natif'","a.pnj?'PNJ d’aperçu':a.previewOnly?'variante d’atelier':'sprite natif'")
tail=replace(tail,"'Meuble retiré. Tu peux annuler cette action.'","'Élément retiré. Tu peux annuler cette action.'")
tail=replace(tail,"'Les nouvelles variantes et les lianes sont des éléments d’aperçu. Choisis PNG ou JSON pour les conserver.'","'Les PNJ, les variantes et les lianes sont des éléments d’aperçu. Le JSON conserve leur placement ; ils ne sont pas installés dans le jeu.'")
tail=replace(tail,'setupAtlas();updatePalette();refresh();setupMotion();','setupAtlas();$(\'palette-pmu\').disabled=true;updatePalette();refresh();setupMotion();openDepuisAtlas(data.rooms[2]);')
tail=replace(tail,'setupAtlas();$(\'palette-pmu\').disabled=true;updatePalette();refresh();setupMotion();openDepuisAtlas(data.rooms[2]);',"""let cliffPhase='jour',cliffTimer=null,cliffFrame=0;
const cliffDialog=$('cliff-dialog'),cliffImage=$('cliff-image');
function showCliff(phase){cliffPhase=phase;cliffFrame=0;cliffImage.src=data.falaise_apercu[phase][0];document.querySelectorAll('[data-cliff-phase]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.cliffPhase===phase)));if(cliffTimer)clearInterval(cliffTimer);if(phase==='nuit'&&!matchMedia('(prefers-reduced-motion: reduce)').matches)cliffTimer=setInterval(()=>{cliffFrame=(cliffFrame+1)%4;cliffImage.src=data.falaise_apercu.nuit[cliffFrame]},167);}
$('ouvrir-falaise').onclick=()=>{cliffDialog.showModal();showCliff('jour')};$('fermer-falaise').onclick=()=>cliffDialog.close();cliffDialog.addEventListener('close',()=>{if(cliffTimer)clearInterval(cliffTimer);cliffTimer=null});document.querySelectorAll('[data-cliff-phase]').forEach(b=>b.onclick=()=>showCliff(b.dataset.cliffPhase));
$('poser-cartes-dortoirs').onclick=()=>{
 const setup=[['guilde_destiny_dortoir_nord_1','carte-dortoir-continent-gauche',137,53],['guilde_destiny_dortoir_nord_2','carte-dortoir-iles-droite',281,53],['guilde_destiny_dortoir_sud_1','carte-dortoir-iles-gauche',137,53],['guilde_destiny_dortoir_sud_2','carte-dortoir-continent-droite',281,53]];
 const next=Object.assign(blank(),layout);let added=0,occupied=false;
 for(const [roomId,id,x,y] of setup){const r=gameMap.get(roomId),existing=dataFor(r),a=assets.get(id);if(existing.some(o=>o.meuble.startsWith('carte-dortoir-')))continue;
  const issue=why(r,a,x,y);if(issue){toast(r.label+' : '+issue,true);return;}
  if(existing.length>=MAX){toast(r.label+' : maximum d’objets atteint.',true);return;}
  if(existing.some(e=>{const b=assets.get(e.meuble);return overlaps([x,y,a.w,a.h],[e.x,e.y,b.w,b.h]);}))occupied=true;
  next[roomId]=[...existing,{id:unique(),meuble:id,x,y}];added++;
 }
 const r=gameMap.get('guilde_destiny_dortoir_nord_1');openDepuisAtlas(r);s.collection='cartesdortoirs';$('collection').value=s.collection;s.category='tout';$('pnj-direction-wrap').hidden=true;$('filters').hidden=false;$('palette-pmu').disabled=true;s.palette='tout';$('palette-pmu').value='tout';$('query').value='';cancel();updatePalette();
 if(!added){refresh();toast('Une carte est déjà présente dans chaque dortoir.');return;}
 if(occupied&&!confirm('Une carte chevauche un objet existant. Ajouter les cartes sans rien supprimer ?'))return;
 remember(next);toast(added+' carte(s) accrochée(s) dans les dortoirs.');
};
$('amenager-refectoire').onclick=()=>{
 const r=gameMap.get('guilde_destiny_refectoire');openDepuisAtlas(r);s.collection='salonchaleureux';$('collection').value=s.collection;s.category='tout';$('pnj-direction-wrap').hidden=true;$('filters').hidden=false;$('palette-pmu').disabled=true;s.palette='tout';$('palette-pmu').value='tout';$('query').value='';cancel();updatePalette();
 const existing=dataFor(r);
 if(existing.some(o=>o.meuble.startsWith('refectoire-chaleureux-'))){refresh();toast('Des meubles de cet ensemble sont déjà présents. Tu peux ajouter les autres depuis le catalogue.');return;}
 const setup=[['tapis-chaleureux',240,280],['table-repas',170,165],['table-repas',318,165],['banc-repas',178,147],['banc-repas',178,220],['banc-repas',326,147],['banc-repas',326,220],['tabouret-repas',144,184],['tabouret-repas',262,184],['tabouret-repas',290,184],['tabouret-repas',413,184],['buffet-vaisselle',437,175],['etagere-vaisselle',382,92],['panier-buches',132,160],['plateau-the',199,174],['plateau-the',347,174]];
 const added=[];for(const [slug,x,y] of setup){const id='refectoire-chaleureux-'+slug,a=assets.get(id),issue=why(r,a,x,y);if(issue){toast('Placement à ajuster : '+issue,true);return;}added.push({id:unique(),meuble:id,x,y});}
 if(existing.length+added.length>MAX){toast('Maximum d’objets atteint.',true);return;}
 if(added.some(o=>{const a=assets.get(o.meuble);return existing.some(e=>{const b=assets.get(e.meuble);return overlaps([o.x,o.y,a.w,a.h],[e.x,e.y,b.w,b.h]);})})&&!confirm('Certains objets se superposeront à des éléments existants. Ajouter sans rien supprimer ?'))return;
 setRoomItems([...existing,...added]);toast('Réfectoire aménagé : tu peux déplacer tous les objets.');
};
$('poser-drapeaux-bureau').onclick=()=>{
 const r=gameMap.get('guilde_destiny_bureau_maitre');openDepuisAtlas(r);s.collection='bureaumaitre';$('collection').value=s.collection;s.category='tout';$('pnj-direction-wrap').hidden=true;$('filters').hidden=false;$('palette-pmu').disabled=true;s.palette='tout';$('palette-pmu').value='tout';$('query').value='';cancel();updatePalette();
 const id='bureau-maitre-drapeau-guilde',existing=dataFor(r),a=assets.get(id);
 if(existing.some(o=>o.meuble===id)){refresh();toast('Les drapeaux sont déjà présents.');return;}
 const coords=[[165,67],[324,67]],added=[];
 for(const [x,y] of coords){const issue=why(r,a,x,y);if(issue){toast(issue,true);return;}added.push({id:unique(),meuble:id,x,y});}
 if(existing.length+added.length>MAX){toast('Maximum d’objets atteint.',true);return;}
 if(added.some(o=>existing.some(e=>{const b=assets.get(e.meuble);return overlaps([o.x,o.y,a.w,a.h],[e.x,e.y,b.w,b.h])}))&&!confirm('Un objet est proche. Ajouter les drapeaux sans le retirer ?'))return;
 setRoomItems([...existing,...added]);toast('Drapeaux de la Guilde ajoutés au bureau.');
};
$('poser-cheminee-refectoire').onclick=()=>{
 const r=gameMap.get('guilde_destiny_refectoire');openDepuisAtlas(r);s.collection='chemineerefectoire';$('collection').value=s.collection;s.category='tout';$('pnj-direction-wrap').hidden=true;$('filters').hidden=false;$('palette-pmu').disabled=true;s.palette='tout';$('palette-pmu').value='tout';$('query').value='';cancel();updatePalette();
 const id='cheminee-refectoire-generee',existing=dataFor(r),a=assets.get(id),x=78,y=117;
 if(existing.some(o=>o.meuble===id)){
  const defaut=existing.find(o=>o.meuble===id&&o.x===78&&o.y===105);
  if(defaut){setRoomItems(existing.map(o=>o.id===defaut.id?{...o,x,y}:o));toast('Cheminée descendue jusqu’au pied du mur.');return;}
  refresh();toast('La cheminée est déjà présente : sa position personnalisée a été conservée.');return;
 }
 const issue=why(r,a,x,y);if(issue){toast(issue,true);return;}
 if(existing.length>=MAX){toast('Maximum d’objets atteint.',true);return;}
 const occupied=existing.some(o=>{const b=assets.get(o.meuble);return overlaps([x,y,a.w,a.h],[o.x,o.y,b.w,b.h]);});
 if(occupied&&!confirm('Un objet est proche de cet emplacement. Ajouter la cheminée sans retirer les autres ?'))return;
 setRoomItems([...existing,{id:unique(),meuble:id,x,y}]);toast('Cheminée animée ajoutée au mur gauche du réfectoire.');
};
$('poser-bois-missions').onclick=()=>{
 const r=gameMap.get('guilde_destiny_missions');openDepuisAtlas(r);s.collection='boismissions';$('collection').value=s.collection;s.category='tout';$('pnj-direction-wrap').hidden=true;$('filters').hidden=false;$('palette-pmu').disabled=true;s.palette='tout';$('palette-pmu').value='tout';$('query').value='';cancel();updatePalette();
 const setup=[['ensemble-missions-comptoir-cloche',104,176],['ensemble-missions-table-buche',376,184],['ensemble-missions-siege-buche',350,184],['ensemble-missions-siege-buche',432,184],['ensemble-missions-siege-buche',350,230],['ensemble-missions-siege-buche',432,230]];
 const existing=dataFor(r);if(existing.some(o=>o.meuble==='ensemble-missions-comptoir-cloche'||o.meuble==='ensemble-missions-table-buche')){refresh();toast('Cet ensemble est déjà présent : tu peux ajouter et déplacer les objets depuis le catalogue.');return;}
 const added=[];for(const [id,x,y] of setup){const a=assets.get(id),issue=why(r,a,x,y);if(issue){toast('Emplacement non disponible : '+issue,true);return;}added.push({id:unique(),meuble:id,x,y});}
 if(existing.length+added.length>MAX){toast('Maximum : '+MAX+' objets par salle.',true);return;}
 const overlap=added.some(o=>{const a=assets.get(o.meuble);return existing.some(e=>{const b=assets.get(e.meuble);return overlaps([o.x,o.y,a.w,a.h],[e.x,e.y,b.w,b.h]);});});
 if(overlap&&!confirm('Cet ensemble chevauchera un objet déjà placé. L’ajouter quand même sans retirer les autres ?'))return;
 setRoomItems([...existing,...added]);toast('Comptoir, table et quatre sièges ajoutés. Déplace-les comme tu veux.');
};
$('poser-fontaine-missions').onclick=()=>{
 const r=gameMap.get('guilde_destiny_missions');openDepuisAtlas(r);s.collection='fontaine';$('collection').value=s.collection;s.category='tout';$('pnj-direction-wrap').hidden=true;$('filters').hidden=false;$('palette-pmu').disabled=true;s.palette='tout';$('palette-pmu').value='tout';$('query').value='';cancel();updatePalette();
 const id='fontaine-verdure-missions',existing=dataFor(r),asset=assets.get(id),x=232,y=224;
 if(existing.some(o=>o.meuble===id)){refresh();toast('La fontaine est déjà dans cette salle.');return;}
 const issue=why(r,asset,x,y);if(issue){toast(issue,true);return;}
 if(existing.length>=MAX){toast('Maximum : '+MAX+' objets par salle.',true);return;}
 const blocked=existing.some(o=>{const a=assets.get(o.meuble);return overlaps([x,y,asset.w,asset.h],[o.x,o.y,a.w,a.h]);});
 if(blocked&&!confirm('La fontaine chevauchera un objet déjà placé. L’ajouter quand même sans retirer les autres ?'))return;
 setRoomItems([...existing,{id:unique(),meuble:id,x,y}]);toast('Fontaine placée au centre en aperçu. Le marqueur central du jeu devra être vérifié avant intégration.');
};
$('poser-rideaux-missions').onclick=()=>{
 const r=gameMap.get('guilde_destiny_missions');openDepuisAtlas(r);s.collection='rideauxmissions';$('collection').value=s.collection;s.category='tout';$('pnj-direction-wrap').hidden=true;$('filters').hidden=false;$('palette-pmu').disabled=true;s.palette='tout';$('palette-pmu').value='tout';$('query').value='';cancel();updatePalette();
 const existing=dataFor(r), toAdd=[];
 for(const [id,x,y] of [['rideau-guilde-missions-gauche',70,57],['rideau-guilde-missions-droite',442,57]]){
   if(existing.some(o=>o.meuble===id))continue;
   const asset=assets.get(id),issue=why(r,asset,x,y);if(issue){toast(issue,true);return;}toAdd.push({id:unique(),meuble:id,x,y});
 }
 if(existing.length+toAdd.length>MAX){toast('Maximum : '+MAX+' objets par salle.',true);return;}
 if(toAdd.length)setRoomItems([...existing,...toAdd]);else refresh();
 toast(toAdd.length?'Rideaux accrochés aux fenêtres de la salle des missions.':'Les rideaux sont déjà dans cette salle.');
};
setupAtlas();$('palette-pmu').disabled=true;updatePalette();refresh();setupMotion();openDepuisAtlas(data.rooms[2]);""")
head+='''<dialog id="cliff-dialog" style="max-width:min(95vw,550px);max-height:95vh;overflow:auto;color:#e9eadb;background:#1d2a22;border:1px solid #58735a;border-radius:12px;padding:18px"><div style="display:flex;gap:10px;justify-content:space-between;align-items:center"><h2 style="margin:0">Falaise de la Guilde</h2><button class="soft" id="fermer-falaise" type="button">Fermer</button></div><p style="line-height:1.4">Aperçu des calques validés : ombre corrigée, braseros et lune. Ce rendu n’est pas encore intégré en jeu.</p><div style="display:flex;flex-wrap:wrap;gap:6px;margin:10px 0"><button class="soft" type="button" data-cliff-phase="jour" aria-pressed="true">Jour</button><button class="soft" type="button" data-cliff-phase="aube">Aube</button><button class="soft" type="button" data-cliff-phase="crepuscule">Crépuscule</button><button class="soft" type="button" data-cliff-phase="nuit">Nuit · braseros</button></div><img id="cliff-image" alt="Falaise de la Guilde Destiny" width="480" height="520" style="display:block;width:min(100%,480px);height:auto;image-rendering:pixelated;margin:auto"></dialog>'''
credits_inline=''.join('<li><b>'+html.escape(a['label'])+'</b> : '+html.escape((root/f"{a['id']:04d}"/'credits.txt').read_text().strip()).replace('\n',' ; ')+'</li>' for a in index)
head+='''<details style="padding:10px 24px;color:#aabaaa"><summary>Crédits et provenance des sprites</summary><p>Mobilier Halcyon et Metano : mod Halcyon de Palika ; D4yz et Edan Momu sont crédités pour les décors intérieurs. Les droits sur les sprites d’origine restent à leurs auteurs ; vérifier leurs conditions avant redistribution. PMU Destiny : banque PMU historique du projet. Les créations originales sont distinctes des découpes Halcyon.</p><p>PNJ : SpriteCollab · CC BY-NC 4.0. Les identifiants sont ceux du registre de crédits d’origine.</p><ul>'''+credits_inline+'''</ul></details>'''
s=head+mark+json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+'</script>'+tail
out=P/'Apercu-actuel/index.html';out.write_text(s,encoding='utf8');print('Aperçu construit',out,len(s),'caractères, 120 sprites (15 Pokémon × 8 directions)')
credits=[]
for a in index:credits.append(f"{a['label']} — https://github.com/PMDCollab/SpriteCollab/tree/master/sprite/{a['id']:04d} — "+(root/f"{a['id']:04d}"/'credits.txt').read_text().strip().replace('\n',' ; '))
(P/'Apercu-actuel/Credits-PNJ.txt').write_text('Sprites de placement : SpriteCollab — CC BY-NC 4.0\n\n'+'\n'.join(credits)+'\n',encoding='utf8')
