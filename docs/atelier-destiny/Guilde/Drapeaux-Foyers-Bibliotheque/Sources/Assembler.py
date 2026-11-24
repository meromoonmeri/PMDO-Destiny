#!/usr/bin/env python3
from Commun import *
S=ROOT/'Sources'

def relocate(q):
    x,y,f=q;return [x,y,b64(ROOT/f)]

def extension_data(d):
    f0=json.loads((ROOT/'Drapeaux/Index-Drapeaux.json').read_text())['variantes'];start=max(a.get('n',0) or 0 for a in d['catalog'])+1
    for j,v in enumerate(f0):
        a={k:v[k] for k in ['id','w','h','direction']};a.update(n=start+j,label='Étendard au gland · '+v['direction'],category='meubles',wall=False,collection='etendards',palette='lierre-or',previewOnly=True,m=[b64(ROOT/v['png'])]);d['catalog'].append(a)
        d['etoffes'][a['id']]={'s':b64(ROOT/v['atlas']),'n':v['poses'],'c':v['colonnes'],'dt':v['duree_ms']}
    f=json.loads((ROOT/'Cheminées/Index-Cheminees.json').read_text());f['ombre']=relocate(f['ombre']);f['reflets']=list(map(relocate,f['reflets']))
    for a in f['modules']:
        for k in ['arret','anime']:a[k]=[b64(ROOT/png) for png in a[k]]
    b=json.loads((ROOT/'Rayonnages/Index-Rayonnages.json').read_text());b.pop('calque_defaut')
    for bu in b['slots']:
        for v in bu['choix'].values():v['png']=b64(ROOT/v['png'])
    cliff=json.loads((ROOT/'Cliff-lumiere/Releve-Lumiere.json').read_text());previous=d['cliff']['calques'][3];d['cliff']['calques'][3]=[[a['x'],a['y'],b64(ROOT/a['png'])] for a in cliff['poses']];d['cliff']['edition_precedente']=previous
    for r in d['rooms']:
        if r['id']==BIB:r['label']='Bibliothèque'
    d['extensions']={'biblio':b,'foyers':f,'accueil':ACC,'drapeaux':[{k:v[k] for k in ['id','direction','nom','flèche','pivot']} for v in f0]}


