#!/usr/bin/env python3
"""Détourage des 3 générations préférées, conversion pixel art 1× et nuanciers dérivés."""
from pathlib import Path
from PIL import Image
from scipy import ndimage as nd
import numpy as np
from collections import Counter
import argparse,csv,hashlib,json,sys
O=Path(__file__).resolve().parents[1]; G=O.parent; REF=G/'Mobilier-Halcyon'; SRC=O/'Sources';
sys.path.insert(0,str(REF/'Sources'))
from Fabriquer import cables,LUMA,VECT

MODELES=[
 {'id':'ia-banquet','souche':'banquet','titre':'Table de banquet','palette':'lierre','fichier':'Table-banquet-Lierre.png','taille':[163,49],'note':'Plateau de noyer, vaisselle verte et attaches de laiton.'},
 {'id':'ia-coffre','souche':'coffre-haut','titre':'Grand coffre','palette':'minuit','fichier':'Grand-coffre-Minuit.png','taille':[36,31],'note':'Panneaux indigo et cerclages de fer bleui. La vue de trois quarts est une interprétation du générateur.'},
 {'id':'ia-bureau','souche':'bureau-rouleau','titre':'Bureau aux parchemins','palette':'ronce','fichier':'Bureau-parchemins-Ronce.png','taille':[46,77],'note':'Noyer rougi et papiers ivoire, dans le cadrage vertical de l’original.'},
]

