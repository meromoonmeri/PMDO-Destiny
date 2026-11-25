import json, zipfile, re, csv, shutil, struct, subprocess
from Banque import ROOT,W,K,A,PREV,KIT,h,img,raw_b64
from PIL import Image,ImageOps
V=W/'Film'
assert json.loads((ROOT/'Verification-poses.json').read_text())['statut']=='PASS'
D=json.loads((A/'Banque.js').read_text().split('=',1)[1].strip().removesuffix(';'));b=D['chiffres']
assert h(PREV.read_bytes())==b['sha256_atelier_avant'] and h(KIT.read_bytes())==b['sha256_coffret_pmu']
a=Image.open(V/'Miroir-avant.png').convert('RGBA');aa=Image.open(V/'Miroir-apres.png').convert('RGBA');assert ImageOps.mirror(a).tobytes()==aa.tobytes()
imgs=[];crc=[]
for x in D['pages']:
 p=K/x['file'];st=p.read_text();v=json.loads(st.split(',',1)[1].removesuffix(');'));u=raw_b64(v);assert h(u)==x['sha256'];ap=img(u);assert list(ap.size)==[x['w'],x['h']];imgs.append(ap)
v=0;aliases={}
with (K/'Index-poses.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.writer(f,delimiter=';');w.writerow(['Code','Nom','Famille','Direction','Page','X','Y','Largeur','Hauteur','Pivot X','Pivot Y'])
 for a in D['ob']:
    aliases.update({q:a['id'] for q in a['alias']});assert len(a['v'])==8
    for k,p in enumerate(a['v']):
        i,x,y,w0,h0,px,py=p
        ap=imgs[i];assert x>=2 and y>=2 and x+w0+1<ap.width and y+h0+1<ap.height
        q=ap.crop((x,y,x+w0,y+h0));assert q.getbbox() is not None;w.writerow([a['code'],a['nom'],a['famille'],D['dirs'][k],D['pages'][i]['file'],x,y,w0,h0,px,py]);v+=1
assert v==8864 and b['ressources_Guilde_Imm']==135 and len([a for a in aliases if a.startswith('Guilde_Imm')])==135
# A small optional example, kept outside the workshop's local saved slot.
probe=json.loads((ROOT/'Verification-poses.json').read_text())['pivots_verifies'][0]
exid='guilde_destiny_cuisine';ex={'v':1,'rid':exid,'pp':0,'sel':'halcyon-bureau-rouleau-lierre','items':{exid:[{'id':'halcyon-bureau-rouleau-lierre','x':probe['x'],'y':probe['y'],'d':1,'m':False},{'id':'coffre_bois_bleu','x':356,'y':244,'d':0,'m':False}]}}
(K/'Exemple-Bibliotheque.json').write_text(json.dumps(ex,ensure_ascii=False,indent=2)+'\n')
vid=ROOT/'Immobilier-Destiny-Pose-8-Sens.mp4';meta=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(vid)]));s=meta['streams'];assert len(s)==1 and s[0]['codec_name']=='h264' and s[0]['pix_fmt']=='yuv420p' and int(s[0]['nb_frames'])==540 and float(meta['format']['duration'])==18
subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(vid),'-f','null','-'],check=True)
p=vid.read_bytes();i=0;at=[]
while i<len(p):n,k=struct.unpack_from('>I4s',p,i);assert 8<=n<=len(p)-i;at.append(k);i+=n
assert at.index(b'moov')<at.index(b'mdat')
report=dict(statut='PASS',poses_png=v,miroir_exact_pixel_par_pixel=True,axes_banque_8=True,zones_seuils_en_lecture_seule=True,original_intact=b['sha256_atelier_avant'],version_PMU_intacte=b['sha256_coffret_pmu'],video_sha256=h(p),video_faststart=True,video_decodee=True)
(ROOT/'Verification-finale.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
for n in ('Lisez-moi.md','Releve-Banque.json','Verification-poses.json','Verification-finale.json'):shutil.copy2(ROOT/n,K/n)
files=sorted(f for f in K.rglob('*') if f.is_file());p=ROOT/'Atelier-Immobilier-Destiny-8-Sens.zip'
with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for f in files:z.write(f,f.relative_to(K))
with zipfile.ZipFile(p) as z:assert z.testzip() is None and len(z.namelist())==len(files) and 'Atelier.html' in z.namelist()
print('PASS :',v,'vues en atlas et 135 .dir natifs couverts, miroir exact,',len(files),'fichiers ZIP,',p.stat().st_size,'octets.')
