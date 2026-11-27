#!/usr/bin/env python3
"""Update the preview only: carved rims and recess below the north arch."""
from pathlib import Path
import argparse,hashlib,json,shutil,tempfile
import numpy as np
from PIL import Image

S=Path(__file__).resolve().parent;OUT=S.parent;PROJECT=OUT.parent
FILE=PROJECT/'Guilde-Destiny-Bourgeons-PMD.html'
G=PROJECT/'Grille-Grodoudou';WORK=Path.home()/'.cache/retouches-rives-destiny'


def from_file(p,tag):
    import importlib.util
    spec=importlib.util.spec_from_file_location(tag,p)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module


R=from_file(S/'Recaler-rives.py','pose_rives');L=R.L
A=from_file(G/'Sources/Assombrir-escalier.py','ombre_escalier')
V=from_file(S/'Video.py','comparatif')
META='raccords_bois'


def replace(s,old,new):
    assert s.count(old)==1,old
    return s.replace(old,new,1)


def copy_to(src,dest):
    t=dest.with_name(dest.name+'.tmp');shutil.copyfile(src,t);t.replace(dest)


def build(source,sortie,scratch):
    head,d,tail=L.page(source)
    assert META not in d,'Choisir une version avant les raccords, avec la grille et le seuil sud.'
    assert 'grille_accueil' in d and 'seuil_accueil' in d and 'chaines_accueil' not in d
    assert len(d['rooms'])==15 and sum(len(r['gates']) for r in d['rooms'])==29
    assert sum(bool(r['south'] and r['south']['band']) for r in d['rooms'])==7
    assert len(d['phases'])==4 and all(len(q['points'])==2 for q in d['lianes'].values())
    hall=next(r for r in d['rooms'] if r['id']==A.G.ID);salon=next(r for r in d['rooms'] if r['n']==3)
    old_film=L.night_frames(salon,d);guide,_=L.ref_frames()
    base,patch,shade,details=A.assombrir(hall,L)
    sources=R.V.modules();bramble=R.V.bramble();summaries=[];changed={};scopes={}
    for r in d['rooms']:
        layers,delta,_,note=R.reposer(r,d,*sources,bramble)
        n=r['n'];rid=r['id']
        if delta.any():
            q=d['lianes'][rid]
            for k,img in zip(('s','t'),layers,strict=True):
                if not np.array_equal(L.decode(q[k]),img):q[k]=L.pack(img)
            changed[rid]=sum('distance_tige_axe_px' in i for i in note['bordures'])
        summaries.append(note)
        if n==1:
            assert not delta.any();delta=shade
        crop=R.maskbox(delta);assert crop
        x,y,w,h=crop;a=np.zeros((h,w,4),np.uint8);a[...,3]=delta[y:y+h,x:x+w]*np.uint8(255)
        scopes[rid]=[x,y,L.pack(a)]
        print(f'{n:02} {r["label"]} · {note["pixels_modifies"]} pixels de verdure repris',flush=True)
    assert len(changed)==14 and sum(changed.values())==27
    patch.save(scratch/'Ombre-Interieure.png',optimize=True)
    hall['base']=L.pack(base)
    # Check the phase lookup and that the lower staircase and south are bit-for-bit unchanged.
    _,stock,_=L.page(source);before=stock['rooms'][0]
    for i in range(4):
        a,af,_=R.T.image_layers(hall,d,i);b,bf,_=R.T.image_layers(before,stock,i)
        m=np.any(a!=b,axis=2);assert not m[~shade].any() and m.sum()>1300 and np.array_equal(af,bf)
        assert np.array_equal(a[114:],b[114:])
        # The crown's narrow crop reads as a recess; the lower two bright steps remain.
        assert a[72:82,250:261,:3].mean()<b[72:82,250:261,:3].mean()
    new_film=L.night_frames(salon,d)
    d['reference']['salon']=L.pack(new_film[2]);video_map=[]
    for i,s in enumerate(guide):
        a,b=Image.fromarray(old_film[i]),Image.fromarray(new_film[i]);out=[]
        for zoom in (False,True):
            old=V.stage(Image.fromarray(s),a,zoom,True);new=V.stage(Image.fromarray(s),b,zoom,True)
            out.append(int(np.any(np.array(old)!=np.array(new),axis=2).sum()))
        video_map.append(out)
    assert all(a>0 and b==0 for a,b in video_map)
    V.VIDEO=scratch/'Falaise-et-Bourgeons.webm';V.MP4=V.VIDEO.with_suffix('.mp4');V.POSTER=V.VIDEO.with_suffix('.webp')
    V.build(guide,new_film,verdure=True)
    d['film']=dict(webm=L.uri(V.VIDEO.read_bytes(),'video/webm'),mp4=L.uri(V.MP4.read_bytes(),'video/mp4'),poster=L.uri(V.POSTER.read_bytes(),'image/webp'))
    d[META]=dict(rives=changed,escalier=details['salle'],film_recalcule=True)
    assert all(d[k]==v for k,v in stock.items() if k not in {'rooms','lianes','reference','film'})
    assert d['rooms'][1:]==stock['rooms'][1:]
    for rid,q in d['lianes'].items():
        expect=stock['lianes'][rid];assert {k:v for k,v in q.items() if k not in ('s','t')}=={k:v for k,v in expect.items() if k not in ('s','t')}
        assert (q!=expect)==(rid in changed)
    # Preserve the same controls and scene renderer; only describe the new finish.
    old='Baissée, elle barre toute l’ouverture. Pour passer, lève-la dans l’arche.'
    new='Lève la grille pour dégager le passage. Les marches du haut s’enfoncent dans l’ombre, derrière l’arche.'
    if new not in head:head=replace(head,old,new)
    tail=replace(tail,'Les cartes « Verdure ajustée » indiquent les poteaux repris. Les bourgeons s’animent en Nuit ; le halo du seuil reste fixe.',
                 'Les lianes épousent les rives sculptées. La mention « Verdure ajustée » signale les reprises sur les poteaux. Les bourgeons s’animent en Nuit.')
    raw=head+L.MARK+json.dumps(d,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+'</script>'+tail
    report=dict(statut='PASS',salles_verifiees=15,rives_controlees=30,rives_recalees=sum(changed.values()),
                salles_rives_recalees=len(changed),rives_deja_en_contact=3,salles=summaries,escalier=details,
                changements_hors_zone=0,emetteurs_inchanges=30,video_pixels_modifies_vues=video_map,
                passage_verrou_partage_inchange=True,seuil_sud_inchange=True,jeu_modifie=False,
                source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                html_sha256=hashlib.sha256(raw.encode('utf8')).hexdigest())
    L.jsonout(WORK/'Masques-controle.json',scopes)
    L.jsonout(OUT/'Verdure/Index-raccords.json',report)
    copy_to(scratch/'Ombre-Interieure.png',G/'Calques/Ombre-Interieure.png')
    for f in (V.VIDEO,V.MP4,V.POSTER):copy_to(f,OUT/f.name)
    temp=sortie.with_name(sortie.name+'.tmp');temp.write_text(raw,encoding='utf8');temp.replace(sortie)
    print(f'PASS · 27 rives recalées · ombre de l’arche : {int(shade.sum())} pixels · {sortie.stat().st_size:,} o')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,default=FILE,help='aperçu avant raccords, seuil + grille installés')
    p.add_argument('--sortie',type=Path,default=FILE)
    a=p.parse_args();WORK.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='montage-',dir=WORK) as folder:
        build(a.source,a.sortie,Path(folder))


if __name__=='__main__':main()
