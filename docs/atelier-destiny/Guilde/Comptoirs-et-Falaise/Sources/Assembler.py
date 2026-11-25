#!/usr/bin/env python3
"""Build an additional self-contained workshop without writing to an upstream file."""
from pathlib import Path
import base64,json,re,hashlib,shutil
from Implantation import BASE,ROOT,config
from Falaise import W,P
S=ROOT/'Sources'; O=ROOT.parent/'Guilde-Destiny-Comptoirs-et-Falaise.html'; C=ROOT/'Falaise'

def b64(file):return base64.b64encode(file.read_bytes()).decode('ascii')

def main():
    upstream=BASE.read_bytes();h=upstream.decode();mt=re.search(r'(<script id="donnees"[^>]*>)(.*?)(</script>)',h,re.S);assert mt
    d=json.loads(mt[2]);old= len(d['catalog']);assert len(d['rooms'])==15 and old==677
    rows=json.loads((ROOT/'Index-Comptoirs.json').read_text())['orientations'];cfg,stats=config(d,rows)
    (ROOT/'Implantations.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2)+'\n')
    data=[]
    for i,v in enumerate(rows):
        a={k:v[k] for k in ['id','w','h']};a.update({'n':621+i,'label':'Comptoir à cloche · '+v['direction'],'category':'meubles','wall':False,'collection':'comptoirs','palette':'noyer','orientation':v['direction'],'previewOnly':True,'m':[b64(ROOT/v['png'])]});data.append(a)
    d['catalog'].extend(data);d['comptoirs']={**cfg,'orientations':[{k:v[k] for k in ('id','w','h','nom','direction','flèche','pivot','empreinte','allée')} for v in rows]}
    r=json.loads((ROOT/'Releve-Cliff.json').read_text());ws=C/'Calques'; ax,ay,aw,ah,f=r['atlas_mer'];
    d['cliff']={'accueil':'guilde_destiny_accueil','maps':[f'guilde_cliff_{p}' for p in P],'taille':[480,520],'porte':r['porte_rect'],'calques':[[[x,y,b64(ws/z)] for x,y,z in r['calques'][p]] for p in P], 'bases':[b64(C/f'Cliff-{p}-sans.png') for p in P],'mer':{'rect':[ax,ay,aw,ah],'fps':r['fps_mer_apercu'],'frames':12,'png':b64(ws/f)},'details':[b64(ROOT/'Braseros'/f'{s}-nuit-1.png') for s in ('ouest','est')],'fps':r['fps_braseros']}
    prefix=h[:mt.start(2)];suffix=h[mt.end(2):]
    def sub(text,old,new):
        assert text.count(old)==1,(old[:100],text.count(old));return text.replace(old,new,1)
    def pre(o,n):
        nonlocal prefix
        prefix=sub(prefix,o,n)
    def js(o,n):
        nonlocal suffix
        suffix=sub(suffix,o,n)
    pre('Destiny · Mobilier Halcyon — Série IA','Destiny · Comptoirs &amp; falaise')
    pre('</style>',(S/'Vues.css').read_text()+'\n</style>')
    prev='''<div class="kicker"><b>0.7.7</b> GÉNÉRATEUR D’IMAGE <i></i> MODÈLES HALCYON</div>
      <h1 id="titre">Mobilier Halcyon · Série IA<span>.</span></h1>
      <p>Trois meubles passés au générateur d’image à partir des sprites de Halcyon. Les versions choisies sont détourées, adaptées en pixel art et déclinées dans les teintes de Destiny.</p>'''
    pre(prev,'''<div class="kicker"><b>0.7.7</b> GUILDE DESTINY <i></i> ATELIER HALCYON</div>
      <h1 id="titre">Comptoirs &amp; falaise<span>.</span></h1>
      <p>Huit orientations pour aménager les salles et deux braseros de Grodoudou pour éclairer la porte, dehors, la nuit.</p>''')
    pre('<div><strong>3</strong><span>GÉNÉRATIONS</span></div><div><strong>10</strong><span>PALETTES</span></div><div><strong>30</strong><span>SPRITES IA ET DÉRIVÉS</span></div>','<div><strong>8</strong><span>ORIENTATIONS</span></div><div><strong>15</strong><span>SALLES</span></div><div><strong>2</strong><span>BRASEROS EXT.</span></div>')
    pre('    <button id="tab-halcyon" class="soft" type="button" aria-pressed="true">','''    <button id="tab-cf" class="soft" type="button" aria-pressed="true"><svg aria-hidden="true"><use href="#i-grid"/></svg><span>Comptoirs</span></button>
    <button id="tab-cliff" class="soft" type="button" aria-pressed="false"><svg aria-hidden="true"><use href="#i-moon"/></svg><span>Falaise</span></button>
    <button id="tab-halcyon" class="soft" type="button" aria-pressed="false">''')
    pre('  <section id="halcyon-page"',(S/'Vues.html').read_text()+'\n  <section id="halcyon-page"')
    pre('<select id="collection"><option value="halcyon-ia" selected>','<select id="collection"><option value="comptoirs" selected>Comptoirs · 8</option><option value="halcyon-ia">')
    pre('« Les 15 salles » montre tous les plans.', '« Les 15 salles » montre tous les plans. Depuis l’Accueil, le passage « Falaise » mène à l’extérieur sans changer d’ambiance.')
    pre('choisis une variante Halcyon ou un objet PMU puis clique sur la carte.', 'choisis un comptoir ou un autre objet puis clique sur la carte. Un comptoir posé peut changer d’orientation autour de son pied si l’allée reste libre.')
    pre('<img id="destiny-foyers" width="576" height="432" alt="Grand Salon de Destiny : deux lueurs discrètes sur les lianes et le bois proche"><figcaption><b>Destiny · Grand Salon</b>Les pétales prennent une teinte chaude. Les feuilles coupent la lueur et le bois reste lisible.', '<img id="destiny-foyers" width="480" height="520" alt="Falaise de Destiny : les deux braseros au pied de la porte, de nuit"><figcaption><b>Destiny · entrée sur la falaise</b>Les deux braseros détournés éclairent le sol aux abords de la porte. Le bâtiment et l’escalier restent ceux de Destiny.')
    pre('La source G01P01C fournit quatre images et les couleurs observées sur les pierres. Destiny adapte cette lumière aux bourgeons, avec des reflets sous 10 % d’opacité. Les seuls pixels repris à l’intérieur sont des valeurs de couleur, pas les flammes ni le décor.', 'G01P01C fournit les quatre poses des flammes. Les trépieds sont détourés et les reflets sont adaptés à l’herbe de Destiny. Les braseros ne sont pas reportés dans les salles.')
    js("  $('destiny-foyers').src=data.reference.salon;showFlames(false);refBox.showModal();", "  showFlames(false);refBox.showModal();cliffReference().catch(e=>toast(e.message,true));")
    js("  $('download-png').querySelector('small').textContent=s.page==='atelier'", "  $('download-png').querySelector('b').textContent=s.page==='cliff'?'Image de la falaise':'Image de la salle';\n  $('download-png').querySelector('small').textContent=s.page==='atelier'")
    js("const STORE='pmd-destiny:guilde:mobilier-halcyon-ia:077:v1'", "const STORE='pmd-destiny:guilde:comptoirs-cliff:077:v1'")
    js("const s={page:'halcyon'", "const s={page:'comptoirs'")
    js('function why(r,a,x,y){','function why(r,a,x,y,ignore=null,items=dataFor(r)){')
    js("  if (!a.wall && r.floor[ty]?.[tx]!=='1') return 'Le pied de ce meuble doit être sur le sol praticable.';\n  return '';", "  if (!cfById.has(a.id) && !a.wall && r.floor[ty]?.[tx]!=='1') return 'Le pied de ce meuble doit être sur le sol praticable.';\n  return whyCounters(r,a,x,y,ignore,items);")
    js('const note=why(r,a,o.x,o.y);','const note=why(r,a,o.x,o.y,o.id,[]);')
    js('    if(cleaned.length)result[n]=cleaned;', '''    if(cleaned.some(o=>cfById.has(o.meuble)))for(const o of cleaned){
      const note=why(r,assets.get(o.meuble),o.x,o.y,o.id,cleaned);if(note)throw new Error(r.label+' : '+note);
    }
    if(cleaned.length)result[n]=cleaned;''')
    js('issue=why(s.room,a,p.x,p.y);if(issue){toast(issue,true);refresh();return false;}', 'issue=why(s.room,a,p.x,p.y,o.id);if(issue){toast(issue,true);refresh();return false;}')
    js('v.bad=why(s.room,a,v.x,v.y);s.drag.position=', 'v.bad=why(s.room,a,v.x,v.y,s.drag.id);s.drag.position=')
    js('  for(let y=0;y<=r.h-a.h;y+=8)for(let x=0;x<=r.w-a.w;x+=8){if(!why(r,a,x,y))candidates.push([x,y,(x-ox)**2+(y-oy)**2]);}\n  candidates.sort((u,v)=>u[2]-v[2]);\n  if(candidates.length)place(a,{x:candidates[0][0],y:candidates[0][1]});else toast', '''  for(let y=0;y<=r.h-a.h;y+=8)for(let x=0;x<=r.w-a.w;x+=8)candidates.push([x,y,(x-ox)**2+(y-oy)**2]);
  candidates.sort((u,v)=>u[2]-v[2]);const good=candidates.find(([x,y])=>!why(r,a,x,y));
  if(good)place(a,{x:good[0],y:good[1]});else toast''')
    js("function draw(){\n  if(s.page==='halcyon')", "function draw(){\n  if(s.page==='comptoirs'){showCounter();return;}\n  if(s.page==='cliff'){paintCliff();return;}\n  if(s.page==='halcyon')")
    js("panel.append(actions);}\n  else{\n    panel.append(make('span','inspect-coords'", "panel.append(actions);cfChooseOrientation(panel,null,a);}\n  else{\n    cfChooseOrientation(panel,o,assets.get(o.meuble));panel.append(make('span','inspect-coords'")
    js('  updateAtlas();\n', '  updateAtlas();cfUpdate();\n')
    js("$('download-png').disabled=s.page!=='atelier';", "$('download-png').disabled=s.page!=='atelier'&&s.page!=='cliff';")
    js("  $('download-png').querySelector('small').textContent=s.page==='atelier'", "  $('download-png').querySelector('small').textContent=s.page==='cliff'?'Falaise · ambiance et pose actuelles':s.page==='atelier'")
    js("$('download-png').onclick=()=>exportPng().catch", "$('download-png').onclick=()=>(s.page==='cliff'?cliffPNG():exportPng()).catch")
    js("function drawMotion(){\n  if(s.page==='halcyon')", "function drawMotion(){\n  if(s.page==='comptoirs'){if(s.phase===3&&s.lianes&&inWindow(cfPlan))showCounter();return;}\n  if(s.page==='halcyon')")
    js('  if(now>=clock.next){clock.next=now+73;if(!queued)drawMotion();}', '''  if(s.page==='cliff'){
    if(inWindow(cliffMap)&&!queued&&cliffMap.dataset.scene!==cliffFrame(s.phase).code)paintCliff();
  }else if(now>=clock.next){clock.next=now+73;if(!queued)drawMotion();}''')
    js('Figer les étoffes, les halos et les ombres','Figer les animations, y compris les flammes à la falaise')
    js('Relancer les étoffes, les halos et les ombres','Relancer les animations, y compris les flammes à la falaise')
    js('// Shared renderer: the overview never substitutes thumbnails for the native maps.',(S/'Vues.js').read_text()+'\n// Shared renderer: the overview never substitutes thumbnails for the native maps.')
    js("atlasTabs={halcyon:'tab-halcyon'", "atlasTabs={comptoirs:'tab-cf',cliff:'tab-cliff',halcyon:'tab-halcyon'")
    js("$('atlas-page').hidden=atelier||hal;", "$('atlas-page').hidden=!['atlas','sud'].includes(s.page);")
    js('  if(gameMap.has(g.dest))selectRoom(g.dest);',"  if(cliffData.maps.includes(g.dest)){openCliff();return;}\n  if(gameMap.has(g.dest))selectRoom(g.dest);")
    js("    const p=to?button('portal',(i+1)+' · '+to.label,()=>suivrePassage(r,g)):make('span','portal-out',(i+1)+' · Falaise');", "    const p=(to||cliffData.maps.includes(g.dest))?button('portal',(i+1)+' · '+(to?.label||'Falaise'),()=>suivrePassage(r,g)):make('span','portal-out',(i+1)+' · Falaise');\n    p.dataset.passage=g.id;")
    js('const source=hal?halData.palettes.map(p=>[p.id,p.nom]):oldTones;',"const source=hal?halData.palettes.map(p=>[p.id,p.nom]):collection==='comptoirs'?[['noyer','Noyer & pierre']]:oldTones;")
    js("el.disabled=collection==='origine';", "el.disabled=['origine','comptoirs'].includes(collection);")
    js("$('editor-bank-name').textContent=hal?", "$('editor-bank-name').textContent=collection==='comptoirs'?'Comptoirs':hal?")
    js('setupGrille();setupSeuil();setupAtlas();setupHalcyon();updatePalette();refresh();setupMotion();','setupGrille();setupSeuil();setupAtlas();setupHalcyon();setupCF();editorBank(\'comptoirs\',\'tout\');updatePalette();refresh();setupMotion();')
    full=prefix+json.dumps(d,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+suffix
    O.write_text(full); assert BASE.read_bytes()==upstream
    W.mkdir(parents=True,exist_ok=True)
    (W/'atelier.js').write_text(suffix.split('<script>',1)[1].split('</script>',1)[0])
    if (W/'Provenance-cliff.json').is_file():shutil.copy2(W/'Provenance-cliff.json',ROOT/'Provenance-cliff.json')
    print(O.name,O.stat().st_size,hashlib.sha256(O.read_bytes()).hexdigest(),f'{old}+{len(data)} objets, 15 salles + extérieur')

if __name__=='__main__':main()
