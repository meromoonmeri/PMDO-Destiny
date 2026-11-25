#!/usr/bin/env python3
"""Assemble the offline visit: original background colours and visible night reflections."""
import argparse,hashlib,json,shutil,tempfile
from pathlib import Path
import numpy as np
from PIL import Image
import importlib.util

S=Path(__file__).resolve().parent;OUT=S.parent;PROJECT=OUT.parent
FILE=PROJECT/'Guilde-Destiny-Bourgeons-PMD.html';WORK=Path.home()/'.cache/fonds-ronces-nuit'

def load(name,p):
    spec=importlib.util.spec_from_file_location(name,p)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod

N=load('nouvelle_visite',S/'Balade-nocturne.py');L=N.L
V=load('film_visite',S/'Video.py')


def swap(s,old,new):
    assert s.count(old)==1,old
    return s.replace(old,new,1)


def unpack_footprints(shape,points):
    footprint=np.zeros(shape,bool)
    for p in points:
        for frame in p['images']:
            for x,y,b in frame:
                q=L.decode(b)[...,3];h,w=q.shape
                footprint[y:y+h,x:x+w]|=q>0
    return footprint


def pack_mask(mask):
    x,y,w,h=N.R.maskbox(mask)
    return [x,y,L.pack(N.F.rgba(mask[y:y+h,x:x+w].astype(np.uint8)*255,[0,0,0]))]


def verify_lighting(r,d,void,folia,keep,lamps):
    base=N.night_bitmap(r,d,void,folia);rgb,new=N.light_frames(base,lamps)
    shape=keep.shape;floor=N.F.freeze_support(r,d)[4]&~keep
    vines=np.maximum(L.decode(folia['s'])[...,3],L.decode(folia['t'])[...,3]);floor&=vines==0
    old_bare=L.night_base(r,d);old_frames=L.night_frames(r,d)
    series=[];sample=None
    for i,(frame,old) in enumerate(zip(new,old_frames,strict=True)):
        delta=(frame-rgb)@L.LUMA;prev=(old-old_bare)@L.LUMA
        assert not delta[keep].any() and not delta[void].any()
        inside=int(((delta>=6)&floor).sum());prevpix=int(((prev>=6)&floor).sum());assert inside>2900 and inside>2.2*prevpix,(r['id'],inside,prevpix)
        a=np.ones(shape,float)
        for p in lamps:
            x,y,bit=p['images'][i][0];m=L.decode(bit)[...,3];h,w=m.shape
            a[y:y+h,x:x+w]*=1-m/255.
        peak=255*float((1-a).max());assert peak<=N.REFLECT_MAX+1.e-6
        series.append(dict(plancher_delta_luma_6=inside,ancienne_version=prevpix,reflet_alpha_max=round(peak,1)))
        if i==0:
            y,x=np.unravel_index(np.argmax(np.where(floor,delta,-1)),floor.shape)
            sample=[int(x),int(y),round(float(delta[y,x]),1)]
    amplitude=np.ptp(np.asarray(new).astype(float)@L.LUMA,axis=0)
    assert (amplitude>=2.5).sum()>340,(r['id'],(amplitude>=2.5).sum())
    return new,dict(images=series,sonde_plancher=sample,pixels_variables=int((amplitude>=2.5).sum()))


