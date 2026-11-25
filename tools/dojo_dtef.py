"""Arenas Kingambit : tableaux originaux, références exactes aux cellules DTEF PMDO.

Le format de lecture est celui de projet-creation-pmdo : 6×8 cases par famille
(paroi / secondaire / sol), 24 px, 47 masques d'adjacence, une case vide.
Aucun PNG généré, redimensionné ou recoloré dans la carte de labyrinthe.
"""
from collections import deque
from functools import lru_cache
import hashlib
import json
from pathlib import Path

from PIL import Image
from lib_tiles import read_tilesheet

WIDTH, HEIGHT, TILE = 15, 11, 24
START, BOSS = (7, 8), (7, 3)
KINDS = ('wall', 'secondary', 'floor')
SLOTS = (137,155,19,9,10,3,205,255,55,5,0,6,76,110,38,12,1,-1,63,207,11,8,15,2,159,111,
         14,13,4,7,127,239,77,39,27,139,191,223,141,23,46,78,143,31,79,47,95,175)
SLOT_OF = {m:i for i,m in enumerate(SLOTS) if m>=0}
CARDINALS = ((0,1),(-1,0),(0,-1),(1,0))
DIAGONALS = ((-1,1),(-1,-1),(1,-1),(1,1))

# (left, right) inclusifs pour les rangées 1 à 9 ; les îlots et poches
# secondaires sont séparés du trajet principal. N = Nord, S = arrivée.
PLANS = {
    'normal': ('Claire-voie', ((6,8),(4,10),(3,11),(2,12),(1,13),(1,13),(2,12),(3,11),(5,9)), ''),
    'fire': ('Caldeira fendue', ((7,8),(6,9),(4,11),(3,11),(3,12),(2,12),(2,11),(4,11),(5,9)),
             '2,2 3,2 2,3 2,4 1,4 12,3 13,3 13,4 13,5 13,6'),
    'water': ('Deux anses', ((4,10),(3,11),(3,11),(4,10),(5,9),(4,10),(3,11),(2,12),(5,9)),
              '1,3 2,3 1,4 2,4 3,4 1,5 2,5 3,5 4,5 1,6 2,6 3,6 11,4 12,4 13,4 10,5 11,5 12,5 13,5 11,6 12,6 13,6'),
    'grass': ('Croisée des racines', ((2,11),(2,11),(3,10),(4,10),(4,10),(3,11),(2,12),(2,12),(3,11)), ''),
    'electric': ('Corniche en zigzag', ((4,7),(3,9),(3,11),(4,12),(5,13),(4,13),(3,12),(2,10),(4,9)), ''),
    'ice': ('Glacis à deux pointes', ((3,11),(2,12),(2,12),(3,11),(4,10),(3,11),(2,12),(3,11),(6,8)),
            '1,5 2,5 3,5 1,6 2,6 11,5 12,5 13,5 12,6 13,6'),
    'fighting': ('Cour creusée', ((4,10),(4,10),(4,10),(2,12),(1,13),(1,13),(2,12),(3,11),(4,10)), ''),
    'poison': ('Mare des spores', ((5,9),(4,10),(3,11),(2,12),(2,12),(3,12),(3,11),(4,10),(5,9)),
               '1,4 1,5 2,6 1,6 1,7 2,7 12,2 13,2 12,3 13,3 13,4 4,5 10,6'),
    'ground': ('Sillons', ((3,9),(2,11),(2,11),(3,12),(3,13),(4,13),(3,12),(2,11),(4,9)),
               '1,4 2,4 1,5 2,5 1,6 2,6 3,6 12,8 13,8 11,9 12,9 13,9'),
    'flying': ('Éperon', ((6,9),(5,11),(4,13),(3,13),(2,12),(1,11),(1,10),(2,10),(4,9)),
               '11,6 12,6 13,6 11,7 12,7 13,7 11,8 12,8 13,8 10,9 11,9 12,9 13,9'),
    'psychic': ('Facettes', ((6,8),(4,10),(3,11),(2,12),(1,13),(2,12),(3,11),(4,10),(4,10)),
                '1,3 2,3 1,4 12,7 13,7 11,8 12,8 13,8'),
    'bug': ('Clairière des cocons', ((2,12),(2,12),(3,11),(4,10),(4,10),(3,11),(3,11),(3,11),(4,10)), ''),
    'rock': ('Mégalithes', ((3,11),(2,12),(2,12),(2,12),(3,11),(3,11),(2,12),(2,12),(4,10)),
             '1,5 2,5 12,5 13,5'),
    'ghost': ('Galerie brisée', ((3,11),(3,11),(3,11),(2,12),(2,12),(2,12),(3,11),(4,10),(4,10)),
              '2,2 12,2 1,4 13,4 1,5 13,5 1,6 13,6'),
    'dragon': ('Antre en tenaille', ((3,11),(2,12),(3,11),(4,11),(3,12),(2,13),(2,12),(3,11),(4,10)), ''),
    'dark': ('Trouée en croissant', ((2,9),(2,10),(2,11),(3,12),(4,13),(5,13),(4,12),(3,11),(2,9)), ''),
    'steel': ('Doubles gradins', ((5,9),(4,10),(3,11),(3,11),(1,13),(1,13),(3,11),(3,11),(5,9)),
              '1,3 2,3 1,4 2,4 12,3 13,3 12,4 13,4 1,7 2,7 1,8 2,8 12,7 13,7 12,8 13,8'),
    'fairy': ('Clairière des lucioles', ((5,11),(3,12),(3,12),(2,11),(2,11),(3,12),(4,12),(4,10),(5,9)),
              '1,3 2,3 1,4 1,5 12,5 13,5 13,6'),
}


