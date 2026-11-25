#!/usr/bin/env python3
"""Publier exclusivement le correctif audité, après autorisation explicite.
Le jeton est lu dans DESTINY_TOKEN uniquement ; il n'est ni affiché ni écrit.
N'utilise aucune sauvegarde ou données locales non vérifiées.
"""
from pathlib import Path
import base64,hashlib,json,os,sys,zipfile,requests
R=Path(__file__).resolve().parent; archive=R/'correctif-herbe-et-chemins-Reverie-0.5.0-ESSAI.zip';token=os.environ.get('DESTINY_TOKEN')
if not token:sys.exit('Accès manquant : configurer DESTINY_TOKEN par un mécanisme sécurisé, puis relancer. Aucun push effectué.')
if not archive.exists():sys.exit('Archive absente : reconstruire le correctif et le vérifier avant de publier.')
expected='61a0812aa4c8318a59ed7a22ddcf764668881b5beb7252a992f7772c3b3ee7e7'
if hashlib.sha256(archive.read_bytes()).hexdigest()!=expected:sys.exit('Archive différente de la version auditée : abandon.')
base='a2db214dc89e675347f670f26594df92158fc9d9';branch='wip/reverie-integration-kingambit-cafe';repo='https://api.github.com/repos/meromoonmeri/PMDO-Destiny'
s=requests.Session();s.headers.update({'Authorization':'Bearer '+token,'Accept':'application/vnd.github+json','User-Agent':'Reverie-Herbe-Audit','X-GitHub-Api-Version':'2022-11-28'})
def req(method,path,data=None):
 r=s.request(method,repo+path,json=data,timeout=180)
 if not r.ok:raise RuntimeError(f'{method} {path} : HTTP {r.status_code} ; arrêt sans exposer de données de connexion')
 return r.json() if r.content else {}
ref='/git/ref/heads/'+branch
if req('GET',ref)['object']['sha']!=base:sys.exit('La branche a avancé depuis la base auditée : interrompu, réaudit nécessaire.')
main=req('GET','/git/ref/heads/main')['object']['sha'];tree=req('GET','/git/commits/'+base)['tree']['sha'];files=[]
with zipfile.ZipFile(archive) as z:
 if z.testzip():sys.exit('Archive incorrecte.')
 for name in z.namelist():
  if name.startswith('payload/') and name.endswith('.rsground.gz') or name=='game/Content/Tile/Reverie_Herbe_Chemins_050.tile' or name=='art/reverie/tilesheets/Reverie_Herbe_Chemins_050.png':files.append((name,z.read(name)))
assert len(files)==12 and sum(n.startswith('payload/') for n,_ in files)==10
entries=[]
for name,data in files:
 blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest();result=req('POST','/git/blobs',{'content':base64.b64encode(data).decode(),'encoding':'base64'});assert result['sha']==blob
 entries.append({'path':name,'mode':'100644','type':'blob','sha':blob});print('Fichier vérifié :',name,flush=True)
for i in range(0,len(entries),8):tree=req('POST','/git/trees',{'base_tree':tree,'tree':entries[i:i+8]})['sha']
if req('GET',ref)['object']['sha']!=base or req('GET','/git/ref/heads/main')['object']['sha']!=main:sys.exit('Références modifiées en cours de préparation : pas de push.')
commit=req('POST','/git/commits',{'message':'Reverie: fix local grass and path seams','tree':tree,'parents':[base]})['sha']
r=req('PATCH','/git/refs/heads/'+branch,{'sha':commit,'force':False});assert r['object']['sha']==commit and req('GET',ref)['object']['sha']==commit
print('Push vérifié sur',branch,':',commit,'; main initial :',main,flush=True)
print('La CI doit encore être vérifiée sur https://github.com/meromoonmeri/PMDO-Destiny/actions',flush=True)