def upgrade(head,tail):
    head=swap(head,'background:#60462f;max-height:285px','background:var(--couleur-vide,#1f1f3f);max-height:285px')
    head=swap(head,'<style>','<style>\n#visite-nuit{border-color:#7287a4;color:#e2ecff;background:#303d57;font-weight:650}#visite-nuit:hover{background:#3b4a69}.badge-ronces-nord{margin-left:auto;color:#dbe6cb;background:#26362a;border:1px solid #475c49;border-radius:4px;padding:1px 4px;font-size:9px;white-space:nowrap}')
    head=swap(head,'<div class="atlas-opts"><div id="atlas-phases"','<div class="atlas-opts"><button id="visite-nuit" class="soft mini" type="button" title="Entrer au Carrefour de nuit et suivre les passages"><svg aria-hidden="true"><use href="#i-moon"/></svg><span>Visiter de nuit</span></button><div id="atlas-phases"')
    head=swap(head,'les bourgeons de Destiny reprennent les quatre phases de cette lumière, sans braseros dans la salle.',
              'les bourgeons de Destiny éclairent le bois et les planches, avec les quatre phases de la référence. Aucun brasero n’est ajouté.')
    tail=swap(tail,"const spritesAmbiance=new Map();",'''const visite=data.balade_nuit;
const fondPlan=r=>visite?.fonds[r.id];
const feuillage=r=>visite?.ronces[r.id]||data.lianes[r.id];
const pointsLumineux=r=>visite?.lumieres[r.id]||data.lianes[r.id].points;
const spritesAmbiance=new Map();''')
    tail=swap(tail,"  const n=ambiance(r,i);if(!n&&!i)return [r.base,r.front];\n  const couleurs=n?{lut:n.lut}:{tint};\n  return [{source:r.base,...couleurs,patches:r.patches[i]}, {source:r.front,...couleurs,patches:[]}];",'''  const n=ambiance(r,i),matte=fondPlan(r)?.matte;if(!n&&!i&&!matte)return [r.base,r.front];
  const couleurs=n?{lut:n.lut,matte}:{tint,matte};
  return [{source:r.base,...couleurs,patches:r.patches[i]}, {source:r.front,...couleurs,patches:[]}];''')
    tail=swap(tail,"  Promise.all([src.promise,...parts.map(([, ,p])=>p.promise)]).then(results=>{",'''  const matte=b.matte?picture(b.matte):null;
  Promise.all([src.promise,...parts.map(([, ,p])=>p.promise),...(matte?[matte.promise]:[])]).then(results=>{''')
    tail=swap(tail,"    for(const [x,y,p] of parts){c.clearRect(x,y,p.pic.width,p.pic.height);c.drawImage(p.pic,x,y);}\n    success();",'''    for(const [x,y,p] of parts){c.clearRect(x,y,p.pic.width,p.pic.height);c.drawImage(p.pic,x,y);}
    if(matte){c.save();c.globalCompositeOperation='destination-out';c.drawImage(matte.pic,0,0);c.restore();}
    success();''')
    tail=swap(tail,"  const n=ambiance(r,p);c.fillStyle=n?`rgb(${n.fond.join(',')})`:'#20221b';c.fillRect(0,0,view.w,view.h);c.translate(-view.x,-view.y);",'''  const n=ambiance(r,p),rgb=fondPlan(r)?.rgb[p]||n?.fond;
  const fond=rgb?`rgb(${rgb.join(',')})`:'#20221b';
  if(c.canvas.style.getPropertyValue('--couleur-vide')!==fond)c.canvas.style.setProperty('--couleur-vide',fond);
  c.fillStyle=fond;c.fillRect(0,0,view.w,view.h);c.translate(-view.x,-view.y);''')
    tail=swap(tail,"  if(vines.length&&p===3)illuminate(c,r,ms);",'''  if(vines.length&&p===3)illuminate(c,r,ms);
  else if(c.canvas.hasAttribute('data-lueur'))c.canvas.removeAttribute('data-lueur');''')
    tail=swap(tail,"  return data.lianes[r.id].points.flatMap(s=>s.images.flatMap(pair=>pair.map(bit=>bit[2])));", "  return pointsLumineux(r).flatMap(s=>s.images.flatMap(pair=>pair.map(bit=>bit[2])));")
    tail=swap(tail,"  const i=frameLueur(ms);c.save();c.globalCompositeOperation='screen';\n  for(const p of data.lianes[r.id].points){",'''  const i=frameLueur(ms);c.save();c.globalCompositeOperation='screen';
  if(c.canvas.dataset.lueur!==String(i))c.canvas.dataset.lueur=String(i);
  for(const p of pointsLumineux(r)){''')
    tail=swap(tail,"  const layer=data.lianes[r.id],key=r.id+':'+p;", "  const layer=feuillage(r),key=r.id+':'+p;")
    tail=swap(tail,"    const matrix=ambiance(r,p)?.lut;\n    vineLUTs.set(key,[layer.s,layer.t].map(source=>matrix?{source,lut:matrix,patches:[]}:source));",'''    const matrix=ambiance(r,p)?.lut,matte=fondPlan(r)?.matte;
    vineLUTs.set(key,[layer.s,layer.t].map(source=>matrix?{source,lut:matrix,matte,patches:[]}:source));''')
    tail=swap(tail,"`Nuit · ${data.lianes[s.room.id].points.length} bourgeons lumineux`", "`Nuit · ${pointsLumineux(s.room).length} bourgeons éclairent le bois`")
    tail=swap(tail,"`${data.lianes[s.room.id].v} poteaux enroulés`", "`${feuillage(s.room).v} poteaux enroulés`")
    tail=swap(tail,"  $('atlas-gates').onclick=()=>{s.gates=!s.gates;refresh();};",'''  $('atlas-gates').onclick=()=>{s.gates=!s.gates;refresh();};
  $('visite-nuit').onclick=()=>{s.phase=3;s.lianes=true;openDepuisAtlas(gameMap.get(visite.depart));};''')
    tail=swap(tail,"    if(r.id===seuil.id)meta.append(make('span','badges-seuil','Halo au seuil'));",'''    if(visite.ronces[r.id])meta.append(make('span','badge-ronces-nord','Ronces au nord'));
    if(r.id===seuil.id)meta.append(make('span','badges-seuil','Halo au seuil'));''')
    tail=swap(tail,"Les lianes épousent les rives sculptées. La mention « Verdure ajustée » signale les reprises sur les poteaux. Les bourgeons s’animent en Nuit.","Fonds bleus relevés sur les cartes de Grodoudou. En Nuit, les bourgeons éclairent le bois et les passages conservent l’ambiance.")
    return head,tail


