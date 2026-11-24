#!/usr/bin/env python3
from Construire import *
from zipfile import ZipFile,ZIP_DEFLATED
import struct,subprocess

M=json.loads((ROOT/'Releve-G01P06.json').read_text());assert M['foyer']['nombre']==1 and M['dimensions_px']==list(C)
A=ROOT/'Refectoire-EoS-Cheminee.mp4';zipname=ROOT/'Kit-Refectoire-EoS-Cheminee.zip';P0=ROOT/'Plans';L=ROOT/'Calques';v=M['zones_preservees'];x,y=M['foyer']['ancre'];r,s=M['foyer']['raccord_ancre'];assert [x,y]==[228,83] and [r,s]==[228,76]
mask=np.logical_or.reduce([bboxmask(q) for q in [*v['vitres'],v['passage'],v['seuil_est'],v['table'],v['fontaine']]])

counts=[]
for j,period in enumerate(PAL):
    off=Image.open(P0/f'Refectoire-{period}-Foyer-Eteint.png').convert('RGBA');aa=play(P0/f'Refectoire-EoS-{period}-Anime.png');base=Image.open(L/period/'01-Salle-bois.png').convert('RGBA')
    calm=Image.open(L/period/'Foyer-eteint.png').convert('RGBA');live=Image.open(L/period/'Foyer-allume-4poses.png').convert('RGBA');comb=Image.open(L/period/'Braises-et-feu-4poses.png').convert('RGBA');n=Image.open(L/period/'Raccord-sous-traverse.png').convert('RGBA');w,ht=calm.size
    assert (w,ht)==(46,94) and live.size==comb.size==(4*w,ht) and n.size==(46,7)
    assert np.all(np.asarray(n)[...,3]<=np.asarray(base.crop((r,s,r+46,s+7)))[...,3])
    b=base.copy();b.alpha_composite(Image.open(L/'Ombres-mobilier.png').convert('RGBA'));sh=Image.open(L/'Ombre-de-contact.png').convert('RGBA');b.alpha_composite(sh)
    furniture=Image.open(L/period/'02-Table-et-corbeilles.png').convert('RGBA');water=Image.open(L/period/'03-Source-4poses.png').convert('RGBA');assembled=[];views=set()
    for i,frame in enumerate(aa):
        bi=(i*w,0,(i+1)*w,ht);fl=comb.crop(bi);pu=live.crop(bi)
        a=np.asarray(fl);m=a[...,3]>0;assert m.sum()>165 and (a[m,0]>206).sum()>90
        assert not (m & ~chamber(Image.open(W/'Foyer-seul.png').convert('RGBA'))).any()
        assert np.array_equal(np.asarray(pu)[...,3],np.asarray(calm)[...,3]);views.add(fl.tobytes())
        globe=Image.open(L/f'Reflets-pose-{i+1}.png').convert('RGBA');q=screen(b,globe,.53 if j==0 else .92);q.alpha_composite(furniture);q.alpha_composite(water.crop((i*C[0],0,(i+1)*C[0],C[1])));q.alpha_composite(n,(r,s));q.alpha_composite(pu,(x,y));assert np.array_equal(np.asarray(q),np.asarray(frame))
        assert np.array_equal(np.asarray(q)[...,3],np.asarray(base)[...,3]);assembled.append(q)
    assert len(views)==4 and len({im.tobytes() for im in aa})==4
    still=Image.open(P0/f'Refectoire-EoS-{period}.png').convert('RGBA');assert still.tobytes()==aa[0].tobytes()
    u=base.copy();u.alpha_composite(Image.open(L/'Ombres-mobilier.png').convert('RGBA'));u.alpha_composite(sh);u.alpha_composite(furniture);u.alpha_composite(water.crop((0,0,*C)));u.alpha_composite(n,(r,s));u.alpha_composite(calm,(x,y));assert u.tobytes()==off.tobytes()
    assert np.array_equal(np.asarray(off)[v['seuil_est'][1]:v['seuil_est'][3],487:],np.asarray(base)[218:244,487:])
    counts.append({'periode':period,'poses':len(views),'images_composees_et_verifiees':len(assembled)+1,'alpha_du_plan_identique':True})

# End-to-end video decode; MP4 moov atom precedes the sample payload for direct playback.
raw=A.read_bytes();i=0;boxes=[]
while i<len(raw):
    n,b=struct.unpack_from('>I4s',raw,i);assert n>=8;boxes.append(b);i+=n
assert i==len(raw) and boxes.index(b'moov')<boxes.index(b'mdat')
meta=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','stream=codec_name,pix_fmt,width,height,avg_frame_rate,nb_frames','-show_entries','format=duration,size','-of','json',str(A)]));u=meta['streams'][0]
assert len(meta['streams'])==1 and u['codec_name']=='h264' and u['pix_fmt']=='yuv420p' and (u['width'],u['height'])==(1280,720) and u['avg_frame_rate']=='30/1' and int(u['nb_frames'])==738 and float(meta['format']['duration'])==24.6
subprocess.run(['ffmpeg','-nostdin','-v','error','-i',str(A),'-f','null','-'],check=True)
paths={'atelier_precedent':('Guilde-Destiny-Drapeaux-Foyers-Bibliotheque.html','005bc65efd4b88102eb0bedc3c484e51dd20750b2f7a99fd7d2caf02662676d5'),'coffret_PMU':('PMU-Orientations/Kit-Destiny-PMU-8-orientations.zip','4479f6210925c8f47f8c74b661a1ca053274d477be72370014bb8a8b6c13062a')}
for n,(filename,stat) in paths.items():assert h(P/filename)==stat
q={'statut':'PASS','composition_alpha':counts,'seuil_est_identique_au_plan_504x360':True,'feu_dans_atre':True,'eau_4poses':True,'fichiers_anterieurs_sha256_inchanges':{n:p[1] for n,p in paths.items()},'film':{'sha256':h(A),'decodage_complet':True,'faststart':True,**meta}}
jsonout(ROOT/'Verification.json',q)
ps=['Lisez-moi.md','Releve-G01P06.json','Verification.json']+[p.relative_to(ROOT).as_posix() for folder in [P0,L] for p in sorted(folder.rglob('*.png'))]
with ZipFile(zipname,'w',compression=ZIP_DEFLATED,compresslevel=6) as z:
    for p in ps:z.write(ROOT/p,p)
with ZipFile(zipname) as z:assert z.testzip() is None and len(set(z.namelist()))==len(ps)
print(f'PASS · 8 images animées + 2 états éteints reconstruits, seuil intact, vidéo décodée, ZIP : {len(ps)} fichiers.')