def plan(typ):
    _, spans, accents = PLANS[typ]
    a = [['#']*WIDTH for _ in range(HEIGHT)]
    for y, (l, r) in enumerate(spans, 1):
        for x in range(l,r+1):
            a[y][x] = '.'
    for coord in accents.split():
        x,y = map(int,coord.split(','))
        a[y][x] = '~'
    return tuple(''.join(row) for row in a)


def libre(x,y,typ='normal'):
    return 0<=x<WIDTH and 0<=y<HEIGHT and plan(typ)[y][x]=='.'


def verifier(grille):
    assert len(grille)==HEIGHT and all(len(r)==WIDTH for r in grille)
    assert all(grille[y][x]=='#' for y in range(HEIGHT) for x in range(WIDTH)
               if y in (0,HEIGHT-1) or x in (0,WIDTH-1))
    floor = {(x,y) for y,row in enumerate(grille) for x,c in enumerate(row) if c=='.'}
    assert len(floor)>=53 and {START,BOSS,(6,8),(8,8),(7,9),(6,3),(8,3)}<=floor
    seen={START}; q=deque(seen)
    while q:
        x,y=q.popleft()
        for dx,dy in CARDINALS:
            xy=(x+dx,y+dy)
            if xy in floor and xy not in seen:
                seen.add(xy);q.append(xy)
    assert seen==floor, floor-seen


def voisinage(grille,x,y):
    cible=grille[y][x]
    def meme(dx,dy):
        nx,ny=x+dx,y+dy
        return 0<=nx<WIDTH and 0<=ny<HEIGHT and grille[ny][nx]==cible or (
            cible=='#' and not(0<=nx<WIDTH and 0<=ny<HEIGHT))
    bits=[meme(*d) for d in CARDINALS]
    mask=sum(1<<i for i,b in enumerate(bits) if b)
    for i,d in enumerate(DIAGONALS):
        if bits[i] and bits[(i+1)%4] and meme(*d): mask |= 1<<(4+i)
    assert mask in SLOT_OF
    return mask


def loc(x,y):
    return {'X': x, 'Y': y}


def cell(layers=()):
    return {'AutoTileset':'','Associates':[],'Layers':list(layers),'NeighborCode':-1}