def build(source,sortie,scratch):
    head,d,tail=L.page(source)
    assert 'raccords_bois' in d and 'balade_nuit' not in d and len(d['rooms'])==15
    assert sum(len(r['gates']) for r in d['rooms'])==29
    assert sum(bool(r['south'] and r['south']['band']) for r in d['rooms'])==7
    refs=N.swatches();guide,paint,response,_=L.read_reference();texture=N.A.Matte()
    layers=dict(fonds={},lumieres={},ronces={},depart=N.CROSS,alpha_max=N.REFLECT_MAX)
    d['balade_nuit']=layers;salon=None;ledger={};scopes={};branch_notes=None
    for r in d['rooms']:
        key=r['id'];fonds,void,f=N.scenery(r,d,refs);layers['fonds'][key]=fonds
        new=[];ronces_mask=np.zeros(void.shape,bool);fo=d['lianes'][key]
        if key==N.CROSS:
            fo,new,ronces,ronces_mask,branch_notes=N.ronces(r,d,void);layers['ronces'][key]=fo
            box=Image.fromarray(ronces);box.crop(box.getbbox()).save(scratch/'Ronces-nord-Carrefour.png',optimize=True)
        lights,notes,keep=N.eclairage(r,d,void,fo,new,texture,paint,response);layers['lumieres'][key]=lights
        frames,proof=verify_lighting(r,d,void,fo,keep,lights)
        if r['n']==3:salon=frames
        ledger[key]=dict(nom=r['label'],**f,bourgeons=notes,**proof)
        night_delta=unpack_footprints(void.shape,lights)|unpack_footprints(void.shape,d['lianes'][key]['points'])
        scopes[key]=dict(jour=pack_mask(void|ronces_mask),nuit=pack_mask(void|ronces_mask|night_delta))
        print(r['label'],f'· fond RGB {f["phases"][0]} / {f["phases"][3]} ·',proof['images'][0]['plancher_delta_luma_6'],'pixels de plancher éclairés',flush=True)
    assert salon is not None and set(layers['ronces'])=={N.CROSS} and branch_notes
    assert sum(len(lamps) for lamps in layers['lumieres'].values())==32
    d['reference']['salon']=L.pack(salon[2]);head,tail=upgrade(head,tail)
    V.VIDEO=scratch/'Falaise-et-Bourgeons.webm';V.MP4=V.VIDEO.with_suffix('.mp4');V.POSTER=V.VIDEO.with_suffix('.webp')
    V.build(guide,salon,verdure=True)
    d['film']=dict(webm=L.uri(V.VIDEO.read_bytes(),'video/webm'),mp4=L.uri(V.MP4.read_bytes(),'video/mp4'),poster=L.uri(V.POSTER.read_bytes(),'image/webp'))
    _,before,_=L.page(source)
    assert all(before[k]==d[k] for k in before if k not in ('film','reference'))
    assert {k:v for k,v in before['reference'].items() if k!='salon'}=={k:v for k,v in d['reference'].items() if k!='salon'}
    raw=head+L.MARK+json.dumps(d,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+'</script>'+tail
    digest=hashlib.sha256(raw.encode('utf8')).hexdigest()
    proof=dict(statut='PASS',salles=ledger,plans_inchanges=15,passages_inchanges=29,cadres_sud_inchanges=7,bourgeons_emetteurs=32,
               alpha_reflet_plafond=N.REFLECT_MAX,cadence_images_s=6,plans_source=refs,ronces_nord=branch_notes,
               zones_protegees=['fond','vitres','seuils et arrivées','arche nord et tapis sud de l’Accueil'],
               alpha_source_generee=texture.info,ambiances_intermediaires='interpolation entre les échantillons Jour et Nuit',
               lecture_video=V.VIDEO.name,jeu_modifie=False,source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),html_sha256=digest)
    L.jsonout(OUT/'Verdure/Index-balade-nuit.json',proof);L.jsonout(WORK/'Masques-balade-test.json',scopes)
    shutil.copyfile(scratch/'Ronces-nord-Carrefour.png',OUT/'Verdure/Ronces-nord-Carrefour.png')
    for src in [V.VIDEO,V.MP4,V.POSTER]:shutil.copyfile(src,OUT/src.name)
    t=sortie.with_name(sortie.name+'.tmp');t.write_text(raw,encoding='utf8');t.replace(sortie)
    print(f'PASS · fonds de 15 plans, deux ronces nord, 32 bourgeons · {sortie.stat().st_size:,} o · {digest}')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,default=FILE);p.add_argument('--sortie',type=Path,default=FILE);a=p.parse_args()
    WORK.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='compo-',dir=WORK) as stage:
        build(a.source,a.sortie,Path(stage))


if __name__=='__main__':main()
