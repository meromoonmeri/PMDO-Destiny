(() => {
  'use strict';
  const data = JSON.parse(document.getElementById('atlas-data').textContent), $ = id => document.getElementById(id);
  const byView = ['base','states','demo'];
  const canvas = $('paper'), context = canvas.getContext('2d', {alpha:false}), scratch = document.createElement('canvas');
  [scratch.width,scratch.height] = data.taille_carte;
  const sctx = scratch.getContext('2d', {alpha:false});
  const fadeOut = data.voile_noir_sortie_ticks, fadeIn = data.voile_noir_entree_ticks, hold = data.delai_objets_ticks;
  const run = data.compteur_objets_ticks, total = fadeOut+run, freq = data.rafraichissement_hz;
  const states = data.etats, poses = data.poses;
  const load = (url) => new Promise((yes,no)=>{const i=new Image();i.onload=()=>yes(i);i.onerror=no;i.src=url;});
  let base, fixed, sprites, view='base', level=1, target=2, tick=0, crop=false, timer=0, playing=false;
  const marker = () => data.transitions[target-2].camera_test;
  const clamp = (value, min, max) => Math.max(min,Math.min(value,max));
  const buttons = $('level-buttons');
  const tab = [...document.querySelectorAll('[data-vue]')];
  $('png').href=data.fond;
  for (let i=1;i<=8;i++){
    const b = document.createElement('button');b.textContent=i;b.type='button';b.setAttribute('aria-label',`Palier ${i}`);b.dataset.n=i;
    b.addEventListener('click',()=>{level=i;draw();});buttons.append(b);
  }
  const selectView = (v) => {
    if (!byView.includes(v)) return;
    stop();view=v;
    if (v==='base') crop=false;
    byView.forEach(x=>$(`details-${x}`).hidden=x!==v);
    tab.forEach(b=>b.setAttribute('aria-pressed',b.dataset.vue===v));
    $('viewport').hidden=v!=='demo';
    draw();
  };
  const resize = (w,h) => {
    if (w!==canvas.width||h!==canvas.height){canvas.width=w;canvas.height=h;}
    context.imageSmoothingEnabled=false;
  };
  function sprite(part, t){
    const at=Math.max(0,t-hold), a=data.sequences[part.sequence][0], meta=poses[a.pose];
    const [vX,vY]=part.vitesse_8_8, [x,y]=part.origine, [ox,oy]=meta.coin_relatif;
    sctx.drawImage(sprites[a.pose],Math.trunc(x + at*vX/256) + ox,Math.trunc(y + at*vY/256) + oy);
  }
  function black(n){
    // The game uses a screen-brightness ramp; emulate its 16 levels, not a dissolve of the cloud pixels.
    sctx.fillStyle=`rgba(0,0,0,${clamp(n,0,16)/16})`;sctx.fillRect(0,0,scratch.width,scratch.height);
  }
  function draw(){
    if(!base)return;
    const framed = view==='demo' && crop;
    canvas.classList.toggle('study',view!=='base');canvas.classList.toggle('ds',framed);
    $('viewport').setAttribute('aria-pressed',framed);
    if(view==='base'){
      resize(base.width,base.height);context.drawImage(base,0,0);
      $('image-caption').textContent='PNG original · Dépôt PMDO';
      canvas.setAttribute('aria-label','Parchemin nu, sans relief, sans lieu et sans nuages mobiles');
    }else{
      const [w,h]=data.taille_carte;
      sctx.imageSmoothingEnabled=true;sctx.drawImage(base,0,0,w,h);sctx.imageSmoothingEnabled=false;
      if(view==='states'){
        sctx.drawImage(fixed[level-1],0,0);
        for(const b of buttons.children) b.setAttribute('aria-pressed',Number(b.dataset.n)===level);
        $('coverage').textContent=new Intl.NumberFormat('fr',{style:'percent',maximumFractionDigits:1}).format(states[level-1].couverture);
        $('image-caption').textContent=`Palier ${level} / 8 · Calque fixe`;
        canvas.setAttribute('aria-label',`Parchemin nu sous le masque EoS du palier ${level}`);
      }else{
        const rec=data.transitions[target-2], t=tick-fadeOut;
        sctx.drawImage(fixed[(t<0 ? target-1 : target)-1],0,0);
        if(t>=0&&t<run){
          // Display the bank and the four separately translated puffs.
          sprite(rec.banc,t);for(const p of rec.petits_nuages)sprite(p,t);
        }
        if(t<0){black(tick);}else if(t<fadeIn){black(fadeIn-t);}
        $('clock').textContent=`${String(tick).padStart(3,'0')} / ${total}`;
        $('timeline').value=tick;
        $('phase').textContent=tick===0?'Palier de départ':t<0?'Fondu au noir':t<fadeIn?'Retour au nouveau palier':t<=hold?'Nuages encore immobiles':t<run?'Déplacement des nuages':'Palier dévoilé';
        const m = marker();
        $('image-caption').textContent = framed ? ((m.carte==='S01P01A'?`Cadrage du test · Cible ${m.id}`:'Cadre DS · Cadrage d’étude')+' · Sans repères') : `Vue entière · ${target-1} → ${target}`;
        canvas.setAttribute('aria-label',`Reconstruction EoS sur parchemin nu : transition du palier ${target-1} au palier ${target}`);
      }
      if(framed){
        const [dw,dh]=data.taille_ecran_ds, m=marker();
        const [x,y]=m.carte==='S01P01A'?m.position:[160,96];
        const left=clamp(x-dw/2,0,w-dw), top=clamp(y-dh/2,0,h-dh);
        resize(dw,dh);context.drawImage(scratch,left,top,dw,dh,0,0,dw,dh);
      }else{resize(w,h);context.drawImage(scratch,0,0);}
    }
    $('size-caption').textContent=`${canvas.width} × ${canvas.height} px`;
  }
  function updatePlay(){
    $('play').innerHTML=playing?'Pause <span aria-hidden="true">Ⅱ</span>':`${tick===total?'Rejouer':'Lire'} <span aria-hidden="true">▷</span>`;
  }
  function stop(){cancelAnimationFrame(timer);playing=false;updatePlay();}
  function seek(t){stop();tick=clamp(t,0,total);draw();updatePlay();}
  function play(){
    if(!base) return;
    if(playing){stop();return;}
    if(tick===total)tick=0;
    const start=performance.now(), from=tick;playing=true;updatePlay();
    const step=(now)=>{
      if(!playing)return;
      const n=Math.min(total,from+Math.floor(Math.max(now-start,0)*freq/1000));
      if(n!==tick){tick=n;draw();}
      if(tick===total){stop();return;}
      timer=requestAnimationFrame(step);
    };
    timer=requestAnimationFrame(step);
  }
  tab.forEach(b=>b.addEventListener('click',()=>selectView(b.dataset.vue)));
  $('watch').addEventListener('click',()=>selectView('demo'));
  $('viewport').addEventListener('click',()=>{crop=!crop;draw();});
  $('to-animation').addEventListener('click',()=>{target=Math.max(level,2);$('transition').value=target;seek(0);selectView('demo');});
  $('transition').addEventListener('change',e=>{target=Number(e.target.value);seek(0);});
  $('timeline').max=total;
  $('timeline').addEventListener('input',e=>seek(Number(e.target.value)));
  $('play').addEventListener('click',play);
  $('reset').addEventListener('click',()=>seek(0));
  document.addEventListener('visibilitychange',()=>{if(document.hidden)stop();});
  Promise.all([load(data.fond),Promise.all(states.map(a=>load(a.uri))),Promise.all(Object.entries(poses).map(async ([k,v])=>[k,await load(v.uri)]))]).then(([p,q,r])=>{
    base=p;fixed=q;sprites=Object.fromEntries(r);selectView('base');
    document.documentElement.dataset.ready='true';
  }).catch(()=>{ $('image-caption').textContent='Impossible de charger les calques intégrés.'; });
})();