class Dtef:
    def __init__(self,data,content=None):
        self.data=Path(data);self.content=Path(content) if content is not None else self.data.parent/'Content'

    @lru_cache(maxsize=None)
    def source(self, biome, kind):
        p=self.data/'AutoTile'/f'{biome}_{kind}.json'
        o=json.loads(p.read_text(encoding='utf-8-sig'))['Object']['Tiles']
        assert o['$type'].startswith('RogueEssence.Dungeon.AutoTileAdjacent,'), o['$type']
        return o

    def variants(self,biome,kind,code):
        return self.source(biome,kind)[f'Tilex{code:02X}']

    def case(self,biome,kind,code,x,y):
        alts=self.variants(biome,kind,code)
        assert alts, (biome,kind,code,x,y)
        # Variantes stables, pas de motif diagonal par simple modulo x+y.
        k=int.from_bytes(hashlib.blake2s(f'{biome}:{kind}:{x}:{y}'.encode(),digest_size=4).digest(),'little')
        return cell(alts[k%len(alts)])

    def arene(self,typ,biome):
        g=plan(typ);verifier(g)
        for i,name in [(-1,'Sol DTEF continu'),(0,'Parois DTEF'),(0,'Relief secondaire DTEF')]:
            kind={'Sol DTEF continu':'floor','Parois DTEF':'wall','Relief secondaire DTEF':'secondary'}[name]
            layer=[]
            for x in range(WIDTH):
                column=[]
                for y in range(HEIGHT):
                    mark=g[y][x]
                    if kind=='floor':
                        # Sol complet, même sous une cellule de paroi partiellement transparente.
                        c=self.case(biome,kind,255,x,y)
                    elif mark==('#' if kind=='wall' else '~'):
                        c=self.case(biome,kind,voisinage(g,x,y),x,y)
                    else:
                        c=cell()
                    column.append(c)
                layer.append(column)
            yield {'Name':name,'Layer':i,'Visible':True,'Tiles':layer}

    @lru_cache(maxsize=None)
    def bank(self,sheet):
        assert sheet and '/' not in sheet and '\\' not in sheet
        s,b=read_tilesheet(self.content/'Tile'/f'{sheet}.tile')
        assert s==TILE
        return b

    def image(self, f):
        return self.bank(f['Sheet'])[f['TexLoc']['X'], f['TexLoc']['Y']]

    def apercu(self, layers, tick=0):
        im=Image.new('RGBA',(WIDTH*TILE,HEIGHT*TILE))
        for layer in layers:
            for x,col in enumerate(layer['Tiles']):
                for y,c in enumerate(col):
                    for l in c['Layers']:
                        frames=l['Frames'];f=frames[(tick//l['FrameLength'])%len(frames)]
                        if f['Sheet']: im.alpha_composite(self.image(f),(x*TILE,y*TILE))
        assert im.getchannel('A').getextrema()==(255,255), 'sol incomplet'
        return im

    def export_dtef(self, biome, destination):
        """Écrit les vraies planches DTEF, y compris les pistes indépendantes."""
        sheets={f'tileset_{v}.png':Image.new('RGBA',(432,192)) for v in range(3)}
        records=[];groups={}
        for i,kind in enumerate(KINDS):
            for slot,mask in enumerate(SLOTS):
                if mask<0: continue
                x,y=(i*6+slot%6)*TILE, (slot//6)*TILE
                for v,tracks in enumerate(self.variants(biome,kind,mask)):
                    assert v<3,(biome,kind,mask)
                    for li,track in enumerate(tracks):
                        frames=track['Frames'];ticks=track['FrameLength']
                        if li==0: assert len(frames)==1
                        else:
                            group=groups.setdefault((kind,li,len(frames),ticks),len(groups))
                        for fi,f in enumerate(frames):
                            if not f['Sheet']:continue
                            file=f'tileset_{v}.png' if not li else f'tileset_{v}_frame{group}_{fi}.{ticks}.png'
                            if file not in sheets:sheets[file]=Image.new('RGBA',(432,192))
                            sheets[file].paste(self.image(f),(x,y))
                            records.append(dict(fichier=file,source=f,xy=[x,y],kind=kind,mask=mask,variante=v,calque=li,frame=fi,ticks=ticks))
        destination.mkdir(parents=True,exist_ok=True)
        for record in records:
            x,y=record['xy']; im=sheets[record['fichier']].crop((x,y,x+TILE,y+TILE))
            assert im.tobytes()==self.image(record['source']).tobytes(),record
        for file,sheet in sheets.items():sheet.save(destination/file,optimize=True)
        (destination/'cellules.json').write_text(json.dumps(dict(biome=biome,taille=TILE,ordre=KINDS,masques=SLOTS,cellules=records),ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
        return len(sheets),len(records)

    def provenance(self,biome):
        sources=set()
        for kind in KINDS:
            for mask in SLOT_OF:
                for alt in self.variants(biome,kind,mask):
                    sources.update(f['Sheet'] for lay in alt for f in lay['Frames'] if f['Sheet'])
        return {s:hashlib.sha256((self.content/'Tile'/f'{s}.tile').read_bytes()).hexdigest() for s in sorted(sources)}


if __name__=='__main__':
    import argparse
    from dojo_reverie_types import TYPES
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--donnees',type=Path,required=True)
    p.add_argument('--biome',choices=[t[3] for t in TYPES],required=True)
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args(); n,c=Dtef(a.donnees).export_dtef(a.biome,a.out)
    print(f'{a.biome} : {n} feuilles DTEF, {c} cellules et poses exactes.')
