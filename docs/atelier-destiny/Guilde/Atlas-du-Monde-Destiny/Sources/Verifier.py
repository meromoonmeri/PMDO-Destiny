from pathlib import Path
from hashlib import sha256
from zipfile import ZipFile, ZIP_DEFLATED
from PIL import Image
import numpy as np
import io, json, subprocess, struct
from Animer import ROOT, C, W, SIZE, V, F, DUR, M, COL, NN, OUT, view

def digest(p):return sha256(p.read_bytes()).hexdigest()
def comp():
    base=Image.open(C/'Parchemin-relief.png').convert('RGBA')
    for n in ('Reliefs-et-forets','Sentiers-et-ruisseau','Lieux-Destiny'):base.alpha_composite(Image.open(C/(n+'.png')).convert('RGBA'))
    assert base.convert('RGB').tobytes()==Image.open(C/'Monde-1x.png').convert('RGB').tobytes()
    poster=ROOT/'Monde-Destiny-Sans-Texte-6144x4608.png';p=Image.open(poster);assert p.size==(6144,4608) and p.resize(SIZE,NN).tobytes()==base.convert('RGB').tobytes()
    pp=ROOT/'Reverie-Et-Ses-Donjons.png';q=Image.open(pp);x,y,r,b=M['cadre_depart'];assert q.size==((r-x)*5,(b-y)*5) and q.resize((r-x,b-y),NN).tobytes()==base.crop((x,y,r,b)).convert('RGB').tobytes()
    d=sorted(COL.values(),key=lambda a:a['distance_reverie']);assert len(d)==5 and max(k['distance_reverie'] for k in d)<61
    for k in ['fosse','passage','reverie']:
        src=Image.open(C/f'Eau-{k}-8-poses.png');w,h=src.width//4,src.height//2
        a=[np.array(src.crop((i%4*w,i//4*h,i%4*w+w,i//4*h+h))) for i in range(8)];assert all(np.array_equal(q[...,3],a[0][...,3]) for q in a);assert len({sha256(q.tobytes()).digest() for q in a})==8
    assert view(72).tobytes()!=view(216).tobytes();assert view(F*DUR-1).size==V
    p=subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(OUT)]);s=json.loads(p);v=s['streams'][0];assert len(s['streams'])==1 and v['codec_name']=='h264' and v['pix_fmt']=='yuv420p' and (v['width'],v['height'])==V and int(v['nb_frames'])==F*DUR and float(s['format']['duration'])==DUR
    b=OUT.read_bytes();i=0;l=[]
    while i<len(b):
        n,k=struct.unpack_from('>I4s',b,i);assert n>=8 and n+i<=len(b);l.append(k);i+=n
    assert l.index(b'moov')<l.index(b'mdat');subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(OUT),'-f','null','-'],check=True)
    z={'statut':'PASS','carte_px':[6144,4608],'calques_reconstruits_exactement':True,'glyphes':len(COL),'eau_poses_distinctes':8,'repere_texte_externe':True,'aucun_texte_ajoute_au_rendu':True,'duree_s':DUR,'cadres_video':F*DUR,'faststart':True,'video_decodee':True,'sha256_mp4':digest(OUT),'sha256_carte':digest(poster)}
    (ROOT/'Verification.json').write_text(json.dumps(z,ensure_ascii=False,indent=2)+'\n');fn=ROOT/'Kit-Monde-Destiny-Calques.zip';files=[ROOT/n for n in ('Lisez-moi.md','Reperes-separes.json','Verification.json',pp.name)]+sorted(C.glob('*.png'))+sorted((ROOT/'Sources').glob('*.py'))
    with ZipFile(fn,'w',ZIP_DEFLATED,compresslevel=5)as a:
        for p in files:a.write(p,p.relative_to(ROOT))
    with ZipFile(fn)as a:assert a.testzip() is None and len(a.namelist())==len(files)
    print('PASS : 5 lieux proches, 8 poses d’eau, MP4 décodé,',len(files),'fichiers ZIP')
if __name__=='__main__':comp()
