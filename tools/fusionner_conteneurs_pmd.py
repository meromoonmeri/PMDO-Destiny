#!/usr/bin/env python3
"""Fusionne des conteneurs graphiques PMDO 0.8.12 sans perdre les formes.

Raison : PMDO choisit un fichier .chara/.portrait par espèce ; un fichier de
Quest incomplet masquerait les autres formes et skins de base/. Ce script
préserve les nœuds et les blobs d'origine, applique seulement les sous-nœuds
importés, et produit un index profond. Les anciennes feuilles remplacées
restent intactes dans base/ ; ce script ne modifie jamais ses entrées.

Les données Remixed doivent être fournies séparément par leur détenteur ;
aucun contenu d'une ROM n'est fourni ou téléchargé par ce programme.
"""
from __future__ import annotations
import argparse, hashlib, io, json, struct
from pathlib import Path
from PIL import Image

class Node:
 def __init__(self,pos=0):self.pos=pos;self.payload=None;self.kids={}

def read(fmt,data,pos):
 n=struct.calcsize(fmt);assert pos+n<=len(data),(fmt,pos,len(data));v=struct.unpack_from(fmt,data,pos)
 return (v[0] if len(v)==1 else v),pos+n

def read_node(data,pos=0):
 (position,count),pos=read('<qi',data,pos);assert 0<=count<10000
 n=Node(position)
 for _ in range(count):
  key,pos=read('<i',data,pos);assert key not in n.kids
  sub,pos=read_node(data,pos);n.kids[key]=sub
 return n,pos

def walk(n,path=()):
 yield path,n
 for key,child in sorted(n.kids.items()):yield from walk(child,path+(key,))

def validate_blob(blob,kind):
 pos=0;length,pos=read('<q',blob,pos);assert 0<length<=len(blob)-pos
 png=blob[pos:pos+length];pos+=length
 image=Image.open(io.BytesIO(png));image.verify()
 (w,h),pos=read('<ii',blob,pos);assert 0<w<=2048 and 0<h<=2048
 if kind=='Portrait':
  count,pos=read('<i',blob,pos);assert 0<=count<=100
  for _ in range(count):
   (_,index,rev),pos=read('<ii?',blob,pos);assert index>=0 and rev in (True,False)
 else:
  (shadow,offcount),pos=read('<ii',blob,pos);assert 0<=shadow<=10 and 0<=offcount<100000
  pos+=offcount*32;assert pos<=len(blob)
  keys,pos=read('<i',blob,pos);assert 0<=keys<10000
  for _ in range(keys):
   (_,internal,copy),pos=read('<iii',blob,pos)
   if copy>-1:continue
   (_,_,_,sequences),pos=read('<iiii',blob,pos);assert 0<=sequences<=100
   for _ in range(sequences):
    frames,pos=read('<i',blob,pos);assert 0<=frames<100000
    pos+=frames*29;assert pos<=len(blob)
 assert pos==len(blob),(kind,'taille de feuille incorrecte',pos,len(blob))

def load_container(path,kind):
 data=path.read_bytes();root,header=read_node(data)
 positions=sorted({n.pos for _,n in walk(root) if n.pos})
 assert not positions or (positions[0]>=header and positions[-1]<len(data)),path
 blobs={}
 for i,p in enumerate(positions):
  end=positions[i+1] if i+1<len(positions) else len(data)
  blob=data[p:end];validate_blob(blob,kind);blobs[p]=blob
 for _,n in walk(root):
  if n.pos:n.payload=blobs[n.pos]
 return root

def copy_node(n):
 out=Node();out.payload=n.payload;out.kids={k:copy_node(v) for k,v in n.kids.items()};return out

def merge(base,overlay):
 if overlay.payload is not None:base.payload=overlay.payload
 for key,child in overlay.kids.items():
  if key not in base.kids:base.kids[key]=Node()
  merge(base.kids[key],child)

def node_at(root,path):
 n=root
 for k in path:
  if k not in n.kids:return None
  n=n.kids[k]
 return n

def ensure(root,path):
 n=root
 for k in path:n=n.kids.setdefault(k,Node())
 return n

def write_node(n,out):
 out.write(struct.pack('<qi',n.pos,len(n.kids)))
 for key,child in sorted(n.kids.items()):out.write(struct.pack('<i',key));write_node(child,out)