def main():
    h=BASE.read_text();m=re.search(r'(<script id="donnees"[^>]*>)(.*?)(</script>)',h,re.S);assert m
    src,data,js=h[:m.start(2)],json.loads(m[2]),h[m.end(2):];assert len(data['rooms'])==15 and len(data['catalog'])==685
    extension_data(data)
    def sub(s,a,b):
        assert s.count(a)==1,(a[:160],s.count(a));return s.replace(a,b,1)
    def html(a,b):
        nonlocal src
        src=sub(src,a,b)
    def code(a,b):
        nonlocal js
        js=sub(js,a,b)
    html('Destiny · Comptoirs &amp; falaise','Destiny · Drapeaux, foyers &amp; bibliothèque')
    html('</style>',(S/'Visuel.css').read_text()+'\n</style>')
    html('Comptoirs &amp; falaise<span>.</span>','Drapeaux, foyers &amp; bibliothèque<span>.</span>')
    html('Huit orientations pour aménager les salles et deux braseros de Grodoudou pour éclairer la porte, dehors, la nuit.','Des étendards orientables, deux cheminées dans le Réfectoire et une bibliothèque encastrée. Dehors, les braseros éclairent aussi la façade.')
    html('<div><strong>8</strong><span>ORIENTATIONS</span></div><div><strong>15</strong><span>SALLES</span></div><div><strong>2</strong><span>BRASEROS EXT.</span></div>','<div><strong>8</strong><span>DRAPEAUX</span></div><div><strong>2</strong><span>CHEMINÉES</span></div><div><strong>3</strong><span>NICHES</span></div>')
    html('    <button id="tab-cf" class="soft" type="button" aria-pressed="true">','    <button id="tab-ext" class="soft" type="button" aria-pressed="true"><svg aria-hidden="true"><use href="#i-leaf"/></svg><span>Nouveautés</span></button>\n    <button id="tab-cf" class="soft" type="button" aria-pressed="false">')
    html('<section id="cf-page"',(S/'Visuel.html').read_text()+'\n<section id="cf-page"')
    html('    </section>\n    <aside class="panel palette"','      <div id="ext-editor" class="ext-editor" hidden></div>\n    </section>\n    <aside class="panel palette"')
    html('<select id="collection"><option value="comptoirs" selected>', '<select id="collection"><option value="etendards" selected>Étendards orientés · 8</option><option value="comptoirs">')
    html('La lueur reste sur l’herbe et les racines proches.','La lueur se pose sur l’herbe, les racines, les marches et le bas de la façade.')
    html('id="cliff-toggle" type="button" aria-pressed="true">Avec braseros</button>', 'id="cliff-toggle" type="button" aria-pressed="true">Avec braseros</button><button class="cf-button" id="cliff-reflets" type="button" aria-pressed="true">Façade éclairée</button>')
    html('Les deux braseros détournés éclairent le sol aux abords de la porte.','Les deux braseros détournés éclairent les marches, le bois et la prairie près de la porte.')
    html('Les braseros ne sont pas reportés dans les salles.','Ces braseros restent dehors ; les deux cheminées du Réfectoire ont leur propre animation et leur propre calque.')
    html('<p><b>3 · Garde une copie.</b>', '<p><b>Calques muraux.</b> La Bibliothèque garde le passage de l’ancienne Cuisine. Chaque niche reçoit un rayonnage au choix. « Calque PNG » télécharge seulement les rayonnages. Au Réfectoire, tu peux allumer, éteindre ou masquer les deux cheminées.</p>\n    <p><b>3 · Garde une copie.</b>')
    code("const STORE='pmd-destiny:guilde:comptoirs-cliff:077:v1'","const STORE='pmd-destiny:guilde:etendards-foyers-biblio:077:v1'")
    code("const s={page:'comptoirs'","const s={page:'extensions'")
    code('const {grid=false,gates=false,interactive=false,items=dataFor(r),lianes=s.lianes,ms=clock.ms,gateFrame=lift.frame}=opts;', 'const {grid=false,gates=false,interactive=false,items=dataFor(r),lianes=s.lianes,ms=clock.ms,gateFrame=lift.frame,architecture=true}=opts;\n  const arc=planArchitecture(r,p,ms,architecture);')
    code('  for(const [x,y,b] of doorstep)drawPicture(c,b,x,y);','  for(const [x,y,b] of doorstep)drawPicture(c,b,x,y);\n  drawArchitecture(c,arc);')
    code('  drawPicture(c,r.m[p][1],0,0);\n  drawGrille','  architectureFront(c,r,p,arc);\n  drawGrille')
    code('const scene=[...r.m[p],...vines,','const scene=[...r.m[p],...vines,...arc.bits,')
    code('  if(c.canvas.dataset.scene!==scene)c.canvas.dataset.scene=scene;', '  if(c.canvas.dataset.scene!==scene)c.canvas.dataset.scene=scene;\n  if(c.canvas.dataset.architecture!==arc.key)c.canvas.dataset.architecture=arc.key;')
    code("function draw(){\n  if(s.page==='comptoirs')","function draw(){\n  if(s.page==='extensions'){extPaint();return;}\n  if(s.page==='comptoirs')")
    code('cfChooseOrientation(panel,null,a);}', 'cfChooseOrientation(panel,null,a);extFlagControl(panel,null,a);}')
    code('cfChooseOrientation(panel,o,assets.get(o.meuble));panel.append', 'cfChooseOrientation(panel,o,assets.get(o.meuble));extFlagControl(panel,o,assets.get(o.meuble));panel.append')
    code('updateAtlas();cfUpdate();','updateAtlas();cfUpdate();extUpdate();')
    code("$('download-ground').disabled=s.page!=='atelier'||dataFor()", "$('download-ground').disabled=s.page!=='atelier'||activeArchitecture(r)||dataFor()")
    code('const virt=dataFor().some(o=>assets.get(o.meuble).previewOnly);','const virt=activeArchitecture(s.room)||dataFor().some(o=>assets.get(o.meuble).previewOnly);')
    code('const clipped={layers:true};','const clipped={layers:true,reflets:true};')
    code("    $('cliff-toggle').textContent=clipped.layers?'Avec braseros':'Sans braseros';", "    $('cliff-toggle').textContent=clipped.layers?'Avec braseros':'Sans braseros';\n    $('cliff-reflets').hidden=s.phase!==3||!clipped.layers;\n    $('cliff-reflets').setAttribute('aria-pressed',String(clipped.reflets));\n    $('cliff-reflets').textContent=clipped.reflets?'Façade éclairée':'Ancienne lueur';")
    code("overlay:withL?cliffData.calques[p][f]:null,code:`cliff:${p}:${sea}:${withL?f:'nu'}`", "overlay:withL?(p===3&&!clipped.reflets?cliffData.edition_precedente[f]:cliffData.calques[p][f]):null,code:`cliff:${p}:${sea}:${withL?(p===3&&!clipped.reflets?'ancien-'+f:f):'nu'}`")
    code("const q=cliffFrame(3,true,0),c=make('canvas');", "const q={...cliffFrame(3,true,0),overlay:cliffData.calques[3][0]},c=make('canvas');")
    code("$('cliff-toggle').onclick=()=>{clipped.layers=!clipped.layers;refresh();};", "$('cliff-toggle').onclick=()=>{clipped.layers=!clipped.layers;refresh();};$('cliff-reflets').onclick=()=>{clipped.reflets=!clipped.reflets;refresh();};")
    code('const bits=[...r.m[i],...lianesAt', 'const bits=[...r.m[i],...planArchitecture(r,i,ms).bits,...lianesAt')
    # Ensure animations move in each room view, not only at night.
    left=js.index('function drawMotion(){');right=js.index('function advance(now){',left)
    js=js[:left]+'''function drawMotion(){
  if(s.page==='extensions'){extPaint(true);return;}
  if(s.page==='comptoirs'){if((s.phase===3&&s.lianes||areFoyersMoving(gameMap.get(cfDemo.room)))&&inWindow(cfPlan))showCounter();return;}
  if(s.page==='halcyon'){if((s.phase===3&&s.lianes||areFoyersMoving(gameMap.get(halData.demo.salle)))&&inWindow($('hal-scene')))halPaint();return;}
  if(s.page!=='atelier'){
    if(s.page==='atlas'&&s.phase===3&&s.lianes){paintSeuil(true);paintGrille(true);}
    for(const [r,c,v] of (s.page==='sud'?southPairs:atlasCards))if((s.phase===3&&s.lianes||areFoyersMoving(r))&&inWindow(c))drawScene(c.getContext('2d'),r,s.phase,v,{gates:s.gates});
    return;
  }
  const r=s.room,v=viewport(),cloth=dataFor(r).some(o=>data.etoffes[o.meuble])||data.etoffes[s.tool]||areFoyersMoving(r);
  if(s.compare){
    for(const [i,c] of comparison.entries())if((cloth||(i===3&&s.lianes))&&inWindow(c))drawScene(c.getContext('2d'),r,i,v,{grid:s.grid,gates:s.gates});
  }else if((cloth||(s.phase===3&&s.lianes))&&inWindow(canvas))drawScene(ctx,r,s.phase,v,{grid:s.grid,gates:s.gates,interactive:s.mode==='plan'});
  if(clothPreviews.length)showCloth(true);
}
'''+js[right:]
    code('// Shared renderer: the overview never substitutes thumbnails for the native maps.',(S/'Modules.js').read_text()+'\n// Shared renderer: the overview never substitutes thumbnails for the native maps.')
    code("const atlasTabs={comptoirs:", "const atlasTabs={extensions:'tab-ext',comptoirs:")
    code("const source=hal?halData.palettes.map", "const source=collection==='etendards'?[['lierre-or','Lierre et or']]:hal?halData.palettes.map")
    code("el.disabled=['origine','comptoirs'].includes(collection);", "el.disabled=['origine','comptoirs','etendards'].includes(collection);")
    code("$('editor-bank-name').textContent=collection==='comptoirs'?", "$('editor-bank-name').textContent=collection==='etendards'?'Étendards orientés':collection==='comptoirs'?")
    code("setupAtlas();setupHalcyon();setupCF();editorBank('comptoirs','tout');", "setupAtlas();setupHalcyon();setupCF();setupExt();editorBank('etendards','tout');")
    full=src+json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+js;OUT.write_text(full)
    W.mkdir(parents=True,exist_ok=True);(W/'atelier.js').write_text(js.split('<script>',1)[1].split('</script>',1)[0]);print(len(data['rooms']),'salles ·',len(data['catalog']),'objets ·',OUT.stat().st_size,'octets',OUT.name)

if __name__=='__main__':main()
