#!/usr/bin/env python3
"""Fetch only the 0.7.7 Cliff entries, or read a locally supplied Windows ZIP."""
import argparse,hashlib,io,json,re,urllib.request,zipfile,zlib
from pathlib import Path
from Falaise import W,A,P
F=Path.home()/'.cache/fenetres-jeu-destiny'
URL='https://github.com/meromoonmeri/PMDO-Destiny/releases/download/v0.7.7/PMDO-Destiny-Windows-x64-0.7.7.zip'
SIZE=1_341_244_828;LIMIT=20*1024*1024;PREFIX='PMDO-Destiny/'

class HttpZip(io.RawIOBase):
    def __init__(self):
        self.pos=0;self.downloaded=0;self.url=URL;self.cache={};self.reg=[]
        for d in (F/'ranges',W/'ranges'):
            for p in d.glob('*.bin'):
                if m:=re.fullmatch(r'(\d+)-(\d+)\.bin',p.name):
                    l,r=map(int,m.groups());self.reg.append((l,r+1,p))
    def seekable(self):return True
    def readable(self):return True
    def tell(self):return self.pos
    def seek(self,n,where=io.SEEK_SET):
        val=n+{io.SEEK_SET:0,io.SEEK_CUR:self.pos,io.SEEK_END:SIZE}[where]
        if val<0:raise OSError('position hors archive')
        self.pos=val;return val
    def part(self,a,b):
        for x,y,p in self.reg:
            if x<=a and y>=b and p.stat().st_size==y-x:
                with p.open('rb') as h:h.seek(a-x);return h.read(b-a)
        if not 0<b-a<=LIMIT-self.downloaded:raise OSError('Quota de lecture sélective dépassé ; fournis le ZIP avec --zip.')
        key=f'{a}-{b-1}';req=urllib.request.Request(self.url,headers={'Range':f'bytes={key}','Accept-Encoding':'identity','User-Agent':'Destiny-Cliff-Preview/1'})
        with urllib.request.urlopen(req,timeout=18) as r:
            if r.status!=206 or r.headers.get('Content-Range')!=f'bytes {key}/{SIZE}':raise OSError('Le serveur ne sert pas la plage du ZIP demandée. Utilise --zip.')
            data=r.read(b-a+1);self.url=r.url
        if len(data)!=b-a:raise OSError('Plage incomplète.')
        dst=W/'ranges'/f'{key}.bin';dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(data);self.reg.append((a,b,dst));self.downloaded+=len(data)
        return data
    def read(self,n=-1):
        a=self.pos;b=SIZE if n<0 else min(SIZE,a+n)
        if a>=b:return b''
        for (l,r),z in self.cache.items():
            if l<=a and b<=r:self.pos=b;return z[a-l:b-l]
        end=min(SIZE,max(b,a+65536));raw=self.part(a,end);self.cache[a,end]=raw;self.pos=b;return raw[:b-a]


def main():
    p=argparse.ArgumentParser();p.add_argument('--zip',type=Path,help='copie locale du ZIP Windows PMDO-Destiny 0.7.7');args=p.parse_args()
    if args.zip and args.zip.stat().st_size!=SIZE:p.error('taille différente du ZIP de publication Windows 0.7.7')
    def checked(z,n):
        i=z.getinfo(PREFIX+n);dst=A/n
        for parent in (A,F/'windows-077',F/'runtime-077'):
            q=parent/n
            if q.is_file() and q.stat().st_size==i.file_size:
                b=q.read_bytes()
                if zlib.crc32(b)==i.CRC:return b
        return z.read(i)
    with zipfile.ZipFile(args.zip or HttpZip()) as z:
        files=set()
        for phase in P:
            name=f'Data/Ground/guilde_cliff_{phase}.rsground';doc=json.loads(checked(z,name).decode('utf-8-sig'))['Object'];assert doc['AssetName']==f'guilde_cliff_{phase}';files.add(name)
            for l in doc['Layers']:
                files.update('Content/Tile/'+r['Sheet']+'.tile' for sub in l['Tiles'] for c in sub for t in c['Layers'] for r in t['Frames'] if r['Sheet'])
            for l in doc['Background']['Layers']:
                files.add('Content/BG/'+l['BG']['BGAnim']['AnimIndex']+'.dir')
            for l in doc['Decorations']:
                for r in l['Anims']:files.add('Content/Object/'+r['ObjectAnim']['AnimIndex']+'.dir')
        assert len(files)==39
        rows=[]
        for n in sorted(files):
            i=z.getinfo(PREFIX+n);dst=A/n;dst.parent.mkdir(parents=True,exist_ok=True);raw=checked(z,n)
            assert len(raw)==i.file_size and zlib.crc32(raw)==i.CRC
            if not dst.is_file() or dst.read_bytes()!=raw:dst.write_bytes(raw)
            rows.append(dict(fichier=n,octets=len(raw),crc32=f'{i.CRC:08x}',sha256=hashlib.sha256(raw).hexdigest()))
    (W/'Provenance-cliff.json').write_text(json.dumps(dict(version='0.7.7',archive=URL,fichiers=rows),indent=2)+'\n');print(len(rows),'ressources Cliff authentifiées dans le ZIP Windows')

if __name__=='__main__':main()
