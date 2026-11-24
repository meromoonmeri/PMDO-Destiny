'use strict';
const fs=require('node:fs'),assert=require('node:assert/strict');
const data=s=>JSON.parse(s.split('<script id="donnees" type="application/json">')[1].split('</script>')[0]);

// Remove only the separately verified, additive artwork revision.
function horsBalade(d,reference){
 const {balade_nuit:b,...rest}=d;
 if(!b)return d;
 assert.equal(Object.keys(b.fonds).length,15);assert.equal(Object.keys(b.lumieres).length,15);
 assert.deepEqual(Object.keys(b.ronces),['guilde_destiny_carrefour']);
 assert.equal(Object.values(b.lumieres).reduce((n,q)=>n+q.length,0),32);
 return {...rest,film:reference.film,reference:{...d.reference,salon:reference.reference.salon}};
}

// Verifier-raccords checks these exceptions against the last full preview.
function horsRaccords(d,reference){
 d=horsBalade(d,reference);
 const {raccords_bois:fix,...rest}=d;
 if(!fix)return d;
 const report=JSON.parse(fs.readFileSync(require('node:path').join(__dirname,'../Verdure/Index-raccords.json'),'utf8'));
 const expected=Object.fromEntries(report.salles.filter(r=>r.pixels_modifies).map(r=>[r.salle,r.bordures.filter(q=>q.distance_tige_axe_px).length]));
 assert.deepEqual(fix.rives,expected);assert.equal(fix.escalier,'guilde_destiny_accueil');
 const oldRooms=new Map(reference.rooms.map(r=>[r.id,r]));
 rest.rooms=d.rooms.map(r=>r.id===fix.escalier?{...r,base:oldRooms.get(r.id).base}:r);
 rest.lianes=Object.fromEntries(Object.entries(d.lianes).map(([id,q])=>[id,fix.rives[id]?{...q,s:reference.lianes[id].s,t:reference.lianes[id].t}:q]));
 if(fix.film_recalcule){rest.film=reference.film;rest.reference={...d.reference,salon:reference.reference.salon};}
 return rest;
}
module.exports={data,horsBalade,horsRaccords};
