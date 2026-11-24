/* The atlas clock and placements. Works in the offline page and in the film exporter. */
(function(factory){const E=factory();if(typeof module==='object'&&module.exports)module.exports=E;else globalThis.AtlasEos=E;})(function(){
 'use strict';
 const clip=(n,a,b)=>Math.max(a,Math.min(b,n));
 const fade=(n,d)=>clip(n/d,0,1);
 const px=v=>Math.trunc(v/256);
 const fixed=v=>v*256;
 function direction(dx,dy){
   const x=Math.abs(dx),y=Math.abs(dy);
   if(y>x*2)return dy<0?4:0;
   if(x>y*2)return dx<0?6:2;
   return dx<0?(dy<0?5:7):(dy<0?3:1);
 }
 function travel(D,key){
   const rec=D.trajets[key],from=D.lieux[rec.depart].position,to=D.lieux[rec.but].position;
   const a=from.map(fixed),b=to.map(fixed);
   let r=Math.max(1,Math.trunc(Math.hypot(b[0]-a[0],b[1]-a[1])/0x200));
   const walk=16+rec.attente_depart, arrive=walk+r, departFade=16, finish=arrive+60, end=finish+60;
   const first=a.slice();let p=a.slice(),d=0,begin=0;const steps=[{p:first,d,begin}];
   // _0230FE78, _0230FF04, sub_0200514C: (current*r+target)/(r+1), r--,
   // then copy target exactly on the first non-moving frame.
   for(let i=0;r>0;i++,r--){
     const q=p.map((v,j)=>Math.trunc((v*r+b[j])/(r+1)));
     const nd=direction(q[0]-p[0],q[1]-p[1]);
     if(d!==nd){d=nd;begin=walk+i;}
     steps.push({p:q,d,begin});p=q;
   }
   steps.push({p:b,d,begin});
   return {...rec,key,from,to,steps,walk,arrive,finish,end,departFade};
 }
 function makePlan(D,part='film',route='blizzard'){
   const T=travel(D,route),U=D.deblocage,acts=[],events=[],marks=[];let tick=0;
   if(part!=='voyage'){
     acts.push({part:'deblocage',start:tick,end:tick+U.ticks});
     marks.push({key:'avant',t:tick+17,label:'Avant'},{key:'nuages',t:tick+U.nuage_depart+32,label:'Nuages'},
       {key:'jingle',t:tick+U.jingle,label:'Jingle'},{key:'rouge',t:tick+U.jingle+8,label:'Flash rouge'});
     events.push({key:'me',at:tick+U.jingle,until:tick+U.fin_lecture,fadeAt:null,gain:1});tick+=U.ticks;
   }
   if(part!=='deblocage'){
     acts.push({part:'voyage',start:tick,end:tick+T.end});
     marks.push({key:'depart',t:tick+T.departFade,label:'Départ'},{key:'marche',t:tick+T.walk+Math.floor((T.arrive-T.walk)/2),label:'En route'},
       {key:'arrive',t:tick+T.arrive,label:'Arrivée'});
     events.push({key:'bgm',at:tick+T.departFade,until:tick+T.end,fadeAt:tick+T.finish,gain:.91});tick+=T.end;
   }
   return {part,route,acts,events,marks,total:tick,T,U};
 }
 function atSequence(seq,t){
   const span=seq.reduce((sum,p)=>sum+p.ticks,0);
   let pos=Math.max(0,Math.trunc(t))%span;
   for(const p of seq){if(pos<p.ticks)return p;pos-=p.ticks;}
   return seq.at(-1);
 }
 function camera(center,mode){
   if(mode==='entier')return {x:0,y:0,w:504,h:336};
   return {x:px(clip(center[0],fixed(128),fixed(376)))-128,
           y:px(clip(center[1],fixed(96),fixed(240)))-96,w:256,h:192};
 }
 function frame(D,P,g,{view='ds',base='eos'}={}){
   const global=clip(Math.floor(g),0,P.total-1),act=P.acts.find(a=>global<a.end),t=global-act.start;
   const T=P.T,U=P.U, sprites=[];let level,center,phase,caption,kind,black=0,highlight=null,hero=null;
   const place=id=>D.lieux[id].position;
   const sprite=(family,pose,p,extra={})=>sprites.push({family,pose,x:p[0],y:p[1],...extra});
   if(act.part==='deblocage'){
     center=place(U.id).map(fixed);level=t<U.nuage_depart?U.palier_avant:U.palier_apres;
     black=1-fade(t,U.fondu_initial);
     if(t>=U.change && t<U.nuage_depart)black=fade(t-U.change,16);
     if(t>=U.nuage_depart && t<U.nuage_depart+16)black=1-fade(t-U.nuage_depart,16);
     if(t<U.change){phase='avant';kind='Avant le dégagement';caption='Au sud-ouest de la carte, la Région Gelée est encore sous les nuages.';}
     else if(t<U.nuage_fin){
       phase='nuages';kind='La brume se dissipe';caption='Le voile change, puis les bancs de nuages glissent hors de la région.';
       if(t>=U.nuage_depart){
         const e=Math.max(0,t-U.nuage_depart-30);
         for(const n of [D.transition.banc,...D.transition.petits_nuages].reverse()){
           sprite('brume',n.pose,n.origine.map((v,i)=>px(fixed(v)+n.vitesse_8_8[i]*e)));
         }
       }
     }
     else if(t<U.texte2){phase='texte';kind='Région Gelée révélée';caption='Les nuages se sont levés sur la Région Gelée et ses alentours.';}
     else if(t<U.jingle){phase='suite';kind='Région Gelée révélée';caption='En outre…';}
     else {
       phase=t<U.fin_lecture?'jingle':'sortie';kind='Île Blizzard débloquée';caption='Désormais, vous pouvez vous rendre sur l’Île Blizzard !';
       const age=t-U.jingle, m=atSequence(D.sequences_reperes['11'],age), a=atSequence(D.sequences_reperes['13'],age),target=place(U.id);
       highlight=m.pose===4?'rouge':m.pose===9?'jaune atténué':'jaune';
       sprite('reperes',m.pose,target,{id:U.id,usage:'clignotant'});sprite('reperes',a.pose,target,{id:U.id,usage:'fleche'});
       if(t>=U.fin_lecture)black=fade(t-U.fin_lecture,15);
     }
   }else{
     const step=t<T.walk?0:clip(t-T.walk+1,1,T.steps.length-1), s=T.steps[step];
     center=s.p;level=T.palier;
     const p=atSequence(D.pikachu.sequences[s.d],t-s.begin);
     for(const id of [T.depart,T.but])sprite('reperes',2,place(id),{id,usage:'fixe'});
     hero={x:px(s.p[0]),y:px(s.p[1]),fx:s.p[0],fy:s.p[1],dir:s.d,pose:p.pose};
     sprite('pikachu',p.pose,[hero.x+p.offset[0],hero.y+p.offset[1]]);
     black=1-fade(t,T.departFade);
     if(t<T.walk){phase='depart';kind='Départ de Bourg-Trésor';caption=`Direction ${T.nom==='Île Blizzard'?'l’Île Blizzard':'la Caverne Saline'}.`;}
     else if(t<T.arrive){phase='marche';kind='En route';caption='Pikachu marche sur la carte pendant que la caméra suit son déplacement.';}
     else {phase='arrive';kind='Arrivée au donjon';caption=T.nom;if(t>=T.finish)black=fade(t-T.finish,30);}
   }
   const cam=camera(center,view);
   return {part:act.part,global,t,phase,caption,kind,level,center,cam,sprites,black,highlight,hero,view,base,route:P.route};
 }
 function poseDef(D,s){
   return (s.family==='reperes'?D.reperes:s.family==='brume'?D.brume_mobile:D.pikachu.poses)[String(s.pose)];
 }
 return {clip,px,travel,makePlan,atSequence,camera,frame,poseDef};
});
