#!/usr/bin/env python3
"""Assembler le lecteur HTML autonome à partir des trois MP4 rendus."""
from pathlib import Path
from base64 import b64encode
import io
import json
import subprocess as sp
from PIL import Image
from rendre import TAKES

HERE = Path(__file__).resolve().parent
OUT = HERE.parent
DATA = [
    dict(short='Compacte', affinity='La plus proche de Deeshura',
         detail='Des anneaux violets se resserrent sur Dracaufeu. L’orbe blanc masque le changement de forme ; l’étoile s’ouvre à l’horizontale et laisse place à l’emblème Guildhouse.',
         steps=[(.17,'Anneaux convergents'),(1.70,'Changement sous l’orbe'),(1.80,'Éclat et révélation')],
         tag='Pour un combat qui repart vite.', reason='La plus courte des trois.'),
    dict(short='Cristalline', affinity='Guildhouse V2 × Deeshura',
         detail='La charge de Deeshura nourrit la sphère arc-en-ciel de ta V2. Elle tourne, se fissure, puis un éclat bleu accompagne la chute des fragments autour de Méga-Dracaufeu X.',
         steps=[(.65,'Formation de la sphère'),(1.93,'Changement sous la coque'),(2.63,'Éclatement et révélation')],
         tag='Ma recommandation.', reason='On reconnaît le mieux ta V2, sans les colonnes.'),
    dict(short='Cyan / rose', affinity='Une signature pour Méga X',
         detail='Deux traînées cyan et rose se croisent devant et derrière Dracaufeu. La spirale devient bleu nuit ; un iris de lumière s’ouvre sur les côtés au lieu du grand flash blanc.',
         steps=[(.16,'Orbites croisées'),(2.03,'Changement sous l’éclipse'),(2.17,'Ouverture latérale')],
         tag='Pour un Méga-Dracaufeu X plus singulier.', reason='La silhouette reste au centre.'),
]


def uri(b, mime):
    return 'data:'+mime+';base64,'+b64encode(b).decode('ascii')


def jpg(im, quality=90):
    f=io.BytesIO();im.save(f,format='JPEG',quality=quality,optimize=True);return f.getvalue()


def main():
    data=[]
    for t,d in zip(TAKES,DATA):
        p=OUT/(t.slug+'.mp4')
        b=sp.check_output(['ffmpeg','-hide_banner','-loglevel','error','-ss',str(t.gallery),'-i',str(p),
                           '-frames:v','1','-f','image2pipe','-codec:v','png','-'])
        still=Image.open(io.BytesIO(b)).convert('RGB')
        assert still.size==(896,576)
        thumb=still.crop((208,127,688,500)).resize((160,124),Image.Resampling.LANCZOS)
        data.append(dict(d,title=t.title,duration=t.nsec,color='#'+bytes(t.accent).hex(),
                         video=uri(p.read_bytes(),'video/mp4'),
                         poster=uri(jpg(still),'image/jpeg'),thumb=uri(jpg(thumb,92),'image/jpeg')))
    out=OUT/'Comparer-les-3-versions.html'
    model=(HERE/'modele-comparateur.html').read_text(encoding='utf-8')
    assert model.count('__TAKES_JSON__')==1
    body=model.replace('__TAKES_JSON__',json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c'))
    out.write_text(body,encoding='utf-8')
    print(out.name, out.stat().st_size, 'octets, trois vidéos et six images embarquées')


if __name__=='__main__':main()
