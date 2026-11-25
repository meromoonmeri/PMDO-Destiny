#!/usr/bin/env python3
"""Place the comparison film above the room atlas. Both video codecs and the poster are embedded."""
from pathlib import Path
import base64,json,os

S=Path(__file__).resolve().parent;O=S.parent;G=O.parent;A=G/'Guilde-Destiny-Lumiere-Ancree.html';W=Path.home()/'.cache/lumiere-braseros';MARK='<script id="donnees" type="application/json">'
BASE=Path(os.environ.get('DESTINY_ATLAS_STAGE',W/'Lueur-Tamisee-sans-video.html'))

def asset(f,mime):return 'data:'+mime+';base64,'+base64.b64encode((O/f).read_bytes()).decode('ascii')
def swap(s,a,b):assert s.count(a)==1,a;return s.replace(a,b,1)

STYLE='''
.video-demo{display:grid;grid-template-columns:minmax(220px,.7fr) minmax(0,1.8fr);gap:clamp(13px,2vw,32px);align-items:center;padding:clamp(11px,1.6vw,23px);margin:0 0 13px;background:linear-gradient(116deg,#243028,#1a2321 72%);border-color:#435343}
.video-intro h2{font:500 clamp(24px,2.5vw,36px)/1.1 var(--display);color:#f8ecd9;margin:6px 0 9px;letter-spacing:-.025em}
.video-intro p{color:#c2c9c0;font-size:13px;line-height:1.5;margin:0 0 11px}
.movie-controls{display:flex;align-items:center;gap:8px;flex-wrap:wrap}
#film-button{border-color:#b59154;color:#322619;background:#edc785}
#film-button:hover{background:#ffe1a4}
#film-button:disabled{opacity:.5}
.film-note{font:11px var(--mono);color:#bfc4b4}
.video-demo figure{margin:0;width:100%;max-width:865px;min-width:0;justify-self:center}
.video-demo video{display:block;aspect-ratio:2/1;width:100%;max-height:404px;object-fit:contain;border:1px solid #6f6a53;border-radius:8px;background:#101615}
.video-demo figcaption{font-size:11px;color:#b9c4b7;margin:6px 2px 0}
#film-issue{color:#eed6ad;margin-top:8px}
@media(max-width:695px){.video-demo{grid-template-columns:1fr;gap:9px}.video-intro h2{font-size:23px;margin:4px 0}.video-intro p{font-size:12px;margin-bottom:7px}#film-button{min-height:32px;font-size:12px}.video-demo video{border-radius:6px}}
'''
PANEL='''  <section class="panel video-demo" id="comparatif-video" aria-labelledby="film-title">
    <div class="video-intro">
      <span class="micro">VIDÉO INTÉGRÉE · 10 SECONDES</span>
      <h2 id="film-title">Les deux foyers en mouvement</h2>
      <p><b>À gauche</b>, la boucle originale des braseros de Grodoudou. <b>À droite</b>, la nouvelle lueur tamisée de Destiny. Regarde le bois au pied des lianes, près des fenêtres.</p>
      <div class="movie-controls"><button class="soft" type="button" id="film-button" aria-controls="film-comparatif"><svg aria-hidden="true"><use href="#i-play-motion"/></svg><span>Lire la vidéo</span></button><span class="film-note">Sans son · en boucle</span></div>
      <p id="film-issue" role="status" hidden>La lecture vidéo n’est pas disponible ici. Le bouton « Référence Grodoudou » permet aussi de voir la boucle originale.</p>
    </div>
    <figure>
      <video id="film-comparatif" aria-label="Comparatif vidéo : les braseros de Grodoudou et les bourgeons de Destiny" controls loop muted playsinline preload="metadata" width="1120" height="560"></video>
      <figcaption>Chambre de Grodoudou <span aria-hidden="true">↔</span> Grand Salon de Destiny · mode Nuit, détail agrandi.</figcaption>
    </figure>
  </section>
'''
CODE='''
const film=$('film-comparatif'),filmButton=$('film-button'),filmPanel=$('comparatif-video');
film.poster=data.film.poster;
film.muted=true;
for(const [src,type] of [[data.film.webm,'video/webm'],[data.film.mp4,'video/mp4']]){
  const source=make('source');source.type=type;source.src=src;film.append(source);
}
function filmState(){
  const active=!film.paused&&!film.ended;filmButton.querySelector('span').textContent=active?'Mettre en pause':'Lire la vidéo';
  filmButton.querySelector('use').setAttribute('href',active?'#i-pause-motion':'#i-play-motion');
}
film.addEventListener('playing',()=>{$('film-issue').hidden=true;filmState();});
film.addEventListener('pause',filmState);film.addEventListener('ended',filmState);
filmButton.onclick=async()=>{
  if(!film.paused){film.pause();return;}
  try{await film.play();}catch{filmState();$('film-issue').hidden=false;}
};
function updateFilm(){
  filmPanel.hidden=s.page!=='atlas';
  if(filmPanel.hidden)film.pause();
}
$('braseros-reference').addEventListener('click',()=>film.pause());
document.addEventListener('visibilitychange',()=>{if(document.hidden)film.pause();});
'''

def main():
 old=BASE.read_text(encoding='utf8')
 head,body=old.split(MARK,1);dstr,tail=body.split('</script>',1);d=json.loads(dstr);assert 'film' not in d
 d['film']=dict(webm=asset('Grodoudou-et-Destiny.webm','video/webm'),mp4=asset('Grodoudou-et-Destiny.mp4','video/mp4'),poster=asset('Grodoudou-et-Destiny.webp','image/webp'))
 head=swap(head,'</style>',STYLE+'\n</style>')
 head=swap(head,'  <section id="atlas-page"',PANEL+'  <section id="atlas-page"')
 tail=swap(tail,'  $(\'editor\').hidden=!atelier;$(\'atlas-page\').hidden=atelier;',"  $('editor').hidden=!atelier;$('atlas-page').hidden=atelier;updateFilm();")
 tail=swap(tail,'setupAtlas();updatePalette();refresh();setupMotion();',CODE+'\nsetupAtlas();updatePalette();refresh();setupMotion();')
 out=head+MARK+json.dumps(d,separators=(',',':'),ensure_ascii=False).replace('</','<\\/')+'</script>'+tail
 staged=A.with_suffix('.tmp');staged.write_text(out,encoding='utf8');staged.replace(A);print(f'PASS · vidéo au-dessus des cartes · HTML autonome {A.stat().st_size:,} o',flush=True)
if __name__=='__main__':main()