def write_container(path,root):
 # La taille de l'arbre est indépendante de ses positions ; une première
 # sérialisation réserve exactement sa place.
 temp=io.BytesIO();write_node(root,temp);position=temp.tell();blobs=[];seen={}
 for _,n in walk(root):
  if n.payload is None:n.pos=0;continue
  digest=hashlib.sha256(n.payload).digest()
  if digest in seen:
   assert seen[digest][1]==n.payload
   n.pos=seen[digest][0]
  else:
   n.pos=position;seen[digest]=(position,n.payload);blobs.append(n.payload);position+=len(n.payload)
 out=io.BytesIO();write_node(root,out);assert out.tell()==temp.tell()
 for b in blobs:out.write(b)
 path.write_bytes(out.getvalue())

def fallback(root,form,skin,gender):
 n=root;best=n.payload
 f=n.kids.get(form)
 if f:
  if f.payload is not None:best=f.payload
  for sk in range(skin,-1,-1):
   if sk in f.kids:
    k=f.kids[sk]
    if k.payload is not None:best=k.payload
    g=k.kids.get(gender)
    if g and g.payload is not None:best=g.payload
    break
 return best

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--base',type=Path,required=True,help='Répertoire Content de la base PMDO')
 ap.add_argument('--converted',type=Path,required=True,help='Répertoire Content du convertisseur PMDO natif')
 ap.add_argument('--out',type=Path,required=True,help='Répertoire Content de la Quest')
 ap.add_argument('--targets',type=Path,required=True,help='Correspondances privées espèce/forme')
 ap.add_argument('--report',type=Path,required=True);args=ap.parse_args()
 targets=json.loads(args.targets.read_text(encoding='utf-8'));assert len(targets)==141
 by_dex={}
 for t in targets:by_dex.setdefault(t['dex'],[]).append(t)
 report={'base_inchangee':True,'conteneurs':[],'cibles':len(targets),'remarque':'Les fiches remplacées restent dans base ; les formes, skins et nœuds non ciblés sont conservés dans la Quest.'}
 for kind,ext in [('Chara','chara'),('Portrait','portrait')]:
  outdir=args.out/kind;outdir.mkdir(parents=True,exist_ok=True);index=Node()
  paths=sorted((args.converted/kind).glob('*.'+ext),key=lambda p:int(p.stem))
  assert set(int(p.stem) for p in paths)==set(by_dex),(kind,len(paths),len(by_dex))
  for converted in paths:
   dex=int(converted.stem);original=args.base/kind/converted.name
   assert original.exists(),original
   base=load_container(original,kind);incoming=load_container(converted,kind);merged=copy_node(base);merge(merged,incoming)
   # Explicit gender fallbacks make sure an older destination-specific gender
   # node cannot silently supersede the imported normal sprite/portrait.
   modified_paths=set()
   for t in by_dex[dex]:
    f=t['forme'];imp=node_at(incoming,(f,0));assert imp and imp.payload,(kind,t)
    normal=imp.payload;female=node_at(incoming,(f,0,2));female=female.payload if female and female.payload is not None else normal
    for gender,payload in ((0,normal),(1,normal),(2,female)):
     ensure(merged,(f,0,gender)).payload=payload
     modified_paths.add((f,0,gender))
    for gender,payload in ((0,normal),(1,normal),(2,female)):
     assert fallback(merged,f,0,gender)==payload
   for path,n in walk(incoming):
    if n.payload is not None:modified_paths.add(path)
   # Verify every pre-existing payload outside intentionally overwritten paths.
   kept=0;changed=0
   for path,n in walk(base):
    new=node_at(merged,path);assert new is not None
    if n.payload is not None:
     if path not in modified_paths:assert new.payload==n.payload,(kind,dex,path);kept+=1
     else:changed+=1
   dst=outdir/converted.name;write_container(dst,merged)
   reloaded=load_container(dst,kind)
   for path,n in walk(merged):
    again=node_at(reloaded,path);assert again is not None and again.payload==n.payload,(kind,dex,path)
   for t in by_dex[dex]:
    f=t['forme'];imp=node_at(incoming,(f,0));female=node_at(incoming,(f,0,2))
    for gender in (0,1,2):
     want=female.payload if gender==2 and female and female.payload is not None else imp.payload
     assert fallback(reloaded,f,0,gender)==want,(kind,dex,f,gender)
   index.kids[dex]=reloaded
   report['conteneurs'].append({'type':kind,'dex':dex,'anciens_noeuds_preserves':kept,'noeuds_cibles_remplaces':changed,
                                'sortie_sha256':hashlib.sha256(dst.read_bytes()).hexdigest()})
  f=io.BytesIO();write_node(index,f);(outdir/'index.idx').write_bytes(f.getvalue())
  print(kind,len(paths),'conteneurs fusionnés ; index profond écrit',flush=True)
 args.report.parent.mkdir(parents=True,exist_ok=True);args.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

if __name__=='__main__':main()