def sha(b): return hashlib.sha256(b).hexdigest()
def write(p,j):p.write_text(json.dumps(j,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def key(r,g,b):return (r-g>51)&(b-g>57)&(b>132)&(r>132)

def couper(file):
 a=np.array(Image.open(file).convert('RGBA'));r,g,b,alpha=a.astype('int16').transpose(2,0,1);
 fg=(alpha>128)&(~key(r,g,b)); lab,n=nd.label(fg,np.ones((3,3),bool));count=np.bincount(lab.ravel());count[0]=0
 core=lab==count.argmax();assert count.max()/fg.sum()>.993,file
 # Les petites zones magenta entourées par le meuble (ex. ruban du livre) sont intentionnelles.
 keep=nd.binary_fill_holes(core);dist=nd.distance_transform_edt(keep)
 fringe=keep&(dist<4.0)&(r-g>20)&(b-g>19)
 if fringe.any():
    idx=nd.distance_transform_edt(~(keep&(~fringe)),return_distances=False,return_indices=True)
    a[fringe,:3]=a[idx[0][fringe],idx[1][fringe],:3]
 a[~keep]=0;a[keep,3]=255;im=Image.fromarray(a);bbox=im.getbbox();assert all(x>10 for x in bbox[:2]);crop=im.crop(bbox)
 assert np.count_nonzero(np.array(crop)[...,3]==0)>0
 return crop,dict(canvas=list(im.size),rectangle=list(bbox),correction_bordure_px=int(fringe.sum()),sha256_generation=sha(file.read_bytes()))

def tint_parts(a,id):
 r,g,b,k=a.astype('int16').transpose(2,0,1);ok=k>0;h,w=ok.shape;Y,X=np.indices((h,w));role=np.full(ok.shape,'bois',dtype='<U10');role[~ok]=''
 def mark(s,m): role[ok&m]=s
 if id=='ia-banquet':
    mark('tissu',(g-r>8)&(g-b>5));mark('metal',(r>158)&(g>109)&(r>g+17)&(b<g-45))
 elif id=='ia-coffre':
    mark('tissu',ok);mark('metal',((r*1.38+13>b)&(g>66)&(b>=g-1))|(g>141))
    # Le trait externe n'est pas une plaque argentée.
    mark('encre',(r<55)&(np.abs(r-g)<14)&(np.abs(r-b)<22))
 else:
    paper=(r>132)&(g>116)&(b>86)&(r-g<53)&(X>=10)&(X<37)&(Y<50)
    mark('papier',paper);mark('metal',(~paper)&(r>154)&(g>=75)&(b<=g-30)&(Y<18))
    mark('tissu',((b>g+18)|(r>2*g+14))&(X>14)&(X<32)&(Y<18))
 return role

def pixeliser(im,m):
 low=np.array(im.resize(m['taille'],Image.Resampling.BOX));low[low[...,3]<128]=0;low[...,3]=np.where(low[...,3]>0,255,0)
 # Enlève uniquement le bruit de tons du rendu agrandi, sans diffuser dans les pixels adjacents.
 role=tint_parts(low,m['id']);prec={'bois':16,'metal':8,'tissu':13,'papier':9,'encre':5}
 for part in prec:
    mask=role==part
    if not mask.any():continue
    rows=low[mask,:3];ref=Image.fromarray(rows[None,...]).quantize(colors=prec[part],dither=Image.Dither.NONE).convert('RGB');low[mask,:3]=np.asarray(ref)[0]
 assert Image.fromarray(low).getbbox()==(0,0,*m['taille']),m['id']
 return low,role

def accord(a,role,p,model):
 if p['id']==model['palette']:return a.copy()
 colors=cables(p);out=a.copy()
 for mat in ('bois','metal','tissu','encre'):
    mask=role==mat
    if not mask.any():continue
    src=a[mask,:3];unique,inv=np.unique(src,axis=0,return_inverse=True);v=unique@LUMA
    t=(v-v.min())/max(1e-6,v.max()-v.min()) if len(v)>1 else np.full_like(v,.63)
    # Les tables gardent le relief des lames, l'argent la rondeur du couvercle.
    lo,hi={'bois':(.04,.92),'metal':(.12,1.),'tissu':(.13,.97),'encre':(.01,.26)}[mat]
    if model['id']=='ia-bureau' and mat=='tissu':lo,hi=.16,.71
    t=lo+(hi-lo)*t
    ramp=colors['ceramique'] if model['id']=='ia-banquet' and mat=='tissu' else colors[mat]
    rgb=np.stack([np.interp(t,VECT,ramp[:,i]) for i in range(3)],axis=1)
    out[mask,:3]=np.rint(rgb[inv]).clip(0,255).astype('uint8')
 return out

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--generations',type=Path,help='Dossier des trois PNG bruts retenus ; omettre pour repartir des HD détourés');a=p.parse_args()
 refs=json.loads((REF/'Index.json').read_text());src={m['id']:m for m in refs['models']};pal=refs['palettes'];regs=[];models=[];proof=[];allsha=set();
 archive=O/'Detoures-HD';archive.mkdir(exist_ok=True)
 if a.generations is None:prev=json.loads((SRC/'Manifest-generation.json').read_text())
 else:prev={}
 trace={}
 for m in MODELES:
    hd=archive/m['fichier'];r0=src[m['souche']]
    if a.generations is not None:
        im,meta=couper(a.generations/m['fichier']);im.save(hd,optimize=True)
    else:im=Image.open(hd);meta=prev[m['id']]
    trace[m['id']]={**meta,'source_halcyon':r0['carte'],'modele_halcyon':m['souche'],'png_hd':hd.relative_to(O).as_posix(),'sha256_hd':sha(hd.read_bytes()),'taille_hd':list(im.size)}
    model={**m,'hd':hd.relative_to(O).as_posix(),'source':r0['carte'],'salle':r0['salle'],'rect_source':r0['rect'],'sha256_sprite_ref':r0['pixels_sha256']};models.append(model)
    base,role=pixeliser(im,m);collection=[]
    for t in pal:
        o=accord(base,role,t,m);assert np.array_equal(o[...,3],base[...,3]);assert (o[o[...,3]==0]==0).all()
        dg=sha(o.tobytes());assert dg not in allsha;allsha.add(dg);collection.append(o)
        rr,gg,bb,aa=o.astype('int16').transpose(2,0,1);assert not (key(rr,gg,bb)&(aa>0)).any(),(m['id'],t['id'])
        path0=O/'PNG-1x'/t['id']/(m['id'].removeprefix('ia-')+'.png');path0.parent.mkdir(parents=True,exist_ok=True)
        Image.fromarray(o).save(path0,optimize=True);regs.append(dict(id='halcyon-'+m['id']+'-'+t['id'],modele=m['id'],nom=m['titre'],palette=t['id'],nom_palette=t['nom'],
          w=m['taille'][0],h=m['taille'][1],traitement='generation-detouree' if t['id']==m['palette'] else 'nuancier-derive',png=path0.relative_to(O).as_posix(),sha256=sha(path0.read_bytes())))
    assert np.array_equal(collection[next(k for k,t in enumerate(pal) if t['id']==m['palette'])],base)
    rgb=np.array(collection)[:,:, :, :3][:,base[...,3]>0].astype(float)
    distance_min=min(np.linalg.norm(rgb[i]-rgb[j],axis=-1).mean() for i in range(len(rgb)) for j in range(i));assert distance_min>3.5
    proof.append(dict(id=m['id'],taille=m['taille'],pixels_opaques=int(np.count_nonzero(base[...,3])),distance_palette_min=round(distance_min,2)))
 write(SRC/'Manifest-generation.json',trace)
 data=dict(format='destiny-halcyon-ia-v1',source=refs['source'],modeles=models,palettes=pal,variantes=regs)
 write(O/'Index.json',data);write(O/'Verification-graphique.json',dict(etat='PASS',modeles=proof,images_issues_directement_du_generateur=3,sprites_1x=30,nuanciers_derives=27,alpha_conserve_sur_declinaisons=True))
 with (O/'Index.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(regs[0]),delimiter=';');w.writeheader();w.writerows(regs)
 print('PASS · 3 générations détourées HD, 3 adaptations 1× et 27 teintes dérivées')

if __name__=='__main__':main()
