#!/usr/bin/env python3
from Commun import *
from Interieurs import overlaps

def load(p):return Image.open(ROOT/p).convert('RGBA')

def verify():
    f=json.loads((ROOT/'Drapeaux/Index-Drapeaux.json').read_text())['variantes'];assert len(f)==8 and len({v['sha256'] for v in f})==8
    for v in f:
        im=load(v['png']);w,h=im.size;atlas=load(v['atlas']);assert (w,h)==(v['w'],v['h']) and atlas.size==(w*3,h*2) and filehash(ROOT/v['png'])==v['sha256'];base=np.array(im)[-9:]
        unique=set()
        for k in range(6):
            x=k%3*w;y=k//3*h;t=atlas.crop((x,y,x+w,y+h));a=np.asarray(t);assert np.array_equal(a[-9:],base) and set(np.unique(a[...,3]))=={0,255};unique.add(t.tobytes())
            if k==0:assert t.tobytes()==im.tobytes()
        assert len(unique)==6
    b=json.loads((ROOT/'Rayonnages/Index-Rayonnages.json').read_text());total=Image.new('RGBA',tuple(b['canvas']));shapes=set();slots=0
    for s in b['slots']:
        ks=[]
        for q in s['choix'].values():
            w,h=q['w'],q['h'];x,y=s['xy'];im=load(q['png']);a=np.array(im);sel=a[...,3]>0
            assert im.size==(w,h) and not np.any(a[~sel,:3]) and set(np.unique(a[...,3]))=={0,255}
            ks.append(im.tobytes());assert y+h<=127 and not any(overlaps([x,y,w,h],g['rect']) for g in room(BIB)['gates']);slots+=1
        assert len(set(ks))==3
        total.alpha_composite(load(s['choix'][s['defaut']]['png']),tuple(s['xy']));shapes.add(im.size)
    assert total.tobytes()==load(b['calque_defaut']).tobytes()
    a=np.asarray(total);delta=a[...,3]>0
    # These are the two actual window-insert rectangles, not just a visual estimate.
    for x,y,s in room(BIB)['patches'][0]:
        w,h=dec(s).size;assert not delta[y:y+h,x:x+w].any()
    assert not delta[127:,:].any() and 5000<delta.sum()<8500
    g=json.loads((ROOT/'Cheminées/Index-Cheminees.json').read_text());assert g['salle']==REFEC and len(g['modules'])==2;frames=0
    for mo in g['modules']:
        x,y=mo['xy'];w,h=mo['size'];assert not any(overlaps([x,y,w,h],gate['rect']) for gate in room(REFEC)['gates'])
        for f,off in zip(mo['anime'],mo['arret']):
            atlas=load(f);assert atlas.size==(w*4,h);stock=set()
            for k in range(4):
                t=atlas.crop((w*k,0,w*k+w,h));assert t.getchannel('A').tobytes()==load(off).getchannel('A').tobytes();stock.add(t.tobytes());frames+=1
            assert len(stock)==4
    o=json.loads((OLD/'Releve-Cliff.json').read_text());c=json.loads((ROOT/'Cliff-lumiere/Releve-Lumiere.json').read_text());native=Image.open(OLD/'Falaise/Cliff-nuit-sans.png').convert('RGBA');z=np.array(native);kin=0
    for i,q in enumerate(c['poses']):
        plate=native.copy();plate.alpha_composite(load(q['png']),(q['x'],q['y']));final=load(f'Cliff-lumiere/Cliff-nuit-{i+1}.png');assert plate.tobytes()==final.tobytes()
        a=np.array(final);delta=np.any(a!=z,axis=2);assert not delta[:137].any() and not delta[352:].any()
        for s in o['trépieds']:
            x,y=s['pose_pied'];px,py=s['pied_dans_image_nuit'];f=Image.open(OLD/'Braseros'/f"{s['cote']}-nuit-{i+1}.png").convert('RGBA');p=np.array(f);roi=p[...,3]>0
            assert np.array_equal(p[roi],a[y-py:y-py+f.height,x-px:x-px+f.width][roi]);kin+=int(roi.sum())
        m=c['verification'][i];assert m['hausse_lum_facade_vs_edition_precedente']>17 and m['hausse_lum_sol_vs_edition_precedente']>11
    write_json(ROOT/'Verification-graphique.json',{'statut':'PASS','drapeaux':8,'trames_drapeaux_et_pieds_stables':48,'modules_rayonnages':slots,'rayonnages_alpha_rgba_et_fenetres_libres':True,'poses_cheminées_4_ambiances':frames,'composites_cliff':4,'pixels_exactement_conservés_sur_trépieds':kin,'reflets_mesurés':c['verification']})
    print('PASS · 48 poses d’étendard, 9 modules muraux, 32 poses/ambiances de cheminée, 4 composites Cliff.')
if __name__=='__main__':verify()
