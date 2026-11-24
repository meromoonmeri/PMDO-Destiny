#!/usr/bin/env python3
"""Verify the map composites, overlap, motion and video before packaging the layers."""
import json,subprocess,struct,zipfile
from io import BytesIO
from FalaiseR2 import *
from Video import frame, pose, im, OUT, POSTER, SHOT


def equal(a,b):return np.array_equal(np.asarray(a),np.asarray(b))


def check():
    rep=json.loads((ROOT/'Releve-Cliff-R2.json').read_text());q={};count=0
    true_input=json.loads((CF/'Provenance-cliff.json').read_text())
    rows=true_input['fichiers'];assert len(rows)==39 and len({e['fichier'] for e in rows})==39
    assert all(get_hash(NATIVE/x['fichier'])==x['sha256'] for x in rows)
    assert get_hash(SRC)==rep['base_sha256']
    _,_,d=mdata();p=d['cliff']['porte'];assert p==rep['porte']
    floors=turf()[0]
    for phase in P:
        meta=rep['couches'][phase];cl=meta['calques'];original=terrain(phase);old_terrain=np.asarray(original);assert passes(phase)==rep['geometrie_native'][phase]
        cleaned=original.copy();cleaned.alpha_composite(im(cl['herbe']));a=np.asarray(cleaned)
        assert np.array_equal(a[~floors],old_terrain[~floors]) and np.array_equal(a[...,3],old_terrain[...,3]);assert not np.array_equal(a[floors],old_terrain[floors])
        cast=im(cl['ombre']);opacity=np.asarray(cast)[...,3].astype(float);before=np.asarray(obj('Object','Guilde_HD_Ombre_'+phase.capitalize())[0])[...,3]
        # Strict checks around the exact failing y=285/286 line of the old sprite.
        old_count=int(np.count_nonzero(before[-1]));after_count=int(np.count_nonzero(opacity[286:,215:269]));dy=np.abs(np.diff(opacity[284:289,215:269],axis=0))
        assert old_count==58 and after_count>900 and float(dy.max())<.14*float(before[-1].max()), (phase,after_count,dy.max())
        assert cast.getbbox()[3]<353 and 0<cast.getbbox()[0]<cast.getbbox()[2]<480
        assert not opacity[~floors].any()
        rebuilt=cleaned.copy();rebuilt.alpha_composite(cast);rebuilt.alpha_composite(house(phase));assert equal(rebuilt,im(cl['terrain']))
        ps=im(cl['ciel_fixe']).copy();h=im(cl['nuages_cime']);l=im(cl['nuages_horizon']);o=im(cl['cime_occlusion']);assert h.size==l.size==(WID+2*PAD,SKH) and o.size==(WID,SKH)
        if phase=='nuit':
            moon=im(cl['lune']);amp=np.asarray(moon)[...,3];xx,yy=rep['reperage']['cible_lune'];idx=amp==255;Y0,X0=np.where(idx);assert abs(X0.mean()+.5-xx)<1 and abs(Y0.mean()+.5-yy)<1
            assert -1<=xx-(326+72.5)<=1 and yy==67+50 and (Y0.max()<135) and len(X0)>600
            assert not (np.asarray(o)[...,3][idx]).any()
            # The old halo and disc are gone; anything brighter here in the backdrop is an original star.
            sky=np.asarray(ps);r=sky[...,0].astype(np.int16);g=sky[...,1].astype(np.int16);b=sky[...,2].astype(np.int16);assert not ((r>125)&(g>119)&(r>b+24)).any()
            ps.alpha_composite(moon)
        oc=np.asarray(o)[...,3]==255
        ps.alpha_composite(cloud_crop(h));ps.alpha_composite(cloud_crop(l))
        sky_test=ps.copy();sky_test.alpha_composite(o);assert equal(sky_test,im(meta['nu']).crop((0,0,480,152)))
        # Clouds cross behind (never paint on) the actual canopy, also while in motion.
        resting=np.asarray(frame(phase,4,2))
        for offset in [1,11,24]:
            cur=np.asarray(frame(phase,4,2,offset,offset//2))
            assert np.array_equal(cur[:SKH][oc],resting[:SKH][oc]) and np.array_equal(cur[SKH:],resting[SKH:])
            assert not np.array_equal(cur[:SKH][~oc],resting[:SKH][~oc])
        nb=len(meta['feux']);assert nb==(4 if phase=='nuit' else 1)
        s0=im(meta['nu']);mset=set();fset=set();
        for k in range(12):
            expected=full(ps,size=SZ);expected.alpha_composite(out_layer(phase,0,k));expected.alpha_composite(rebuilt);assert equal(expected,scenery(phase,k))
            mset.add(sha256(expected.tobytes()).hexdigest())
            for f in range(nb):
                z=expected.copy();z.alpha_composite(im(meta['feux'][f]));assert equal(z.convert('RGB'),frame(phase,k,f));count+=1
                if k==0:
                    nm=f'Cliff-nuit-{f+1}.png' if phase=='nuit' else f'Cliff-{phase}.png';assert equal(z,im('Plans/'+nm));fset.add(sha256(z.tobytes()).hexdigest())
        assert len(mset)==12 and len(fset)==nb
        q[phase]={'mer_poses_distinctes':len(mset),'braseros_poses_distinctes':len(fset),'ombre_pixels_sous_les_marches_apres_y285':after_count,'saut_alpha_max_raccord':int(dy.max()),'relief_et_entrees_intacts':True}
    data=json.loads(subprocess.check_output(['ffprobe','-hide_banner','-v','error','-show_streams','-show_format','-of','json',str(OUT)]));v=data['streams'];assert len(v)==1 and v[0]['codec_name']=='h264' and v[0]['pix_fmt']=='yuv420p' and [v[0]['width'],v[0]['height']]==[1920,1080]
    n=sum(n for _,n,_ in SHOT);assert int(v[0]['nb_frames'])==n and v[0]['r_frame_rate']=='30/1' and abs(float(data['format']['duration'])-n/30)<.002
    subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(OUT),'-map','0:v','-f','null','-'],check=True)
    b=OUT.read_bytes();i=0;boxes=[]
    while i<len(b):
        nt,key=struct.unpack_from('>I4s',b,i);assert 8<=nt<=len(b)-i;boxes.append(key);i+=nt
    assert boxes.index(b'moov')<boxes.index(b'mdat') and i==len(b)
    return {'statut':'PASS','version_cliff':'0.7.7','ressources_originales_sha256_intactes':len(rows),'cadres_de_calques_reconstruits':count,'passages_conserves':True,'lune_xy':rep['reperage']['cible_lune'],'ambiances':q,'video':{'nom':OUT.name,'format':'H.264 1920×1080 yuv420p, 30 i/s','images':n,'duree_s':n/30,'octets':OUT.stat().st_size,'sha256':get_hash(OUT),'faststart':True,'decode_integral':True},'source_precedente_sha256':get_hash(SRC)}


def archive():
    v=check();dump(ROOT/'Verification.json',v);files=[ROOT/n for n in ['Lisez-moi.md','Releve-Cliff-R2.json','Verification.json',POSTER.name]]
    for p in ('Calques','Plans','Sources'):files.extend(f for f in (ROOT/p).rglob('*') if f.is_file() and '__pycache__' not in f.parts)
    files=sorted(files);assert len(files)==len(set(files));p=ROOT/'Kit-Falaise-Destiny-Calques.zip';tmp=W/p.name
    with zipfile.ZipFile(tmp,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for f in files:z.write(f,'Falaise-Ombre-et-Lune/'+str(f.relative_to(ROOT)))
    with zipfile.ZipFile(tmp) as z:
        assert z.testzip() is None and len(z.namelist())==len(files)
        for f,nm in zip(files,z.namelist()):assert sha256(z.read(nm)).hexdigest()==get_hash(f)
    tmp.replace(p)
    print(f"PASS · {v['cadres_de_calques_reconstruits']} assemblages exacts, 4 ambiances, porte / relief intacts, {v['video']['images']} images MP4 décodées, {len(files)} fichiers ZIP vérifiés.")

if __name__=='__main__':archive()
